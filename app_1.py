import streamlit as st
from streamlit_image_select import image_select
from stl import mesh
import tempfile
import os
import pandas as pd
from streamlit_stl import stl_from_file

# 1. 基礎頁面設定
st.set_page_config(page_title="3D列印專業服務系統", page_icon="🖨️", layout="wide")

# --- 2. 密碼驗證系統 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 內部系統存取限制")
        pwd = st.text_input("請輸入開啟密碼", type="password")
        if st.button("登入"):
            if pwd == "1234":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("密碼錯誤")
        return False
    return True

# --- 3. 讀取材料清單 ---
@st.cache_data
def load_materials():
    try:
        # 讀取你提供的 Formlabs材料.csv
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 程式主體 ---
if check_password():
    df_materials = load_materials()
    
    with st.sidebar:
        st.title("🛠️ 功能選單")
        selection = image_select(
            label="功能導覽",
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png",
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ],
            captions=["自動估價系統", "SLA 尺寸校正"],
            index=0
        )

    if "2953536" in selection:
        st.title("💰 Formlabs 自動估價系統")
        
        uploaded_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        col1, col2 = st.columns([1.5, 1])
        
        v_cm3 = 0.0
        
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            with col1:
                st.subheader("📦 3D 網格預覽")
                # --- 開啟三角網格模式 ---
                stl_from_file(
                    file_path=tmp_path, 
                    color='#808080',      # 設定成沉穩的灰色
                    material='flat', 
                    auto_rotate=True,
                    wireframe=True        # <--- 重點！開啟三角網格顯示
                )
                st.caption("提示：滑鼠左鍵旋轉、右鍵平移、滾輪縮放。可以看到細膩的三角網格。")

            with col2:
                st.subheader("📊 數據分析")
                try:
                    m = mesh.Mesh.from_file(tmp_path)
                    vol, _, _ = m.get_mass_properties()
                    v_cm3 = float(vol) / 1000.0
                    st.metric("模型體積", f"{v_cm3:.2f} cm³")
                except:
                    st.error("解析失敗")
                
                material_choice = st.selectbox("選擇材料型號", df_materials["Formlabs"].tolist())
                cost_unit = df_materials.loc[df_materials["Formlabs"] == material_choice, "每cm3成本"].values[0]
                
                markup = st.slider("報價倍率", 1.0, 10.0, 3.0)
                base_fee = st.number_input("基本起鍋費", value=150)
                
                total_price = (v_cm3 * cost_unit * markup) + base_fee
                st.divider()
                st.markdown(f"### 📢 建議報價：<span style='color:red; font-size:40px;'>NT$ {int(total_price)}</span>", unsafe_allow_html=True)

            os.remove(tmp_path)
        else:
            st.info("請先上傳 STL 檔案以查看預覽與價格。")

    else:
        # 校正助手邏輯保持不變...
        st.title("📏 SLA 尺寸校正助手")
        # (您的校正程式碼...)
