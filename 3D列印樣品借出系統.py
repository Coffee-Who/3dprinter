import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
import requests

# =====================
# GitHub 圖片來源
# =====================
GITHUB_API = "https://api.github.com/repos/Coffee-Who/3dprinter/contents/image"

def get_images():
    response = requests.get(GITHUB_API)
    data = response.json()

    images = []
    for file in data:
        if file["name"].lower().endswith(("png", "jpg", "jpeg")):
            images.append({
                "name": file["name"],
                "url": file["download_url"]
            })
    return images

# =====================
# DB
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
    status TEXT
)
""")
conn.commit()

# =====================
# 查詢是否已借出
# =====================
def is_borrowed(sample_name):
    df = pd.read_sql(f"""
    SELECT * FROM records 
    WHERE sample_name='{sample_name}' AND status='borrowed'
    """, conn)
    return not df.empty

# =====================
# UI
# =====================
st.set_page_config(layout="wide")
st.title("📦 3D列印樣品借出系統")

images = get_images()

# =====================
# 顯示樣品
# =====================
cols = st.columns(4)

for i, img in enumerate(images):
    col = cols[i % 4]

    with col:
        st.image(img["url"], use_column_width=True)
        st.write(img["name"])

        borrowed = is_borrowed(img["name"])

        if borrowed:
            st.error("🔴 已借出")

            # 歸還功能
            user = st.text_input(f"歸還人員_{i}")
            if st.button(f"確認歸還_{i}"):
                c.execute("""
                UPDATE records
                SET return_date=?, status='returned'
                WHERE sample_name=? AND status='borrowed'
                """, (str(date.today()), img["name"]))
                conn.commit()
                st.success("已歸還")
                st.rerun()

        else:
            st.success("🟢 可借出")

            with st.form(f"borrow_form_{i}"):
                user = st.text_input("借出人員")
                borrow_date = st.date_input("借出日期", date.today())
                return_date = st.date_input("預計歸還日期")

                submit = st.form_submit_button("借出")

                if submit:
                    c.execute("""
                    INSERT INTO records 
                    (sample_name, user_name, borrow_date, return_date, status)
                    VALUES (?, ?, ?, ?, 'borrowed')
                    """, (img["name"], user, str(borrow_date), str(return_date)))

                    conn.commit()
                    st.success("借出成功")
                    st.rerun()

# =====================
# 歷史紀錄
# =====================
st.subheader("📊 借出紀錄")

df = pd.read_sql("SELECT * FROM records ORDER BY id DESC", conn)
st.dataframe(df)
