import streamlit as st
from streamlit_image_select import image_select
from stl import mesh
import tempfile
import os
import pandas as pd

# 1. 基礎頁面設定
st.set_page_config(page_title="3D列印專業服務系統", page_icon="🖨️", layout="wide")

# --- 2. 密碼驗證系統 ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234":  # 這裡設定你的開啟密碼
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 內部系統存取限制")
        st.text_input("請輸入開啟密碼", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("密碼錯誤，請重新輸入", type="password", on_change=password_entered, key="password")
        st.error("😕 密碼不正確")
        return False
    return True

# --- 3. 讀取材料清單並換算單價 ---
@st.cache_data
def load_materials():
    try:
        # 讀取你上傳的 CSV 檔案
        df = pd.read_csv("Formlabs材料.xlsx - 工作表1.csv")
        # 自動計算每 cm3 的成本 (單價 / 1000)
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except Exception as e:
        st.error(f"找不到材料清單檔案: {e}")
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 程式主體 ---
if check_password():
    df_materials = load_materials()
    
    # --- 側邊欄：功能選單 ---
    with st.sidebar:
        st.title("🛠️ 功能選單")
        selection = image_select(
            label="請選擇服務項目",
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png", # 估價
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"  # 校正
            ],
            captions=["自動估價系統", "SLA 尺寸校正"],
            index=0
        )
        st.success("身分驗證成功")

    # --- 邏輯 A：自動估價系統 ---
    if "2953536" in selection:
        st.title("💰 Formlabs 自動估價系統")
        st.write("上傳 STL 檔案即可根據您的 Formlabs 材料表自動計算報價。")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("1. 檔案分析")
            uploaded_file = st.file_uploader("請上傳 STL 檔案 (單位: mm)", type=["stl"])
            
            v_cm3 = 0.0
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                m = mesh.Mesh.from_file(tmp_path)
                vol, _, _ = m.get_mass_properties()
                os.remove(tmp_path)
                v_cm3 = vol / 1000
                st.success(f"✅ 偵測模型體積：{v_cm3:.2f
