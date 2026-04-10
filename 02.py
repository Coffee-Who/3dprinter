import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. PreForm UI 風格整合 ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm AI", layout="wide")

st.markdown("""
    <style>
    /* 側邊欄與按鈕 PreForm 化 */
    [data-testid="stSidebar"] { background-color: #f1f5f9; border-right: 1px solid #cbd5e1; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: 600; background-color: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; }
    .stButton>button:hover { background-color: #0081FF; color: white; border-color: #0081FF; }
    
    /* 報價看板設計 */
    .price-container { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .price-result { color: #ef4444; font-size: 36px; font-weight: 900; }
    .data-row { display: flex; justify-content: space-between; border-top: 1px solid #f1f5f9; padding-top: 8px; margin-top: 8px; }
    .data-item { text-align: left; }
    .data-label { color: #64748b; font-size: 11px; font-weight: bold; }
    .data-value { color: #0f172a; font-size: 15px; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心狀態初始化 ---
if 'offset' not in st.session_state: st.session_state.offset = [0.0, 0.0]
if 'mesh' not in st.session_state: st.session_state.mesh = None
if 'fname' not in st.session_state: st.session_state.fname = ""

# --- 3. 材料與設備資料 (同步 GitHub) ---
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

# --- 4. 3D 空間處理邏輯 ---
def get_scene_glb(mesh, printer_box, qty, off_x, off_y):
    w, d, h = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.15
    
    instances = []
    for i in range(qty):
        m_inst = mesh.copy()
        m_inst.visual.face_colors = [0, 129, 255, 255] # PreForm 經典藍
        r, c = divmod(i, cols)
        tx = (c - (cols-1)/2) * spacing + off_x
        ty = (r - (cols-1)/2) * spacing + off_y
        tz = -h/2 - m_inst.bounds[0][2] # 底部對齊
        m_inst.apply_translation([tx, ty, tz])
        instances.append(m_inst)
    
    combined = trimesh.util.concatenate(instances)
    scene.add_geometry(combined)
    
    # 邊界檢測與線框
    b = combined.bounds
    is_over = (b[0][0] < -w/2 or b[1][0] > w/2 or b[0][1] < -d/2 or b[1][1] > d/2 or b[1][2] > h/2)
    box_color = [239, 68, 68, 255] if is_over else [203, 213, 225, 255]
    
    # 細線 Wireframe
    v = np.array([[-w/2,-d/2,-h/2], [w/2,-d/2,-h/2], [w/2,d/2,-h/2], [-w/2,d/2,-h/2],
                  [-w/2,-d/2,h/2], [w/2,-d/2,h/2], [w/2,d/2,h/2], [-w/2,d/2,h/2]])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    for s, e in edges:
        line = trimesh.creation.cylinder(radius=0.15, segment=[v[s], v[e]])
        line.visual.face_colors = box_color
        scene.add_geometry(line)
        
    return base64.b64encode(scene.export(file_type='glb')).decode(), is_over

# --- 5. 左側 PreForm 側欄選單 ---
with st.sidebar:
    st.image("https://formlabs.com/favicon.ico", width=24)
    st.title("PreForm 估價系統")
    
    with st.expander("⌨️ 手動輸入體積", expanded=False):
        m_unit = st.radio("單位", ["mm³", "cm³ (ml)"], horizontal=True)
        manual_v = st.number_input("輸入數值", min_value=0.0, step=100.0)
    
    with st.expander("📂 上傳檔案估價", expanded=True):
        up_file = st.file_uploader("選擇模型 STL", type=["stl"])
    
    st.divider()
    m_choice = st.selectbox("Formlabs 材料連動", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("設備機型 (框線範圍)", list(PRINTERS.keys()))
    qty = st.number_input("陣列數量同步", min_value=1, value=1)
    markup = st.number_input("報價加成比率", min_value=1.0, value=2.0)
    min_t_val = st.slider("最小薄度偵測 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 6. 報價與交互介面實作 ---
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
    
    # 報價看板 (Requirement 7)
    st.markdown(f"""
    <div class="price-container">
        <div style="font-size: 14px; color: #64748b; font-weight: bold;">預估報價總計</div>
        <div class="price-result">NT$ {total_price:,.0f}</div>
        <div class="data-row">
            <div class="data-item"><div class="data-label">材料連動</div><div class="data-value">{m_choice}</div></div>
            <div class="data-item"><div class="data-label">單體體積</div><div class="data-value">{calc_vol:,.1f} mm³</div></div>
            <div class="data-item"><div class="data-label">總消耗量</div><div class="data-value">{calc_vol*qty/1000:,.2f} mL</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if up_file:
        st.divider()
        col_ctrl, col_view = st.columns([1, 3])
        
        with col_ctrl:
            st.write("🕹️ 零件操作 (左鍵邏輯)")
            if st.button("✨ 自動定位 (SLA 45° 斜角)"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot)
                st.rerun()
            
            if st.button("🔴 薄度偵測"):
                tree = cKDTree(st.session_state.mesh.triangles_center)
                v_colors = np.full((len(st.session_state.mesh.vertices), 4), [0, 129, 255, 255], dtype=np.uint8)
                for i, (v, n) in enumerate(zip(st.session_state.mesh.vertices, st.session_state.mesh.vertex_normals)):
                    d, idx = tree.query(v, k=5)
                    for dist, f_idx in zip(d, idx):
                        if np.dot(n, st.session_state.mesh.face_normals[f_idx]) < -0.5 and dist < min_t_val:
                            v_colors[i] = [255, 0, 0, 255]
                            break
                st.session_state.mesh.visual.vertex_colors = v_colors
                st.success(f"完成偵測 (閾值: {min_t_val}mm)")

            st.write("📏 位置與方向控制")
            c1, c2 = st.columns(2)
            if c1.button("⬅️ X-"): st.session_state.offset[0] -= 10; st.rerun()
            if c2.button("➡️ X+"): st.session_state.offset[0] += 10; st.rerun()
            c3, c4 = st.columns(2)
            if c3.button("⬆️ Y+"): st.session_state.offset[1] += 10; st.rerun()
            if c4.button("⬇️ Y-"): st.session_state.offset[1] -= 10; st.rerun()
            if st.button("🔄 旋轉零件 90°"):
                st.session_state.mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0,0,1]))
                st.rerun()

        with col_view:
            glb_str, over = get_scene_glb(st.session_state.mesh, PRINTERS[p_choice], qty, 
                                          st.session_state.offset[0], st.session_state.offset[1])
            if over: st.error("❌ 模型已超出列印機型範圍！框線已變紅。")
            
            # 整合 PreForm 操作邏輯 (Requirement 6)
            st.components.v1.html(f"""
                <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                <model-viewer src="data:model/gltf-binary;base64,{glb_str}" 
                    camera-controls 
                    camera-orbit="45deg 75deg 105%" 
                    min-camera-orbit="auto auto auto"
                    style="width:100%; height:600px; background-color: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0;">
                </model-viewer>
                <div style="font-size:11px; color:#94a3b8; text-align:right; padding:5px;">
                    💡 右鍵：旋轉列印框視角 | 左側工具列：平移/旋轉/偵測零件 (框線不動)
                </div>
            """, height=630)
else:
    st.info("👋 歡迎。請由左側執行「手動估價」或「上傳 STL」來啟動 PreForm 專業模擬。")
