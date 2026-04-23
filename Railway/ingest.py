import os
import requests
from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.Client()
collection = client.get_or_create_collection("docs")

def load_web(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text()

def add(text, id):
    chunks = [text[i:i+500] for i in range(0, len(text), 500)]
    for i, chunk in enumerate(chunks):
        emb = model.encode(chunk).tolist()
        collection.add(
            documents=[chunk],
            embeddings=[emb],
            ids=[f"{id}_{i}"]
        )

# 📂 文件
for file in os.listdir("documents"):
    with open(f"documents/{file}", encoding="utf-8", errors="ignore") as f:
        add(f.read(), file)

# 🌐 網站
urls = [
    "https://example.com"
]

for url in urls:
    text = load_web(url)
    add(text, url)

print("完成")
