import streamlit as st
from streamlit_image_select import image_select
from stl import mesh
import tempfile
import os
import pandas as pd
from streamlit_stl import stl_from_file # 導入預覽套件

st.set_page_config(page_title="3D列印專業服務系統", page_icon="🖨️", layout="wide")

# --- 密碼與材料讀取 (保持不變) ---
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

@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

if check_password():
    df_materials = load_materials()
    
    with st.sidebar:
        selection = image_select(
            label="功能選單",
            images=["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"],
            captions=["自動估價系統", "SLA 尺寸校正"]
        )

    if "2953536" in selection:
        st.title("💰 Formlabs 自動估價與 3D 預覽")
        
        uploaded_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        col1, col2 = st.columns([1.5, 1]) # 左邊放預覽，寬度設大一點
        
        v_cm3 = 0.0
        
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            with col1:
                st.subheader("📦 3D 模型預覽")
                # 顯示 3D 預覽，可調整顏色與高度
                stl_from_file(file_path=tmp_path, color='#FF4B4B', material='flat', auto_rotate=True)
                st.caption("您可以按住左鍵旋轉，滾輪縮放模型")

            with col2:
                st.subheader("📊 體積與報價")
                try:
                    m = mesh.Mesh.from_file(tmp_path)
                    vol, _, _ = m.get_mass_properties()
                    v_cm3 = float(vol) / 1000.0
                    st.metric("偵測體積", f"{v_cm3:.2f} cm³")
                except:
                    st.error("解析失敗")
                
                material_choice = st.selectbox("樹脂型號", df_materials["Formlabs"].tolist())
                cost_unit = df_materials.loc[df_materials["Formlabs"] == material_choice, "每cm3成本"].values[0]
                markup = st.slider("報價倍率", 1.0, 10.0, 3.0)
                base_fee = st.number_input("基本起鍋費", value=150)
                
                total_price = (v_cm3 * cost_unit * markup) + base_fee
                st.divider()
                st.markdown(f"### 建議報價：<span style='color:red; font-size:40px;'>NT$ {int(total_price)}</span>", unsafe_allow_html=True)

            os.remove(tmp_path)
        else:
            st.info("💡 請上傳檔案來啟動 3D 預覽與估價")

    else:
        st.title("📏 SLA 尺寸校正助手")
        # (校正邏輯...)
