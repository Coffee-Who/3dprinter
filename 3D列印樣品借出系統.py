import streamlit as st
import requests

st.title("📦 3D列印樣品借出系統")

url = "https://api.github.com/repos/Coffee-Who/3dprinter/contents/image?ref=main"
response = requests.get(url)

st.write("API狀態:", response.status_code)
st.write("回傳內容:", response.text)  # 👈 關鍵debug

if response.status_code == 200:
    data = response.json()

    for file in data:import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# =====================
# 🔥 1. 圖片清單（唯一來源）
# =====================
image_names = [
    "sample1.jpg",
    "sample2.png",
    "sample3.jpg"
]

BASE_URL = "https://raw.githubusercontent.com/Coffee-Who/3dprinter/main/image/"

# =====================
# 2. DB
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
# 3. 判斷是否借出
# =====================
def is_borrowed(sample_name):
    df = pd.read_sql("""
        SELECT * FROM records
        WHERE sample_name=? AND status='borrowed'
    """, conn, params=(sample_name,))
    return not df.empty

# =====================
# 4. UI
# =====================
st.set_page_config(layout="wide")
st.title("📦 3D列印樣品借出系統（穩定版）")

cols = st.columns(4)

# =====================
# 5. 顯示樣品
# =====================
for i, name in enumerate(image_names):
    col = cols[i % 4]

    with col:
        img_url = BASE_URL + name

        st.image(img_url, caption=name, use_container_width=True)

        if is_borrowed(name):
            st.error("🔴 已借出")

            if st.button(f"歸還_{i}"):
                c.execute("""
                    UPDATE records
                    SET return_date=?, status='returned'
                    WHERE sample_name=? AND status='borrowed'
                """, (str(date.today()), name))

                conn.commit()
                st.success("已歸還")
                st.rerun()

        else:
            st.success("🟢 可借出")

            with st.form(f"form_{i}"):
                user = st.text_input("借出人員", key=f"user_{i}")
                borrow_date = st.date_input("借出日期", date.today())
                return_date = st.date_input("預計歸還日期")

                submit = st.form_submit_button("借出")

                if submit:
                    if user.strip() == "":
                        st.warning("請輸入借出人員")
                    else:
                        c.execute("""
                            INSERT INTO records
                            (sample_name, user_name, borrow_date, return_date, status)
                            VALUES (?, ?, ?, ?, 'borrowed')
                        """, (name, user, str(borrow_date), str(return_date)))

                        conn.commit()
                        st.success("借出成功")
                        st.rerun()

# =====================
# 6. 紀錄
# =====================
st.subheader("📊 借出紀錄")

df = pd.read_sql("SELECT * FROM records ORDER BY id DESC", conn)
st.dataframe(df, use_container_width=True)
        if file["name"].lower().endswith(("jpg", "png", "jpeg")):
            st.image(file["download_url"], caption=file["name"])
else:
    st.error("抓不到 GitHub 圖片")
