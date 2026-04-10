import streamlit as st
import requests

st.title("📦 3D列印樣品借出系統")

url = "https://api.github.com/repos/Coffee-Who/3dprinter/contents/image?ref=main"
response = requests.get(url)

st.write("API狀態:", response.status_code)
st.write("回傳內容:", response.text)  # 👈 關鍵debug

if response.status_code == 200:
    data = response.json()

    for file in data:
        if file["name"].lower().endswith(("jpg", "png", "jpeg")):
            st.image(file["download_url"], caption=file["name"])
else:
    st.error("抓不到 GitHub 圖片")
