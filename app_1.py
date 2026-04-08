import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# ==========================================
# 1. 頁面基本配置
# ==========================================
st.set_page_config(
    page_title="實威國際 3D列印線上估價", 
    layout="wide", 
    page_icon="🖨️"
)

# ==========================================
# 2. 深度穿透 CSS (專門處理置中與輸入框顏色)
# ==========================================
def apply_login_style():
    st.markdown("""
        <style>
        /* 隱藏預設 Header & 側邊欄 */
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }

        /* A. 全站背景：深藍色漸層 */
        .stApp {
            background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%) !important;
            height: 100vh !important;
            width: 100vw !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        /* B. 強制破除 Streamlit 容器限制，達成絕對置中 */
        [data-testid="stAppViewContainer"], 
        [data-testid="stMain"], 
        [data-testid="stMainBlockContainer"],
        .main .block-container,
        .stVerticalBlock {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important; 
            justify-content: center !important;
            width: 100% !important;
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* C. Logo 置中 */
        [data-testid="stImage"] {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin-bottom: 20px !important;
        }

        /* D. 標題文字樣式 */
        .user-name {
            color: white !important;
            font-size: 32px !important;
            font-weight: 600 !important;
            margin-bottom: 40px !important;
            text-align: center !important;
            width: 100% !important;
            font-family: "Segoe UI", "Microsoft JhengHei", sans-serif;
        }

        /* E. 密碼輸入框：背景調亮，文字設定為黑色 */
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.95) !important; /* 近乎純白，方便看黑字 */
            border: 2px solid #3B82F6 !important;
            border-radius: 6px !important;
            width: 280px !important;
            margin: 0 auto !important;
        }
        input { 
            color: #000000 !important; /* 密碼文字黑色 */
            text-align: center !important; 
            font-size: 18px !important;
        }
        
        /* F. 登入按鈕置中 */
        div.stButton {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin-top: 25px !important;
        }
        .stButton button {
            width: 140px !important;
            height: 45px !important;
            background-color: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
            transition: 0.3s;
        }
        .stButton button:hover {
            background-color: rgba(255, 255, 255, 0.4) !important;
            border-color: white !important;
        }

        /* 錯誤提示 */
        .stAlert {
            background: transparent !important;
            border: none !important;
            color: #FDA4AF !important;
            text-align: center !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. 材料資料載入
# ==========================================
@st.cache_data
def load_materials():
    try:
        # 嘗試讀取 CSV
        df = pd.read_csv("Formlabs材料.csv")
        # 假設 CSV 欄位有 'Formlabs' (名稱) 與 '單價' (每升價格)
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        # 若讀取失敗的備份資料
        return pd.DataFrame({
            "Formlabs": ["一般樹脂 (Clear/Grey/White)", "Tough 2000", "Flexible 80A"],
            "每cm3成本": [6.5, 8.5, 9.5]
        })

# ==========================================
# 4. 登入系統邏輯
# ==========================================
if "password_correct" not in st.session_state:
    apply_login_style()
    
    # 顯示 Logo
    try:
        st.image("solidwizard_logo.png", width=250)
    except:
        st.write("🔧 **SolidWizard 3D Printing**")

    # 標題
    st.markdown('<div class="user-name">實威國際 3D列印線上估價</div>', unsafe_allow_html=True)
    
    # 輸入框
    pwd = st.text_input("PW", type="password", label_visibility="collapsed", placeholder="請輸入登入密碼")
    
    # 按鈕
    if st.button("進入系統"):
