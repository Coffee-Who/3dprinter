import streamlit as st
import pandas as pd
import trimesh
import requests
import io

# =========================
# 頁面設定（手機預設開sidebar）
# =========================
st.set_page_config(
    page_title="3D列印估價系統",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# UI STYLE（產品級）
# =========================
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
    color: white;
}

/* 卡片 */
.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* 報價卡 */
.price-card {
    background: linear-gradient(135deg, #2563eb, #1e3a8a);
    color: white;
    padding: 30px;
    border-radius: 20px;
    text-align: center;
}

/* 價格 */
.price {
    font-size: 60px;
    font-weight: 800;
}

/* 小字 */
.label {
    font-size: 14px;
    opacity: 0.85;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 讀取材料 CSV
# =========================
@st.cache_data
def load_materials():
    url = "https://raw.githubusercontent.com/Coffee-Who/3dprinter/main/Formlabs%E6%9D%90%E6%96%99.csv"
    r = requests.get(url)
    r.encoding = "utf-8"
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = df.columns.str.strip().str.replace('\ufeff', '')
    return df

df = load_materials()

# =========================
# Sidebar 控制台
# =========================
st.sidebar.title("⚙️ 控制面板")

mode = st.sidebar.radio("輸入方式", ["上傳 STL", "手動輸入"])

volume_cm3 = 0
mesh = None
uploaded_file = None

# ===== STL =====
if mode == "上傳 STL":
    uploaded_file = st.sidebar.file_uploader("上傳 STL", type=["stl"])

    if uploaded_file:
        try:
            mesh = trimesh.load(uploaded_file, file_type='stl')
            volume_cm3 = mesh.volume / 1000
            st.sidebar.success(f"{volume_cm3:.2f} cm³")
        except:
            st.sidebar.error("檔案解析失敗")

# ===== 手動 =====
else:
    cm = st.sidebar.number_input("體積 (cm³)", 0.0)
    mm = st.sidebar.number_input("體積 (mm³)", 0.0)

    if cm > 0:
        volume_cm3 = cm
        st.sidebar.caption(f"{cm*1000:.0f} mm³")
    elif mm > 0:
        volume_cm3 = mm / 1000
        st.sidebar.caption(f"{volume_cm3:.2f} cm³")

# ===== 材料 =====
material = st.sidebar.selectbox("材料", df["Formlabs"])
row = df[df["Formlabs"] == material].iloc[0]

cost_cm3 = row["單價"] / 1000

# ===== 參數 =====
profit = st.sidebar.number_input("利潤倍率", 1.0, step=0.5)
support = st.sidebar.slider("支撐 (%)", 0, 50, 20, step=5)

# =========================
# 主畫面
# =========================
st.title("🧮 3D列印即時估價系統")

if volume_cm3 > 0:

    effective = volume_cm3 * (1 + support / 100)
    cost = effective * cost_cm3
    price = cost * profit

    # 🔥 報價主卡
    st.markdown(f"""
    <div class="price-card">
        <div class="label">預估報價</div>
        <div class="price">NT$ {int(price)}</div>
    </div>
    """, unsafe_allow_html=True)

    # 📊 數據卡
    c1, c2, c3 = st.columns(3)

    c1.markdown(f"""
    <div class="card">
        <div class="label">原始體積</div>
        <h2>{volume_cm3:.2f} cm³</h2>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="card">
        <div class="label">含支撐體積</div>
        <h2>{effective:.2f} cm³</h2>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="card">
        <div class="label">材料成本</div>
        <h2>{int(cost)} 元</h2>
    </div>
    """, unsafe_allow_html=True)

    # =========================
    # 🔥 3D 預覽
    # =========================
    if mesh is not None:

        st.markdown("### 🧊 3D模型預覽")

        try:
            import plotly.graph_objects as go

            vertices = mesh.vertices
            faces = mesh.faces

            fig = go.Figure(data=[go.Mesh3d(
                x=vertices[:, 0],
                y=vertices[:, 1],
                z=vertices[:, 2],
                i=faces[:, 0],
                j=faces[:, 1],
                k=faces[:, 2],
                color='lightblue'
            )])

            fig.update_layout(height=500, margin=dict(l=0,r=0,t=0,b=0))

            st.plotly_chart(fig, use_container_width=True)

        except:
            st.warning("模型過大或無法預覽")

    # =========================
    # 報價文字
    # =========================
    st.markdown("### 📋 報價內容")

    st.code(f"""
材料：{material}
體積：{volume_cm3:.2f} cm³
支撐：{support}%
報價：NT$ {int(price)}
""")

else:
    st.info("請從左側開始輸入資料")
