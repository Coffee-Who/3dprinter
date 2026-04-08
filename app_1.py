import streamlit as st
from streamlit_image_select import image_select
from stl import mesh
import tempfile
import os
import pandas as pd

# 1. 必須放在最開頭的設定
st.set_page_config(page_title="3D列印專業助手", page_icon="🖨️", layout="wide")

# --- 簡單的密碼驗證系統 ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234": # 這裡可以改你的密碼
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
    else:
        return True

# --- 讀取 Excel 材料清單 ---
@st.cache_data
def load_materials():
    try:
        return pd.read_excel("materials.xlsx")
    except:
        return pd.DataFrame({"材料名稱": ["一般樹脂"], "每單位單價": [15]})

# --- 程式主體判斷 ---
if check_password():
    df_materials = load_materials()
    
    # --- 側邊欄：功能導覽 ---
    with st.sidebar:
        st.title("🛠️ 功能選單")
        selection = image_select(
            label="請選擇服務項目",
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png",
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ],
            captions=["自動估價系統", "SLA 尺寸校正"],
            index=0
        )
        st.success("身分驗證成功")

    # --- 邏輯 A：自動估價系統 ---
    if "2953536" in selection:
        st.title("💰 3D 列印自動估價系統")
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("1. 檔案分析")
            uploaded_file = st.file_uploader("上傳 STL 檔案", type=["stl"])
            v_cm3 = 0.0
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                m = mesh.Mesh.from_file(tmp_path)
                vol, _, _ = m.get_mass_properties()
                os.remove(tmp_path)
                v_cm3 = vol / 1000
                st.success(f"✅ 偵測體積：{v_cm3:.2f} cm³")
            else:
                v_cm3 = st.number_input("手動輸入體積 (cm³)", min_value=0.0)

        with col2:
            st.subheader("2. 報價設定")
            material_choice = st.selectbox("選擇材料 (從 Excel 讀取)", df_materials["材料名稱"])
            unit_price = df_materials.loc[df_materials["材料名稱"] == material_choice, "每單位單價"].values[0]
            
            price_per_cm3 = st.slider("調整單價 (NT$)", 5, 200, int(unit_price))
            base_fee = st.number_input("上機固定費 (NT$)", value=100)
            
            total = (v_cm3 * price_per_cm3) + base_fee
            st.divider()
            st.header(f"建議總價：NT$ {int(total)}")

    # --- 邏輯 B：尺寸校正助手 ---
    else:
        st.title("📏 SLA 尺寸校正助手")
        st.info("參考 Formlabs SOP 操作")
        c1, c2 = st.columns(2)
        with c1:
            cad_val = st.number_input("CAD 設計尺寸 (mm)", value=10.0)
        with c2:
            real_val = st.number_input("實際量測尺寸 (mm)", value=10.0)
        
        if cad_val > 0:
            factor = real_val / cad_val
            st.metric("應填入 Preform 的校正因子", f"{factor:.4f}")
