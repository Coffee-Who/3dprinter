import streamlit as st
import trimesh
import numpy as np
import io
import base64

# --- 網頁配置 ---
st.set_page_config(page_title="SLA Expert Analysis", layout="wide")

st.title("🖨️ SLA 專業預檢：區域厚度視覺化系統")

# --- 側邊欄參數 ---
with st.sidebar:
    st.header("🔧 分析設定")
    min_wall_threshold = st.slider("最小壁厚警告門檻 (mm)", 0.1, 10.0, 0.6, 0.1)
    
    st.divider()
    st.subheader("支撐模擬設定")
    support_density = st.slider("支撐密度", 1.0, 5.0, 2.5)
    touchpoint_size = st.slider("接觸點直徑 (mm)", 0.3, 1.2, 0.6)

# --- 核心邏輯：局部厚度分析 ---
def analyze_thickness_to_color(mesh, threshold):
    """
    計算每個頂點的厚度：向內發射射線並偵測對面距離。
    """
    # 複製一個模型來進行染色
    color_mesh = mesh.copy()
    
    # 預設灰色 (RGBA)
    base_color = [200, 200, 200, 255]
    red_color = [255, 0, 0, 255]
    
    # 初始化顏色矩陣
    vertex_colors = np.full((len(color_mesh.vertices), 4), base_color, dtype=np.uint8)
    
    # 獲取頂點法向量並向內探測
    origins = color_mesh.vertices
    directions = -color_mesh.vertex_normals 
    
    # 使用射線交叉檢測 (Ray Intersect)
    # 此處邏輯：從頂點向內射，找到第一個交點即為厚度
    locations, index_ray, _ = color_mesh.ray.intersects_location(
        ray_origins=origins,
        ray_directions=directions,
        multiple_hits=False
    )
    
    # 計算厚度距離
    if len(locations) > 0:
        distances = np.linalg.norm(locations - origins[index_ray], axis=1)
        
        # 建立索引遮罩
        too_thin_ray_indices = index_ray[distances < threshold]
        
        # 將對應頂點染成紅色
        vertex_colors[too_thin_ray_indices] = red_color
        
    color_mesh.visual.vertex_colors = vertex_colors
    return color_mesh

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
        # 支撐架設為半透明藍色以方便辨識
        cyl.visual.face_colors = [100, 149, 237, 100]
        supports.append(cyl)
            
    return trimesh.util.concatenate(supports) if supports else None

# --- 3D 渲染器 (GLB 格式以支援頂點顏色) ---
def render_3d(mesh):
    glb_data = mesh.export(file_type='glb')
    b64 = base64.b64encode(glb_data).decode()
    return f"""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <model-viewer src="data:model/gltf-binary;base64,{b64}" 
                  style="width: 100%; height: 600px; background-color: #f8f9fa;" 
                  camera-controls shadow-intensity="1">
    </model-viewer>
    """

# --- 主流程 ---
uploaded_file = st.file_uploader("上傳 STL 檔案", type=["stl"])

if uploaded_file:
    # 暫存原始模型以便多次分析
    if 'current_mesh' not in st.session_state or st.session_state.file_name != uploaded_file.name:
        mesh_raw = trimesh.load(io.BytesIO(uploaded_file.read()), file_type='stl')
        # 統一執行 45 度預旋轉
        rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
        mesh_raw.apply_transform(rot)
        st.session_state.current_mesh = mesh_raw
        st.session_state.file_name = uploaded_file.name
        st.session_state.display_mesh = mesh_raw.copy()

    mesh = st.session_state.current_mesh

    # 功能按鈕
    col_btn, _ = st.columns([1, 2])
    check_btn = col_btn.button("🔍 開始壁厚偵測 (紅色標示)")

    if check_btn:
        with st.spinner("正在進行射線採樣分析..."):
            st.session_state.display_mesh = analyze_thickness_to_color(mesh, min_wall_threshold)
            st.success(f"分析完成！厚度低於 {min_wall_threshold}mm 的區域已染成紅色。")

    # 儀表板
    c1, c2, c3 = st.columns(3)
    c1.metric("預估體積", f"{mesh.volume/1000:.2f} ml")
    c2.metric("模型表面積", f"{mesh.area/100:.1f} cm²")
    c3.metric("頂點數量", f"{len(mesh.vertices)}")

    # 3D 展示區
    with st.container():
        st.subheader("📦 3D 預覽與分析畫面")
        # 這裡不合併支撐，避免干擾厚度顏色判斷，改為選項
        show_supports = st.checkbox("顯示模擬支撐架 (半透明藍)", value=True)
        
        preview_mesh = st.session_state.display_mesh.copy()
        
        if show_supports:
            support_mesh = generate_supports(mesh, support_density, touchpoint_size)
            if support_mesh:
                preview_mesh = trimesh.util.concatenate([preview_mesh, support_mesh])
        
        st.components.v1.html(render_3d(preview_mesh), height=620)

    if mesh.convex_hull.volume / mesh.volume > 1.25:
        st.warning("⚠️ 偵測到模型內部有較大空腔，請確保已設計排氣孔防止吸盤效應。")
else:
    st.info("👋 請上傳 STL 檔案以啟動分析。建議檔案大小不超過 10MB。")
