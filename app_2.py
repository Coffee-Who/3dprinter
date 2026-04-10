import streamlit as st
import sqlite3
from datetime import date
import pandas as pd

# =========================
# 📦 1. 樣品清單配置
# =========================
# 建議將顯示名稱與檔案名稱分開，UI 會更專業
image_items = [
    {"name": "sample1.jpg", "label": "樣品 A (精密齒輪)"},
    {"name": "sample2.jpg", "label": "樣品 B (外殼原型)"},
    {"name": "sample3.jpg", "label": "樣品 C (支架組件)"}
]

BASE_URL = "https://raw.githubusercontent.com/Coffee-Who/3dprinter/main/image/"

# =========================
# 🗄️ 2. 資料庫功能優化
# =========================
def get_db_connection():
    # 使用 check_same_thread=False 確保在 Streamlit 中穩定運行
    conn = sqlite3.connect("sample_v3.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_name TEXT,
        user_name TEXT,
        borrow_date TEXT,
        expected_return TEXT,
        status TEXT
    )
    """)
    conn.commit()
    conn.close()

def is_borrowed(name):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM records WHERE sample_name=? AND status='borrowed'", (name,))
    result = c.fetchone()[0] > 0
    conn.close()
    return result

# =========================
# 🖥️ 3. 頁面設定
# =========================
st.set_page_config(page_title="3D列印借出系統 v3.0", layout="wide", page_icon="🖨️")
init_db()

st.title("📦 3D列印樣品管理系統")
st.markdown("---")

# 使用側邊欄導航，減少單一頁面過於擁擠導致的渲染錯誤
tab1, tab2 = st.tabs(["🏗️ 借還中心", "📊 歷史紀錄庫"])

# =========================
# 🏗️ Tab 1: 樣品借還中心
# =========================
with tab1:
    cols = st.columns(3)

    for i, item in enumerate(image_items):
        name = item["name"]
        label = item["label"]
        col = cols[i % 3]

        with col:
            # 使用 container 包裹，增加 React 渲染穩定性
            with st.container(border=True):
                st.subheader(label)
                img_url = BASE_URL + name
                st.image(img_url, use_container_width=True)

                if is_borrowed(name):
                    st.error("🔴 狀態：已借出")
                    
                    # 歸還邏輯
                    # 這裡的 key 結合了 index 與 name，確保唯一
                    if st.button(f"確認歸還", key=f"btn_ret_{name}_{i}"):
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("""
                            UPDATE records 
                            SET status='returned' 
                            WHERE sample_name=? AND status='borrowed'
                        """, (name,))
                        conn.commit()
                        conn.close()
                        st.toast(f"✅ {name} 已歸還")
                        st.rerun()
                
                else:
                    st.success("🟢 狀態：在庫中")
                    
                    # 借出表單：使用 expander 節省空間
                    with st.expander("填寫借出單"):
                        with st.form(key=f"form_borrow_{name}_{i}"):
                            user = st.text_input("借出人員", key=f"user_{name}_{i}")
                            b_date = st.date_input("借出日期", date.today(), key=f"bdate_{name}_{i}")
                            r_date = st.date_input("預計歸還日期", key=f"rdate_{name}_{i}")
                            
                            submit = st.form_submit_button("送出申請")

                            if submit:
                                if not user.strip():
                                    st.warning("請輸入人員姓名")
                                else:
                                    conn = get_db_connection()
                                    c = conn.cursor()
                                    c.execute("""
                                        INSERT INTO records (sample_name, user_name, borrow_date, expected_return, status)
                                        VALUES (?, ?, ?, ?, 'borrowed')
                                    """, (name, user, str(b_date), str(r_date), 'borrowed'))
                                    conn.commit()
                                    conn.close()
                                    st.rerun()

# =========================
# 📊 Tab 2: 歷史紀錄庫
# =========================
with tab2:
    st.subheader("📋 所有借還明細")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT id, sample_name, user_name, borrow_date, expected_return, status FROM records ORDER BY id DESC", conn)
    conn.close()

    if not df.empty:
        # 格式化顯示表格
        st.dataframe(
            df, 
            column_config={
                "id": "編號",
                "sample_name": "樣品名稱",
                "user_name": "借用人",
                "borrow_date": "借出日期",
                "expected_return": "預計歸還",
                "status": "狀態"
            },
            use_container_width=True,
            hide_index=True
        )
        
        # 下載功能
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 下載報表 (CSV)",
            data=csv,
            file_name=f"3d_print_records_{date.today()}.csv",
            mime="text/csv",
        )
    else:
        st.info("目前尚無任何借還紀錄。")

# =========================
# ℹ️ 頁尾腳註
# =========================
st.markdown("---")
st.caption("3D列印樣品借出系統 v3.0 | 穩定增強版")
