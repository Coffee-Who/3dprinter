import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. PreForm 介面風格配置 ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm Mode", layout="wide")

st.markdown("""
    <style>
    /* PreForm 側邊導覽列風格 */
    [data-testid="stSidebar"] { background-color: #f3f4f6; border-right: 1px solid #d1d5db; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: 600; background-color: #ffffff; color: #374151; border: 1px solid #d1d5db; transition: 0.2s; }
    .stButton>button:hover { background-color: #0081FF; color: white; border-color: #0081FF; }
    
    /* 報價區塊 PreForm 化 */
    .price-container { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .price-result { color: #E11D48; font-size: 36px; font-weight: 900; }
    .data-card { border-top: 1px solid #f3f4f6; padding-top: 10px; margin-top: 10px; }
    .data-label { color: #6b7280; font-size: 12px; font-weight: bold; text-transform: uppercase; }
    .data-value { color: #111827; font-size: 16px; font-weight: 700; }
    
    /* 側邊功能盒 */
    .sidebar-box { background-color: #ffffff; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #e5e7eb; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化持久狀態 ---
if 'offset' not in st.session_state: st.session_state.offset = [0.0, 0.0]
if 'rotation_matrix' not in st.session_state: st.session_state.rotation_matrix = np.eye(4)
if 'mesh' not in st.session_state: st.session_state.mesh = None
if 'fname' not in st.session_state: st.session_state.fname = ""

# --- 3. 材料資料連動 (GitHub) ---
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
        "單價": [6900, 6900, 6900, 6900, 6900, 6900, 8500, 8500, 8500, 8500, 12000, 8500, 9500, 9500, 11000, 12000, 12000, 13500, 13500, 13500, 13500, 13500, 13500, 8500, 15000, 15000, 18000, 25000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df

df_m = load_materials()
PRINTERS = {"Form 4": {"w": 200.0, "d": 125.0, "h": 210.0}, "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0}}

# --- 4. 核心 3D 渲染引擎 ---
def get_scene_glb(mesh, printer_box, qty, off_x, off_y):
    w_l, d_l, h_l = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.15
    
    # 模型陣列化並設為藍色 (PreForm Style)
    instances = []
    for i in range(qty):
        m_inst = mesh.copy()
        m_inst.visual.face_colors = [0, 129, 255, 255] # Preform Blue
        r, c = divmod(i, cols)
        tx = (c - (cols-1)/2) * spacing + off_x
        ty = (r - (cols-1)/2) * spacing + off_y
        tz = -h_l/2 - m_inst.bounds[0][2] # 對齊底部
        m_inst.apply_translation([tx, ty, tz])
        instances.append(m_inst)
    
    combined = trimesh.util.concatenate(instances)
    scene.add_geometry(combined)
    
    # 邊界檢測與線框
    b = combined.bounds
    is_over = (b[0][0] < -w_l/2 or b[1][0] > w_l/2 or b[0][1] < -d_l/2 or b[1][1] > d_l/2 or b[1][2] > h_l/2)
    
    # 細線架構 Wireframe
    v = np.array([[-w/2,-d/2,-h/2], [w/2,-d/2,-h/2], [w/2,d/2,-h/2], [-w/2,d/2,-h/2],
                  [-w/2,-d/2,h/2], [w/2,-d/2,h/2], [w/2,d/2,h/2], [-w/2,d/2,h/2]])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    box_color = [255, 0, 0, 255] if is_over else [150, 150, 150, 255]
    for s, e in edges:
        line = trimesh.creation.cylinder(radius=0.2, segment=[v[s], v[e]])
        line.visual.face_colors = box_color
        scene.add_geometry(line)
        
    return base64.b64encode(scene.export(file_type='glb')).decode(), is_over

# --- 5. 左側功能選單 ---
with st.sidebar:
    st.title("PreForm 控制台")
    
    # 功能 4: 手動輸入
    with st.expander("⌨️ 手動輸入體積", expanded=False):
        m_unit = st.radio("單位", ["mm³", "cm³"], horizontal=True)
        manual_v = st.number_input("輸入體積", min_value=0.0, step=100.0)
    
    # 功能 5: 上傳檔案
    with st.expander("📂 上傳檔案估價", expanded=True):
        up_file = st.file_uploader("選擇 STL 檔案", type=["stl"])
    
    st.divider()
    m_choice = st.selectbox("Formlabs 材料", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("印表機型號", list(PRINTERS.keys()))
    qty = st.number_input("列印數量", min_value=1, value=1)
    markup = st.number_input("價格加成 (倍率)", min_value=1.0, value=2.0)
    min_t_val = st.slider("薄度偵測 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 6. 主畫面邏輯 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

if manual_v > 0 or up_file:
    # 體積與報價計算
    calc_vol = 0
    if up_file:
        if st.session_state.fname != up_file.name:
            st.session_state.mesh = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
            st.session_state.fname = up_file.name
            st.session_state.offset = [0.0, 0.0]
        calc_vol = st.session_state.mesh.volume
    else:
        calc_vol = manual_v if m_unit == "mm³" else manual_v * 1000

    total_price = (calc_vol * u_cost * markup * qty) + (200 * qty)
    
    # 報價顯示區 (Requirement 7)
    st.markdown(f"""
    <div class="price-container">
        <div style="font-size: 14px; color: #6b7280; font-weight: bold;">預估總列印成本 (含稅)</div>
        <div class="price-result">NT$ {total_price:,.0f}</div>
        <div class="data-card">
            <div style="display: flex; justify-content: space-between;">
                <div><div class="data-label">使用材料</div><div class="data-value">{m_choice}</div></div>
                <div><div class="data-label">單件體積</div><div class="data-value">{calc_vol:,.1f} mm³</div></div>
                <div><div class="data-label">總樹脂消耗</div><div class="data-value">{calc_vol*qty/1000:,.2f} mL</div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if up_file:
        st.divider()
        # PreForm 操作面板 (Requirement 5 & 6)
        col_ctrl, col_view = st.columns([1, 3])
        
        with col_ctrl:
            st.subheader("操控工具")
            if st.button("✨ 自動定位 (45° 斜角)"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot)
                st.rerun()
            
            if st.button("🔴 薄度偵測分析"):
                tree = cKDTree(st.session_state.mesh.triangles_center)
                v_colors = np.full((len(st.session_state.mesh.vertices), 4), [0, 129, 255, 255], dtype=np.uint8)
                for i, (v, n) in enumerate(zip(st.session_state.mesh.vertices, st.session_state.mesh.vertex_normals)):
                    d, idx = tree.query(v, k=5)
                    for dist, f_idx in zip(d, idx):
                        if np.dot(n, st.session_state.mesh.face_normals[f_idx]) < -0.5 and dist < min_t_val:
                            v_colors[i] = [255, 0, 0, 255] # 標紅
                            break
                st.session_state.mesh.visual.vertex_colors = v_colors
                st.success("分析完成：紅色為過薄區域")

            st.write("🕹️ 手動平移 (mm)")
            c1, c2 = st.columns(2)
            if c1.button("⬅️ X-"): st.session_state.offset[0] -= 10; st.rerun()
            if c2.button("➡️ X+"): st.session_state.offset[0] += 10; st.rerun()
            c3, c4 = st.columns(2)
            if c3.button("⬆️ Y+"): st.session_state.offset[1] += 10; st.rerun()
            if c4.button("⬇️ Y-"): st.session_state.offset[1] -= 10; st.rerun()
            
            if st.button("🔄 水平旋轉 90°"):
                st.session_state.mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0,0,1]))
                st.rerun()

        with col_view:
            # 3D 渲染與陣列同步
            glb_b64, over = get_scene_glb(st.session_state.mesh, PRINTERS[p_choice], qty, 
                                          st.session_state.offset[0], st.session_state.offset[1])
            
            if over: st.error("⚠️ 物件超出列印邊界！框線已變紅。")
            
            html_content = f"""
                <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                <model-viewer src="data:model/gltf-binary;base64,{glb_b64}" camera-controls auto-rotate 
                    exposure="1.0" shadow-intensity="1" 
                    style="width:100%; height:600px; background-color: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px;">
                </model-viewer>
            """
            st.components.v1.html(html_content, height=620)
else:
    st.info("👋 歡迎使用 PreForm 報價系統。請由左側上傳模型或輸入體積開始。")
