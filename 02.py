import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. 頁面配置與 CSS 風格 ---
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
    .over-limit { color: #FF0000; font-weight: bold; }
    .safe-limit { color: #1E40AF; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 完整的 Formlabs 材料資料庫 ---
@st.cache_data
def load_materials():
    data = {
        "材料分類": ["標準", "標準", "標準", "標準", "工程", "工程", "工程", "工程", "工程", "工程", "醫療", "醫療", "珠寶"],
        "材料名稱": [
            "Clear Resin V4", "Grey Resin V4", "White Resin V4", "Black Resin V4",
            "Tough 2000", "Grey Pro", "Rigid 10K", "Flexible 80A", "Elastic 50A", "High Temp",
            "BioMed Clear", "BioMed Amber", "Castable Wax 40"
        ],
        "單價": [6900, 6900, 6900, 6900, 8500, 7500, 12000, 9500, 9500, 11000, 13500, 13500, 15000]
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

# --- 4. 核心邏輯：壁厚與渲染 ---
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

def render_3d_pro(mesh, printer_box):
    # 建立設備空間線框 (Bounding Box Visual)
    w, d, h = printer_box['w'], printer_box['d'], printer_box['h']
    # 建立一個透明的方框表示列印空間
    box_geom = trimesh.creation.box(extents=[w, d, h])
    box_edge = trimesh.graph.geometry_to_wireframe(box_geom)
    box_edge.visual.colors = [100, 100, 100, 100]
    # 移動方框讓底部對齊 Z=0 (簡化版)
    box_edge.apply_translation([0, 0, h/2 - 50]) # 略微位移以配合 45度旋轉後的模型
    
    # 導出 GLB
    scene = trimesh.Scene([mesh, box_edge])
    glb_data = scene.export(file_type='glb')
    b64 = base64.b64encode(glb_data).decode()
    return f"""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate shadow-intensity="1.5" exposure="1.3" style="width: 100%; height: 600px; background-color: #ffffff;"></model-viewer>
    """

# --- 5. 側邊欄 UI ---
with st.sidebar:
    st.title("SOLIDWIZARD")
    st.header("⚙️ 參數設定")
    p_choice = st.selectbox("選擇列印設備", list(PRINTERS.keys()))
    min_wall_threshold = st.slider("最小壁厚警告門檻 (mm)", 0.1, 10.0, 0.6, 0.1)
    st.divider()
    choice = st.radio("功能選單：", ["💰 自動估價與預檢", "📏 尺寸補償計算"])

# --- 6. 主程式流程 ---
if choice == "💰 自動估價與預檢":
    st.title(f"💰 {p_choice} 自動報價預檢")
    
    up_file = st.file_uploader("上傳 STL 模型", type=["stl"])
    
    if up_file:
        if 'raw_mesh' not in st.session_state or st.session_state.get('last_file') != up_file.name:
            raw = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
            rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
            raw.apply_transform(rot)
            st.session_state.raw_mesh = raw
            st.session_state.display_mesh = raw.copy()
            st.session_state.last_file = up_file.name
        
        mesh = st.session_state.raw_mesh
        vol_mm3 = int(abs(mesh.volume))
        
        # 尺寸檢查
        bounds = mesh.extents
        p_limit = PRINTERS[p_choice]
        
        # 報價區
        col_m1, col_m2, col_m3 = st.columns([2, 1, 1])
        with col_m1:
            m_choice = st.selectbox("選擇列印材料", df_m["材料名稱"].tolist())
        with col_m2:
            quantity = st.number_input("列印數量", min_value=1, value=1, step=1)
        with col_m3:
            markup = st.number_input("利潤倍率", min_value=0.1, value=2.0, step=0.5)

        u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]
        pure_cost_single = vol_mm3 * u_cost
        total_price = (pure_cost_single * markup * quantity) + (200 * quantity) # 包含單件基本費
        
        st.markdown(f'💸 建議總報價 ({quantity} 件)：NT$ <span class="price-result">{total_price:,.0f}</span>', unsafe_allow_html=True)

        # 尺寸與空間判定顯示
        st.subheader("📏 空間尺寸確認")
        dim_cols = st.columns(3)
        dims = ['w', 'd', 'h']
        labels = ['寬 (X)', '深 (Y)', '高 (Z)']
        for i, d in enumerate(dims):
            is_over = bounds[i] > p_limit[d]
            color_class = "over-limit" if is_over else "safe-limit"
            dim_cols[i].markdown(f"{labels[i]}: <span class='{color_class}'>{bounds[i]:.1f} / {p_limit[d]} mm</span>", unsafe_allow_html=True)
            if is_over: st.error(f"⚠️ {labels[i]} 超過 {p_choice} 的列印範圍！")

        # 3. 3D 預檢與厚度
        if st.button("🔍 執行壁厚檢查"):
            st.session_state.display_mesh = analyze_thickness_robust(mesh, min_wall_threshold)
        
        st.components.v1.html(render_3d_pro(st.session_state.display_mesh, p_limit), height=620)

else:
    st.title("📏 尺寸補償計算")
    d_size = st.number_input("設計尺寸 (mm)", min_value=0.1, value=20.0)
    a_size = st.number_input("實測尺寸 (mm)", min_value=0.1, value=19.8)
    st.markdown(f'建議縮放比例：<span class="price-result">{(d_size/a_size)*100:.2f}%</span>', unsafe_allow_html=True)
