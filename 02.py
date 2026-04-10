import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. PreForm 介面與操作邏輯樣式 ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm Mode", layout="wide")

st.markdown("""
    <style>
    /* 側邊欄風格 */
    [data-testid="stSidebar"] { background-color: #f3f4f6; border-right: 1px solid #d1d5db; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: 600; background-color: #ffffff; color: #374151; border: 1px solid #d1d5db; }
    .stButton>button:hover { background-color: #0081FF; color: white; border-color: #0081FF; }
    
    /* PreForm 報價面板 */
    .price-container { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .price-result { color: #E11D48; font-size: 36px; font-weight: 900; }
    .data-card { border-top: 1px solid #f3f4f6; padding-top: 10px; margin-top: 10px; }
    .data-label { color: #6b7280; font-size: 12px; font-weight: bold; text-transform: uppercase; }
    .data-value { color: #111827; font-size: 16px; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化持久狀態 (State Management) ---
if 'offset' not in st.session_state: st.session_state.offset = [0.0, 0.0]
if 'mesh' not in st.session_state: st.session_state.mesh = None
if 'fname' not in st.session_state: st.session_state.fname = ""

# --- 3. 材料與設備資料 (GitHub 連動) ---
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

# --- 4. 核心 3D 渲染邏輯 ---
def get_scene_glb(mesh, printer_box, qty, off_x, off_y):
    w, d, h = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.15
    
    instances = []
    for i in range(qty):
        m_inst = mesh.copy()
        # PreForm 藍色呈現
        m_inst.visual.face_colors = [0, 129, 255, 255]
        r, c = divmod(i, cols)
        tx = (c - (cols-1)/2) * spacing + off_x
        ty = (r - (cols-1)/2) * spacing + off_y
        # 底部對齊與置中
        tz = -h/2 - m_inst.bounds[0][2] 
        m_inst.apply_translation([tx, ty, tz])
        instances.append(m_inst)
    
    combined = trimesh.util.concatenate(instances)
    scene.add_geometry(combined)
    
    # 邊界檢測
    b = combined.bounds
    is_over = (b[0][0] < -w/2 or b[1][0] > w/2 or b[0][1] < -d/2 or b[1][1] > d/2 or b[1][2] > h/2)
    
    # 細線網格與邊框 (Wireframe)
    v = np.array([[-w/2,-d/2,-h/2], [w/2,-d/2,-h/2], [w/2,d/2,-h/2], [-w/2,d/2,-h/2],
                  [-w/2,-d/2,h/2], [w/2,-d/2,h/2], [w/2,d/2,h/2], [-w/2,d/2,h/2]])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    box_color = [255, 0, 0, 255] if is_over else [200, 200, 200, 255]
    
    for s, e in edges:
        line = trimesh.creation.cylinder(radius=0.2, segment=[v[s], v[e]])
        line.visual.face_colors = box_color
        scene.add_geometry(line)
        
    return base64.b64encode(scene.export(file_type='glb')).decode(), is_over

# --- 5. 左側 PreForm 操作面板 ---
with st.sidebar:
    st.title("PreForm 控制台")
    
    with st.container():
        st.subheader("⌨️ 手動輸入估價")
        m_unit = st.radio("單位", ["mm³", "cm³"], horizontal=True)
        manual_v = st.number_input("輸入體積", min_value=0.0, step=100.0)

    with st.container():
        st.subheader("📂 上傳檔案估價")
        up_file = st.file_uploader("選擇 STL 檔案", type=["stl"])
    
    st.divider()
    m_choice = st.selectbox("選擇材料 (Formlabs)", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("選擇設備 (機型範圍)", list(PRINTERS.keys()))
    qty = st.number_input("增加數量", min_value=1, value=1)
    markup = st.number_input("報價加成倍率", min_value=1.0, value=2.0)
    min_t_val = st.slider("最小薄度偵測 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 6. 主頁面：價格顯示與 3D 交互 ---
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
    
    st.markdown(f"""
    <div class="price-container">
        <div style="font-size: 14px; color: #6b7280; font-weight: bold;">預估總成本 (含稅)</div>
        <div class="price-result">NT$ {total_price:,.0f}</div>
        <div class="data-card">
            <div style="display: flex; justify-content: space-between;">
                <div><div class="data-label">使用材料</div><div class="data-value">{m_choice}</div></div>
                <div><div class="data-label">單件體積</div><div class="data-value">{calc_vol:,.1f} mm³</div></div>
                <div><div class="data-label">總消耗 mL</div><div class="data-value">{calc_vol*qty/1000:,.2f}</div></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if up_file:
        st.divider()
        col_ctrl, col_view = st.columns([1, 3])
        
        with col_ctrl:
            st.write("🕹️ 定向與偵測")
            if st.button("✨ SLA 45° 擺放建議"):
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
                st.success("低於門檻區域標紅完成")

            st.write("📐 手動微調位置")
            c1, c2 = st.columns(2)
            if c1.button("⬅️ X-"): st.session_state.offset[0] -= 10; st.rerun()
            if c2.button("➡️ X+"): st.session_state.offset[0] += 10; st.rerun()
            c3, c4 = st.columns(2)
            if c3.button("⬆️ Y+"): st.session_state.offset[1] += 10; st.rerun()
            if c4.button("⬇️ Y-"): st.session_state.offset[1] -= 10; st.rerun()
            if st.button("🔄 旋轉 90°"):
                st.session_state.mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0,0,1]))
                st.rerun()

        with col_view:
            glb_b64, over = get_scene_glb(st.session_state.mesh, PRINTERS[p_choice], qty, 
                                          st.session_state.offset[0], st.session_state.offset[1])
            if over: st.error("⚠️ 超出列印範圍！框線變紅。")
            
            # 使用 model-viewer 模擬 PreForm 的等角觀看與右鍵旋轉邏輯
            # camera-orbit 設定初始方位角 (等角視圖)
            st.components.v1.html(f"""
                <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                <model-viewer src="data:model/gltf-binary;base64,{glb_b64}" 
                    camera-controls 
                    camera-orbit="45deg 75deg 105%" 
                    min-camera-orbit="auto auto auto"
                    style="width:100%; height:600px; background-color: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px;">
                </model-viewer>
                <div style="font-size:12px; color:#94a3b8; text-align:right;">右鍵：旋轉視角 | 左鍵：縮放觀看 | 控制盤：調整位置</div>
            """, height=630)
else:
    st.info("💡 請上傳 STL 模型或輸入體積開始專業報價。")
