from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from supabase import create_client
from groq import Groq
from sentence_transformers import SentenceTransformer

app = FastAPI()

# ── CORS（允許 GitHub Pages 呼叫）──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 環境變數 ──
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ── 模型載入（只載入一次）──
_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    return _model

# ── Supabase ──
def get_db():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# ── 向量化 ──
def get_embedding(text: str) -> list:
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()

# ── 向量搜尋 ──
def search_chunks(query_embedding: list, match_count: int = 5, threshold: float = 0.3) -> list:
    db = get_db()
    result = db.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": match_count
    }).execute()
    return result.data or []

# ── AI 回答 ──
def generate_answer(query: str, context_chunks: list) -> str:
    client = Groq(api_key=GROQ_API_KEY)

    if not context_chunks:
        context = "（知識庫中未找到相關資料）"
    else:
        context = "\n\n---\n\n".join([
            f"【來源：{c.get('source_title', '未知')}】\n{c['content']}"
            for c in context_chunks
        ])

    system_prompt = """你是實威國際的 AI 知識庫助理。
你只能根據提供的知識庫內容回答問題，不可以使用知識庫以外的知識。

規則：
1. 只能使用提供的知識庫內容回答，並標明來源
2. 如果知識庫內容不足以回答，請直接說「知識庫中沒有找到相關資料，請聯繫客服」
3. 絕對不可以自行補充或推測知識庫以外的資訊
4. 使用者用中文問，就用中文回答
5. 回答要清楚有條理，適當使用標題和條列"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"知識庫內容：\n{context}\n\n使用者問題：{query}"}
        ],
        max_tokens=2048,
        temperature=0.3
    )
    return response.choices[0].message.content

# ══════════════════════════════════
# API 端點
# ══════════════════════════════════

@app.get("/")
def root():
    return {"status": "ok", "message": "實威國際 AI 知識庫 API"}

@app.get("/health")
def health():
    return {"status": "ok"}

class SearchRequest(BaseModel):
    query: str
    match_count: int = 5
    threshold: float = 0.3

@app.post("/search")
def search(req: SearchRequest):
    try:
        # 1. 向量化
        embedding = get_embedding(req.query)

        # 2. 搜尋
        chunks = search_chunks(embedding, req.match_count, req.threshold)

        # 3. 取得來源
        sources = []
        if chunks:
            db = get_db()
            doc_ids = list(set(c['document_id'] for c in chunks))
            docs = db.table("documents").select("id,title,source_type,source_url").in_("id", doc_ids).execute()
            doc_map = {d['id']: d for d in (docs.data or [])}
            seen = set()
            for c in chunks:
                doc = doc_map.get(c['document_id'], {})
                c['source_title'] = doc.get('title', '未知來源')
                c['source_type']  = doc.get('source_type', 'file')
                c['source_url']   = doc.get('source_url', '')
                title = c['source_title']
                if title not in seen:
                    seen.add(title)
                    sources.append({
                        "title": title,
                        "type": c['source_type'],
                        "url": c['source_url']
                    })

        # 4. AI 回答
        answer = generate_answer(req.query, chunks)

        return {
            "success": True,
            "answer": answer,
            "sources": sources,
            "chunk_count": len(chunks)
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/stats")
def stats():
    try:
        db = get_db()
        docs = db.table("documents").select("source_type").execute()
        data = docs.data or []
        file_count = len([d for d in data if d['source_type'] == 'file'])
        web_count  = len([d for d in data if d['source_type'] == 'website'])
        return {
            "success": True,
            "total": len(data),
            "files": file_count,
            "websites": web_count
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
