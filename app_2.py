import streamlit as st
import pandas as pd
import trimesh
import requests
import io

# =========================
# 頁面設定
# =========================
st.set_page_config(
    page_title="3D列印估價系統",
    layout="wide"
)

# =========================
# 高級 UI 樣式
# =========================
st.markdown("""
<style>
/* 背景 */
.main {
    background-color: #f3f4f6;
}

/* 標題 */
.title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 10px;
}

/* 卡片 */
.card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* 報價 */
.price {
    font-size: 48px;
    font-weight: 800;
    color: #2563eb;
}

/* 小字 */
.label {
    color: #6b7280;
    font-size: 14px;
}

/* 分隔 */
hr {
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 讀取材料
# =========================
@st.cache_data
def load_materials():
    url = "https://raw.githubusercontent.com/Coffee-Who/3dprinter/main/Formlabs%E6%9D%90%E6%96%99.csv"
    response = requests.get(url)
    response.encoding = 'utf-8'
    df = pd.read_csv(io.StringIO(response.text))
    df.columns = df.columns.str.strip().str.replace('\ufeff', '')
    return df

materials_df = load_materials()

# =========================
# 標題
# =========================
st.markdown('<div class="title">🧮 3D列印快速估價系統</div>', unsafe_allow_html=True)

# =========================
# 版面
# =========================
left, right = st.columns([1, 1.3])

volume_cm3 = None

# =========================
# 左側（控制面板）
# =========================
with left:

    # 輸入
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📥 輸入方式")

    mode = st.radio("", ["上傳 STL", "手動輸入"])

    if mode == "上傳 STL":
        file = st.file_uploader("上傳 STL", type=["stl"])
        if file:
            mesh = trimesh.load(file, file_type='stl')
            volume_cm3 = mesh.volume / 1000
            st.success(f"體積：{volume_cm3:.2f} cm³")
    else:
        cm = st.number_input("cm³", 0.0)
        mm = st.number_input("mm³", 0.0)

        if cm > 0:
            volume_cm3 = cm
            st.caption(f"{cm*1000:.0f} mm³")
        elif mm > 0:
            volume_cm3 = mm / 1000
            st.caption(f"{volume_cm3:.2f} cm³")

    st.markdown('</div>', unsafe_allow_html=True)

    # 材料
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧪 材料")

    material = st.selectbox("", materials_df["Formlabs"])
    row = materials_df[materials_df["Formlabs"] == material].iloc[0]

    price_l = row["單價"]
    cost_cm3 = price_l / 1000

    st.caption(f"{cost_cm3:.3f} 元 / cm³")

    st.markdown('</div>', unsafe_allow_html=True)

    # 設定
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("⚙️ 設定")

    profit = st.number_input("利潤倍率", value=1.0, step=0.5)
    support = st.slider("支撐 (%)", 0, 50, 20, step=5)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 右側（報價儀表板）
# =========================
with right:

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 即時報價")

    if volume_cm3 and volume_cm3 > 0:

        effective_volume = volume_cm3 * (1 + support / 100)
        cost = effective_volume * cost_cm3
        price = cost * profit

        # 大價格
        st.markdown(f'<div class="price">NT$ {int(price)}</div>', unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        col1.metric("原始體積", f"{volume_cm3:.2f}")
        col2.metric("含支撐", f"{effective_volume:.2f}")
        col3.metric("材料成本", f"{cost:.0f}")

        st.markdown("<hr>", unsafe_allow_html=True)

        st.caption(f"材料：{material}")
        st.caption(f"利潤倍率：{profit}")
        st.caption(f"支撐比例：{support}%")

        # 報價文字
        st.code(f"""
材料：{material}
體積：{volume_cm3:.2f} cm³
支撐：{support}%
報價：NT$ {int(price)}
""")

    else:
        st.info("請輸入體積或上傳檔案")

    st.markdown('</div>', unsafe_allow_html=True)
