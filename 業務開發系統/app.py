import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# DB
conn = sqlite3.connect("pro.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS companies (
id INTEGER PRIMARY KEY,
name TEXT, industry TEXT, location TEXT, website TEXT
)""")

c.execute("""CREATE TABLE IF NOT EXISTS leads (
id INTEGER PRIMARY KEY,
name TEXT, email TEXT, company TEXT, source TEXT, created_at TEXT
)""")

conn.commit()

LINE_TOKEN = "你的Token"

st.set_page_config(layout="wide")
menu = st.sidebar.radio("選單", ["抓名單", "公司池", "客戶頁", "名單"])

# ===== 抓名單 =====
if menu == "抓名單":
    kw = st.text_input("關鍵字（例：台中 牙科診所）")

    if st.button("開始抓取"):
        data = scrape_google_maps(kw)

        for d in data:
            c.execute("INSERT INTO companies (name, industry, location, website) VALUES (?, ?, ?, ?)",
                      (d['name'], d['industry'], d['location'], d['website']))
        conn.commit()
        st.success(f"抓到 {len(data)} 筆")

# ===== 公司池 =====
elif menu == "公司池":
    df = pd.read_sql("SELECT * FROM companies", conn)
    st.dataframe(df)

# ===== 客戶頁 =====
elif menu == "客戶頁":
    st.title("📢 最新活動")

    with st.form("lead_form"):
        name = st.text_input("姓名")
        email = st.text_input("Email")
        company = st.text_input("公司")

        if st.form_submit_button("送出"):
            c.execute("INSERT INTO leads VALUES (NULL, ?, ?, ?, ?, ?)",
                      (name, email, company, "活動頁", str(datetime.now())))
            conn.commit()

            # LINE 通知
            send_line_notify(f"新名單：{name} / {company}", LINE_TOKEN)

            st.success("已送出")

# ===== 名單 =====
elif menu == "名單":
    df = pd.read_sql("SELECT * FROM leads", conn)
    st.dataframe(df)
