import streamlit as st
import pandas as pd
from datetime import datetime
import os
import altair as alt

# 設定網頁標題與寬度佈局
st.set_page_config(page_title="3D 列印樣品管理系統專業版", layout="wide")

# --- 1. 配置與資料初始化 ---
IMAGE_FOLDER = "image"
RECORD_FILE = "loan_records.csv"
USER_FILE = "users.csv"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)import streamlit as st
import pandas as pd
from datetime import datetime
import os
import altair as alt

# 設定網頁標題與寬度佈局
st.set_page_config(page_title="3D 列印樣品管理系統專業版", layout="wide")

# --- 1. 配置與資料初始化 ---
IMAGE_FOLDER = "image"
RECORD_FILE = "loan_records.csv"
USER_FILE = "users.csv"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

def load_data(file, columns):
    if os.path.exists(file):
        try:
            return pd.read_csv(file).fillna("")
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# 載入現有資料
records = load_data(RECORD_FILE, ["項次", "樣品名稱", "借出人員", "借出日期", "歸還日期", "備註", "狀態"])
user_df = load_data(USER_FILE, ["姓名"])
if user_df.empty:
    user_df = pd.DataFrame({"姓名": ["管理員"]})
    save_data(user_df, USER_FILE)

# --- 2. 側邊欄管理功能 ---
with st.sidebar:
    st.title("⚙️ 系統管理面板")
    
    # A. 新增樣品
    st.subheader("📷 新增樣品圖片")
    uploaded_file = st.file_uploader("上傳圖片 (jpg/png)", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        with open(os.path.join(IMAGE_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"樣品 {uploaded_file.name} 已新增")
        st.rerun()

    st.divider()

    # B. 人員名單管理
    st.subheader("👥 人員名單維護")
    new_user = st.text_input("輸入新姓名")
    if st.button("➕ 新增人員", use_container_width=True):
        if new_user and new_user not in user_df["姓名"].values:
            user_df = pd.concat([user_df, pd.DataFrame({"姓名": [new_user]})], ignore_index=True)
            save_data(user_df, USER_FILE)
            st.rerun()

    if not user_df.empty:
        target_user = st.selectbox("選取編輯對象", user_df["姓名"])
        edit_name = st.text_input("修改姓名為", value=target_user)
        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("📝 修改", use_container_width=True):
                user_df.loc[user_df["姓名"] == target_user, "姓名"] = edit_name
                save_data(user_df, USER_FILE)
                st.rerun()
        with col_del:
            if st.button("🗑️ 刪除人員", use_container_width=True):
                user_df = user_df[user_df["姓名"] != target_user]
                save_data(user_df, USER_FILE)
                st.rerun()

# --- 3. 主介面：借還登記區 ---
st.title("📦 3D 列印樣品借出登記系統")
st.write("---")

image_files = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
user_list = user_df["姓名"].tolist()

# 定義標題列 (比例微調以容納刪除按鈕)
h_num, h_img, h_info, h_form, h_manage = st.columns([0.5, 1.5, 2, 4.5, 1])
h_num.markdown("**項次**")
h_img.markdown("**樣品圖片**")
h_info.markdown("**狀態資訊**")
h_form.markdown("**登記與歸還操作**")
h_manage.markdown("**管理**")
st.write("---")

if not image_files:
    st.info("💡 目前沒有樣品，請從左側側邊欄上傳圖片。")
else:
    for i, img_name in enumerate(image_files, start=1):
        col_n, col_i, col_s, col_f, col_m = st.columns([0.5, 1.5, 2, 4.5, 1])
        
        # 1. 項次
        col_n.write(f"### {i}")
        
        # 2. 圖片 (150px)
        col_i.image(os.path.join(IMAGE_FOLDER, img_name), width=150)
        
        # 3. 狀態判斷
        sample_history = records[records["樣品名稱"] == img_name]
        is_loaned = False
        if not sample_history.empty:
            last_rec = sample_history.iloc[-1]
            if last_rec["狀態"] == "借出中" and not last_rec["歸還日期"]:
                is_loaned = True
        
        with col_s:
            st.write(f"**{img_name}**")
            if is_loaned:
                st.error(f"❌ 已借出\n\n({last_rec['借出人員']})")
            else:
                st.success("✅ 在庫可借")

        # 4. 操作表單
        with col_f:
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
                    borrower = f1.selectbox("借用人", ["請選擇"] + user_list, key=f"sel_{i}")
                    l_date = f2.date_input("日期", datetime.now(), key=f"date_{i}")
                    note = f3.text_input("備註", key=f"note_{i}", placeholder="用途...")
                    if st.form_submit_button(f"登記借出 (項次 {i})", use_container_width=True):
                        if borrower == "請選擇":
                            st.error("請選人")
                        else:
                            new_row = {"項次": i, "樣品名稱": img_name, "借出人員": borrower,
                                       "借出日期": l_date.strftime("%Y-%m-%d"), "歸還日期": "",
                                       "備註": note, "狀態": "借出中"}
                            records = pd.concat([records, pd.DataFrame([new_row])], ignore_index=True)
                            save_data(records, RECORD_FILE)
                            st.rerun()

        # 5. 刪除項次功能
        with col_m:
            st.write("") # 對齊
            if st.button("🗑️", key=f"del_item_{i}", help="刪除此樣品及所有相關紀錄"):
                # 刪除實體檔案
                os.remove(os.path.join(IMAGE_FOLDER, img_name))
                # 刪除相關紀錄
                records = records[records["樣品名稱"] != img_name]
                save_data(records, RECORD_FILE)
                st.warning(f"項次 {i} 已刪除")
                st.rerun()
        st.write("---")

# --- 4. 數據分析區 ---
st.header("📊 歷史紀錄與數據分析")
tab1, tab2 = st.tabs(["📋 流向紀錄總表", "📈 借出數據分析"])

with tab1:
    st.dataframe(records, use_container_width=True, height=400)
    csv = records.to_csv(index=False).encode('utf-8')
    st.download_button("📥 匯出資料 (CSV)", csv, "3d_loan_history.csv", "text/csv")

with tab2:
    if not records.empty:
        st.markdown("### a. 各樣品借出次數統計")
        s_counts = records["樣品名稱"].value_counts().reset_index()
        s_counts.columns = ["樣品", "次數"]
        chart_a = alt.Chart(s_counts).mark_bar(color="#29b5e8").encode(
            x=alt.X("樣品:N", title="樣品名稱", sort='-y'),
            y=alt.Y("次數:Q", title="次數", axis=alt.Axis(tickMinStep=1, format='d'))
        ).properties(height=300)
        st.altair_chart(chart_a, use_container_width=True)

        st.markdown("### b. 熱門借用人員排行")
        u_counts = records["借出人員"].value_counts().reset_index()
        u_counts.columns = ["人員", "次數"]
        chart_b = alt.Chart(u_counts).mark_bar(color="#ff4b4b").encode(
            x=alt.X("人員:N", title="人員姓名", sort='-y'),
            y=alt.Y("次數:Q", title="次數", axis=alt.Axis(tickMinStep=1, format='d'))
        ).properties(height=300)
        st.altair_chart(chart_b, use_container_width=True)
    else:
        st.info("尚無足夠數據分析。")

def load_data(file, columns):
    if os.path.exists(file):
        try:
            return pd.read_csv(file).fillna("")
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, file):
    df.to_csv(file, index=False)

# 載入現有資料
records = load_data(RECORD_FILE, ["項次", "樣品名稱", "借出人員", "借出日期", "歸還日期", "備註", "狀態"])
user_df = load_data(USER_FILE, ["姓名"])
if user_df.empty:
    user_df = pd.DataFrame({"姓名": ["管理員"]})
    save_data(user_df, USER_FILE)

# --- 2. 側邊欄管理功能 ---
with st.sidebar:
    st.title("⚙️ 系統管理面板")
    
    # A. 新增樣品
    st.subheader("📷 新增樣品圖片")
    uploaded_file = st.file_uploader("上傳圖片 (jpg/png)", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        with open(os.path.join(IMAGE_FOLDER, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"樣品 {uploaded_file.name} 已新增")
        st.rerun()

    st.divider()

    # B. 人員名單管理
    st.subheader("👥 人員名單維護")
    new_user = st.text_input("輸入新姓名")
    if st.button("➕ 新增人員", use_container_width=True):
        if new_user and new_user not in user_df["姓名"].values:
            user_df = pd.concat([user_df, pd.DataFrame({"姓名": [new_user]})], ignore_index=True)
            save_data(user_df, USER_FILE)
            st.rerun()

    if not user_df.empty:
        target_user = st.selectbox("選取編輯對象", user_df["姓名"])
        edit_name = st.text_input("修改姓名為", value=target_user)
        col_edit, col_del = st.columns(2)
        with col_edit:
            if st.button("📝 修改", use_container_width=True):
                user_df.loc[user_df["姓名"] == target_user, "姓名"] = edit_name
                save_data(user_df, USER_FILE)
                st.rerun()
        with col_del:
            if st.button("🗑️ 刪除人員", use_container_width=True):
                user_df = user_df[user_df["姓名"] != target_user]
                save_data(user_df, USER_FILE)
                st.rerun()

# --- 3. 主介面：借還登記區 ---
st.title("📦 3D 列印樣品借出登記系統")
st.write("---")

image_files = sorted([f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
user_list = user_df["姓名"].tolist()

# 定義標題列 (比例微調以容納刪除按鈕)
h_num, h_img, h_info, h_form, h_manage = st.columns([0.5, 1.5, 2, 4.5, 1])
h_num.markdown("**項次**")
h_img.markdown("**樣品圖片**")
h_info.markdown("**狀態資訊**")
h_form.markdown("**登記與歸還操作**")
h_manage.markdown("**管理**")
st.write("---")

if not image_files:
    st.info("💡 目前沒有樣品，請從左側側邊欄上傳圖片。")
else:
    for i, img_name in enumerate(image_files, start=1):
        col_n, col_i, col_s, col_f, col_m = st.columns([0.5, 1.5, 2, 4.5, 1])
        
        # 1. 項次
        col_n.write(f"### {i}")
        
        # 2. 圖片 (150px)
        col_i.image(os.path.join(IMAGE_FOLDER, img_name), width=150)
        
        # 3. 狀態判斷
        sample_history = records[records["樣品名稱"] == img_name]
        is_loaned = False
        if not sample_history.empty:
            last_rec = sample_history.iloc[-1]
            if last_rec["狀態"] == "借出中" and not last_rec["歸還日期"]:
                is_loaned = True
        
        with col_s:
            st.write(f"**{img_name}**")
            if is_loaned:
                st.error(f"❌ 已借出\n\n({last_rec['借出人員']})")
            else:
                st.success("✅ 在庫可借")

        # 4. 操作表單
        with col_f:
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
                    borrower = f1.selectbox("借用人", ["請選擇"] + user_list, key=f"sel_{i}")
                    l_date = f2.date_input("日期", datetime.now(), key=f"date_{i}")
                    note = f3.text_input("備註", key=f"note_{i}", placeholder="用途...")
                    if st.form_submit_button(f"登記借出 (項次 {i})", use_container_width=True):
                        if borrower == "請選擇":
                            st.error("請選人")
                        else:
                            new_row = {"項次": i, "樣品名稱": img_name, "借出人員": borrower,
                                       "借出日期": l_date.strftime("%Y-%m-%d"), "歸還日期": "",
                                       "備註": note, "狀態": "借出中"}
                            records = pd.concat([records, pd.DataFrame([new_row])], ignore_index=True)
                            save_data(records, RECORD_FILE)
                            st.rerun()

        # 5. 刪除項次功能
        with col_m:
            st.write("") # 對齊
            if st.button("🗑️", key=f"del_item_{i}", help="刪除此樣品及所有相關紀錄"):
                # 刪除實體檔案
                os.remove(os.path.join(IMAGE_FOLDER, img_name))
                # 刪除相關紀錄
                records = records[records["樣品名稱"] != img_name]
                save_data(records, RECORD_FILE)
                st.warning(f"項次 {i} 已刪除")
                st.rerun()
        st.write("---")

# --- 4. 數據分析區 ---
st.header("📊 歷史紀錄與數據分析")
tab1, tab2 = st.tabs(["📋 流向紀錄總表", "📈 借出數據分析"])

with tab1:
    st.dataframe(records, use_container_width=True, height=400)
    csv = records.to_csv(index=False).encode('utf-8')
    st.download_button("📥 匯出資料 (CSV)", csv, "3d_loan_history.csv", "text/csv")

with tab2:
    if not records.empty:
        st.markdown("### a. 各樣品借出次數統計")
        s_counts = records["樣品名稱"].value_counts().reset_index()
        s_counts.columns = ["樣品", "次數"]
        chart_a = alt.Chart(s_counts).mark_bar(color="#29b5e8").encode(
            x=alt.X("樣品:N", title="樣品名稱", sort='-y'),
            y=alt.Y("次數:Q", title="次數", axis=alt.Axis(tickMinStep=1, format='d'))
        ).properties(height=300)
        st.altair_chart(chart_a, use_container_width=True)

        st.markdown("### b. 熱門借用人員排行")
        u_counts = records["借出人員"].value_counts().reset_index()
        u_counts.columns = ["人員", "次數"]
        chart_b = alt.Chart(u_counts).mark_bar(color="#ff4b4b").encode(
            x=alt.X("人員:N", title="人員姓名", sort='-y'),
            y=alt.Y("次數:Q", title="次數", axis=alt.Axis(tickMinStep=1, format='d'))
        ).properties(height=300)
        st.altair_chart(chart_b, use_container_width=True)
    else:
        st.info("尚無足夠數據分析。")
