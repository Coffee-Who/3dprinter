import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁標題
st.set_page_config(page_title="3D 列印樣品管理系統", layout="wide")

# --- 1. 檔案路徑與初始化 ---
IMAGE_FOLDER = "image"
RECORD_FILE = "loan_records.csv"
USER_FILE = "users.csv"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file).fillna("")
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# 載入初始資料
records = load_data(RECORD_FILE, ["項次", "樣品名稱", "借出人員", "借出日期", "歸還日期", "備註", "狀態"])
user_df = load_data(USER_FILE, ["姓名"])
if user_df.empty:
    user_df = pd.DataFrame({"姓名": ["管理員"]})
    save_data(user_df, USER_FILE)

# --- 2. 側邊欄：管理功能 ---
with st.sidebar:
    st.title("⚙️ 系統管理")
    
    # A. 新增樣品
    st.subheader("📷 新增樣品圖片")
    uploaded_file = st.file_uploader("上傳新樣品", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        with open(os.path.join(IMAGE_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("上傳成功！")
        st.rerun()

    st.divider()

    # B. 人員管理 (新增/修改/刪除)
    st.subheader("👥 人員名單管理")
    new_user = st.text_input("輸入新姓名", placeholder="例如：王小明")
    if st.button("➕ 新增人員", use_container_width=True):
        if new_user and new_user not in user_df["姓名"].values:
            user_df = pd.concat([user_df, pd.DataFrame({"姓名": [new_user]})], ignore_index=True)
            save_data(user_df, USER_FILE)
            st.rerun()

    if not user_df.empty:
        target_user = st.selectbox("選擇要編輯的人員", user_df["姓名"])
        edit_name = st.text_input("修改姓名為", value=target_user)
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

# --- 3. 主頁面：登記清單 ---
st.title("📦 3D 列印樣品借出登記系統")

image_files = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
user_list = user_df["姓名"].tolist()

# 表頭
h1, h2, h3, h4 = st.columns([0.5, 1.5, 2, 5])
h1.markdown("**項次**")
h2.markdown("**樣品圖片**")
h3.markdown("**狀態資訊**")
h4.markdown("**登記與歸還操作 (請直接輸入)**")
st.write("---")

if not image_files:
    st.info("目前沒有樣品，請由左側上傳圖片。")
else:
    for i, img_name in enumerate(image_files, start=1):
        c_num, c_img, c_info, c_form = st.columns([0.5, 1.5, 2, 5])
        
        # 1. 項次
        c_num.write(f"### {i}")
        
        # 2. 圖片 (150px)
        c_img.image(os.path.join(IMAGE_FOLDER, img_name), width=150)
        
        # 3. 狀態
        sample_history = records[records["樣品名稱"] == img_name]
        is_loaned = False
        if not sample_history.empty:
            last_rec = sample_history.iloc[-1]
            if last_rec["狀態"] == "借出中" and not last_rec["歸還日期"]:
                is_loaned = True
        
        with c_info:
            st.write(f"**{img_name}**")
            if is_loaned:
                st.error(f"🔴 已借出\n借用人：{last_rec['借出人員']}")
            else:
                st.success("🟢 在庫可借")

        # 4. 操作表單 (直接顯示)
        with c_form:
            if is_loaned:
                if st.button(f"確認歸還 (項次 {i})", key=f"ret_{i}", use_container_width=True):
                    idx = sample_history.index[-1]
                    records.at[idx, "歸還日期"] = datetime.now().strftime("%Y-%m-%d")
                    records.at[idx, "狀態"] = "已歸還"
                    save_data(records, RECORD_FILE)
                    st.rerun()
            else:
                with st.form(key=f"form_{i}", clear_on_submit=True):
                    f1, f2, f3 = st.columns([2, 2, 3])
                    name = f1.selectbox("借用人", ["請選擇"] + user_list, key=f"sel_{i}")
                    date = f2.date_input("借出日期", datetime.now(), key=f"date_{i}")
                    note = f3.text_input("備註", key=f"note_{i}", placeholder="用途...")
                    if st.form_submit_button(f"登記借出 (項次 {i})", use_container_width=True):
                        if name == "請選擇":
                            st.error("請選人員")
                        else:
                            new_row = {
                                "項次": i, "樣品名稱": img_name, "借出人員": name,
                                "借出日期": date.strftime("%Y-%m-%d"), "歸還日期": "",
                                "備註": note, "狀態": "借出中"
                            }
                            records = pd.concat([records, pd.DataFrame([new_row])], ignore_index=True)
                            save_data(records, RECORD_FILE)
                            st.rerun()
        st.write("---")

# --- 4. 數據分析與匯出 ---
st.header("📊 紀錄匯出與數據分析")
col_table, col_analysis = st.columns([1, 1])

with col_table:
    st.subheader("📋 流向紀錄總表")
    st.dataframe(records, use_container_width=True, height=400)
    csv = records.to_csv(index=False).encode('utf-8')
    st.download_button("📥 匯出 CSV 紀錄檔", csv, "history.csv", "text/csv")

with col_analysis:
    st.subheader("📈 借出數據分析")
    if not records.empty:
        # A. 樣品次數統計
        s_counts = records["樣品名稱"].value_counts().reset_index()
        s_counts.columns = ["樣品", "次數"]
        
        # B. 人員排行
        u_counts = records["借出人員"].value_counts().reset_index()
        u_counts.columns = ["人員", "次數"]

        ana1, ana2 = st.columns(2)
        with ana1:
            st.write("**樣品熱度**")
            st.bar_chart(s_counts.set_index("樣品"), color="#29b5e8")
            # 顯示整數統計
            for _, row in s_counts.iterrows():
                st.write(f"🔹 {row['樣品']}: {int(row['次數'])} 次")

        with ana2:
            st.write("**借用排行**")
            st.bar_chart(u_counts.set_index("人員"), color="#ff4b4b")
            for _, row in u_counts.iterrows():
                st.write(f"🔸 {row['人員']}: {int(row['次數'])} 次")
    else:
        st.info("尚無數據可分析")
