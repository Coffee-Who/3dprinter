import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁標題
st.set_page_config(page_title="3D 列印樣品借出系統", layout="wide")

# --- 1. 配置區域 ---
IMAGE_FOLDER = "image" 
RECORD_FILE = "loan_records.csv"

# 初始化借還紀錄檔
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
    image_files.sort() 
else:
    image_files = []

# --- 3. UI 介面 ---
st.title("📦 3D 列印樣品借出系統")
st.write("---")

records = load_records()

if not image_files:
    st.warning("請在 GitHub 的 image/ 資料夾中放入圖片。")
else:
    # 建立標題列
    h_col1, h_col2, h_col3, h_col4 = st.columns([0.5, 1.5, 1.5, 4])
    with h_col1: st.markdown("**項次**")
    with h_col2: st.markdown("**樣品圖片**")
    with h_col3: st.markdown("**樣品資訊**")
    with h_col4: st.markdown("**借登記/歸還操作**")
    st.write("---")

    # 遍歷所有圖片項目
    for i, img_name in enumerate(image_files, start=1):
        # 建立每一列的四個欄位
        col_num, col_img, col_info, col_form = st.columns([0.5, 1.5, 1.5, 4])
        
        # 1. 項次數字
        with col_num:
            st.write(f"### {i}")
        
        # 2. 樣品圖片 (固定寬度 150)
        with col_img:
            img_path = os.path.join(IMAGE_FOLDER, img_name)
            st.image(img_path, width=150)
            
        # 3. 樣品資訊與狀態
        with col_info:
            st.write(f"**{img_name}**")
            
            # 檢查目前借出狀態
            sample_history = records[records["樣品名稱"] == img_name]
            is_loaned = False
            last_user = ""
            if not sample_history.empty:
                last_rec = sample_history.iloc[-1]
                if last_rec["狀態"] == "借出中" and (not last_rec["歸還日期"]):
                    is_loaned = True
                    last_user = last_rec['借出人員']
            
            if is_loaned:
                st.error(f"❌ 已借出\n\n借用人：{last_user}")
            else:
                st.success("✅ 在庫可借")

        # 4. 操作表單 (借出與歸還並排)
        with col_form:
            if is_loaned:
                # 顯示歸還按鈕
                st.write("") # 增加一點間距對齊
                if st.button(f"確認歸還 (項次 {i})", key=f"ret_{i}"):
                    last_idx = sample_history.index[-1]
                    records.at[last_idx, "歸還日期"] = datetime.now().strftime("%Y-%m-%d")
                    records.at[last_idx, "狀態"] = "已歸還"
                    save_record(records)
                    st.toast(f"項次 {i} 已歸還")
                    st.rerun()
            else:
                # 顯示登記表單
                with st.form(key=f"form_{i}", clear_on_submit=True):
                    f_col1, f_col2, f_col3 = st.columns([2, 2, 3])
                    with f_col1:
                        user_input = st.text_input("借出人員", key=f"u_{i}", placeholder="請輸入姓名")
                    with f_col2:
                        loan_date = st.date_input("借出日期", datetime.now(), key=f"d_{i}")
                    with f_col3:
                        note = st.text_input("備註", key=f"n_{i}", placeholder="用途說明")
                    
                    submit = st.form_submit_button(f"登記借出 (項次 {i})")
                    
                    if submit:
                        if not user_input:
                            st.error("請輸入人員姓名！")
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
        
        st.write("---") # 每個項目間的分割線

# --- 4. 歷史紀錄區 ---
st.subheader("📋 完整流向紀錄")
with st.expander("點擊展開/收合歷史資料表格"):
    st.dataframe(records, use_container_width=True)
    csv_data = records.to_csv(index=False).encode('utf-8')
    st.download_button("匯出紀錄為 CSV", csv_data, "3d_loan_log.csv", "text/csv")
