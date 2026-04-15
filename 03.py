import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import hashlib

# ==============================
# ✅ 一定要先設定（避免錯誤）
# ==============================
st.set_page_config(
    page_title="SOLIDWIZARD | PreForm AI",
    layout="wide"
)

# ==============================
# 🌙 高對比深色 UI（桌機＋手機）
# ==============================
st.markdown("""
<style>

/* ===== 全域 ===== */
html, body, .main, .block-container {
    background-color: #0a0f1c !important;
    color: #e5e7eb !important;
}

/* ===== Sidebar ===== */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}

[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* ===== 標題 ===== */
h1, h2, h3, h4 {
    color: #f8fafc !important;
}

/* ===== Label ===== */
label {
    color: #9ca3af !important;
}

/* ===== Input ===== */
input, textarea, select {
    background-color: #111827 !important;
    color: #f9fafb !important;
    border: 1px solid #374151 !important;
}

/* ===== Button ===== */
.stButton>button {
    background-color: #1f2937;
    color: #e5e7eb;
    border: 1px solid #374151;
}

.stButton>button:hover {
    background-color: #2563eb;
    color: white;
}

/* ===== 卡片 ===== */
.price-box {
    background: #111827;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #1f2937;
}

.price {
    font-size: 32px;
    font-weight: 800;
    color: #22d3ee;
}

/* ===== 提示 ===== */
.priority-note {
    background: rgba(59,130,246,0.2);
    padding: 10px;
    border-left: 4px solid #3b82f6;
    color: #93c5fd;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# 📦 材料資料
# ==============================
@st.cache_data
def load_materials():
    df = pd.DataFrame({
        "材料名稱": ["Clear Resin V4", "Grey Resin V4", "Tough 2000 Resin"],
        "單價": [6900, 6900, 8500]
    })
    df["每mm3成本"] = df["單價"] / 1000000
    return df

df_m = load_materials()

# ==============================
# 🔧 Sidebar
# ==============================
with st.sidebar:
    st.title("PreForm 模擬報價")

    st.markdown('<div class="priority-note">📌 上傳 STL 優先</div>', unsafe_allow_html=True)

    manual_v = st.number_input("體積 (mm³)", min_value=0.0)

    uploaded_file = st.file_uploader("上傳 STL", type=["stl"])

    material = st.selectbox("材料", df_m["材料名稱"])
    qty = st.number_input("數量", min_value=1, value=1)
    markup = st.number_input("倍率", min_value=1.0, value=2.0)

# ==============================
# 📂 STL 載入
# ==============================
mesh = None

if uploaded_file:
    try:
        file_bytes = uploaded_file.read()
        mesh = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
    except:
        st.error("❌ STL 載入失敗")

# ==============================
# 💰 計算
# ==============================
use_stl = mesh is not None

if use_stl or manual_v > 0:

    if use_stl:
        try:
            volume = abs(mesh.volume)
        except:
            volume = 0
    else:
        volume = manual_v

    unit_cost = df_m[df_m["材料名稱"] == material]["每mm3成本"].values[0]

    material_cost = volume * unit_cost * qty
    final_price = material_cost * markup

    # ==============================
    # 📊 顯示
    # ==============================
    st.markdown(f"""
    <div class="price-box">
        <div>💰 預估報價</div>
        <div class="price">NT$ {final_price:,.0f}</div>
        <br>
        <div>體積：{volume:,.0f} mm³</div>
        <div>數量：{qty}</div>
        <div>材料：{material}</div>
    </div>
    """, unsafe_allow_html=True)

    if use_stl:
        st.write("📐 模型面數：", len(mesh.faces))

else:
    st.info("👉 請上傳 STL 或輸入體積")
