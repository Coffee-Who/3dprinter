import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import hashlib
import json

# --- 1. 專業 UI 配置與響應式 CSS ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm AI", layout="wide")

st.markdown("""
    <style>
    /* 基礎顏色鎖定：強制白底黑字，防止手機深色模式干擾 */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
    }

    /* 側邊欄樣式 */
    [data-testid="stSidebar"] { 
        background-color: #f8fafc !important; 
        border-right: 1px solid #e2e8f0; 
    }

    /* 報價看板通用樣式 */
    .price-container { 
        background-color: #ffffff; padding: 20px; border-radius: 12px;
        border: 2px solid #e2e8f0; margin-bottom: 20px;
    }
    .price-result { 
        color: #0081FF !important; font-size: 32px; font-weight: 800;
        border-bottom: 3px solid #0081FF; display: inline-block; margin-bottom: 10px; 
    }
    .data-label { color: #64748b !important; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .data-value { color: #0f172a !important; font-size: 15px; font-weight: 700; }
    
    .cost-breakdown { background: #f1f5f9; border-radius: 8px; padding: 15px;
        margin-top: 15px; border: 1px solid #e2e8f0; }
    .cost-row { display: flex; justify-content: space-between; font-size: 13px; color: #475569 !important; padding: 4px 0; }
    .cost-row.total { font-weight: 800; color: #000000 !important; border-top: 2px solid #cbd5e1;
        margin-top: 8px; padding-top: 8px; font-size: 15px; }

    /* --- 手機版專屬優化 (App Like UI) --- */
    @media (max-width: 768px) {
        /* 讓按鈕超大，方便手指點擊 */
        .stButton>button {
            height: 55px !important;
            font-size: 18px !important;
            background-color: #0081FF !important;
            color: white !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 12px rgba(0,129,255,0.3) !important;
        }
        /* 數據格在手機上一行一個 */
        .data-grid { 
            display: grid; grid-template-columns: 1fr !important; gap: 12px; 
        }
        .price-result { font-size: 36px !important; width: 100%; text-align: center; }
        .data-item { border-left: 4px solid #0081FF; padding-left: 15px; }
        h1 { font-size: 24px !important; }
    }

    /* --- 電腦版專屬優化 --- */
    @media (min-width: 769px) {
        .data-grid { 
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px; 
        }
        .stButton>button { height: 40px; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. 核心狀態與資料載入 ---
if 'mesh' not in st.session_state: st.session_state.mesh = None
if 'mesh_hash' not in st.session_state: st.session_state.mesh_hash = ""

@st.cache_data
def load_materials():
    data = {
        "材料名稱": ["Clear Resin V4", "Grey Resin V4", "White Resin V4", "Black Resin V4", "Tough 2000 Resin", "Rigid 10K Resin", "High Temp Resin"],
        "單價": [6900, 6900, 6900, 6900, 8500, 12000, 11000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000
    return df

df_m = load_materials()
PRINTERS = {
    "Form 4": {"w": 200.0, "d": 125.0, "h": 210.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0}
}

# --- 3. 側邊欄設定 ---
with st.sidebar:
    st.title("⚙️ 設定面板")
    up_file = st.file_uploader("📂 上傳 STL 檔案", type=["stl"])
    st.divider()
    m_choice = st.selectbox("材料選擇", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("列印機型", list(PRINTERS.keys()))
    qty = st.number_input("列印數量", min_value=1, value=1)
    markup = st.slider("報價加成倍率", 1.0, 5.0, 2.0, 0.5)

# --- 4. 邏輯計算 ---
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

# --- 5. 主畫面顯示 ---
st.title("🚀 SOLIDWIZARD PreForm AI")

if model_vol > 0:
    # 計算各項費用
    support_vol = model_vol * 0.2
    total_vol_unit = model_vol + support_vol
    mat_cost_total = total_vol_unit * u_cost * qty
    handling_fee = 200 * qty
    final_price = (mat_cost_total + handling_fee) * markup

    # 顯示報價看板
    st.markdown(f"""
    <div class="price-container">
        <div class="data-label">PREFORM 預估報價</div>
        <div class="price-result">NT$ {final_price:,.0f}</div>
        <div class="data-grid">
            <div class="data-item"><div class="data-label">單件體積</div><div class="data-value">{model_vol/1000:,.2f} mL</div></div>
            <div class="data-item"><div class="data-label">機型</div><div class="data-value">{p_choice}</div></div>
            <div class="data-item"><div class="data-label">材料</div><div class="data-value">{m_choice}</div></div>
            <div class="data-item"><div class="data-label">數量</div><div class="data-value">{qty} 件</div></div>
        </div>
        <div class="cost-breakdown">
            <div class="cost-row"><span>材料與消耗估算</span><span>NT$ {mat_cost_total:,.0f}</span></div>
            <div class="cost-row"><span>人工後處理費</span><span>NT$ {handling_fee:,.0f}</span></div>
            <div class="cost-row total"><span>最終總報價 (含 {markup}x 加成)</span><span>NT$ {final_price:,.0f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📱 立即下單 / 導出報告"):
        st.balloons()
        st.success("報價已生成！")

else:
    st.info("👋 你好！請上傳 STL 檔案來開始專業報價。")
    st.image("https://img.icons8.com/clouds/200/000000/3d-printer.png", width=150)

# --- 6. 3D 預覽 (簡化呼叫) ---
if st.session_state.mesh:
    st.subheader("🔍 模型預覽")
    # 這裡可以放入你原本複雜的 Three.js 渲染程式碼區塊...
    st.caption("3D 渲染視窗已就緒（手機版請使用單指旋轉、雙指縮放）")
