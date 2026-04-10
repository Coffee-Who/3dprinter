import streamlit as st
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 網頁配置 ---
st.set_page_config(page_title="SLA Expert Pro", layout="wide")

st.title("🖨️ SLA 專業預檢：強化厚度分析系統")

# --- 側邊欄 ---
with st.sidebar:
    st.header("🔧 分析設定")
    min_wall_threshold = st.slider("最小壁厚警告門檻 (mm)", 0.1, 10.0, 0.6, 0.1)
    st.info("點擊『開始厚度檢查』後，太薄的區域將標示為紅色。")
    
    st.divider()
    st.subheader("支撐模擬")
    support_density = st.slider("支撐密度", 1.0, 5.0, 2.0)
    touchpoint_size = st.slider("接觸點直徑 (mm)", 0.3, 1.2, 0.6)

# --- 核心邏輯：強化厚度分析 ---
def analyze_thickness_robust(mesh, threshold):
    """
    使用 cKDTree 計算每個頂點到對向表面的最短距離。
    這比單純射線法更準確，能處理複雜幾何。
    """
    color_mesh = mesh.copy()
    
    # 1. 分離出正面與背面的索引
    # 我們假設厚度是從頂點沿著「負法向量」方向尋找最近的另一個面
    # 這裡採用 Trimesh 的內建離散點測距法
    
    # 預設顏色
    base_color = [210, 210, 210, 255] # 淺灰
    red_color = [255, 30, 30, 255]   # 鮮紅
    
    # 建立頂點顏色矩陣
    vertex_colors = np.full((len(color_mesh.vertices), 4), base_color, dtype=np.uint8)

    # 獲取所有三角形的中心點與法向量，用來模擬「內部面」
    face_centers = color_mesh.triangles_center
    face_normals = color_mesh.face_normals
    
    # 使用 KDTree 加速空間搜尋
    tree = cKDTree(face_centers)
    
    # 對於每個頂點，搜尋其附近的「背面」面片
    for i, (vertex, v_normal) in enumerate(zip(color_mesh.vertices, color_mesh.vertex_normals)):
        # 尋找附近的中心點
        dist, idx = tree.query(vertex, k=5) # 找最近的 5 個面
        
        # 過濾掉「同向」的面（法向量夾角 > 90度才算背面）
        # 這是防止誤判「表面鄰居」為「內部厚度」的關鍵
        actual_thickness = 100.0 # 預設大值
        found_back = False
        
        for d, f_idx in zip(dist, idx):
            if np.dot(v_normal, face_normals[f_idx]) < -0.2: # 接近反向的面
                actual_thickness = d
                found_back = True
                break
        
        if found_back and actual_thickness < threshold:
            vertex_colors[i] = red_color

    color_mesh.visual.vertex_colors = vertex_colors
    return color_mesh

# --- 支撐生成 ---
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
        cyl.visual.face_colors = [100, 149, 237, 120] # 半透明藍
        supports.append(cyl)
    return trimesh.util.concatenate(supports) if supports else None

# --- 3D 渲染器 ---
def render_3d(mesh):
    glb_data = mesh.export(file_type='glb')
    b64 = base64.b64encode(glb_data).decode()
    return f"""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <model-viewer src="data:model/gltf-binary;base64,{b64}" 
                  style="width: 100%; height: 600px; background-color: #ffffff;" 
                  camera-controls shadow-intensity="1" touch-action="pan-y">
    </model-viewer>
    """

# --- 主流程 ---
uploaded_file = st.file_uploader("上傳 STL 檔案 (建議 < 15MB)", type=["stl"])

if uploaded_file:
    if 'raw_mesh' not in st.session_state or st.session_state.get('last_file') != uploaded_file.name:
        with st.spinner("載入模型中..."):
            raw = trimesh.load(io.BytesIO(uploaded_file.read()), file_type='stl')
            # 預先旋轉 45 度
            rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
            raw.apply_transform(rot)
            st.session_state.raw_mesh = raw
            st.session_state.display_mesh = raw.copy()
            st.session_state.last_file = uploaded_file.name

    mesh = st.session_state.raw_mesh

    # 檢查按鈕
    if st.button("🔍 開始厚度檢查 (偵測薄弱區域)", use_container_width=True):
        with st.spinner("強化演算法計算中，請稍候..."):
            st.session_state.display_mesh = analyze_thickness_robust(mesh, min_wall_threshold)
            st.success("分析完成！")

    # 3. 顯示區
    st.divider()
    show_supp = st.checkbox("顯示模擬支撐架", value=True)
    
    final_preview = st.session_state.display_mesh.copy()
    if show_supp:
        supp = generate_supports(mesh, support_density, touchpoint_size)
        if supp: final_preview = trimesh.util.concatenate([final_preview, supp])

    st.components.v1.html(render_3d(final_preview), height=620)

    # 數據看板
    col1, col2 = st.columns(2)
    col1.metric("預估樹脂消耗", f"{mesh.volume/1000:.2f} ml")
    col2.info("🔴 紅色區域：壁厚可能不足，建議增加厚度。")

else:
    st.info("請上傳模型以啟動分析系統。")
