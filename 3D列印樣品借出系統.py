import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import requests
import base64

# =====================
# GitHub 設定
# =====================
GITHUB_TOKEN = "你的token"
REPO = "Coffee-Who/3dprinter"
BRANCH = "main"
FOLDER = "image"

# =====================
# 上傳圖片到 GitHub
# =====================
def upload_to_github(file):
    file_content = file.read()
    encoded = base64.b64encode(file_content).decode()

    url = f"https://api.github.com/repos/{REPO}/contents/{FOLDER}/{file.name}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}"
    }

    data = {
        "message": f"upload {file.name}",
        "content": encoded,
        "branch": BRANCH
    }

    response = requests.put(url, json=data, headers=headers)

    if response.status_code in [200, 201]:
        return response.json()["content"]["download_url"]
    else:
        st.error("❌ 上傳 GitHub 失敗")
        return ""

# =====================
# 資料庫
# =====================
conn = sqlite3.connect("sample.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_name TEXT,
    user_name TEXT,
    borrow_date TEXT,
    return_date TEXT,
    note TEXT,
    image_url TEXT
)
""")

conn.commit()

# =====================
# UI
# =====================
st.set_page_config(page_title="3D列印樣品借出系統", layout="centered")
st.title("📦 3D列印樣品借出登記")

# =====================
# 表單（重點）
# =====================
with st.form("borrow_form"):
    st.subheader("✏️ 借出登記表單")

    sample_name = st.text_input("1️⃣ 樣品名稱")
    user_name = st.text_input("2️⃣ 借出人員")

    borrow_date = st.date_input("3️⃣ 借出日期", date.today())
    return_date = st.date_input("4️⃣ 歸還日期")

    uploaded_file = st.file_uploader("5️⃣ 上傳樣品圖片", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        st.image(uploaded_file, caption="圖片預覽")

    note = st.text_area("6️⃣ 備註")

    submit = st.form_submit_button("📤 送出")

# =====================
# 提交
# =====================
if submit:
    image_url = ""

    if uploaded_file:
        image_url = upload_to_github(uploaded_file)

    c.execute("""
    INSERT INTO records (sample_name, user_name, borrow_date, return_date, note, image_url)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (sample_name, user_name, str(borrow_date), str(return_date), note, image_url))

    conn.commit()
    st.success("✅ 登記完成！")

# =====================
# 紀錄顯示
# =====================
st.subheader("📊 借出紀錄")

df = pd.read_sql("SELECT * FROM records ORDER BY id DESC", conn)

for index, row in df.iterrows():
    with st.expander(f"{row['sample_name']} - {row['user_name']}"):
        if row["image_url"]:
            st.image(row["image_url"])

        st.write(f"借出日期：{row['borrow_date']}")
        st.write(f"歸還日期：{row['return_date']}")
        st.write(f"備註：{row['note']}")
