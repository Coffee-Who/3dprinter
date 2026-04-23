from fastapi import FastAPI
import chromadb
from sentence_transformers import SentenceTransformer
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.Client()
collection = client.get_or_create_collection("docs")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def ask_groq(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [{"role": "user", "content": prompt}]
    }

    r = requests.post(url, headers=headers, json=data)
    return r.json()["choices"][0]["message"]["content"]

@app.get("/ask")
def ask(q: str):
    q_emb = model.encode(q).tolist()

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=3
    )

    context = "\n".join(results["documents"][0])

    prompt = f"""
你是公司知識庫AI，請依據內容回答：

{context}

問題：{q}

請用中文回答，並整理重點。
"""

    answer = ask_groq(prompt)

    return {"answer": answer}
