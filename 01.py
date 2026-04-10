import streamlit as st
import trimesh
import numpy as np
import io

st.set_page_config(page_title="3D 列印預檢工具", layout="wide")
st.title("🖨️ Formlabs 列印前檢查與擺放建議")

# 檔案上傳器
uploaded_file = st.file_uploader("上傳 STL 檔案", type=["stl"])

if uploaded_file is not None:
    # 讀取檔案
    file_bytes = uploaded_file.read()
    mesh = trimesh.load(io.BytesIO(file_bytes), file_type='stl')

    # 建立兩欄佈局
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ 模型基本檢查")
        st.write(f"**模型名稱:** {uploaded_file.name}")
        
        # 檢查水密性
        if mesh.is_watertight:
            st.success("水密性檢查：通過 (無破面)")
        else:
            st.error("水密性檢查：失敗 (模型有破面，請修復)")

        # 尺寸資訊
        st.write(f"**模型尺寸:** {np.round(mesh.extents, 1)} mm")
        st.write(f"**預估樹脂量:** {mesh.volume/1000:.2f} ml")

    with col2:
        st.subheader("📐 擺放與方向建議")
        
        # 杯吸效應檢查
        suction_ratio = mesh.convex_hull.volume / mesh.volume
        if suction_ratio > 1.15:
            st.warning("⚠️ 偵測到杯吸風險！建議傾斜模型或增加排氣孔。")
        else:
            st.info("未偵測到明顯杯吸結構。")

        # 擺放建議
        st.markdown("""
        **建議操作：**
        1. **旋轉 35°-45°**：減少每層離型力，提高成功率。
        2. **細節朝上**：確保支撐點不破壞重要表面。
        3. **遠離平台**：大底面應與平台保持至少 5mm 距離。
        """)

else:
    st.info("請在上方上傳一個 .stl 檔案以開始分析。")
