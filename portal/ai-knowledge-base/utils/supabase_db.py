from supabase import create_client
import streamlit as st

@st.cache_resource
def get_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

def insert_document(title: str, source_type: str, source_url: str = None) -> str:
    """新增文件記錄，回傳 document_id"""
    db = get_client()
    result = db.table("documents").insert({
        "title": title,
        "source_type": source_type,
        "source_url": source_url
    }).execute()
    return result.data[0]["id"]

def insert_chunks(document_id: str, chunks: list, embeddings: list):
    """批次新增段落與向量"""
    db = get_client()
    rows = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        rows.append({
            "document_id": document_id,
            "content": chunk,
            "embedding": embedding,
            "chunk_index": i
        })
    db.table("chunks").insert(rows).execute()

def search_chunks(query_embedding: list, match_count: int = 5, threshold: float = 0.3) -> list:
    """向量相似度搜尋"""
    db = get_client()
    result = db.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": match_count
    }).execute()
    return result.data or []

def get_all_documents() -> list:
    """取得所有文件列表"""
    db = get_client()
    result = db.table("documents").select("*").order("created_at", desc=True).execute()
    return result.data or []

def delete_document(document_id: str):
    """刪除文件（chunks 會自動 cascade 刪除）"""
    db = get_client()
    db.table("documents").delete().eq("id", document_id).execute()

def get_document_chunk_count(document_id: str) -> int:
    """取得文件的段落數"""
    db = get_client()
    result = db.table("chunks").select("id", count="exact").eq("document_id", document_id).execute()
    return result.count or 0

def insert_crawl_job(url: str, max_pages: int) -> str:
    """新增爬蟲任務"""
    db = get_client()
    result = db.table("crawl_jobs").insert({
        "url": url,
        "max_pages": max_pages,
        "status": "pending"
    }).execute()
    return result.data[0]["id"]

def update_crawl_job(job_id: str, status: str, pages_done: int = 0):
    """更新爬蟲任務狀態"""
    db = get_client()
    db.table("crawl_jobs").update({
        "status": status,
        "pages_done": pages_done
    }).eq("id", job_id).execute()

def get_crawl_jobs() -> list:
    """取得所有爬蟲任務"""
    db = get_client()
    result = db.table("crawl_jobs").select("*").order("created_at", desc=True).execute()
    return result.data or []
