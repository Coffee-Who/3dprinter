from fastapi import FastAPI
import chromadb
from sentence_transformers import SentenceTransformer
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

client = chromadb.Client()
collection = client.get_or_create_collection("docs")

model = SentenceTransformer("all-MiniLM-L6-v2")

claude = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

@app.get("/ask")
def ask(q: str):
    query_vec = model.encode(q).tolist()

    results = collection.query(
        query_embeddings=[query_vec],
        n_results=3
    )

    context = "\n".join(results["documents"][0])

    prompt = f"""
你是公司內部知識庫助理，請根據以下內容回答：

{context}

問題：{q}

如果找不到答案，請回覆：此問題超出知識庫範圍
"""

    response = claude.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return {"answer": response.content[0].text}
