import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(layout="wide")

st.title("🚀 自動CRM系統")

# =========================
# 📍 取得正確路徑（關鍵）
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "customers.json")

# =========================
# 🧪 Debug資訊（可保留）
# =========================
with st.expander("🛠 Debug資訊"):
    st.write("目前工作目錄：", os.getcwd())
    st.write("app.py位置：", BASE_DIR)

    if os.path.exists(BASE_DIR):
        st.write("根目錄內容：", os.listdir(BASE_DIR))

    if os.path.exists(os.path.join(BASE_DIR, "data")):
        st.write("data資料夾內容：", os.listdir(os.path.join(BASE_DIR, "data")))
    else:
        st.error("❌ 找不到 data 資料夾")

    st.write("實際讀取路徑：", file_path)

# =========================
# ❌ 找不到檔案就停止
# =========================
if not os.path.exists(file_path):
    st.error(f"❌ 找不到 customers.json\n\n路徑：{file_path}")
    st.stop()

# =========================
# 📥 讀取資料
# =========================
try:
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    st.error(f"❌ 讀取 JSON 失敗：{e}")
    st.stop()

# =========================
# 🛑 空資料防呆
# =========================
if not data:
    st.warning("⚠️ 目前沒有客戶資料")
    st.stop()

df = pd.DataFrame(data)

# =========================
# 📊 儀表板
# =========================
st.subheader("📊 客戶狀態分析")

if "status" in df.columns:
    st.bar_chart(df["status"].value_counts())
else:
    st.warning("⚠️ 資料缺少 status 欄位")

# =========================
# 🔍 篩選功能
# =========================
st.subheader("🔍 篩選")

if "status" in df.columns:
    status_list = ["全部"] + list(df["status"].dropna().unique())
    status_filter = st.selectbox("選擇狀態", status_list)

    if status_filter != "全部":
        df = df[df["status"] == status_filter]

# =========================
# 📋 客戶清單
# =========================
st.subheader("📋 客戶清單")

for _, row in df.iterrows():
    with st.expander(f"🏢 {row.get('name', '未命名')}"):

        st.write("📌 狀態：", row.get("status", ""))
        st.write("🏭 產業：", row.get("industry", ""))
        st.write("📅 最後聯絡：", row.get("last_contact", ""))
        st.write("👉 下一步：", row.get("next_action", ""))

        st.divider()
