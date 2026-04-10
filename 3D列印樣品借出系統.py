import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁標題
st.set_page_config(page_title="3D 列印樣品管理系統專業版", layout="wide")

# --- 1. 配置與初始化 ---
IMAGE_FOLDER = "image"
RECORD_FILE = "loan_records.csv"
USER_FILE = "users.csv"

# 確保資料夾存在
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# 初始化紀錄檔
if not os.path.exists(RECORD_FILE):
    pd.DataFrame(columns=["項次", "樣品名稱", "借出人員", "借出日期", "歸還日期", "備註", "狀態"]).to_csv(RECORD_FILE, index=False)

# 初始化人員清單
if not os.path.exists(USER_FILE):
    pd.DataFrame({"姓名": ["管理員"]}).to_csv(USER_FILE, index=False)

def load_data(file):
    try:
        return pd.read_csv(file).fillna("")
    except:
        return pd.DataFrame()

def save_data(df, file):
    df.to_csv(file, index=False)

# --- 2. 側邊欄：進階管理功能 ---
with st.sidebar:
    st.title("⚙️ 系統管理面板")
    
    # A. 新增樣品圖片
    st.subheader("📷 新增樣品")
    uploaded_file = st.file_uploader("上傳圖片檔", type=['png', 'jpg', 'jpeg'])
    if uploaded_file is not None:
        with open(os.path.join(IMAGE_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"樣品 {uploaded_file.name} 已新增")
        st.rerun()

    st.divider()

    # B. 人員清單管理 (新增/修改/刪除)
    st.subheader("👥 人員清單管理")
    user_df = load_data(USER_FILE)
    
    # 新增人員
    new_user = st.text_input("輸入新人員姓名")
    if st.button("➕ 新增人員"):
        if new_user and new_user not in user_df["姓名"].values:
            user_df = pd.concat([user_df, pd.DataFrame({"姓名": [new_user]})], ignore_index=True)
            save_data(user_df, USER_FILE)
            st.rerun()

    # 修改/刪除人員
    if not user_df.empty:
        st.write("---")
        target_user = st.selectbox("選擇管理對象", user_df["姓名"])
        edit_name = st.text_input("修改姓名為", value=target_user)
        
        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("📝 修改"):
                user_df.loc[user_df["姓名"] == target_user, "姓名"] = edit_name
                save_data(user_df, USER_FILE)
                st.rerun()
        with col_del:
            if st.button("🗑️ 刪除"):
                user_df = user_df[user_df["姓名"] != target_user]
                save_data(user_df, USER_FILE)
                st.rerun()

# --- 3. 主介面：登記清單 ---
st.title("📦 3D 列印樣品借出系統")

records = load_data(RECORD_FILE)
user_list = user_df["姓名"].tolist() if 'user_df' in locals() else []
image_files = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])

# 標題列佈局
h_col1, h_col2, h_col3, h_col4 = st.columns([0.5, 1.5, 2, 5])
with h_col1: st.markdown("**項次**")
with h_col2: st.markdown("**樣品圖片**")
with h_col3: st.markdown("**狀態資訊**")
with h_col4: st.markdown("**登記/歸還操作**")
st.write("---")

if not image_files:
    st.warning("目前無樣品，請從左側上傳圖片。")
else:
    for i, img_name in enumerate(image_files, start=1):
        col_num, col_img, col_info, col_form = st.columns([0.5, 1.5, 2, 5])
        
        with col_num:
            st.write(f"### {i}")
        
        with col_img:
            st.image(os.path.join(IMAGE_FOLDER, img_name), width=150)
            
        with col_info:
            st.write(f"**{img_name}**")
            sample_history = records[records["樣品名稱"] == img_name]
            is_loaned = False
            if not sample_history.empty:
                last_rec = sample_history.iloc[-1]
                if last_rec["狀態"] == "借出中" and not last_rec["歸還日期"]:
                    is_loaned = True
            
            if is_loaned:
                st.error(f"❌ 已借出\n\n借用人：{last_rec['借出人員']}")
            else:
                st.success("✅ 在庫可借")

        with col_form:
            if is_loaned:
                st.write("") 
                if st.button(f"確認歸還 (項次 {i})", key=f"ret_{i}", use_container_width=True):
                    idx = sample_history.index[-1]
                    records.at[idx, "歸還日期"] = datetime.now().strftime("%Y-%m-%d")
                    records.at[idx, "狀態"] = "已歸還"
                    save_data(records, RECORD_FILE)
                    st.rerun()
            else:
                with st.form(key=f"form_{i}", clear_on_submit=True):
                    f_c1, f_c2, f_c3 = st.columns([2, 2, 3])
                    with f_c1:
                        sel_user = st.selectbox("借用人", options=["請選擇"] + user_list, key=f"u_{i}")
                    with f_c2:
                        l_date = st.date_input("日期", datetime.now(), key=f"d_{i}")
                    with f_c3:
                        note = st.text_input("備註", key=f"n_{i}", placeholder="選填")
                    
                    if st.form_submit_button(f"登記借出 (項次 {i})", use_container_width=True):
                        if sel_user == "請選擇":
                            st.error("請選擇人員")
                        else:
                            new_data = {
                                "項次": i, "樣品名稱": img_name, "借出人員": sel_user,
                                "借出日期": loan_date.strftime("%Y-%m-%d"), "歸還日期": "",
                                "備註": note, "狀態": "借出中"
                            }
                            records = pd.concat([records, pd.DataFrame([new_data])], ignore_index=True)
                            save_data(records, RECORD_FILE)
                            st.rerun()
        st.write("---")

# --- 4. 數據分析與匯出 ---
st.header("📊 系統數據分析與紀錄")
tab1, tab2 = st.tabs(["📋 流向紀錄表", "📈 借出數據分析"])

with tab1:
    st.dataframe(records, use_container_width=True)
    csv = records.to_csv(index=False).encode('utf-8')
    st.download_button("📥 匯出紀錄 (CSV)", csv, "3d_loan_records.csv", "text/csv")

with tab2:
    if not records.empty:
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.subheader("a. 各樣品借出次數統計")
            sample_counts = records["樣品名稱"].value_counts().reset_index()
            sample_counts.columns = ["樣品名稱", "借出次數"]
            # 強制整數並顯示顏色區分
            st.bar_chart(sample_counts.set_index("樣品名稱"), color="#29b5e8")
            st.table(sample_counts) # 輔助顯示整數表格

        with col_b:
            st.subheader("b. 熱門借用人員排行")
            user_counts = records["借出人員"].value_counts().reset_index()
            user_counts.columns = ["借出人員", "借出次數"]
            # 使用不同顏色區分
            st.bar_chart(user_counts.set_index("借出人員"), color="#ff4b4b")
            st.table(user_counts)
    else:
        st.info("尚無借還數據可供分析。")
