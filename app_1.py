import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide", page_icon="🖨️")

# --- 2. 暴力破解置中 CSS ---
def apply_ultra_center_css():
    st.markdown("""
        <style>
        /* 隱藏預設元件 */
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }

        /* A. 強制最外層容器撐滿全螢幕並水平垂直置中 */
        .stApp {
            background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%) !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            height: 100vh !important;
            width: 100vw !important;
            overflow: hidden !important;
        }

        /* B. 核心：穿透 Streamlit 的隱形窄容器，強制它變寬並置中 */
        [data-testid="stAppViewContainer"], [data-testid="stMain"], .main .block-container {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important; 
            justify-content: center !important;
            width: 100% !important;
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 auto !important;
        }

        /* C. Logo 置中：無視所有預設 padding */
        [data-testid="stImage"] {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
        }
        [data-testid="stImage"] img {
            margin: 0 auto !important;
        }

        /* D. 標題文字 */
        .user-name {
            color: white !important;
            font-size: 28px !important;
            font-weight: 500 !important;
            margin: 20px 0 35px 0 !important;
            text-align: center !important;
            width: 100% !important;
        }

        /* E. 密碼框：精準控制寬度 */
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 4px !important;
            width: 260px !important;
            margin: 0 auto !important;
        }
        input { color: white !important; text-align: center !important; }
        
        /* F. 按鈕置中：這是最難搞的一層，直接針對 div 強制 flex */
        div.stButton {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin: 15px 0 0 0 !important;
        }
        .stButton button {
            width: 120px !important;
            background-color: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            margin: 0 auto !important;
            display: block !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. 密碼邏輯 ---
if "password_correct" not in st.session_state:
    apply_ultra_center_css()
    
    # 這裡「絕對不要」使用 st.columns，因為 columns 會產生新的偏左容器
    try:
        st.image("solidwizard_logo.png", width=240)
    except:
        st.warning("⚠️ 請確認 solidwizard_logo.png 存在")

    st.markdown('<div class="user-name">實威國際 3D列印線上估價</div>', unsafe_allow_html=True)
    
    pwd = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="輸入密碼")
    
    if st.button("登入"):
        if pwd == "1234":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("密碼錯誤")
    st.stop() # 停止執行後續程式碼，確保登入畫面乾淨

# --- 4. 登入後的內容 (恢復正常報價系統) ---
st.markdown("""
    <style>
    .stApp { background: white !important; align-items: flex-start !important; justify-content: flex-start !important; height: auto !important; overflow: auto !important;}
    .main .block-container { max-width: 1200px !important; padding: 2rem !important; display: block !important;}
    [data-testid="stHeader"] { display: block !important; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 專業 3D 列印自動報價")
st.write("恭喜登入成功！請開始使用系統。")
# ... (後續報價程式碼維持不變)
