
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import os

# --- 資料庫 ---
conn = sqlite3.connect("sample.db", check_same_thread=False)
c = conn.cursor()

# 建立資料表
c.execute("""
CREATE TABLE IF NOT EXISTS samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_name TEXT,
    user_name TEXT,
    borrow_date TEXT,
    return_date TEXT,
    note TEXT,
    image_path TEXT
)
""")

conn.commit()

# --- UI ---
st.set_page_config(page_title="3D列印樣品借出系統", layout="wide")
st.title("📦 3D列印樣品借出系統")

menu = st.sidebar.selectbox("選單", ["借出登記", "資料管理", "借出紀錄"])

# =====================
# 借出登記
# =====================
if menu == "借出登記":
    st.subheader("✏️ 借出登記")

    # 讀取資料
    samples = pd.read_sql("SELECT name FROM samples", conn)
    users = pd.read_sql("SELECT name FROM users", conn)

    col1, col2 = st.columns(2)

    with col1:
        sample_name = st.selectbox("樣品項目", samples["name"] if not samples.empty else [])

        user_name = st.selectbox("借出人員", users["name"] if not users.empty else [])

        borrow_date = st.date_input("借出日期", date.today())
        return_date = st.date_input("歸還日期")

    with col2:
        uploaded_file = st.file_uploader("樣品圖片", type=["png", "jpg", "jpeg"])

        note = st.text_area("備註")

        if uploaded_file:
            st.image(uploaded_file, caption="預覽圖片", use_column_width=True)

    if st.button("確認借出"):
        image_path = ""

        if uploaded_file:
            os.makedirs("images", exist_ok=True)
            image_path = f"images/{uploaded_file.name}"
            with open(image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        c.execute("""
        INSERT INTO records (sample_name, user_name, borrow_date, return_date, note, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (sample_name, user_name, str(borrow_date), str(return_date), note, image_path))

        conn.commit()
        st.success("✅ 借出登記完成！")

# =====================
# 資料管理
# =====================
elif menu == "資料管理":
    st.subheader("⚙️ 基本資料管理")

    col1, col2 = st.columns(2)

    # 樣品管理
    with col1:
        st.markdown("### 📦 新增樣品")
        new_sample = st.text_input("樣品名稱")

        if st.button("新增樣品"):
            c.execute("INSERT INTO samples (name) VALUES (?)", (new_sample,))
            conn.commit()
            st.success("新增成功")

        st.markdown("### 樣品列表")
        st.dataframe(pd.read_sql("SELECT * FROM samples", conn))

    # 人員管理
    with col2:
        st.markdown("### 👤 新增人員")
        new_user = st.text_input("人員名稱")

        if st.button("新增人員"):
            c.execute("INSERT INTO users (name) VALUES (?)", (new_user,))
            conn.commit()
            st.success("新增成功")

        st.markdown("### 人員列表")
        st.dataframe(pd.read_sql("SELECT * FROM users", conn))

# =====================
# 借出紀錄
# =====================
elif menu == "借出紀錄":
    st.subheader("📊 借出紀錄")

    df = pd.read_sql("SELECT * FROM records ORDER BY id DESC", conn)

    if not df.empty:
        for index, row in df.iterrows():
            with st.expander(f"{row['sample_name']} - {row['user_name']}"):
                col1, col2 = st.columns([1, 2])

                with col1:
                    if row["image_path"] and os.path.exists(row["image_path"]):
                        st.image(row["image_path"])

                with col2:
                    st.write(f"借出人員：{row['user_name']}")
                    st.write(f"借出日期：{row['borrow_date']}")
                    st.write(f"歸還日期：{row['return_date']}")
                    st.write(f"備註：{row['note']}")
    else:
        st.info("目前沒有借出紀錄")
