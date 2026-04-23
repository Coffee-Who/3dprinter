import os
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.Client()
collection = client.get_or_create_collection("docs")

folder = "documents"

for file in os.listdir(folder):
    with open(f"{folder}/{file}", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    chunks = [text[i:i+500] for i in range(0, len(text), 500)]

    for i, chunk in enumerate(chunks):
        emb = model.encode(chunk).tolist()
        collection.add(
            documents=[chunk],
            embeddings=[emb],
            ids=[f"{file}_{i}"]
        )

print("完成")
