import streamlit as st
import requests
import sqlite3
import pandas as pd
from datetime import date

# 快取（避免 GitHub 限制）
@st.cache_data(ttl=600)
def get_images():
    url = "https://api.github.com/repos/Coffee-Who/3dprinter/contents/image?ref=main"
    response = requests.get(url)
    data = response.json()

    images = []
    if isinstance(data, list):
        for file in data:
            name = file.get("name", "")
            if name.lower().endswith(("png", "jpg", "jpeg")):
                images.append({
                    "name": name,
                    "url": file.get("download_url", "")
                })

    return images
