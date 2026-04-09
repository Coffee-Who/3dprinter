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
    return df

materials_df = load_materials()

# =========================
# 輸入方式選擇
# =========================
mode = st.radio("選擇輸入方式", ["📂 上傳檔案", "✏️ 手動輸入體積"])

volume = None

# =========================
# 上傳檔案
# =========================
if mode == "📂 上傳檔案":
    uploaded_file = st.file_uploader("上傳 STL 檔案", type=["stl"])

    if uploaded_file is not None:
        try:
            mesh = trimesh.load(uploaded_file, file_type='stl')
            volume = mesh.volume / 1000  # mm³ → cm³

            st.success(f"✅ 成功解析檔案")
            st.write(f"📦 體積：約 {volume:.2f} cm³")

        except Exception as e:
            st.error(f"❌ 檔案解析失敗: {e}")

# =========================
# 手動輸入
# =========================
else:
    volume = st.number_input("輸入體積 (cm³)", min_value=0.0, value=0.0)

# =========================
# 材料選擇
# =========================
st.subheader("材料選擇")

material_name = st.selectbox("選擇材料", materials_df["材料名稱"])

material_row = materials_df[materials_df["材料名稱"] == material_name].iloc[0]

cost_per_cm3 = material_row["成本(元/cm3)"]

st.write(f"📌 單位成本：{cost_per_cm3} 元/cm³")

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
# 計算按鈕
# =========================
if st.button("💰 計算報價"):

    if volume is None or volume <= 0:
        st.warning("⚠️ 請先提供有效體積")
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
        # 一鍵複製內容
        # =========================
        st.markdown("### 📋 報價文字")

        quote_text = f"""
材料：{material_name}
體積：{volume:.2f} cm³
填充率：{infill}%
報價：NT$ {int(final_price)}
"""

        st.code(quote_text)
