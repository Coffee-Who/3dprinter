import streamlit as st
import sqlite3
from datetime import date

# =========================
# 📦 樣品清單（唯一來源）
# =========================
image_items = [
    "sample1.jpg",
    "sample2.jpg",
    "sample3.jpg"
]

BASE_URL = "https://raw.githubusercontent.com/Coffee-Who/3dprinter/main/image/"

# =========================
# 🗄️ DB 安全連線（v3 核心）
# =========================
DB_PATH = "sample.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def execute_db(query, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def fetch_all(query, params=()):
    conn = get_conn()
    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

# =========================
# 🏗️ 建表（安全）
# =========================
execute_db("""
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sample_name TEXT,
    user_name TEXT,
    borrow_date TEXT,
    return_date TEXT,
    status TEXT
)
""")

# =========================
# 🔍 是否借出
# =========================
def is_borrowed(name):
    rows = fetch_all("""
        SELECT COUNT(*) FROM records
        WHERE sample_name=? AND status='borrowed'
    """, (name,))
    return rows[0][0] > 0

# =========================
# 🖥️ UI
# =========================
st.set_page_config(page_title="3D列印借出系統 v3", layout="wide")
st.title("📦 3D列印樣品借出系統（企業 v3 穩定版）")

cols = st.columns(4)

# =========================
# 📦 樣品卡片
# =========================
for i, name in enumerate(image_items):
    col = cols[i % 4]

    with col:
        img_url = BASE_URL + name
        st.image(img_url, caption=name, use_container_width=True)

        # =====================
        # 🔴 已借出
        # =====================
        if is_borrowed(name):
            st.error("🔴 已借出")

            if st.button(f"歸還_{i}"):
                execute_db("""
                    UPDATE records
                    SET return_date=?, status='returned'
                    WHERE sample_name=? AND status='borrowed'
                """, (str(date.today()), name))

                st.success("已歸還")
                st.rerun()

        # =====================
        # 🟢 可借出
        # =====================
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
                        execute_db("""
                            INSERT INTO records
                            (sample_name, user_name, borrow_date, return_date, status)
                            VALUES (?, ?, ?, ?, 'borrowed')
                        """, (name, user, str(borrow_date), str(return_date)))

                        st.success("借出成功")
                        st.rerun()

# =========================
# 📊 借出紀錄
# =========================
st.divider()
st.subheader("📊 借出紀錄")

rows = fetch_all("""
    SELECT sample_name, user_name, borrow_date, return_date, status
    FROM records
    ORDER BY id DESC
""")

st.dataframe(rows, use_container_width=True)
