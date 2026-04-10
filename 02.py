import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. 網頁配置 ---
st.set_page_config(page_title="SOLIDWIZARD Pro SLA 專家系統", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .price-result { display: inline-block; background-color: #FFFF00; color: #E11D48; padding: 10px 20px; border-radius: 8px; font-size: 28px; font-weight: 900; border: 3px solid #E11D48; }
    .sidebar-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #d1d5db; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 載入 GitHub 材料資料庫 (完整列入) ---
@st.cache_data
def load_materials():
    # 根據您的 GitHub 連結內容整理出的完整清單
    data = {
        "材料名稱": [
            "Clear Resin V4", "Grey Resin V4", "White Resin V4", "Black Resin V4",
            "Draft Resin V2", "Model Resin V3", "Tough 2000 Resin", "Tough 1500 Resin",
            "Durable Resin", "Grey Pro Resin", "Rigid 10K Resin", "Rigid 4000 Resin",
            "Flexible 80A Resin", "Elastic 50A Resin", "High Temp Resin", "Flame Retardant Resin",
            "ESD Resin", "BioMed Clear Resin", "BioMed Amber Resin", "BioMed White Resin",
            "BioMed Black Resin", "Custom Tray Resin", "IBT Resin", "Precision Model Resin",
            "Castable Wax 40 Resin", "Castable Wax Resin", "Silicone 40A Resin", "Alumina 4N Resin"
        ],
        "單價": [
            6900, 6900, 6900, 6900, 6900, 6900, 8500, 8500, 
            8500, 8500, 12000, 8500, 9500, 9500, 11000, 12000, 
            12000, 13500, 13500, 13500, 13500, 13500, 13500, 8500, 
            15000, 15000, 18000, 25000
        ]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df

df_m = load_materials()

# --- 3. 設備規格 ---
PRINTERS = {
    "Form 4": {"w": 200.0, "d": 125.0, "h": 210.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0}
}

# --- 4. 核心 3D 邏輯 ---

def create_wireframe_box(w, d, h, color):
    """建立細線構件框，不遮擋物件"""
    v = np.array([
        [-w/2, -d/2, -h/2], [w/2, -d/2, -h/2], [w/2, d/2, -h/2], [-w/2, d/2, -h/2],
        [-w/2, -d/2, h/2], [w/2, -d/2, h/2], [w/2, d/2, h/2], [-w/2, d/2, h/2]
    ])
    edges = [[0,1], [1,2], [2,3], [3,0], [4,5], [5,6], [6,7], [7,4], [0,4], [1,5], [2,6], [3,7]]
    lines = []
    for s, e in edges:
        line = trimesh.creation.cylinder(radius=0.4, segment=[v[s], v[e]])
        line.visual.face_colors = color
        lines.append(line)
    return trimesh.util.concatenate(lines)

def analyze_thickness(mesh, threshold):
    """最小薄度偵測：低於門檻標示紅色"""
    if threshold <= 0: return mesh
    color_mesh = mesh.copy()
    vertex_colors = np.full((len(color_mesh.vertices), 4), [200, 200, 200, 255], dtype=np.uint8)
    tree = cKDTree(color_mesh.triangles_center)
    for i, (vertex, v_normal) in enumerate(zip(color_mesh.vertices, color_mesh.vertex_normals)):
        dist, idx = tree.query(vertex, k=5)
        for d, f_idx in zip(dist, idx):
            if np.dot(v_normal, color_mesh.face_normals[f_idx]) < -0.5:
                if d < threshold:
                    vertex_colors[i] = [255, 0, 0, 255]
                break
    color_mesh.visual.vertex_colors = vertex_colors
    return color_mesh

def render_preview(mesh, printer_box, qty):
    """同步陣列預覽與框線變色邏輯"""
    w_limit, d_limit, h_limit = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    
    # 陣列擺放邏輯
    items = []
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.1 
    
    for i in range(qty):
        m_copy = mesh.copy()
        r, c = divmod(i, cols)
        m_copy.apply_translation([(c - (cols-1)/2) * spacing, (r - (cols-1)/2) * spacing, -m_copy.bounds[0][2] - h_limit/2])
        items.append(m_copy)
    
    final_mesh = trimesh.util.concatenate(items)
    scene.add_geometry(final_mesh)
    
    # 檢查是否超出範圍
    is_over = any(final_mesh.extents[i] > [w_limit, d_limit, h_limit][i] for i in range(3))
    box_color = [255, 0, 0, 255] if is_over else [150, 150, 150, 255]
    
    box_wire = create_wireframe_box(w_limit, d_limit, h_limit, box_color)
    scene.add_geometry(box_wire)
    
    glb = scene.export(file_type='glb')
    return base64.b64encode(glb).decode(), is_over

# --- 5. 左側側邊欄：設定與手動估價 ---
with st.sidebar:
    st.title("⚙️ 系統設定")
    
    # 手動輸入估價功能區 (Requirement 4)
    st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
    st.subheader("⌨️ 手動輸入估價")
    unit = st.radio("選擇體積單位", ["mm³", "cm³ (ml)"], horizontal=True)
    manual_v = st.number_input(f"輸入體積 ({unit})", min_value=0.0, value=0.0)
    st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📦 列印參數")
    p_choice = st.selectbox("選擇設備空間", list(PRINTERS.keys()))
    m_choice = st.selectbox("選擇材料", df_m["材料名稱"].tolist())
    qty = st.number_input("列印數量", min_value=1, value=1)
    markup = st.number_input("利潤倍率", min_value=1.0, value=2.0, step=0.1)
    
    st.subheader("🔍 薄度偵測設定")
    min_t = st.slider("薄度門檻 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 6. 主頁面邏輯 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

# 優先計算手動估價價格
if manual_v > 0:
    v_mm3 = manual_v if unit == "mm³" else manual_v * 1000
    m_price = (v_mm3 * u_cost * markup * qty) + (200 * qty)
    st.sidebar.warning(f"手動估價金額：NT$ {m_price:,.0f}")

st.title("🚀 SLA 多功能自動估價預檢系統")
up_file = st.file_uploader("上傳 STL 模型進行 3D 預檢", type=["stl"])

if up_file:
    if 'mesh' not in st.session_state or st.session_state.get('fname') != up_file.name:
        st.session_state.mesh = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
        st.session_state.fname = up_file.name

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✨ 建議擺放方向 (45° 斜角)"):
            rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
            st.session_state.mesh.apply_transform(rot)
            st.rerun()
    with col2:
        if st.button("🔴 執行最小薄度偵測"):
            st.session_state.mesh = analyze_thickness(st.session_state.mesh, min_t)
            st.success("分析完成，危險區域已標紅")

    # 價格計算
    vol = st.session_state.mesh.volume
    total_price = (vol * u_cost * markup * qty) + (200 * qty)
    st.markdown(f"建議總報價：<span class='price-result'>NT$ {total_price:,.0f}</span>", unsafe_allow_html=True)
    
    # 3D 同步預覽
    b64, over = render_preview(st.session_state.mesh, PRINTERS[p_choice], qty)
    if over: st.error(f"❌ 警告：數量或物件大小已超出 {p_choice} 列印範圍！")

    html = f"""
        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate style="width:100%; height:600px;"></model-viewer>
    """
    st.components.v1.html(html, height=620)
    
    st.info(f"當前模型體積: {vol:.2f} mm³ | 總材料消耗: {vol*qty/1000:.2f} ml")
