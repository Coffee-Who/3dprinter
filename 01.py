import streamlit as st
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 網頁配置 ---
st.set_page_config(page_title="SLA Expert Pre-Check", layout="wide")

st.title("🖨️ SLA 專業預檢：區域厚度視覺化系統")

# --- 側邊欄參數 ---
with st.sidebar:
    st.header("🔧 厚度分析設定")
    # 數值調整最大到 10mm
    min_wall_threshold = st.slider("最小壁厚警告門檻 (mm)", 0.1, 10.0, 0.6, 0.1)
    st.info("💡 小於此門檻的區域將在 3D 預覽中顯示為紅色。")
    
    st.divider()
    st.subheader("支撐架模擬")
    support_density = st.slider("支撐密度", 1.0, 5.0, 2.5)
    touchpoint_size = st.slider("接觸點直徑 (mm)", 0.3, 1.2, 0.6)

# --- 核心邏輯：局部厚度著色演算法 ---
def apply_thickness_coloring(mesh, threshold):
    """
    計算每個頂點的局部厚度，並根據門檻賦予顏色
    """
    # 建立顏色陣列 (預設灰色: R:200, G:200, B:200)
    vertex_colors = np.full((len(mesh.vertices), 4), [200, 200, 200, 255], dtype=np.uint8)
    
    # 使用簡化射線法估算局部厚度：
    # 獲取頂點法向量並向內探測
    ray_origins = mesh.vertices
    ray_directions = -mesh.vertex_normals # 向內打射線
    
    # 執行射線碰撞偵測
    locations, index_ray, index_tri = mesh.ray.intersects_location(
        ray_origins=ray_origins,
        ray_directions=ray_directions,
        multiple_hits=False
    )
    
    # 計算距離
    distances = np.full(len(mesh.vertices), 10.0) # 預設安全值
    if len(locations) > 0:
        dist = np.linalg.norm(locations - ray_origins[index_ray], axis=1)
        distances[index_ray] = dist
        
    # 將小於門檻的點染成紅色 (R:255, G:0, B:0)
    too_thin_mask = distances < threshold
    vertex_colors[too_thin_mask] = [255, 0, 0, 255]
    
    mesh.visual.vertex_colors = vertex_colors
    return mesh, np.min(distances) if len(locations) > 0 else 0.0

# --- 支撐生成邏輯 ---
def generate_supports(mesh, density, touch_size):
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
        cyl = trimesh.creation.cylinder(radius=touch_size/2, height=height)
        cyl.apply_translation([p[0], p[1], raft_z_top + height/2])
        # 支撐架設為半透明藍色
        cyl.visual.face_colors = [100, 149, 237, 150]
        supports.append(cyl)
            
    return trimesh.util.concatenate(supports) if supports else None

# --- 3D 渲染器 ---
def render_3d(mesh):
    # 注意：匯出 GLB 才能保留頂點顏色
    glb_data = mesh.export(file_type='glb')
    b64 = base64.b64encode(glb_data).decode()
    return f"""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <model-viewer src="data:model/gltf-binary;base64,{b64}" 
                  style="width: 100%; height: 600px;" camera-controls shadow-intensity="1">
    </model-viewer>
    """

# --- 主流程 ---
uploaded_file = st.file_uploader("上傳 STL 檔案", type=["stl"])

if uploaded_file:
    try:
        mesh = trimesh.load(io.BytesIO(uploaded_file.read()), file_type='stl')
        
        # 1. 旋轉 45 度
        rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
        mesh.apply_transform(rot)

        # 2. 進行厚度計算與染色
        with st.spinner("正在分析壁厚分布..."):
            colored_mesh, min_detected = apply_thickness_coloring(mesh.copy(), min_wall_threshold)

        # 3. 看板顯示
        c1, c2, c3 = st.columns(3)
        c1.metric("預估體積", f"{mesh.volume/1000:.2f} ml")
        c2.metric("偵測最小厚度", f"{min_detected:.2f} mm", 
                  delta="太薄" if min_detected < min_wall_threshold else "安全",
                  delta_color="inverse" if min_detected < min_wall_threshold else "normal")
        c3.metric("頂點數量", f"{len(mesh.vertices)}")

        # 4. 生成支撐並合併
        support_mesh = generate_supports(mesh, support_density, touchpoint_size)
        
        st.subheader("🔍 厚度視覺化預覽 (紅色 = 低於門檻)")
        if support_mesh:
            # 合併時保留各自顏色
            scene = trimesh.util.concatenate([colored_mesh, support_mesh])
            st.components.v1.html(render_3d(scene), height=620)
        else:
            st.components.v1.html(render_3d(colored_mesh), height=620)

        if min_detected < min_wall_threshold:
            st.error(f"⚠️ 偵測到厚度不足區域！請檢查畫面中的**紅色部位**。")

    except Exception as e:
        st.error(f"分析失敗: {e}")
