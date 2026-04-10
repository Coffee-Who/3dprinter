import streamlit as st
import trimesh
import numpy as np
import io

# 嘗試導入預覽組件，若失敗則顯示引導訊息
try:
    from stl_viewer import stl_viewer
    ST_STL_AVAILABLE = True
except ImportError:
    ST_STL_AVAILABLE = False

# --- 1. 網頁配置 ---
st.set_page_config(page_title="SLA 3D Print Pre-Check", layout="wide")

if not ST_STL_AVAILABLE:
    st.error("⚠️ 套件載入失敗：請點擊右下角 'Manage app' -> 'Reboot App' 強制重新安裝環境。")
    st.stop()

st.title("🖨️ Formlabs SLA 列印預檢與支撐模擬")
st.info("系統會自動執行：旋轉 45 度優化、杯吸效應偵測、簡易支撐架生成。")

# --- 2. 側邊欄參數 ---
with st.sidebar:
    st.header("🔧 模擬參數")
    support_density = st.slider("支撐密度", 1.0, 5.0, 2.0)
    touchpoint_size = st.slider("接觸點直徑 (mm)", 0.3, 1.2, 0.6)
    raft_thick = st.slider("底座厚度 (mm)", 1.0, 3.0, 2.0)
    st.divider()
    st.caption("建議：SLA 列印請務必傾斜擺放以減少離型力。")

# --- 3. 支撐生成邏輯 ---
def generate_support_visual(mesh, density, touch_size, raft_h):
    z_min = mesh.bounds[0][2]
    raft_z_top = z_min - 5 # 模型與底座留 5mm 間隙
    
    # 篩選懸空面 (法向量向上分量小於 -0.5)
    overhang_indices = np.where(mesh.face_normals[:, 2] < -0.5)[0]
    if len(overhang_indices) == 0:
        return None
    
    overhang_mesh = mesh.submesh([overhang_indices], append=True)
    num_points = max(15, int(overhang_mesh.area * (density / 100))) 
    points, _ = overhang_mesh.sample(num_points, return_index=True)
    
    supports = []
    for p in points:
        height = p[2] - raft_z_top
        if height > 0:
            cyl = trimesh.creation.cylinder(radius=touch_size/2, height=height)
            cyl.apply_translation([p[0], p[1], raft_z_top + height/2])
            supports.append(cyl)
            
    if not supports: return None
        
    support_mesh = trimesh.util.concatenate(supports)
    
    # 生成底座 (Raft)
    extents = mesh.extents
    raft = trimesh.creation.box(extents=[extents[0]*1.2, extents[1]*1.2, raft_h])
    raft.apply_translation([mesh.center_mass[0], mesh.center_mass[1], raft_z_top - raft_h/2])
    
    return trimesh.util.concatenate([support_mesh, raft])

# --- 4. 主流程 ---
uploaded_file = st.file_uploader("上傳 STL 檔案", type=["stl"])

if uploaded_file:
    try:
        # 讀取模型
        mesh = trimesh.load(io.BytesIO(uploaded_file.read()), file_type='stl')
        
        # 核心優化：旋轉 45 度
        rot_matrix = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
        mesh.apply_transform(rot_matrix)

        # 數據展示
        c1, c2, c3 = st.columns(3)
        c1.metric("尺寸 (X)", f"{mesh.extents[0]:.1f} mm")
        c2.metric("尺寸 (Y)", f"{mesh.extents[1]:.1f} mm")
        c3.metric("預估樹脂", f"{mesh.volume/1000:.2f} ml")

        with st.spinner("生成支撐預覽中..."):
            support_mesh = generate_support_visual(mesh, support_density, touchpoint_size, raft_thick)
            
            if support_mesh:
                # 合併模型與支撐
                final_scene = trimesh.util.concatenate([mesh, support_mesh])
                
                # 轉為 BytesIO 供 stl_viewer 使用
                tmp_stl = io.BytesIO()
                final_scene.export(tmp_stl, file_type='stl')
                tmp_stl.seek(0)
                
                st.subheader("📦 3D 模擬預覽 (含支撐)")
                stl_viewer(tmp_stl)
                
                # 安全檢查
                if mesh.convex_hull.volume / mesh.volume > 1.25:
                    st.warning("⚠️ 偵測到吸盤效應風險，建議調整擺放角度或打孔。")
            else:
                st.warning("偵測不到懸空區域，顯示原始模型。")
                stl_viewer(uploaded_file)

    except Exception as e:
        st.error(f"分析出錯: {e}")
else:
    st.info("請上傳模型檔案以開始預檢。")
