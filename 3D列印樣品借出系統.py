import streamlit as st
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt

# 設定網頁標題
st.set_page_config(page_title="3D 列印樣品管理系統專業版", layout="wide")

# --- 1. 配置與初始化 ---
IMAGE_FOLDER = "image"
RECORD_FILE = "loan_records.csv"
USER_FILE = "users.csv"

# 確保必要的資料夾與檔案存在
for folder in [IMAGE_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

if not os.path.exists(RECORD_FILE):
    pd.DataFrame(columns=["項次", "樣品名稱", "借出人員", "借出日期", "歸還日期", "備註", "狀態"]).to_csv(RECORD_FILE, index=False)

if not os.path.exists(USER_FILE):
    pd.DataFrame({"姓名": ["管理員", "測試員"]}).to_csv(USER_FILE, index=False)

# 讀取資料函式
def load_data(file):
    return pd.read_csv(file).fillna("")

def save_data(df, file):
    df.to_csv(file, index=False)

# --- 2. 側邊欄：功能設定 ---
with st.sidebar:
    st.title("⚙️ 系統設定")
    
    # 功能 A: 自行新增圖片
    st.subheader("📷 新增樣品圖片")
    uploaded_file = st.file_uploader("選擇圖片檔...", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        with open(os.path.join(IMAGE_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"圖片 {uploaded_file.name} 上傳成功！")
        st.rerun()

    st.divider()

    # 功能 B: 自行加入借出人員
    st.subheader("👥 人員管理")
    new_user = st.text_input("新增人員姓名")
    if st.button("加入選單"):
        if new_user:
            user_df = load_data(USER_FILE)
            if new_user not in user_df["姓名"].values:
                new_user_df = pd.concat([user_df, pd.DataFrame({"姓名": [new_user]})], ignore_index=True)
                save_data(new_user_df, USER_FILE)
                st.success(f"已加入：{new_user}")
                st.rerun()

# --- 3. 主介面 ---
st.title("📦 3D 列印樣品借出系統")

records = load_data(RECORD_FILE)
user_list = load_data(USER_FILE)["姓名"].tolist()
image_files = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])

# 建立表格標題
h_col1, h_col2, h_col3, h_col4 = st.columns([0.5, 1.5, 1.5, 5])
with h_col1: st.markdown("**項次**")
with h_col2: st.markdown("**樣品圖片**")
with h_col3: st.markdown("**樣品資訊**")
with h_col4: st.markdown("**登記/歸還操作**")
st.divider()

if not image_files:
    st.warning("目前無樣品，請從側邊欄上傳圖片。")
else:
    for i, img_name in enumerate(image_files, start=1):
        col_num, col_img, col_info, col_form = st.columns([0.5, 1.5, 1.5, 5])
        
        with col_num:
            st.write(f"### {i}")
        
        with col_img:
            st.image(os.path.join(IMAGE_FOLDER, img_name), width=150)
            
        with col_info:
            st.write(f"**{img_name}**")
            sample_history = records[records["樣品名稱"] == img_name]
            is_loaned = any((sample_history["狀態"] == "借出中") & (sample_history["歸還日期"] == ""))
            
            if is_loaned:
                last_user = sample_history.iloc[-1]["借出人員"]
                st.error(f"❌ 已借出\n\n({last_user})")
            else:
                st.success("✅ 在庫可借")

        with col_form:
            if is_loaned:
                if st.button(f"確認歸還 (項次 {i})", key=f"ret_{i}"):
                    last_idx = sample_history.index[-1]
                    records.at[last_idx, "歸還日期"] = datetime.now().strftime("%Y-%m-%d")
                    records.at[last_idx, "狀態"] = "已歸還"
                    save_record_df = records.drop(columns=['項次']) # 不儲存動態項次
                    save_data(records, RECORD_FILE)
                    st.rerun()
            else:
                with st.form(key=f"form_{i}", clear_on_submit=True):
                    f_c1, f_c2, f_c3 = st.columns([2, 2, 3])
                    with f_c1:
                        selected_user = st.selectbox("借出人員", options=["請選擇"] + user_list, key=f"u_{i}")
                    with f_c2:
                        loan_date = st.date_input("日期", datetime.now(), key=f"d_{i}")
                    with f_c3:
                        note = st.text_input("備註", key=f"n_{i}")
                    
                    if st.form_submit_button(f"登記借出 (項次 {i})"):
                        if selected_user == "請選擇":
                            st.error("請選擇人員")
                        else:
                            new_row = {
                                "項次": i, "樣品名稱": img_name, "借出人員": selected_user,
                                "借出日期": loan_date.strftime("%Y-%m-%d"), "歸還日期": "",
                                "備註": note, "狀態": "借出中"
                            }
                            records = pd.concat([records, pd.DataFrame([new_row])], ignore_index=True)
                            save_data(records, RECORD_FILE)
                            st.rerun()
        st.divider()

# --- 4. 歷史紀錄與數據分析 ---
st.subheader("📋 紀錄與分析")
tab1, tab2 = st.tabs(["歷史流向表", "📊 借出數據分析"])

with tab1:
    st.dataframe(records, use_container_width=True)
    csv_data = records.to_csv(index=False).encode('utf-8')
    st.download_button("匯出 CSV 紀錄", csv_data, "loan_history.csv", "text/csv")

with tab2:
    if not records.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.write("**各樣品借出次數統計**")
            counts = records["樣品名稱"].value_counts()
            st.bar_chart(counts)
        with c2:
            st.write("**熱門借用人員排行**")
            user_counts = records["借出人員"].value_counts()
            st.bar_chart(user_counts)
    else:
        st.write("尚無數據可分析")
