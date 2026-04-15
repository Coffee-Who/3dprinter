import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import hashlib
import json
from scipy.spatial import cKDTree

# ==============================
# 🌙 100% 深色 UI
# ==============================
st.set_page_config(page_title="SOLIDWIZARD | PreForm AI", layout="wide")

st.markdown("""
<style>

/* ===== 全域 ===== */
html, body, [class*="css"] {
    background-color: #0b1220 !important;
    color: #e2e8f0 !important;
}

/* 主畫面 */
.main, .block-container {
    background-color: #0b1220 !important;
}

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ===== 標題 ===== */
h1, h2, h3, h4 {
    color: #f1f5f9 !important;
}

/* ===== Input ===== */
input, textarea, select {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}

/* ===== 按鈕 ===== */
.stButton>button {
    width: 100%;
    border-radius: 6px;
    font-weight: 600;
    background-color: #1e293b;
    color: #e2e8f0;
    border: 1px solid #334155;
    height: 38px;
    transition: all .15s;
}

.stButton>button:hover {
    background-color: #2563eb;
    color: white;
}

/* ===== 卡片 ===== */
.price-container {
    background-color: #111827;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #1f2937;
}

.price-result {
    color: #38bdf8;
    font-size: 32px;
    font-weight: 800;
}

/* ===== scrollbar ===== */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #334155;
}

/* ===== 提示 ===== */
.priority-note {
    background: rgba(59,130,246,0.15);
    color: #93c5fd;
    border-left: 3px solid #3b82f6;
    padding: 8px;
    border-radius: 4px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# 初始化
# ==============================
for k, v in [('mesh', None), ('mesh_hash', ""), ('thin_faces', None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ==============================
# 材料資料
# ==============================
@st.cache_data
def load_materials():
    df = pd.DataFrame({
        "材料名稱": ["Clear Resin V4", "Grey Resin V4", "Tough 2000"],
        "單價": [6900, 6900, 8500]
    })
    df["每mm3成本"] = df["單價"] / 1000000
    return df

df_m = load_materials()

PRINTERS = {
    "Form 4": {"w":200,"d":125,"h":210,"layer_time_sec":5},
    "Form 4L": {"w":353,"d":196,"h":350,"layer_time_sec":6},
}

# ==============================
# Sidebar
# ==============================
with st.sidebar:
    st.title("PreForm 模擬報價")

    st.markdown('<div class="priority-note">📌 上傳 STL 優先</div>', unsafe_allow_html=True)

    manual_v = st.number_input("體積 mm³", 0.0)

    up_file = st.file_uploader("上傳 STL", type=["stl"])

    m_choice = st.selectbox("材料", df_m["材料名稱"])
    p_choice = st.selectbox("機型", list(PRINTERS.keys()))

    qty = st.number_input("數量", 1)
    markup = st.number_input("倍率", 2.0)

# ==============================
# STL 讀取
# ==============================
if up_file:
    file_bytes = up_file.read()
    file_hash = hashlib.md5(file_bytes).hexdigest()

    if file_hash != st.session_state.mesh_hash:
        mesh = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
        st.session_state.mesh = mesh
        st.session_state.mesh_hash = file_hash

# ==============================
# 計算
# ==============================
use_stl = st.session_state.mesh is not None

if use_stl or manual_v > 0:

    if use_stl:
        vol = abs(st.session_state.mesh.volume)
    else:
        vol = manual_v

    u_cost = df_m[df_m["材料名稱"] == m_choice]["每mm3成本"].values[0]

    total = vol * u_cost * qty
    final = total * markup

    st.markdown(f"""
    <div class="price-container">
        <div>預估價格</div>
        <div class="price-result">NT$ {final:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

    if use_stl:
        st.write("模型體積:", f"{vol:,.0f} mm³")
        st.write("面數:", len(st.session_state.mesh.faces))

else:
    st.info("請上傳 STL 或輸入體積")
