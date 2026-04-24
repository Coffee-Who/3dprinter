import requests
import streamlit as st

JINA_API_KEY = "jina_ea129d66ed154c3595c2f7c3f6cffe1biNBryTf2VV0b60NfVp5hEoEDhX71"
JINA_URL = "https://api.jina.ai/v1/embeddings"
JINA_MODEL = "jina-embeddings-v2-base-zh"

def get_embedding(text: str) -> list:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {JINA_API_KEY}"
    }
    response = requests.post(
        JINA_URL,
        headers=headers,
        json={"input": [text], "model": JINA_MODEL},
        timeout=30
    )
    if response.status_code != 200:
        raise Exception(f"Jina API 錯誤 {response.status_code}: {response.text[:200]}")

    result = response.json()
    embedding = result["data"][0]["embedding"]
    norm = sum(x**2 for x in embedding) ** 0.5 or 1.0
    return [x / norm for x in embedding]

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """將長文字切成段落"""
    chunks = []
    words = text.split()
    i = 0
    while i < len(words):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks
