import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import hashlib
import json

# --- 1. 專業 UI 配置（確保電腦版功能完整） ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm AI", layout="wide")

st.markdown("""
    <style>
    /* 基礎背景與文字：確保任何模式下文字都清晰 */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
    }
    
    /* 修正文字看不見的問題：鎖定所有主要文字顏色 */
    .stMarkdown, p, span, label, h1, h2, h3, h4 {
        color: #1e293b !important;
    }

    /* --- 手機版 (Mobile) 專屬優化 --- */
    @media (max-width: 768px) {
        /* 1. 讓按鈕變大，方便手指點擊 */
        div.stButton > button {
            height: 55px !important;
            font-size: 18px !important;
            background-color: #0081FF !important;
            color: white !important;
            border-radius: 12px !important;
            margin-top: 10px;
            margin-bottom: 10px;
        }

        /* 2. 報價看板手機版：單欄排版 */
        .price-container {
            padding: 15px !important;
            border: 2px solid #0081FF !important;
            border-radius: 12px;
        }
        .data-grid {
            display: flex !important;
            flex-direction: column !important;
            gap: 12px;
        }
        .price-result {
            font-size: 32px !important;
            color: #0081FF !important;
            font-weight: 800;
        }
        
        /* 3. 防止側邊欄在手機上卡住 */
        [data-testid="stSidebar"] {
            width: 80vw !important;
        }
    }

    /* --- 電腦版 (Desktop) 樣式修正：維持原樣 --- */
    @media (min-width: 769px) {
        .data-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
    }

    /* 報價看板內部的通用細節 */
    .data-item { border-left: 3px solid #0081FF; padding-left: 10px; }
    .data-label { color: #64748b !important; font-size: 10px; font-weight: bold; }
    .data-value { color: #0f172a !important; font-size: 16px; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 狀態初始化 ---
if 'mesh' not in st.session_state: st.session_state.mesh = None
if 'mesh_hash' not in st.session_state: st.session_state.mesh_hash = ""

# --- 3. 資料與側邊欄 (電腦版會顯示在左側) ---
@st.cache_data
def load_materials():
    data = {"材料名稱": ["Clear Resin V4", "Grey Resin V4", "White Resin V4", "Tough 2000 Resin"],
            "單價": [6900, 6900, 6900, 8500]}
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000
    return df

df_m = load_materials()

with st.sidebar:
    st.header("⚙️ 設定面板")
    up_file = st.file_uploader("📂 上傳 STL", type=["stl"])
    m_choice = st.selectbox("材料", df_m["材料名稱"].tolist())
    qty = st.number_input("數量", min_value=1, value=1)
    markup = st.number_input("加成", value=2.0)

# --- 4. 核心邏輯 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

if up_file:
    file_bytes = up_file.read()
    file_hash = hashlib.md5(file_bytes).hexdigest()
    if st.session_state.mesh_hash != file_hash:
        st.session_state.mesh = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
        st.session_state.mesh_hash = file_hash
    model_vol = abs(st.session_state.mesh.volume)
else:
    model_vol = 0

# --- 5. 主畫面 ---
st.title("SOLIDWIZARD PreForm")

if model_vol > 0:
    final_price = (model_vol * 1.2 * u_cost * qty + 200 * qty) * markup
    
    # 這裡使用我們定義的 CSS Class
    st.markdown(f"""
    <div class="price-container">
        <div class="data-label">預估報價</div>
        <div class="price-result">NT$ {final_price:,.0f}</div>
        <hr>
        <div class="data-grid">
            <div class="data-item"><div class="data-label">材料</div><div class="data-value">{m_choice}</div></div>
            <div class="data-item"><div class="data-label">數量</div><div class="data-value">{qty}</div></div>
            <div class="data-item"><div class="data-label">體積</div><div class="data-value">{model_vol/1000:.1f} mL</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 手機版這個按鈕會變超大，電腦版維持正常
    st.button("⚡ 確認下單")
    
    # 這裡放 3D 預覽 (Streamlit 內建原生支援，最保險)
    st.subheader("🔍 3D 預覽")
    # 如果要放你原本的渲染器程式碼，請放在這裡
    st.write("模型載入成功，可以開始進行分析。")
else:
    st.info("請從側邊欄上傳檔案。")
