from sentence_transformers import SentenceTransformer
import streamlit as st

@st.cache_resource
def load_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def get_embedding(text: str) -> list:
    model = load_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

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
