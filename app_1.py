import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面配置 (一定要在最前面)
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide", page_icon="🖨️")

# --- 2. 深度穿透 CSS (解決 Streamlit Cloud 偏左問題) ---
def apply_ultra_center_css():
    st.markdown("""
        <style>
        /* 隱藏預設 Header & 側邊欄 */
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }

        /* A. 強制全螢幕背景 */
        .stApp {
            background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%) !important;
            height: 100vh !important;
            width: 100vw !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        /* B. 強制破除 Streamlit 的隱形窄容器 (最重要的一段) */
        [data-testid="stAppViewContainer"], 
        [data-testid="stMain"], 
        [data-testid="stMainBlockContainer"],
        .main .block-container,
        .stVerticalBlock {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important; /* 水平軸置中 */
            justify-content: center !important; /* 垂直軸置中 */
            width: 100% !important;
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* C. Logo 置中修正 */
        [data-testid="stImage"] {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin-bottom: 20px !important;
        }
        [data-testid="stImage"] img {
            margin: 0 auto !important;
        }

        /* D. 標題文字 */
        .user-name {
            color: white !important;
            font-size: 32px !important;
            font-weight: 600 !important;
            margin-bottom: 40px !important;
            text-align: center !important;
            width: 100% !important;
            font-family: "Segoe UI", sans-serif;
        }

        /* E. 密碼框：精準置中 */
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 4px !important;
            width: 280px !important;
            margin: 0 auto !important;
        }
        input { 
            color: white !important; 
            text-align: center !important; 
            font-size: 18px !important;
        }
        
        /* F. 按鈕置中：強制覆寫 stButton 的容器 */
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
            border-radius: 4px !important;
            font-size: 16px !important;
            transition: 0.3s !important;
        }
        .stButton button:hover {
            background-color: rgba(255, 255, 255, 0.3) !important;
            border-color: white !important;
        }

        /* 錯誤提示置中 */
        .stAlert {
            background: transparent !important;
            border: none !important;
            color: #FDA4AF !important;
            text-align: center !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. 登入邏輯 (使用 st.stop 確保畫面乾淨) ---
if "password_correct" not in st.session_state:
    apply_ultra_center_css()
    
    # 直接垂直擺放，不使用 columns 以免產生側邊位移
    try:
        # 注意：請確認 solidwizard_logo.png 在你的 GitHub 根目錄
        st.image("solidwizard_logo.png", width=250)
    except:
        st.error("Logo 檔案讀取失敗，請確認檔案路徑。")

    st.markdown('<div class="user-name">實威國際 3D列印線上估價</div>', unsafe_allow_html=True)
    
    # 這裡的 label 要隱藏
    pwd = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="請輸入登入密碼")
    
    if st.button("登入系統"):
        if pwd == "1234":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("密碼驗證失敗，請重新輸入。")
    
    st.stop() # 這行很關鍵，沒登入就不跑後面的 Code

# --- 4. 登入成功後的內容 (恢復正常報價介面) ---
st.markdown("""
    <style>
    .stApp { background: white !important; align-items: flex-start !important; justify-content: flex-start !important; height: auto !important; }
    [data-testid="stAppViewContainer"], .main .block-container { 
        display: block !important; max-width: 1200px !important; margin: 0 auto !important; padding: 2rem !important; 
    }
    [data-testid="stSidebar"] { display: block !important; }
    [data-testid="stHeader"] { display: block !important; }
    </style>
""", unsafe_allow_html=True)

# 這裡放入你原本的 3D 報價程式碼...
st.title("💰 專業 3D 列印自動報價系統")
st.success("成功登入，歡迎使用！")
# (後面接原本的物料讀取與 3D 渲染邏輯)
