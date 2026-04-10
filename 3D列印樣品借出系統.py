import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁標題
st.set_page_config(page_title="3D 列印樣品借出系統", layout="wide")

# --- 1. 配置區域 ---
# GitHub 圖片資料夾路徑 (基於你提供的 URL 結構)
IMAGE_FOLDER = "image" 
RECORD_FILE = "loan_records.csv"

# 初始化借還紀錄 (如果檔案不存在則建立)
if not os.path.exists(RECORD_FILE):
    df_init = pd.DataFrame(columns=["樣品名稱", "借出人員", "借出日期", "歸還日期", "備註", "狀態"])
    df_init.to_csv(RECORD_FILE, index=False)

def load_records():
    return pd.read_csv(RECORD_FILE)

def save_record(df):
    df.to_csv(RECORD_FILE, index=False)

# --- 2. 獲取圖片清單 ---
# 假設你的圖片放在 GitHub 專案的 image/ 資料夾下
if os.path.exists(IMAGE_FOLDER):
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg'))]
else:
    image_files = []
    st.warning(f"找不到資料夾: {IMAGE_FOLDER}，請確保 GitHub 專案中有此資料夾。")

# --- 3. UI 介面 ---
st.title("📦 3D 列印樣品借出系統")

# 讀取現有紀錄
records = load_records()

# 顯示樣品列表 (Grid 方式排列)
st.subheader("樣品清單與狀態")
cols = st.columns(3)  # 一列顯示 3 個

for idx, img_name in enumerate(image_files):
    with cols[idx % 3]:
        st.image(os.path.join(IMAGE_FOLDER, img_name), use_column_width=True)
        st.write(f"**樣品名稱:** {img_name}")
        
        # 判斷該樣品目前的狀態
        # 找出該樣品最後一筆紀錄
        sample_history = records[records["樣品名稱"] == img_name]
        
        is_loaned = False
        if not sample_history.empty:
            last_record = sample_history.iloc[-1]
            # 如果歸還日期為空，代表還沒還
            if pd.isna(last_record["歸還日期"]) or last_record["歸還日期"] == "":
                is_loaned = True
        
        if is_loaned:
            st.error(f"🔴 已借出 (借用人: {last_record['借出人員']})")
            # 歸還功能
            if st.button(f"辦理歸還: {img_name}", key=f"return_{idx}"):
                records.loc[sample_history.index[-1], "歸還日期"] = datetime.now().strftime("%Y-%m-%d")
                records.loc[sample_history.index[-1], "狀態"] = "已歸還"
                save_record(records)
                st.rerun()
        else:
            st.success("🟢 可借出")
            # 借出表單按鈕
            with st.expander(f"登記借出: {img_name}"):
                with st.form(key=f"form_{idx}"):
                    staff = st.selectbox("借出人員", ["請選擇", "人員A", "人員B", "人員C", "新增人員..."], key=f"staff_{idx}")
                    loan_date = st.date_input("借出日期", datetime.now(), key=f"ldate_{idx}")
                    note = st.text_input("備註", key=f"note_{idx}")
                    submit = st.form_submit_button("確認借出")
                    
                    if submit:
                        if staff == "請選擇":
                            st.warning("請選擇人員")
                        else:
                            new_data = {
                                "樣品名稱": img_name,
                                "借出人員": staff,
                                "借出日期": loan_date.strftime("%Y-%m-%d"),
                                "歸還日期": "",
                                "備註": note,
                                "狀態": "借出中"
                            }
                            records = pd.concat([records, pd.DataFrame([new_data])], ignore_index=True)
                            save_record(records)
                            st.success(f"{img_name} 借出成功！")
                            st.rerun()

---
st.divider()
st.subheader("📋 歷史借還紀錄匯總")
st.dataframe(records, use_container_width=True)
