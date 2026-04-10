import streamlit as st
import trimesh
import numpy as np
import io
from stl_viewer import stl_viewer

# --- 1. 網頁配置與標題 ---
st.set_page_config(page_title="Formlabs SLA 預檢工具", layout="wide")

st.title("🖨️ Formlabs SLA 列印預檢與支撐模擬")
st.markdown("""
本工具會自動將模型旋轉 **45度** 以優化列印品質，並生成模擬支撐架供您預覽。
""")

# --- 2. 側邊欄：參數調整 ---
st.sidebar.header("🔧 模擬參數設定")
support_density = st.sidebar.slider("支撐密度 (點/cm²)", 1.0, 5.0, 2.0)
touchpoint_size = st.sidebar.slider("接觸點直徑 (mm)", 0.3, 1.2, 0.6)
raft_thick = st.sidebar.slider("底座厚度 (mm)", 1.0, 3.0, 2.0)

# --- 3. 核心功能：生成模擬支撐架 ---
def generate_support_visual(mesh, density, touch_size, raft_h):
    """根據懸空面生成簡易支撐柱與底座"""
    # 確保模型底部與底座有固定距離 (5mm)
    z_min = mesh.bounds[0][2]
    raft_z_top = z_min - 5
    
    # 找出懸空面 (法向量朝下)
    overhang_indices = np.where(mesh.face_normals[:, 2] < -0.5)[0]
    if len(overhang_indices) == 0:
        return None
    
    overhang_mesh = mesh.submesh([overhang_indices], append=True)
    
    # 採樣支撐點
    num_points = int(overhang_mesh.area * (density / 100)) 
    num_points = max(15, num_points) # 最少 15 根
    points, _ = overhang_mesh.sample(num_points, return_index=True)
    
    supports = []
    for p in points:
        height = p[2] - raft_z_top
        if height > 0:
            # 生成支撐柱
            cyl = trimesh.creation.cylinder(radius=touch_size/2, height=height)
            cyl.apply_translation([p[0], p[1], raft_z_top + height/2])
            supports.append(cyl)
            
    if not supports:
        return None
        
    # 合併所有支撐柱
    support_mesh = trimesh.util.concatenate(supports)
    
    # 生成底座 (Raft)
    extents = mesh.extents
    raft = trimesh.creation.box(extents=[extents[0]*1.2, extents[1]*1.2, raft_h])
    raft.apply_translation([mesh.center_mass[0], mesh.center_mass[1], raft_z_top - raft_h/2])
    
    return trimesh.util.concatenate([support_mesh, raft])

# --- 4. 檔案上傳與處理 ---
uploaded_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])

if uploaded_file:
    try:
        # 讀取並旋轉模型 (SLA 最佳實踐：旋轉 45 度)
        mesh = trimesh.load(io.BytesIO(uploaded_file.read()), file_type='stl')
        
        # 執行 45 度旋轉優化
        rot_matrix = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
        mesh.apply_transform(rot_matrix)

        # 顯示分析數據
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("模型長度", f"{mesh.extents[0]:.1f} mm")
        with col2:
            st.metric("模型寬度", f"{mesh.extents[1]:.1f} mm")
        with col3:
            st.metric("預估體積", f"{mesh.volume/1000:.2f} ml")

        # 生成支撐模擬
        with st.spinner("計算支撐結構中..."):
            support_mesh = generate_support_visual(mesh, support_density, touchpoint_size, raft_thick)
            
            if support_mesh:
                # 合併模型與支撐供展示
                final_scene = trimesh.util.concatenate([mesh, support_mesh])
                
                # 匯出暫存 STL
                tmp_stl = io.BytesIO()
                final_scene.export(tmp_stl, file_type='stl')
                tmp_stl.seek(0)
                
                st.subheader("📦 3D 模擬預覽 (含支撐與 45° 擺放)")
                st.info("💡 滑鼠左鍵旋轉、右鍵平移、滾輪縮放。")
                
                # 呼叫 3D 預覽器
                stl_viewer(tmp_stl)
                
                # 提示檢查
                if not mesh.is_watertight:
                    st.error("⚠️ 偵測到模型有破面 (Non-watertight)，支撐可能不完全精準。")
                
                # 分析吸盤效應
                if mesh.convex_hull.volume / mesh.volume > 1.25:
                    st.warning("⚠️ 偵測到杯吸效應風險 (Suction Cup)，請檢查內部是否需要打孔。")
            else:
                st.warning("無法生成支撐，請確認模型是否過小或結構過於簡單。")
                stl_viewer(uploaded_file)

    except Exception as e:
        st.error(f"分析失敗: {e}")
else:
    st.info("等待上傳檔案...")

# --- 5. 腳註 ---
st.divider()
st.caption("註：本工具僅供預覽參考，最終切片請以 Formlabs PreForm 官方軟體結果為準。")
