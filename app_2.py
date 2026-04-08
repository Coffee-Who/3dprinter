import streamlit as st
import tempfile
from stl import mesh
import plotly.graph_objects as go

st.set_page_config(page_title="3D列印估價工具", layout="wide")

st.title("🧠 3D列印快速估價工具")

# =========================
# 上傳檔案
# =========================
uploaded_file = st.file_uploader("上傳 STL / STEP 檔案", type=["stl", "step", "stp"])

volume = None

# =========================
# STL 處理 + 預覽
# =========================
if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()

    if file_type == "stl":
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        your_mesh = mesh.Mesh.from_file(tmp_path)

        # 計算體積
        volume_mm3, _, _ = your_mesh.get_mass_properties()
        volume = volume_mm3 / 1000  # cm³

        st.success(f"✅ 體積：約 {volume:.2f} cm³")

        # 3D 預覽（Plotly）
        x, y, z = your_mesh.x.flatten(), your_mesh.y.flatten(), your_mesh.z.flatten()

        fig = go.Figure(data=[
            go.Mesh3d(
                x=x,
                y=y,
                z=z,
                opacity=0.5
            )
        ])

        fig.update_layout(
            title="模型預覽",
            scene=dict(aspectmode='data')
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ STEP 檔案目前無法直接預覽，請轉為 STL")
        st.info("👉 建議使用 Fusion360 / SolidWorks 轉 STL")

# =========================
# 估價區
# =========================
st.subheader("⚙️ 估價設定")

material = st.selectbox("材料", [
    "標準樹脂",
    "高強度樹脂",
    "耐溫樹脂"
])

usage = st.selectbox("用途", [
    "外觀件",
    "功能件"
])

# 成本設定
material_cost = {
    "標準樹脂": 20,
    "高強度樹脂": 35,
    "耐溫樹脂": 40
}

machine_rate = 300

# =========================
# 計算
# =========================
if st.button("💰 立即估價"):

    if volume is None:
        st.error("請先上傳 STL 檔案")
    else:
        print_time = volume * 0.1

        material_price = volume * material_cost[material]
        machine_price = print_time * machine_rate
        post_process = 500 if usage == "功能件" else 300

        total_cost = material_price + machine_price + post_process
        final_price = int(total_cost * 1.3)

        lead_time = "2~3 天" if volume < 100 else "3~5 天"

        st.success("✅ 估價完成")

        st.markdown(f"""
        ## 💰 預估價格：NTD {final_price}
        ## ⏱ 交期：{lead_time}

        ---
        ### 🔍 成本拆解
        - 材料：{int(material_price)}
        - 機台：{int(machine_price)}
        - 後處理：{post_process}
        """)
