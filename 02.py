import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. 網頁配置與 CSS 風格 ---
st.set_page_config(page_title="實威國際 Pro SLA 系統", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background-color: #1E40AF; color: white; font-weight: bold; border: none;
    }
    .price-result { 
        display: inline-block; background-color: #FFFF00; color: #E11D48; 
        padding: 8px 16px; border-radius: 8px; font-size: 32px; font-weight: 900; border: 3px solid #E11D48; 
    }
    .over-limit { color: #FF0000; font-weight: bold; background-color: #FFEBEB; padding: 2px 5px; border-radius: 4px; }
    .safe-limit { color: #1E40AF; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 完整的 Formlabs 材料資料庫 ---
@st.cache_data
def load_materials():
    data = {
        "材料分類": ["標準", "標準", "標準", "標準", "工程", "工程", "工程", "工程", "工程", "工程", "醫療", "醫療", "珠寶", "矽膠"],
        "材料名稱": [
            "Clear Resin V4", "Grey Resin V4", "White Resin V4", "Black Resin V4",
            "Tough 2000", "Grey Pro", "Rigid 10K", "Flexible 80A", "Elastic 50A", "High Temp",
            "BioMed Clear", "BioMed Amber", "Castable Wax 40", "Silicone 40A"
        ],
        "單價": [6900, 6900, 6900, 6900, 8500, 7500, 12000, 9500, 9500, 11000, 13500, 13500, 15000, 18000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df

df_m = load_materials()

# --- 3. 設備規格資料 ---
PRINTERS = {
    "Form 4": {"w": 200.0, "d": 125.0, "h": 210.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0}
}

# --- 4. 核心邏輯：壁厚與 3D 渲染 ---
def analyze_thickness_robust(mesh, threshold):
    color_mesh = mesh.copy()
    vertex_colors = np.full((len(color_mesh.vertices), 4), [225, 225, 225, 255], dtype=np.uint8)
    tree = cKDTree(color_mesh.triangles_center)
    for i, (vertex, v_normal) in enumerate(zip(color_mesh.vertices, color_mesh.vertex_normals)):
        dist, idx = tree.query(vertex, k=5)
        for d, f_idx in zip(dist, idx):
            if np.dot(v_normal, color_mesh.face_normals[f_idx]) < -0.3:
                if d < threshold:
                    vertex_colors[i] = [255, 0, 0, 255]
                break
    color_mesh.visual.vertex_colors = vertex_colors
    return color_mesh

def create_wireframe_box(w, d, h, color):
    """手動建立線條構成的方框，避免 AttributeError"""
    # 定義 8 個頂點
    v = np.array([
        [-w/2, -d/2, -h/2], [w/2, -d/2, -h/2], [w/2, d/2, -h/2], [-w/2, d/2, -h/2],
        [-w/2, -d/2, h/2], [w/2, -d/2, h/2], [w/2, d/2, h/2], [-w/2, d/2, h/2]
    ])
    # 定義 12 條邊
    e = np.array([
        [0,1], [1,2], [2,3], [3,0], [4,5], [5,6], [6,7], [7,4], [0,4], [1,5], [2,6], [3,7]
    ])
    
    # 將線段轉為細小的圓柱體（因為 GLB 對純線條支援度差，圓柱體渲染最穩定）
    lines = []
    for start, end in e:
        line = trimesh.creation.cylinder(radius=0.5, segment=[v[start], v[end]])
        line.visual.face_colors = color
        lines.append(line)
    return trimesh.util.concatenate(lines)

def render_3d_pro(mesh, printer_box, is_over_limit=False):
    w, d, h = printer_box['w'], printer_box['d'], printer_box['h']
    
    # 建立純線條架構 (Wireframe)
    box_color = [255, 0, 0, 255] if is_over_limit else [150, 150, 150, 255]
    box_wire = create_wireframe_box(w, d, h, box_color)
    
    scene = trimesh.Scene()
    
    # 模型處理：底部對齊框線底部 Z=0
    mesh_copy = mesh.copy()
    mesh_bottom = mesh_copy.bounds[0][2]
    # 置中並移至框線底部
    mesh_copy.apply_translation([-mesh_copy.centroid[0], -mesh_copy.centroid[1], -mesh_bottom - h/2])
    
    scene.add_geometry(mesh_copy)
    scene.add_geometry(box_wire)
    
    glb_data = scene.export(file_type='glb')
    b64 = base64.b64encode(glb_data).decode()
    
    return f"""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <style> model-viewer {{ width: 100%; height: 650px; background-color: #ffffff; border-radius: 12px; }} </style>
    <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate shadow-intensity="1.5" exposure="1.3" environment-image="neutral" touch-action="pan-y"></model-viewer>
    """

# --- 5. 主選單流程 ---
with st.sidebar:
    st.image("https://www.swtc.com/images/logo.png", width=180)
    st.header("⚙️ 設備設定")
    p_choice = st.selectbox("切換列印範圍框線", list(PRINTERS.keys()))
    min_wall_threshold = st.slider("最小壁厚警告門檻 (mm)", 0.1, 10.0, 0.6, 0.1)
    st.divider()
    menu = st.radio("選單", ["💰 自動估價報價", "📏 比例補償計算"])

if menu == "💰 自動估價報價":
    st.title(f"💰 {p_choice} 智慧報價系統")
    up_file = st.file_uploader("上傳 STL 檔案", type=["stl"])
    
    if up_file:
        if 'raw_mesh' not in st.session_state or st.session_state.get('last_file') != up_file.name:
            with st.spinner("模型載入中..."):
                raw = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
                # 45度 SLA 放置建議
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
                raw.apply_transform(rot)
                st.session_state.raw_mesh = raw
                st.session_state.display_mesh = raw.copy()
                st.session_state.last_file = up_file.name
        
        mesh = st.session_state.raw_mesh
        vol_mm3 = int(abs(mesh.volume))
        p_limit = PRINTERS[p_choice]
        
        # --- 數量與價格計算 ---
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            m_selected = st.selectbox("1. 選擇 Formlabs 材料", df_m["材料名稱"].tolist())
        with c2:
            qty = st.number_input("2. 數量", min_value=1, value=1, step=1)
        with c3:
            markup = st.number_input("3. 利潤倍率", min_value=0.1, value=2.0, step=0.1)

        u_cost = df_m.loc[df_m["材料名稱"] == m_selected, "每mm3成本"].values[0]
        # 總價 = (單件成本 * 倍率 * 數量) + (基本處理費 * 數量)
        total_price = (vol_mm3 * u_cost * markup * qty) + (200 * qty)
        
        st.markdown(f'💸 建議總報價：NT$ <span class="price-result">{total_price:,.0f}</span>', unsafe_allow_html=True)
        st.divider()

        # --- 空間尺寸檢查 ---
        bounds = mesh.extents
        is_over = any(bounds[i] > list(p_limit.values())[i] for i in range(3))
        
        st.subheader("📏 列印空間校驗 (細框線預覽)")
        dim_cols = st.columns(3)
        dims = ['w', 'd', 'h']; labels = ['寬 (X)', '深 (Y)', '高 (Z)']
        for i, d in enumerate(dims):
            style = "over-limit" if bounds[i] > p_limit[d] else "safe-limit"
            dim_cols[i].markdown(f"{labels[i]}: <span class='{style}'>{bounds[i]:.1f} / {p_limit[d]} mm</span>", unsafe_allow_html=True)
        
        if is_over:
            st.error(f"❌ 警告：物件已超出 {p_choice} 可列印範圍！")

        # --- 3D 渲染 ---
        if st.button("🔍 執行最小壁厚檢查 (紅色區域)"):
            with st.spinner("正在進行射線追蹤分析..."):
                st.session_state.display_mesh = analyze_thickness_robust(mesh, min_wall_threshold)
        
        st.components.v1.html(render_3d_pro(st.session_state.display_mesh, p_limit, is_over), height=670)

else:
    st.title("📏 尺寸補償計算")
    d_size = st.number_input("設計尺寸 (mm)", min_value=0.1, value=20.0)
    a_size = st.number_input("實測尺寸 (mm)", min_value=0.1, value=19.8)
    st.markdown(f'建議縮放比例：<span class="price-result">{(d_size/a_size)*100:.2f}%</span>', unsafe_allow_html=True)
