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
        # 直接讀取你上傳的這個檔名
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except Exception as e:
        st.error(f"⚠️ 找不到材料清單：請確認 GitHub 倉庫內有 Formlabs材料.csv 檔案")
        # 備用數據
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 程式主體 ---
if check_password():
    df_materials = load_materials()
    
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

    if "2953536" in selection:
        st.title("💰 Formlabs 自動估價系統")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("1. 檔案分析")
            uploaded_file = st.file_uploader("請上傳 STL 檔案 (單位: mm)", type=["stl"])
            
            v_cm3 = 0.0
            if uploaded_file:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                try:
                    m = mesh.Mesh.from_file(tmp_path)
                    vol, _, _ = m.get_mass_properties()
                    v_cm3 = float(vol) / 1000.0
                    st.success(f"✅ 偵測體積：{v_cm3:.2f} cm³")
                except:
                    st.error("STL 解析出錯")
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            
            # 即使沒上傳也可以手動微調體積
            v_cm3 = st.number_input("確認體積 (cm³)", value=v_cm3, step=0.1)

        with col2:
            st.subheader("2. 報價計算")
            # 選擇材料 (對應 CSV 中的 Formlabs 欄位)
            material_choice = st.selectbox("請選擇樹脂型號", df_materials["Formlabs"].tolist())
            
            # 取得單價
            cost_unit = df_materials.loc[df_materials["Formlabs"] == material_choice, "每cm3成本"].values[0]
            
            st.info(f"材料單價：NT$ {cost_unit:.2f} / cm³")
            
            # 設定參數
            markup = st.slider("報價倍率 (含支撐與利潤)", 1.0, 10.0, 3.0)
            base_fee = st.number_input("基本起鍋費", value=150)
            
            # 計算總價
            total_price = (v_cm3 * cost_unit * markup) + base_fee
            
            st.divider()
            # 顯示顯眼的總價
            st.markdown(f"### 📢 建議報價：<span style='color:red; font-size:40px;'>NT$ {int(total_price)}</span>", unsafe_allow_html=True)
            
            with st.expander("計算細節"):
                st.write(f"材料成本: {v_cm3 * cost_unit:.2f} 元")
                st.write(f"倍率加成: {(v_cm3 * cost_unit) * (markup - 1):.2f} 元")
                st.write(f"固定費用: {base_fee} 元")

    else:
        st.title("📏 SLA 尺寸校正助手")
        c1, c2 = st.columns(2)
        with c1:
            cad = st.number_input("CAD 設計值 (mm)", value=10.0)
        with c2:
            real = st.number_input("實際量測值 (mm)", value=10.0)
        
        if cad > 0:
            factor = real / cad
            st.metric("應填入 Preform 的校正因子", f"{factor:.4f}")
