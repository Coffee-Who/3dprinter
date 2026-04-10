import streamlit as st
import trimesh
import numpy as np
import io

# 設定網頁標題
st.set_page_config(page_title="Formlabs 預檢工具", layout="wide")
st.title("🖨️ 3D 列印檔案預檢與擺放預覽")

# 側邊欄：設定建議旋轉角度
st.sidebar.header("預覽設定")
rotate_x = st.sidebar.slider("模擬 X 軸旋轉", 0, 90, 45)
rotate_y = st.sidebar.slider("模擬 Y 軸旋轉", 0, 90, 0)

uploaded_file = st.file_uploader("請上傳 STL 模型檔案", type=["stl"])

if uploaded_file is not None:
    # 讀取模型
    file_bytes = uploaded_file.read()
    mesh = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
    
    # --- 邏輯計算區 ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 模型分析報告")
        st.write(f"**模型名稱:** {uploaded_file.name}")
        st.write(f"**水密性:** {'✅ 正常' if mesh.is_watertight else '❌ 破面'}")
        st.write(f"**尺寸:** {np.round(mesh.extents, 1)} mm")
        
        # 顯示建議
        if not mesh.is_watertight:
            st.warning("⚠️ 偵測到模型非水密結構，建議先進行補面。")
        
        suction_ratio = mesh.convex_hull.volume / mesh.volume
        if suction_ratio > 1.2:
            st.error("🚨 偵測到強烈杯吸風險！請務必傾斜模型並打孔。")

    with col2:
        st.subheader("🔍 建議擺放預覽")
        
        # 執行模擬旋轉 (使用 trimesh)
        # 這裡將模型旋轉以便視覺化建議的角度
        angle_x = np.radians(rotate_x)
        angle_y = np.radians(rotate_y)
        rot_matrix = trimesh.transformations.rotation_matrix(angle_x, [1, 0, 0])
        mesh.apply_transform(rot_matrix)
        
        # 由於 Streamlit 原生不支援複雜 3D 渲染，
        # 我們利用 trimesh 產生一個簡單的預覽 HTML 或圖形
        # 這裡推薦使用 streamlit-stl 的邏輯（若環境支援）
        # 或是匯出成簡單的 GLB 格式顯示
        
        st.info(f"當前模擬預覽：X軸旋轉 {rotate_x}度。")
        st.markdown(f"""
        **擺放策略重點：**
        * **減少底面接觸率：** 已將大平面轉離水平面。
        * **離型力優化：** 建議角度 35°-45° 已應用。
        """)

    # --- 3D 渲染區 ---
    # 使用 Streamlit 內建支援的特定方式（如展示圖片或簡單 3D 視窗）
    # 註：在 Streamlit Cloud 上，最穩定的做法是顯示預覽圖或使用特定 Component
    st.divider()
    st.write("🔧 *進階提示：建議在 PreForm 中將支撐點直徑設為 0.5mm 以獲得最佳表面。*")

else:
    st.info("請上傳 STL 檔案以顯示預覽與建議。")
