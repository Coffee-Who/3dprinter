import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面基本配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide", page_icon="🖨️")

# 2. 全域樣式優化
st.markdown("""
    <style>
    /* 確保手機版側邊欄切換按鈕清晰可見 */
    [data-testid="stSidebarCollapseButton"] {
        background-color: #E2E8F0 !important;
        color: #1E40AF !important;
        border-radius: 8px !important;
        top: 10px !important;
    }
    
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #000000 !important; font-family: "Microsoft JhengHei", sans-serif; }

    /* --- 1. Upload 區塊：白底黑字 --- */
    div[data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important; 
        color: #000000 !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 8px !important;
        max-width: 250px !important; 
    }
    div[data-testid="stFileUploader"] label, 
    div[data-testid="stFileUploader"] p, 
    div[data-testid="stFileUploader"] small {
        color: #000000 !important;
    }

    /* --- 2. 輸入框 (數字、選單) 寬度縮小且藍底白字 --- */
    div[data-testid="stNumberInput"], 
    div[data-baseweb="select"] {
        max-width: 250px !important; 
    }

    div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] > div {
        background-color: #1E40AF !important; 
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    
    /* 強制輸入框內文字為白色 */
    div[data-testid="stNumberInput"] input, 
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* 3. 建議報價結果樣式 */
    .price-result {
        display: inline-block;
        background-color: #FFFF00 !important;
        color: #E11D48 !important;
        padding: 5px 15px;
        border-radius: 8px;
        font-size: 42px !important;
        font-weight: 900 !important;
        border: 3px solid #E11D48;
        max-width: 100%;
        word-break: break-all;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 登入檢核
if "password_correct" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>實威國際 3D列印線上估價</h2>", unsafe_allow_html=True)
    pwd = st.text_input("請輸入登入密碼", type="password")
    if st.button("進入系統"):
        if pwd == "1234":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("密碼錯誤")
    st.stop()

# 4. 資料加載
@st.cache_data
def load_materials():
    data = {
        "Formlabs": ["Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K"],
        "單價": [9975, 8500, 7500, 12000]
    }
    df = pd.DataFrame(data)
    # 換算每 mm3 的純材料成本
    df['每mm3成本'] = df['單價'] / 1000000 
    return df

# 5. 側邊欄導覽
with st.sidebar:
    try:
        st.image("solidwizard_logo.png", use_container_width=True)
    except:
        st.write("### SOLIDWIZARD")
    st.subheader("🛠️ 功能選單")
    choice = st.radio("請選擇作業項目：", ["💰 自動估價系統", "📏 尺寸校正計算"])
    st.divider()
    if st.button("登出系統"):
        del st.session_state["password_correct"]
        st.rerun()

# 6. 主程式邏輯
df_m = load_materials()

if choice == "💰 自動估價系統":
    st.title("💰 專業 3D 列印自動報價")
    input_method = st.radio("選擇體積來源：", ["📤 上傳 STL 檔案", "⌨️ 手動輸入數值"], horizontal=True)
    st.divider()
    
    vol_mm3 = 0
    if input_method == "📤 上傳 STL 檔案":
        st.write("### 第一步：請上傳 STL 檔案")
        up_file = st.file_uploader("Upload STL", type=["stl"], label_visibility="collapsed")
        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue()); t_path = tmp.name
            try:
                m_mesh = mesh.Mesh.from_file(t_path)
                v_val, _, _ = m_mesh.get_mass_properties()
                vol_mm3 = int(v_val)
            except: st.error("STL 解析失敗")
            finally: 
                if os.path.exists(t_path): os.remove(t_path)
    else:
        st.write("### 第一步：請手動輸入模型體積 (mm³)")
        vol_mm3 = st.number_input("體積 (mm³)", min_value=0, value=0, step=1, format="%d", label_visibility="collapsed")

    if vol_mm3 > 0:
        st.subheader("📊 報價參數設定")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**📐 當前體積:** {vol_mm3:,} mm³")
            # --- 材料選擇與成本顯示 ---
            m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
            u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每mm3成本"].values[0]
            raw_p = df_m.loc[df_m["Formlabs"] == m_choice, "單價"].values[0]
            
            # 新增：顯示材料成本
            st.info(f"💡 **材料成本詳細：**\n* 材料單價：NT$ {int(raw_p):,}/L\n* 換算成本：NT$ {u_cost:.6f}/mm³")

        with col2:
            markup = st.slider("2. 利潤倍率調整", 0.5, 10.0, 3.0, 0.5)
            base_fee = st.number_input("3. 報價基本費 (NT$)", value=150, step=10, format="%d")

        # 計算結果
        total = (vol_mm3 * u_cost * markup) + base_fee
        st.divider()
        st.write("### 建議報價總計")
        st.markdown(f'NT$ <span class="price-result">{int(total):,}</span>', unsafe_allow_html=True)

elif choice == "📏 尺寸校正計算":
    st.title("📏 尺寸校正補償計算")
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        d_size = st.number_input("CAD 設計尺寸 (mm)", min_value=0.01, value=20.00, step=0.01)
        a_size = st.number_input("實測成品尺寸 (mm)", min_value=0.01, value=19.80, step=0.01)
    
    if d_size > 0:
        factor = a_size / d_size
        suggested_scale = (1 / factor) * 100 if factor != 0 else 0
        st.divider()
        st.write("建議縮放比例")
        st.markdown(f'<span class="price-result">{suggested_scale:.2f}%</span>', unsafe_allow_html=True)
