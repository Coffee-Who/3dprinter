import streamlit as st
import pandas as pd
import trimesh
import requests
import io

st.set_page_config(page_title="3D列印快速估價工具", layout="wide")

st.title("🧮 3D列印快速估價工具（內部版）")

# =========================
# 讀取材料 CSV（GitHub）
# =========================
@st.cache_data
def load_materials():
    url = "https://raw.githubusercontent.com/Coffee-Who/3dprinter/main/Formlabs%E6%9D%90%E6%96%99.csv"
    response = requests.get(url)
    response.encoding = 'utf-8'

    df = pd.read_csv(io.StringIO(response.text))

    # 🔥 清除 BOM / 空白
    df.columns = df.columns.str.strip().str.replace('\ufeff', '')

    return df

materials_df = load_materials()

# Debug（可先打開確認）
# st.write(materials_df.columns.tolist())

# =========================
# 輸入方式
# =========================
mode = st.radio("選擇輸入方式", ["📂 上傳 STL", "✏️ 手動輸入體積"])

volume = None

# =========================
# STL 上傳
# =========================
if mode == "📂 上傳 STL":
    uploaded_file = st.file_uploader("上傳 STL 檔案", type=["stl"])

    if uploaded_file is not None:
        try:
            mesh = trimesh.load(uploaded_file, file_type='stl')

            # mm³ → cm³
            volume = mesh.volume / 1000  

            st.success("✅ 檔案解析成功")
            st.write(f"📦 體積：約 {volume:.2f} cm³")

        except Exception as e:
            st.error(f"❌ 解析失敗：{e}")

# =========================
# 手動輸入
# =========================
else:
    volume = st.number_input("輸入體積 (cm³)", min_value=0.0, value=0.0)

# =========================
# 材料選擇
# =========================
st.subheader("材料選擇")

material_name = st.selectbox("選擇材料", materials_df["Formlabs"])

material_row = materials_df[materials_df["Formlabs"] == material_name].iloc[0]

price_per_liter = material_row["單價"]  # 1L價格

# 換算 cm³
cost_per_cm3 = price_per_liter / 1000

st.write(f"📌 1L價格：{price_per_liter} 元")
st.write(f"📌 每 cm³ 成本：約 {cost_per_cm3:.3f} 元")

# =========================
# 進階設定
# =========================
st.subheader("進階設定")

col1, col2, col3 = st.columns(3)

with col1:
    profit_multiplier = st.number_input("利潤倍率", value=2.0)

with col2:
    infill = st.slider("填充率 (%)", 10, 100, 100)

with col3:
    minimum_price = st.number_input("最低收費", value=500)

# =========================
# 計算
# =========================
if st.button("💰 計算報價"):

    if volume is None or volume <= 0:
        st.warning("⚠️ 請輸入有效體積")
    else:
        effective_volume = volume * (infill / 100)

        cost = effective_volume * cost_per_cm3
        final_price = cost * profit_multiplier

        if final_price < minimum_price:
            final_price = minimum_price

        # =========================
        # 顯示結果
        # =========================
        st.markdown("---")
        st.subheader("📊 報價結果")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("原始體積 (cm³)", f"{volume:.2f}")
            st.metric("有效體積 (cm³)", f"{effective_volume:.2f}")
            st.metric("材料成本 (元)", f"{cost:.0f}")

        with col2:
            st.metric("利潤倍率", f"{profit_multiplier}")
            st.metric("最低收費", f"{minimum_price}")
            st.metric("💰 最終報價", f"{final_price:.0f} 元")

        # =========================
        # 報價文字（業務用）
        # =========================
        st.markdown("### 📋 報價內容")

        quote_text = f"""
材料：{material_name}
體積：{volume:.2f} cm³
填充率：{infill}%
報價：NT$ {int(final_price)}
"""

        st.code(quote_text)
