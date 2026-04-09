import streamlit as st
import pandas as pd
import trimesh
import requests
import io

st.set_page_config(layout="wide", page_title="3D列印估價系統")

# ================= UI 強化 =================
st.markdown("""
<style>
/* 整體背景 */
.main {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}

/* 側邊欄 */
section[data-testid="stSidebar"] {
    background-color: #111827;
    color: white;
}

/* 卡片 */
.card {
    background: white;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* 報價主卡 */
.price-card {
    background: linear-gradient(135deg, #2563eb, #1e40af);
    color: white;
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(37,99,235,0.3);
}

/* 價格字 */
.price {
    font-size: 60px;
    font-weight: 800;
}

/* 小標題 */
.label {
    font-size: 14px;
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)

# ================= 讀 CSV =================
@st.cache_data
def load_materials():
    url = "https://raw.githubusercontent.com/Coffee-Who/3dprinter/main/Formlabs%E6%9D%90%E6%96%99.csv"
    r = requests.get(url)
    r.encoding = "utf-8"
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = df.columns.str.strip().str.replace('\ufeff', '')
    return df

df = load_materials()

# ================= Sidebar（真正控制台🔥） =================
st.sidebar.title("⚙️ 控制面板")

mode = st.sidebar.radio("輸入方式", ["上傳 STL", "手動輸入"])

volume_cm3 = 0

if mode == "上傳 STL":
    file = st.sidebar.file_uploader("上傳 STL", type=["stl"])
    if file:
        mesh = trimesh.load(file, file_type='stl')
        volume_cm3 = mesh.volume / 1000
        st.sidebar.success(f"{volume_cm3:.2f} cm³")
else:
    cm = st.sidebar.number_input("cm³", 0.0)
    mm = st.sidebar.number_input("mm³", 0.0)

    if cm > 0:
        volume_cm3 = cm
        st.sidebar.caption(f"{cm*1000:.0f} mm³")
    elif mm > 0:
        volume_cm3 = mm / 1000
        st.sidebar.caption(f"{volume_cm3:.2f} cm³")

material = st.sidebar.selectbox("材料", df["Formlabs"])
row = df[df["Formlabs"] == material].iloc[0]

cost_cm3 = row["單價"] / 1000

profit = st.sidebar.number_input("利潤倍率", 1.0, step=0.5)
support = st.sidebar.slider("支撐 (%)", 0, 50, 20, step=5)

# ================= 主畫面 =================
st.title("🧮 3D列印即時估價系統")

if volume_cm3 > 0:

    effective = volume_cm3 * (1 + support / 100)
    cost = effective * cost_cm3
    price = cost * profit

    # 🔥 主報價卡（超有感）
    st.markdown(f"""
    <div class="price-card">
        <div class="label">預估報價</div>
        <div class="price">NT$ {int(price)}</div>
    </div>
    """, unsafe_allow_html=True)

    # 📊 數據卡片
    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div class="card">
        <div class="label">原始體積</div>
        <h2>{volume_cm3:.2f} cm³</h2>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="card">
        <div class="label">含支撐體積</div>
        <h2>{effective:.2f} cm³</h2>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="card">
        <div class="label">材料成本</div>
        <h2>{int(cost)} 元</h2>
    </div>
    """, unsafe_allow_html=True)

    # 📋 報價文字
    st.markdown("### 📋 報價內容")
    st.code(f"""
材料：{material}
體積：{volume_cm3:.2f} cm³
支撐：{support}%
報價：NT$ {int(price)}
""")

else:
    st.info("請在左側輸入資料")
