import streamlit as st
import requests
import sqlite3
import pandas as pd
from datetime import date

# =====================
# GitHub 設定
# =====================
GITHUB_API = "https://api.github.com/repos/Coffee-Who/3dprinter/contents/image"

# =====================
# 讀取 GitHub 圖片（已防呆）
# =====================
@st.cache_data(ttl=600)
def get_images():
    try:
        response = requests.get(GITHUB_API)

        if response.status_code != 200:
            st.error(f"GitHub API 錯誤：{response.status_code}")
            return []

        data = response.json()

        if not isinstance(data, list):
            st.error("GitHub 回傳格式錯誤")
            return []

        images = []
        for file in data:
            if isinstance(file, dict):
                name = file.get("name", "")
                url = file.get("download_url", "")

                if name.lower().endswith(("png", "jpg", "jpeg")):
                    images.append({
                        "name": name,
                        "url": url
                    })

        return images

    except Exception as e:
        st.error(f"讀取圖片失敗：{e}")
        return []

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
# 判斷是否借出
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

if len(images) == 0:
    st.warning("⚠️ 沒有抓到任何圖片，請確認 GitHub 路徑")
    st.stop()

# =====================
# 樣品卡片
# =====================
cols = st.columns(4)

for i, img in enumerate(images):
    col = cols[i % 4]

    with col:
        st.image(img["url"], use_column_width=True)
        st.write(f"📌 {img['name']}")

        borrowed = is_borrowed(img["name"])

        # =====================
        # 已借出
        # =====================
        if borrowed:
            st.error("🔴 已借出")

            if st.button(f"歸還_{i}"):
                c.execute("""
                UPDATE records
                SET return_date=?, status='returned'
                WHERE sample_name=? AND status='borrowed'
                """, (str(date.today()), img["name"]))

                conn.commit()
                st.success("✅ 已歸還")
                st.rerun()

        # =====================
        # 可借出
        # =====================
        else:
            st.success("🟢 可借出")

            with st.form(f"borrow_form_{i}"):
                user = st.text_input("借出人員", key=f"user_{i}")
                borrow_date = st.date_input("借出日期", date.today(), key=f"bd_{i}")
                return_date = st.date_input("預計歸還日期", key=f"rd_{i}")

                submit = st.form_submit_button("借出")

                if submit:
                    if user == "":
                        st.warning("請填寫借出人員")
                    else:
                        c.execute("""
                        INSERT INTO records 
                        (sample_name, user_name, borrow_date, return_date, status)
                        VALUES (?, ?, ?, ?, 'borrowed')
                        """, (img["name"], user, str(borrow_date), str(return_date)))

                        conn.commit()
                        st.success("✅ 借出成功")
                        st.rerun()

# =====================
# 借出紀錄
# =====================
st.subheader("📊 借出紀錄")

df = pd.read_sql("SELECT * FROM records ORDER BY id DESC", conn)
st.dataframe(df)
