import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁標題
st.set_page_config(page_title="3D 列印樣品借出系統", layout="wide")

# --- 1. 配置區域 ---
IMAGE_FOLDER = "image" 
RECORD_FILE = "loan_records.csv"

# 初始化借還紀錄
if not os.path.exists(RECORD_FILE):
    df_init = pd.DataFrame(columns=["項次", "樣品名稱", "借出人員", "借出日期", "歸還日期", "備註", "狀態"])
    df_init.to_csv(RECORD_FILE, index=False)

def load_records():
    return pd.read_csv(RECORD_FILE).fillna("")

def save_record(df):
    df.to_csv(RECORD_FILE, index=False)

# --- 2. 獲取圖片清單 ---
if os.path.exists(IMAGE_FOLDER):
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    image_files.sort() # 排序讓編號更穩定
else:
    image_files = []

# --- 3. UI 介面 ---
st.title("📦 3D 列印樣品借出系統")

records = load_records()

st.subheader("🖼️ 樣品借還登記 (由上往下排列)")

if not image_files:
    st.warning("請在 GitHub 的 image/ 資料夾中放入圖片。")
else:
    # 遍歷所有圖片，由上往下排列
    for i, img_name in enumerate(image_files, start=1):
        # 使用分隔線區分每個項目
        st.divider()
        
        # 建立三欄佈局：編號與圖片、樣品資訊、操作表單
        col1, col2, col3 = st.columns([1, 2, 4])
        
        with col1:
            st.markdown(f"### 項次 {i}")
            img_path = os.path.join(IMAGE_FOLDER, img_name)
            # 設定圖片顯示寬度為 50 (Streamlit 寬度單位為像素)
            st.image(img_path, width=50)
            
        with col2:
            st.write(f"**檔案名稱:** \n{img_name}")
            
            # 判斷狀態
            sample_history = records[records["樣品名稱"] == img_name]
            is_loaned = False
            last_user = ""
            if not sample_history.empty:
                last_rec = sample_history.iloc[-1]
                if last_rec["狀態"] == "借出中" and (not last_rec["歸還日期"]):
                    is_loaned = True
                    last_user = last_rec['借出人員']
            
            if is_loaned:
                st.error(f"🔴 狀態：已借出\n(借用人：{last_user})")
            else:
                st.success("🟢 狀態：在庫 (可借出)")

        with col3:
            if is_loaned:
                # 歸還表單
                if st.button(f"按此辦理歸還 (項次 {i})", key=f"ret_{i}"):
                    last_idx = sample_history.index[-1]
                    records.at[last_idx, "歸還日期"] = datetime.now().strftime("%Y-%m-%d")
                    records.at[last_idx, "狀態"] = "已歸還"
                    save_record(records)
                    st.toast(f"項次 {i} 已成功歸還！")
                    st.rerun()
            else:
                # 借出表單 (展開式)
                with st.expander(f"填寫借出資料 (項次 {i})"):
                    with st.form(key=f"form_{i}"):
                        user_input = st.text_input("借出人員姓名", key=f"user_{i}")
                        loan_date = st.date_input("借出日期", datetime.now(), key=f"date_{i}")
                        note = st.text_input("備註", key=f"note_{i}")
                        submit = st.form_submit_button("確認借出登記")
                        
                        if submit:
                            if not user_input:
                                st.error("請輸入借出人員姓名")
                            else:
                                new_row = {
                                    "項次": i,
                                    "樣品名稱": img_name,
                                    "借出人員": user_input,
                                    "借出日期": loan_date.strftime("%Y-%m-%d"),
                                    "歸還日期": "",
                                    "備註": note,
                                    "狀態": "借出中"
                                }
                                records = pd.concat([records, pd.DataFrame([new_row])], ignore_index=True)
                                save_record(records)
                                st.rerun()

# --- 4. 歷史紀錄區 ---
st.divider()
st.subheader("📋 完整借還紀錄表")
st.dataframe(records, use_container_width=True)

# 下載按鈕
csv_data = records.to_csv(index=False).encode('utf-8')
st.download_button("匯出 CSV 紀錄檔", csv_data, "loan_records.csv", "text/csv")
