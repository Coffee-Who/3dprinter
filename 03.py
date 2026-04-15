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
import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import hashlib
import json
from scipy.spatial import cKDTree

# --- 1. PreForm 專業 UI 配置 (包含手機版顏色修正) ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm AI", layout="wide")

st.markdown("""
    <style>
    /* 強制網頁背景為白色，文字為深色，防止手機深色模式干擾 */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }

    /* 修正所有 Markdown 文字顏色 */
    .stMarkdown, p, span, label {
        color: #1e293b !important;
    }

    /* 側邊欄樣式修正 */
    [data-testid="stSidebar"] { 
        background-color: #f8fafc !important; 
        border-right: 1px solid #e2e8f0; 
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: #334155 !important;
    }

    /* 按鈕樣式 */
    .stButton>button { 
        width: 100%; border-radius: 4px; font-weight: 600; background-color: #ffffff;
        border: 1px solid #cbd5e1; height: 36px; font-size: 12px; transition: all .15s;
        color: #1e293b !important;
    }
    .stButton>button:hover { 
        background-color: #0081FF !important; color: white !important; border-color: #0081FF; 
    }

    /* 報價看板樣式優化 */
    .price-container { 
        background-color: #ffffff; padding: 20px; border-radius: 8px;
        border: 2px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); 
    }
    .price-result { 
        color: #0081FF !important; font-size: 32px; font-weight: 800;
        border-bottom: 3px solid #0081FF; display: inline-block; margin-bottom: 10px; 
    }
    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .data-item { border-left: 3px solid #0081FF; padding-left: 10px; }
    .data-label { color: #64748b !important; font-size: 10px; font-weight: bold; text-transform: uppercase; }
    .data-value { color: #0f172a !important; font-size: 14px; font-weight: 700; }
    
    .cost-breakdown { background: #f1f5f9; border-radius: 6px; padding: 12px 16px;
        margin-top: 12px; border: 1px solid #e2e8f0; }
    .cost-row { display: flex; justify-content: space-between; font-size: 12px; color: #475569 !important; padding: 3px 0; }
    .cost-row.total { font-weight: 700; color: #000000 !important; border-top: 1px solid #cbd5e1;
        margin-top: 6px; padding-top: 6px; font-size: 13px; }

    /* 工具面板標題 */
    h1, h2, h3, h4 { color: #0f172a !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 核心狀態初始化 ---
for k, v in [('offset', [0.0, 0.0]), ('mesh', None), ('mesh_hash', ""), ('thin_faces', None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# --- 3. 材料與設備規格 ---
@st.cache_data
def load_materials():
    data = {
        "材料名稱": [
            "Clear Resin V4", "Grey Resin V4", "White Resin V4", "Black Resin V4",
            "Draft Resin V2", "Model Resin V3", "Tough 2000 Resin", "Tough 1500 Resin",
            "Durable Resin", "Grey Pro Resin", "Rigid 10K Resin", "Rigid 4000 Resin",
            "Flexible 80A Resin", "Elastic 50A Resin", "High Temp Resin", "Flame Retardant Resin",
            "ESD Resin", "BioMed Clear Resin", "BioMed Amber Resin", "BioMed White Resin",
            "BioMed Black Resin", "Custom Tray Resin", "IBT Resin", "Precision Model Resin",
            "Castable Wax 40 Resin", "Castable Wax Resin", "Silicone 40A Resin", "Alumina 4N Resin"
        ],
        "單價": [6900, 6900, 6900, 6900, 6900, 6900, 8500, 8500, 8500, 8500, 12000, 8500,
                 9500, 9500, 11000, 12000, 12000, 13500, 13500, 13500, 13500, 13500, 13500,
                 8500, 15000, 15000, 18000, 25000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000
    return df

df_m = load_materials()
PRINTERS = {
    "Form 4":  {"w": 200.0, "d": 125.0, "h": 210.0, "layer_time_sec": 5.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0, "layer_time_sec": 6.0},
}

# --- 4. 側邊欄 UI ---
with st.sidebar:
    st.title("PreForm 模擬報價")
    st.info("📌 上傳 STL 優先；未上傳時使用手動體積估算。")

    st.subheader("⌨️ 手動估價")
    m_unit = st.radio("單位", ["mm³", "cm³"], horizontal=True)
    manual_v = st.number_input("體積值", min_value=0.0, step=100.0)

    st.subheader("📂 上傳 STL 檔案")
    up_file = st.file_uploader("選擇 STL 檔案", type=["stl"])

    st.divider()
    m_choice = st.selectbox("材料選擇", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("機型選擇", list(PRINTERS.keys()))
    qty = st.number_input("數量", min_value=1, value=1)
    markup = st.number_input("報價加成倍率", min_value=1.0, value=2.0)
    handling_fee = st.number_input("基本處理費/件 (NT$)", min_value=0, value=200)

# --- 5. 計算與邏輯 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

# STL 處理邏輯 (簡化示意)
if up_file:
    file_bytes = up_file.read()
    st.session_state.mesh = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
    model_vol = st.session_state.mesh.volume
else:
    model_vol = manual_v if m_unit == "mm³" else manual_v * 1000

if model_vol > 0:
    support_vol = model_vol * 0.2
    total_vol = model_vol + support_vol
    material_cost = total_vol * u_cost * qty
    total_handling = handling_fee * qty
    final_price = (material_cost + total_handling) * markup

    # --- 6. 顯示報價結果 ---
    st.markdown(f"""
    <div class="price-container">
        <div style="font-size:13px;color:#64748b;font-weight:bold;margin-bottom:4px;">PREFORM 預估總列印成本</div>
        <div class="price-result">NT$ {final_price:,.0f}</div>
        <div class="data-grid">
            <div class="data-item"><div class="data-label">模型體積</div><div class="data-value">{model_vol:,.1f} mm³</div></div>
            <div class="data-item"><div class="data-label">使用材料</div><div class="data-value">{m_choice}</div></div>
            <div class="data-item"><div class="data-label">含支撐消耗</div><div class="data-value">{total_vol*qty/1000:,.2f} mL</div></div>
            <div class="data-item"><div class="data-label">加成倍率</div><div class="data-value">{markup} x</div></div>
        </div>
        <div class="cost-breakdown">
            <div class="cost-row"><span>材料費 (含支撐)</span><span>NT$ {material_cost:,.0f}</span></div>
            <div class="cost-row"><span>後處理費</span><span>NT$ {total_handling:,.0f}</span></div>
            <div class="cost-row total"><span>最終總報價</span><span>NT$ {final_price:,.0f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("請於左側輸入體積或上傳檔案以開始計算。")
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
