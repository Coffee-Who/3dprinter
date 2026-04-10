import streamlit as st
import trimesh
import numpy as np
import io
import base64

# --- 網頁配置 ---
st.set_page_config(page_title="3D Print Pre-Check", layout="wide")

st.title("🖨️ SLA 3D 列印專家預檢系統")
st.markdown("本版本採用 Google Model-Viewer 技術，無需額外 3D 套件即可預覽。")

# --- 側邊欄參數 ---
with st.sidebar:
    st.header("🔧 模擬參數")
    support_density = st.slider("支撐密度", 1.0, 5.0, 2.5)
    touchpoint_size = st.slider("接觸點直徑 (mm)", 0.3, 1.2, 0.6)
    raft_thick = st.slider("底座厚度 (mm)", 1.0, 3.0, 2.0)

# --- 支撐生成邏輯 ---
def generate_support_visual(mesh, density, touch_size, raft_h):
    z_min = mesh.bounds[0][2]
    raft_z_top = z_min - 5
    overhang_indices = np.where(mesh.face_normals[:, 2] < -0.5)[0]
    if len(overhang_indices) == 0: return None
    
    overhang_mesh = mesh.submesh([overhang_indices], append=True)
    num_points = max(20, int(overhang_mesh.area * (density / 100))) 
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
    
    # 生成底座
    ext = mesh.extents
    raft = trimesh.creation.box(extents=[ext[0]*1.2, ext[1]*1.2, raft_h])
    raft.apply_translation([mesh.center_mass[0], mesh.center_mass[1], raft_z_top - raft_h/2])
    return trimesh.util.concatenate([support_mesh, raft])

# --- 3D 渲染 HTML 生成器 ---
def render_3d_viewer(mesh):
    # 將模型轉為 GLB 格式 (網頁通用格式)
    glb_data = mesh.export(file_type='glb')
    b64_model = base64.b64encode(glb_data).decode()
    
    html_code = f"""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <model-viewer src="data:model/gltf-binary;base64,{b64_model}" 
                  style="width: 100%; height: 500px; background-color: #f0f2f6;" 
                  camera-controls auto-rotate shadow-intensity="1">
    </model-viewer>
    """
    return html_code

# --- 主流程 ---
uploaded_file = st.file_uploader("上傳 STL 檔案", type=["stl"])

if uploaded_file:
    try:
        # 讀取並自動旋轉 45 度
        mesh = trimesh.load(io.BytesIO(uploaded_file.read()), file_type='stl')
        rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
        mesh.apply_transform(rot)

        # 數據看板
        c1, c2, c3 = st.columns(3)
        c1.metric("尺寸 (X/Y)", f"{mesh.extents[0]:.1f}/{mesh.extents[1]:.1f} mm")
        c2.metric("預估體積", f"{mesh.volume/1000:.2f} ml")
        c3.metric("結構狀態", "✅ 水密" if mesh.is_watertight else "⚠️ 破面")

        with st.spinner("幾何運算與支撐渲染中..."):
            support_mesh = generate_support_visual(mesh, support_density, touchpoint_size, raft_thick)
            
            if support_mesh:
                final_scene = trimesh.util.concatenate([mesh, support_mesh])
                st.subheader("📦 3D 擺放預覽 (自動 45° + 支撐架)")
                st.components.v1.html(render_3d_viewer(final_scene), height=550)
                
                if mesh.convex_hull.volume / mesh.volume > 1.25:
                    st.warning("🚨 偵測到吸盤效應風險，請確認是否有排氣孔。")
            else:
                st.components.v1.html(render_3d_viewer(mesh), height=550)
                
    except Exception as e:
        st.error(f"分析失敗: {e}")
else:
    st.info("👋 你好！請上傳一個 STL 檔案，我將為你分析 Formlabs 的列印參數。")
