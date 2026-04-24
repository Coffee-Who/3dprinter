import os
import streamlit as st

st.write("目前工作目錄：", os.getcwd())
st.write("目前檔案列表：", os.listdir())
import streamlit as st
import json
import pandas as pd

st.title("🚀 自動CRM系統")

import os
import json
import streamlit as st

file_path = "data/customers.json"

if not os.path.exists(file_path):
    st.error("❌ 找不到 customers.json（請確認 GitHub 是否有 data/customers.json）")
    st.stop()

with open(file_path, encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)

st.subheader("📊 客戶狀態")
st.bar_chart(df["status"].value_counts())

st.subheader("📋 客戶列表")

for _, row in df.iterrows():
    with st.expander(row.get("name", "")):
        st.write("狀態:", row.get("status", ""))
        st.write("產業:", row.get("industry", ""))
        st.write("最後聯絡:", row.get("last_contact", ""))
        st.write("下一步:", row.get("next_action", ""))
