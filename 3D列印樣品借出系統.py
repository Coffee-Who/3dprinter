import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 設定網頁標題與圖示
st.set_page_config(page_title="3D 列印樣品借出系統", layout="wide")

# --- 1. 配置區域 ---
IMAGE_FOLDER = "image" 
RECORD_FILE = "loan_records.csv"

# 初始化借還紀錄 (如果檔案不存在則建立)
if not os.path.exists(RECORD_FILE):
    df_init = pd.DataFrame(columns=["樣品名稱", "借出人員", "借出日期", "歸還日期", "備註", "狀態"])
    df_init.to_csv(RECORD_FILE, index=False)

# 讀取紀錄的函式
def load_records():
    return pd.read_csv(RECORD_FILE).fillna("")

# 儲存紀錄的函式
def save_record(df):
    df.to_csv(RECORD_FILE, index=False)

# --- 2. 獲取圖片清單 ---
if os.path.exists(IMAGE_FOLDER):
    # 支援常見圖片格式
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
else:
    image_files = []

# --- 3. UI 介面 ---
st.title("📦 3D 列印樣品借出系統")
st.info("說明：請在後台將圖片上傳至 GitHub 的 `image/` 資料夾，系統將自動同步。")

# 讀取現有紀錄
records = load_records()

# 顯示樣品列表
st.subheader("🖼️ 樣品借還管理")

if not image_files:
    st.warning("目前 image 資料夾中沒有圖片，請先上傳圖片。")
else:
    # 建立網格佈局 (每列 4 個)
    cols = st.columns(4)
    
    for idx, img_name in enumerate(image_files):
        with cols[idx % 4]:
            # 顯示圖片
            img_path = os.path.join(IMAGE_FOLDER, img_name)
            st.image(img_path, use_container_width=True)
            st.write(f"**{img_name}**")
            
            # 取得該樣品的最後一筆紀錄來判斷狀態
            sample_history = records[records["樣品名稱"] == img_name]
            
            is_loaned = False
            if not sample_history.empty:
                last_rec = sample_history.iloc[-1]
                # 如果狀態是借出中，且歸還日期為空
                if last_rec["狀態"] == "借出中" and (not last_rec["歸還日期"]):
                    is_loaned = True
            
            if is_loaned:
                st.error(f"🔴 已借出\n({last_rec['借出人員']})")
                # 歸還按鈕
                if st.button(f"辦理歸還", key=f"ret_{idx}"):
                    # 更新最後一筆紀錄的歸還日期
                    last_idx = sample_history.index[-1]
                    records.at[last_idx, "歸還日期"] = datetime.now().strftime("%Y-%m-%d")
                    records.at[last_idx, "狀態"] = "已歸還"
                    save_record(records)
                    st.success("歸還成功！")
                    st.rerun()
            else:
                st.success("🟢 可借出")
                # 借出表單
                with st.popover(f"登記借出"):
                    with st.form(key=f"form_{idx}"):
                        user_input = st.text_input("借出人員姓名")
                        loan_date = st.date_input("借出日期", datetime.now())
                        note = st.text_input("備註")
                        submit = st.form_submit_button("確認登記")
                        
                        if submit:
                            if not user_input:
                                st.error("請輸入借出人員！")
                            else:
                                new_row = {
                                    "樣品名稱": img_name,
                                    "借出人員": user_input,
                                    "借出日期": loan_date.strftime("%Y-%m-%d"),
                                    "歸還日期": "",
                                    "備註": note,
                                    "狀態": "借出中"
                                }
                                records = pd.concat([records, pd.DataFrame([new_row])], ignore_index=True)
                                save_record(records)
                                st.success("登記成功！")
                                st.rerun()

# --- 4. 歷史紀錄區 ---
st.divider()
st.subheader("📋 所有借還歷史紀錄")

# 搜尋功能 (可選)
search_query = st.text_input("搜尋樣品名稱或人員", "")
if search_query:
    display_df = records[records.apply(lambda row: search_query.lower() in row.astype(str).str.lower().values, axis=1)]
else:
    display_df = records

st.dataframe(display_df, use_container_width=True)

# 下載按鈕
csv_data = records.to_csv(index=False).encode('utf-8')
st.download_button("匯出紀錄為 CSV", csv_data, "loan_history.csv", "text/csv")
