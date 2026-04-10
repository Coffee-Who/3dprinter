import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. 網頁配置與風格 ---
st.set_page_config(page_title="SOLIDWIZARD Pro SLA 專家系統", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #1E40AF; color: white; }
    .price-result { display: inline-block; background-color: #FFFF00; color: #E11D48; padding: 10px 20px; border-radius: 8px; font-size: 28px; font-weight: 900; border: 3px solid #E11D48; }
    .sidebar-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #d1d5db; }
    .over-limit { color: #FF0000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 完整材料資料庫 (連動 GitHub 清單) ---
@st.cache_data
def load_materials():
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
PRINTERS = {"Form 4": {"w": 200.0, "d": 125.0, "h": 210.0}, "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0}}

# --- 3. 核心 3D 邏輯 ---
def create_wireframe_box(w, d, h, color):
    """細線框線架構"""
    v = np.array([[-w/2,-d/2,-h/2], [w/2,-d/2,-h/2], [w/2,d/2,-h/2], [-w/2,d/2,-h/2],
                  [-w/2,-d/2,h/2], [w/2,-d/2,h/2], [w/2,d/2,h/2], [-w/2,d/2,h/2]])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    cyls = [trimesh.creation.cylinder(radius=0.4, segment=[v[s], v[e]]) for s,e in edges]
    box = trimesh.util.concatenate(cyls)
    box.visual.face_colors = color
    return box

def analyze_thickness(mesh, threshold):
    """薄度偵測標色"""
    if threshold <= 0: return mesh
    color_mesh = mesh.copy()
    vertex_colors = np.full((len(color_mesh.vertices), 4), [200, 200, 200, 255], dtype=np.uint8)
    tree = cKDTree(color_mesh.triangles_center)
    for i, (vertex, v_normal) in enumerate(zip(color_mesh.vertices, color_mesh.vertex_normals)):
        dist, idx = tree.query(vertex, k=5)
        for d, f_idx in zip(dist, idx):
            if np.dot(v_normal, color_mesh.face_normals[f_idx]) < -0.5:
                if d < threshold: vertex_colors[i] = [255, 0, 0, 255]
                break
    color_mesh.visual.vertex_colors = vertex_colors
    return color_mesh

def render_preview(mesh, printer_box, qty):
    """陣列預覽與空間檢核"""
    w_l, d_l, h_l = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    items = []
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.15
    for i in range(qty):
        m_copy = mesh.copy()
        r, c = divmod(i, cols)
        m_copy.apply_translation([(c - (cols-1)/2)*spacing, (r - (cols-1)/2)*spacing, -m_copy.bounds[0][2] - h_l/2])
        items.append(m_copy)
    final_mesh = trimesh.util.concatenate(items)
    scene.add_geometry(final_mesh)
    is_over = any(final_mesh.extents[i] > [w_l, d_l, h_l][i] for i in range(3))
    box_color = [255, 0, 0, 255] if is_over else [150, 150, 150, 255]
    scene.add_geometry(create_wireframe_box(w_l, d_l, h_l, box_color))
    glb = scene.export(file_type='glb')
    return base64.b64encode(glb).decode(), is_over

# --- 4. 左側側邊欄：功能選單 ---
with st.sidebar:
    st.title("🛡️ 專家報價選單")
    
    # 功能 4: 手動輸入體積
    st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
    st.subheader("⌨️ 手動輸入估價")
    m_unit = st.radio("單位", ["mm³", "cm³ (ml)"], horizontal=True)
    manual_v = st.number_input("輸入體積", min_value=0.0, step=100.0)
    st.markdown('</div>', unsafe_allow_html=True)

    # 功能 5: 上傳檔案估價
    st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
    st.subheader("📂 上傳檔案估價")
    up_file = st.file_uploader("選擇 STL 檔案", type=["stl"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    m_choice = st.selectbox("選擇 Formlabs 材料", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("切換列印空間", list(PRINTERS.keys()))
    qty = st.number_input("增加列印數量", min_value=1, value=1)
    markup = st.number_input("利潤倍率", min_value=1.0, value=2.0, step=0.1)
    min_t = st.slider("最小薄度偵測 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 5. 主頁面邏輯 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

# 計算價格邏輯
if manual_v > 0 or up_file:
    st.title("💰 SLA 智慧報價預檢")
    
    # 決定計算基準體積
    calc_vol = 0
    if up_file:
        if 'mesh' not in st.session_state or st.session_state.get('fname') != up_file.name:
            st.session_state.mesh = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
            st.session_state.fname = up_file.name
        calc_vol = st.session_state.mesh.volume
    else:
        calc_vol = manual_v if m_unit == "mm³" else manual_v * 1000

    total_price = (calc_vol * u_cost * markup * qty) + (200 * qty)
    st.markdown(f"建議總報價：<span class='price-result'>NT$ {total_price:,.0f}</span>", unsafe_allow_html=True)

    if up_file:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ 擺放建議 (45° 斜角)"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot); st.rerun()
        with col2:
            if st.button("🔴 執行薄度偵測標色"):
                st.session_state.mesh = analyze_thickness(st.session_state.mesh, min_t); st.success("分析完成")

        # 3D 渲染與同步陣列
        b64, over = render_preview(st.session_state.mesh, PRINTERS[p_choice], qty)
        if over: st.error(f"❌ 警告：物件排列已超出 {p_choice} 範圍！")
        
        html = f"""<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                   <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate shadow-intensity="1" style="width:100%; height:600px;"></model-viewer>"""
        st.components.v1.html(html, height=620)
        st.info(f"單件體積: {calc_vol:.2f} mm³ | 總材料消耗: {calc_vol*qty/1000:.2f} ml")
    else:
        st.info("目前使用手動輸入模式，上傳 STL 檔案可開啟 3D 預檢功能。")
else:
    st.info("請於左側選單「手動輸入體積」或「上傳 STL 檔案」開始估價。")
