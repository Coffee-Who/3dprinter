import streamlit as st
import sqlite3
from datetime import date
import pandas as pd

# =========================
# 📦 1. 樣品清單配置
# =========================
IMAGE_ITEMS = [
    {"name": "sample1.jpg", "label": "3D 列印齒輪"},
    {"name": "sample2.jpg", "label": "原型外殼"},
    {"name": "sample3.jpg", "label": "精密螺絲元件"}
]
BASE_URL = "https://raw.githubusercontent.com/Coffee-Who/3dprinter/main/image/"

# =========================
# 🗄️ 2. 資料庫邏輯（封裝化）
# =========================
DB_NAME = "sample_v2.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_name TEXT,
            user_name TEXT,
            borrow_date TEXT,
            expected_return TEXT,
            actual_return TEXT,
            status TEXT
        )
        """)
        conn.commit()

def get_db_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def is_borrowed(name):
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM records WHERE sample_name=? AND status='borrowed'", (name,))
        return c.fetchone()[0] > 0

# =========================
# 🖥️ 3. UI 設定
# =========================
st.set_page_config(page_title="3D列印管理系統", layout="wide", page_icon="📦")
init_db()

st.title("📦 3D列印樣品借出系統")

# 側邊欄選單
menu = st.sidebar.radio("系統選單", ["樣品借還中心", "歷史紀錄查詢"])

if menu == "樣品借還中心":
    cols = st.columns(3) # 調整為 3 欄讓表單空間更大

    for i, item in enumerate(IMAGE_ITEMS):
        name = item["name"]
        label = item["label"]
        col = cols[i % 3]

        with col:
            st.markdown(f"### {label}")
            st.image(BASE_URL + name, use_container_width=True)

            borrowed_status = is_borrowed(name)

            if borrowed_status:
                st.error("🔴 狀態：已借出")
                if st.button(f"確認歸還 ({i})", use_container_width=True):
                    with get_db_connection() as conn:
                        c = conn.cursor()
                        c.execute("""
                            UPDATE records 
                            SET actual_return=?, status='returned' 
                            WHERE sample_name=? AND status='borrowed'
                        """, (str(date.today()), name))
                        conn.commit()
                    st.success(f"{name} 已成功歸還！")
                    st.rerun()
            else:
                st.success("🟢 狀態：在庫中")
                with st.expander("填寫借出表單"):
                    with st.form(f"form_{i}"):
                        user = st.text_input("借出人姓名", key=f"user_{i}")
                        b_date = st.date_input("借出日期", date.today(), key=f"b_{i}")
                        r_date = st.date_input("預計歸還日期", key=f"r_{i}")
                        
                        submit = st.form_submit_button("送出借出申請", use_container_width=True)

                        if submit:
                            if not user.strip():
                                st.warning("請輸入借出人員名稱")
                            else:
                                with get_db_connection() as conn:
                                    c = conn.cursor()
                                    c.execute("""
                                        INSERT INTO records (sample_name, user_name, borrow_date, expected_return, status)
                                        VALUES (?, ?, ?, ?, 'borrowed')
                                    """, (name, user, str(b_date), str(r_date)))
                                    conn.commit()
                                st.rerun()

elif menu == "歷史紀錄查詢":
    st.subheader("📊 全系統借還紀錄匯總")
    with get_db_connection() as conn:
        # 使用 Pandas 讀取資料會比直接拿 Tuple 好看很多
        df = pd.read_sql_query("SELECT * FROM records ORDER BY id DESC", conn)
    
    if not df.empty:
        # 美化表格顯示
        st.dataframe(df, use_container_width=True)
        
        # 提供 CSV 下載（企業常用需求）
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 下載紀錄報表 (CSV)", csv, "inventory_report.csv", "text/csv")
    else:
        st.info("目前尚無借還紀錄。")
