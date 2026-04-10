import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. PreForm 專業 UI 配置 ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm AI", layout="wide")

st.markdown("""
    <style>
    /* 側邊欄風格：灰白極簡 */
    [data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: 600; background-color: #ffffff; border: 1px solid #cbd5e1; height: 38px; font-size: 13px; }
    .stButton>button:hover { background-color: #0081FF; color: white; border-color: #0081FF; }
    
    /* 報價看板：模擬 PreForm 左下角統計資訊 */
    .price-container { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .price-result { color: #1e293b; font-size: 32px; font-weight: 800; border-bottom: 2px solid #0081FF; display: inline-block; margin-bottom: 10px; }
    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .data-item { border-left: 3px solid #cbd5e1; padding-left: 10px; }
    .data-label { color: #64748b; font-size: 10px; font-weight: bold; text-transform: uppercase; }
    .data-value { color: #0f172a; font-size: 14px; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心狀態初始化 ---
if 'offset' not in st.session_state: st.session_state.offset = [0.0, 0.0]
if 'mesh' not in st.session_state: st.session_state.mesh = None
if 'fname' not in st.session_state: st.session_state.fname = ""

# --- 3. 材料與設備規格定義 (Requirement 1 & 6) ---
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
# 精確尺寸設定 (單位: mm)
PRINTERS = {
    "Form 4": {"w": 200.0, "d": 125.0, "h": 210.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0}
}

# --- 4. 3D 渲染核心：陣列、線框與底部網格 ---
def get_scene_glb(mesh, printer_box, qty, off_x, off_y):
    w, d, h = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.15 # 零件間距
    
    # 模型處理 (PreForm 經典藍)
    instances = []
    for i in range(qty):
        m_inst = mesh.copy()
        m_inst.visual.face_colors = [0, 129, 255, 200] # 半透明藍
        r, c = divmod(i, cols)
        tx = (c - (cols-1)/2) * spacing + off_x
        ty = (r - (cols-1)/2) * spacing + off_y
        tz = -h/2 - m_inst.bounds[0][2] # 貼齊底部
        m_inst.apply_translation([tx, ty, tz])
        instances.append(m_inst)
    
    combined = trimesh.util.concatenate(instances)
    scene.add_geometry(combined)
    
    # 邊界檢測
    b = combined.bounds
    is_over = (b[0][0] < -w/2 or b[1][0] > w/2 or b[0][1] < -d/2 or b[1][1] > d/2 or b[1][2] > h/2)
    box_color = [225, 29, 72, 255] if is_over else [156, 163, 175, 255]
    
    # 細線框 Wireframe
    v = np.array([[-w/2,-d/2,-h/2], [w/2,-d/2,-h/2], [w/2,d/2,-h/2], [-w/2,d/2,-h/2],
                  [-w/2,-d/2,h/2], [w/2,-d/2,h/2], [w/2,d/2,h/2], [-w/2,d/2,h/2]])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    for s, e in edges:
        line = trimesh.creation.cylinder(radius=0.12, segment=[v[s], v[e]])
        line.visual.face_colors = box_color
        scene.add_geometry(line)
        
    # 底部網格地板 (Requirement 6)
    grid_res = 10.0 # 10mm 一格
    for i in np.arange(-w/2, w/2 + 1, grid_res):
        line = trimesh.creation.cylinder(radius=0.04, segment=[[i, -d/2, -h/2], [i, d/2, -h/2]])
        line.visual.face_colors = [203, 213, 225, 255]
        scene.add_geometry(line)
    for j in np.arange(-d/2, d/2 + 1, grid_res):
        line = trimesh.creation.cylinder(radius=0.04, segment=[[-w/2, j, -h/2], [w/2, j, -h/2]])
        line.visual.face_colors = [203, 213, 225, 255]
        scene.add_geometry(line)
        
    return base64.b64encode(scene.export(file_type='glb')).decode(), is_over

# --- 5. 左側導覽列實作 (Requirement 4 & 5) ---
with st.sidebar:
    st.image("https://formlabs.com/favicon.ico", width=20)
    st.title("PreForm 模擬報價")
    
    with st.container():
        st.subheader("⌨️ 手動估價 (左側)")
        m_unit = st.radio("單位", ["mm³", "cm³"], horizontal=True)
        manual_v = st.number_input("體積值", min_value=0.0, step=100.0)

    with st.container():
        st.subheader("📂 上傳檔案 (左側)")
        up_file = st.file_uploader("STL 檔案上傳", type=["stl"])
    
    st.divider()
    m_choice = st.selectbox("Formlabs 材料選擇", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("列印機型範圍", list(PRINTERS.keys()))
    qty = st.number_input("數量陣列同步", min_value=1, value=1)
    markup = st.number_input("報價加成倍率", min_value=1.0, value=2.0)
    min_t_val = st.slider("最小薄度偵測 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 6. 主畫面報價與 3D 交互 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

if manual_v > 0 or up_file:
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
    
    # 價格資料顯示 (Requirement 7)
    st.markdown(f"""
    <div class="price-container">
        <div style="font-size: 13px; color: #64748b; font-weight: bold;">PREFORM 預估總列印成本</div>
        <div class="price-result">NT$ {total_price:,.0f}</div>
        <div class="data-grid">
            <div class="data-item"><div class="data-label">列印體積</div><div class="data-value">{calc_vol:,.1f} mm³</div></div>
            <div class="data-item"><div class="data-label">使用材料</div><div class="data-value">{m_choice}</div></div>
            <div class="data-item"><div class="data-label">總消耗 (mL)</div><div class="data-value">{calc_vol*qty/1000:,.2f}</div></div>
            <div class="data-item"><div class="data-label">列印機型</div><div class="data-value">{p_choice}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if up_file:
        st.divider()
        col_tool, col_view = st.columns([1, 3])
        
        with col_tool:
            st.write("🕹️ 零件操作 (左鍵控制)")
            if st.button("✨ SLA 45° 擺放建議"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot)
                st.rerun()
            
            if st.button("🔴 薄度偵測分析"):
                tree = cKDTree(st.session_state.mesh.triangles_center)
                v_colors = np.full((len(st.session_state.mesh.vertices), 4), [0, 129, 255, 200], dtype=np.uint8)
                for i, (v, n) in enumerate(zip(st.session_state.mesh.vertices, st.session_state.mesh.vertex_normals)):
                    d, idx = tree.query(v, k=5)
                    for dist, f_idx in zip(d, idx):
                        if np.dot(n, st.session_state.mesh.face_normals[f_idx]) < -0.5 and dist < min_t_val:
                            v_colors[i] = [255, 0, 0, 255]
                            break
                st.session_state.mesh.visual.vertex_colors = v_colors
                st.success(f"標記完成: {min_t_val}mm")

            st.write("📏 X/Y 平面位置調整")
            c1, c2 = st.columns(2)
            if c1.button("⬅️ X-"): st.session_state.offset[0] -= 10; st.rerun()
            if c2.button("➡️ X+"): st.session_state.offset[0] += 10; st.rerun()
            c3, c4 = st.columns(2)
            if c3.button("⬆️ Y+"): st.session_state.offset[1] += 10; st.rerun()
            if c4.button("⬇️ Y-"): st.session_state.offset[1] -= 10; st.rerun()
            if st.button("🔄 旋轉物件 90°"):
                st.session_state.mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0,0,1]))
                st.rerun()

        with col_view:
            glb_b64, over = get_scene_glb(st.session_state.mesh, PRINTERS[p_choice], qty, 
                                          st.session_state.offset[0], st.session_state.offset[1])
            if over: st.error("⚠️ 零件超出設備列印範圍！框線已標紅。")
            
            # Model-viewer 深度模擬操作邏輯 (Requirement 6)
            st.components.v1.html(f"""
                <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                <model-viewer src="data:model/gltf-binary;base64,{glb_b64}" 
                    camera-controls 
                    camera-orbit="45deg 75deg 105%" 
                    min-camera-orbit="auto auto auto"
                    field-of-view="25deg"
                    style="width:100%; height:600px; background-color: #f1f5f9; border-radius: 8px; border: 1px solid #cbd5e1;">
                </model-viewer>
                <div style="font-size:11px; color:#94a3b8; text-align:right; margin-top:5px;">
                    等角方位視圖 | 右鍵：操作視角旋轉 | 左側按鈕：操作零件移動 (框線維持原本方位)
                </div>
            """, height=630)
else:
    st.info("💡 請上傳 STL 模型或手動輸入體積，開始 PreForm 專業模擬。")
