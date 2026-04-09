import streamlit as st
import pandas as pd
import trimesh
import requests
import io
import numpy as np

st.set_page_config(page_title="3D列印快速估價工具", layout="wide")

st.title("🧮 3D列印快速估價工具（內部版）")

# =========================
# 讀取 CSV
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
# 輸入方式
# =========================
mode = st.radio("選擇輸入方式", ["📂 上傳 STL", "✏️ 手動輸入"])

volume_cm3 = None

# =========================
# STL 上傳 + 預覽
# =========================
if mode == "📂 上傳 STL":
    uploaded_file = st.file_uploader("上傳 STL", type=["stl"])

    if uploaded_file is not None:
        mesh = trimesh.load(uploaded_file, file_type='stl')

        # 體積 mm³ → cm³
        volume_cm3 = mesh.volume / 1000

        st.success("✅ 檔案解析成功")
        st.write(f"📦 體積：約 {volume_cm3:.2f} cm³")

        # ====== 3D 預覽（簡化版）======
        st.subheader("3D預覽")
        st.write("（可旋轉）")

        vertices = mesh.vertices
        faces = mesh.faces

        st.plotly_chart({
            "data": [{
                "type": "mesh3d",
                "x": vertices[:, 0],
                "y": vertices[:, 1],
                "z": vertices[:, 2],
                "i": faces[:, 0],
                "j": faces[:, 1],
                "k": faces[:, 2],
                "opacity": 1.0,
            }],
            "layout": {"margin": dict(l=0, r=0, b=0, t=0)}
        }, use_container_width=True)

# =========================
# 手動輸入（雙單位）
# =========================
else:
    col1, col2 = st.columns(2)

    with col1:
        volume_cm = st.number_input("體積 (cm³)", min_value=0.0, value=0.0)

    with col2:
        volume_mm = st.number_input("體積 (mm³)", min_value=0.0, value=0.0)

    # 🔥 自動互斥 + 換算
    if volume_cm > 0:
        volume_cm3 = volume_cm
        st.info(f"自動換算：{volume_cm * 1000:.2f} mm³")
    elif volume_mm > 0:
        volume_cm3 = volume_mm / 1000
        st.info(f"自動換算：{volume_cm3:.2f} cm³")

# =========================
# 材料
# =========================
st.subheader("材料選擇")

material_name = st.selectbox("材料", materials_df["Formlabs"])
material_row = materials_df[materials_df["Formlabs"] == material_name].iloc[0]

price_per_liter = material_row["單價"]
cost_per_cm3 = price_per_liter / 1000

st.write(f"📌 每 cm³ 成本：約 {cost_per_cm3:.3f} 元")

# =========================
# 參數設定
# =========================
st.subheader("計算設定")

col1, col2 = st.columns(2)

with col1:
    profit_multiplier = st.number_input("利潤倍率", value=1.0, step=0.5)

with col2:
    support_percent = st.slider("支撐比例 (%)", 0, 50, 20, step=5)

# =========================
# 即時計算
# =========================
if volume_cm3 and volume_cm3 > 0:

    effective_volume = volume_cm3 * (1 + support_percent / 100)

    cost = effective_volume * cost_per_cm3
    final_price = cost * profit_multiplier

    # =========================
    # 顯示
    # =========================
    st.markdown("---")
    st.subheader("📊 報價結果")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("原始體積 (cm³)", f"{volume_cm3:.2f}")
        st.metric("含支撐體積 (cm³)", f"{effective_volume:.2f}")
        st.metric("材料成本", f"{cost:.0f} 元")

    with col2:
        st.metric("支撐比例", f"{support_percent}%")
        st.metric("利潤倍率", f"{profit_multiplier}")
        st.metric("💰 報價", f"{final_price:.0f} 元")

    # 報價文字
    quote_text = f"""
材料：{material_name}
體積：{volume_cm3:.2f} cm³
支撐：{support_percent}%
報價：NT$ {int(final_price)}
"""

    st.code(quote_text)

else:
    st.info("請輸入體積或上傳檔案")
