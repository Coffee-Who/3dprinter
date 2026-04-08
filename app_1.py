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
    /* 基礎背景與文字 */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #000000 !important; font-family: "Microsoft JhengHei", sans-serif; }
    
    /* 1. 所有輸入框 (STL上傳、數字輸入、下拉選單) 藍底白字 + 縮小寬度 */
    div[data-testid="stFileUploader"], 
    div[data-testid="stNumberInput"], 
    div[data-baseweb="select"] {
        max-width: 300px !important; /* 5. 縮小所有輸入框寬度 */
    }

    /* 藍底白字樣式強制覆蓋 */
    div[data-testid="stFileUploader"] section,
    div[data-testid="stNumberInput"] input,
    div[data-baseweb="select"] > div {
        background-color: #1E40AF !important; 
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    
    /* 針對輸入內容的文字顏色 */
    div[data-testid="stNumberInput"] input, 
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* 2. 建議報價結果：黃底紅字且符合手機寬度 */
    .price-result {
        display: inline-block;
        background-color: #FFFF00 !important;
        color: #E11D48 !important;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 48px !important;
        font-weight: 900 !important;
        border: 3px solid #E11D48;
        max-width: 100%; /* 確保不超出螢幕 */
        word-break: break-all;
    }

    /* 滑桿標籤顏色 */
    .stSlider label p { color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 登入介面 (簡化版)
def apply_login_style():
    st.markdown("""
        <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stToolbar"] { display: none !important; }
        .stApp { background: #0F172A !important; }
        </style>
    """, unsafe_allow_html=True)

if "password_correct" not in st.session_state:
    apply_login_style()
    st.markdown("<h2 style='color:white; text-align:center;'>實威國際 3D列印線上估價</h2>", unsafe_allow_html=True)
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
    # 預設資料
    data = {
        "Formlabs": ["Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K"],
        "單價": [9975, 8500, 7500, 12000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 # 從 1L(1000000 mm3) 換算
    return df

# 5. 主程式
df_m = load_materials()
st.title("💰 專業 3D 列印自動報價")

input_method = st.radio("選擇體積來源：", ["📤 上傳 STL 檔案", "⌨️ 手動輸入數值"], horizontal=True)

vol_mm3 = 0
show_preview = False

if input_method == "📤 上傳 STL 檔案":
    st.write("### 第一步：請上傳 STL 檔案")
    up_file = st.file_uploader("Upload", type=["stl"], label_visibility="collapsed")
    if up_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
            tmp.write(up_file.getvalue()); t_path = tmp.name
        try:
            m_mesh = mesh.Mesh.from_file(t_path)
            v_val, _, _ = m_mesh.get_mass_properties()
            vol_mm3 = int(v_val) # 這裡獲得的是 mm3
            show_preview = True
        except: st.error("STL 解析失敗")
        finally: 
            if os.path.exists(t_path): os.remove(t_path)

else:
    # 3 & 4. 單位改為 mm³ 且內容預設為整數
    st.write("### 第一步：請手動輸入模型體積 (mm³)")
    vol_mm3 = st.number_input("體積輸入", min_value=0, value=0, step=1, format="%d", label_visibility="collapsed")

if vol_mm3 > 0:
    st.divider()
    
    # 參數設定區
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write(f"**📐 當前體積:** {vol_mm3:,} mm³")
        # 1. 選擇材料 (寬度已由 CSS 控制)
        m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
        u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每mm3成本"].values[0]
        raw_p = df_m.loc[df_m["Formlabs"] == m_choice, "單價"].values[0]
        st.write(f"材料單價: NT$ {int(raw_p):,}/L")

    with col2:
        # 6. 利潤倍率：0.5的倍數, 最高10倍
        markup = st.slider("2. 利潤倍率調整", 0.5, 10.0, 3.0, 0.5)
        # 3. 基本費
        base_fee = st.number_input("3. 報價基本費 (NT$)", value=150, step=10, format="%d")

    # 計算結果
    total = (vol_mm3 * u_cost * markup) + base_fee
    
    st.write("---")
    st.write("### 建議報價總計")
    # 2. 僅數字部分黃底紅字，且符合螢幕寬度
    st.markdown(f'NT$ <span class="price-result">{int(total):,}</span>', unsafe_allow_html=True)
    
    if show_preview:
        st.write("---")
        st.write("📦 模型預覽")
        # 簡單預覽圖省略以維持速度
