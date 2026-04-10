import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁標題
st.set_page_config(page_title="3D 列印樣品管理系統", layout="wide")

# --- 1. 初始化環境 ---
IMAGE_FOLDER = "image"
RECORD_FILE = "loan_records.csv"
USER_FILE = "users.csv"

for folder in [IMAGE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file).fillna("")
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# 載入資料
records = load_data(RECORD_FILE, ["項次", "樣品名稱", "借出人員", "借出日期", "歸還日期", "備註", "狀態"])
user_df = load_data(USER_FILE, ["姓名"])
if user_df.empty:
    user_df = pd.DataFrame({"姓名": ["管理員"]})
    save_data(user_df, USER_FILE)

# --- 2. 側邊欄管理功能 ---
with st.sidebar:
    st.title("⚙️ 管理員面板")
    
    # A. 樣品上傳
    st.subheader("📷 新增樣品圖片")
    uploaded_file = st.file_uploader("上傳圖片", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        with open(os.path.join(IMAGE_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("樣品已新增！")
        st.rerun()

    st.divider()

    # B. 人員名單維護
    st.subheader("👥 人員名單管理")
    new_user = st.text_input("新增人員", placeholder="請輸入姓名")
    if st.button("➕ 加入名單", use_container_width=True):
        if new_user and new_user not in user_df["姓名"].values:
            user_df = pd.concat([user_df, pd.DataFrame({"姓名": [new_user]})], ignore_index=True)
            save_data(user_df, USER_FILE)
            st.rerun()

    if not user_df.empty:
        target_user = st.selectbox("選取對象", user_df["姓名"])
        edit_name = st.text_input("修改為", value=target_user)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📝 修改", use_container_width=True):
                user_df.loc[user_df["姓名"] == target_user, "姓名"] = edit_name
                save_data(user_df, USER_FILE)
                st.rerun()
        with c2:
            if st.button("🗑️ 刪除", use_container_width=True):
                user_df = user_df[user_df["姓名"] != target_user]
                save_data(user_df, USER_FILE)
                st.rerun()

# --- 3. 主頁面：借還登記清單 ---
st.title("📦 3D 列印樣品借還登記")
st.write("---")

image_files = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
user_list = user_df["姓名"].tolist()

# 標題欄位
h_num, h_img, h_info, h_form = st.columns([0.5, 1.5, 2, 5])
h_num.write("**項次**")
h_img.write("**樣品圖片**")
h_info.write("**狀態**")
h_form.write("**登記操作 (姓名/日期/備註)**")
st.write("---")

if not image_files:
    st.info("目前無樣品資料，請使用側邊欄上傳圖片。")
else:
    for i, img_name in enumerate(image_files, start=1):
        c_num, c_img, c_info, c_form = st.columns([0.5, 1.5, 2, 5])
        
        # 1. 項次
        c_num.write(f"### {i}")
        
        # 2. 圖片 (150px)
        c_img.image(os.path.join(IMAGE_FOLDER, img_name), width=150)
        
        # 3. 資訊與狀態
        sample_history = records[records["樣品名稱"] == img_name]
        is_loaned = False
        if not sample_history.empty:
            last_rec = sample_history.iloc[-1]
            if last_rec["狀態"] == "借出中" and not last_rec["歸還日期"]:
                is_loaned = True
        
        with c_info:
            st.write(f"**{img_name}**")
            if is_loaned:
                st.error(f"🔴 已借出\n\n借用人：{last_rec['借出人員']}")
            else:
                st.success("🟢 在庫中")

        # 4. 操作表單
        with c_form:
            if is_loaned:
                st.write("") # 保持對齊
                if st.button(f"辦理歸還 (項次 {i})", key=f"ret_{i}", use_container_width=True):
                    idx = sample_history.index[-1]
                    records.at[idx, "歸還日期"] = datetime.now().strftime("%Y-%m-%d")
                    records.at[idx, "狀態"] = "已歸還"
                    save_data(records, RECORD_FILE)
                    st.rerun()
            else:
                with st.form(key=f"form_{i}", clear_on_submit=True):
                    f1, f2, f3 = st.columns([2, 2, 3])
                    user = f1.selectbox("人員", ["請選擇"] + user_list, key=f"sel_{i}")
                    date = f2.date_input("日期", datetime.now(), key=f"date_{i}")
                    note = f3.text_input("備註", key=f"note_{i}")
                    if st.form_submit_button(f"登記借出 (項次 {i})", use_container_width=True):
                        if user == "請選擇":
                            st.error("請選取人員")
                        else:
                            new_row = {
                                "項次": i, "樣品名稱": img_name, "借出人員": user,
                                "借出日期": date.strftime("%Y-%m-%d"), "歸還日期": "",
                                "備註": note, "狀態": "借出中"
                            }
                            records = pd.concat([records, pd.DataFrame([new_row])], ignore_index=True)
                            save_data(records, RECORD_FILE)
                            st.rerun()
        st.write("---")

# --- 4. 紀錄匯出與數據分析 ---
st.header("📊 歷史紀錄與數據分析")
col_table, col_analysis = st.columns([1, 1])

with col_table:
    st.subheader("📋 借還流向總表")
    st.dataframe(records, use_container_width=True, height=450)
    csv = records.to_csv(index=False).encode('utf-8')
    st.download_button("📥 匯出資料 (CSV)", csv, "inventory_history.csv", "text/csv")

with col_analysis:
    st.subheader("📈 統計分析圖表")
    if not records.empty:
        # a. 各樣品借出次數
        st.write("**a. 各樣品借出次數統計**")
        s_counts = records["樣品名稱"].value_counts().sort_values(ascending=True)
        st.bar_chart(s_counts, color="#29b5e8")
        
        # b. 熱門借用人員排行
        st.write("**b. 熱門借用人員排行**")
        u_counts = records["借出人員"].value_counts().sort_values(ascending=True)
        st.bar_chart(u_counts, color="#ff4b4b")
        
        st.info("💡 提示：直條圖左側 Y 軸會根據數值自動呈現整數級距 (1, 2, 3...)。")
    else:
        st.info("尚無足夠數據進行分析。")
