import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. PreForm UI/UX 視覺與風格 ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm Pro", layout="wide")

st.markdown("""
    <style>
    /* 側邊欄風格 */
    [data-testid="stSidebar"] { background-color: #f1f5f9; border-right: 1px solid #cbd5e1; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: 600; background-color: #ffffff; border: 1px solid #cbd5e1; height: 40px; }
    .stButton>button:hover { background-color: #0081FF; color: white; border-color: #0081FF; }
    
    /* 報價面板設計 */
    .price-container { background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
    .price-result { color: #e11d48; font-size: 38px; font-weight: 900; letter-spacing: -1px; }
    .data-row { display: flex; justify-content: space-between; border-top: 1px solid #f1f5f9; padding-top: 12px; margin-top: 12px; }
    .data-label { color: #64748b; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .data-value { color: #0f172a; font-size: 16px; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 狀態管理 ---
if 'offset' not in st.session_state: st.session_state.offset = [0.0, 0.0]
if 'mesh' not in st.session_state: st.session_state.mesh = None
if 'fname' not in st.session_state: st.session_state.fname = ""

# --- 3. 材料與設備精確定義 (Requirement 1 & 6) ---
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

# --- 4. 核心 3D 渲染與 PreForm 邏輯 ---
def get_scene_glb(mesh, printer_box, qty, off_x, off_y):
    w, d, h = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.1 # PreForm 排列間距
    
    # 模型處理 (藍色呈現)
    instances = []
    for i in range(qty):
        m_inst = mesh.copy()
        m_inst.visual.face_colors = [0, 129, 255, 180] # PreForm 透明藍
        r, c = divmod(i, cols)
        tx = (c - (cols-1)/2) * spacing + off_x
        ty = (r - (cols-1)/2) * spacing + off_y
        tz = -h/2 - m_inst.bounds[0][2] # 對齊底部
        m_inst.apply_translation([tx, ty, tz])
        instances.append(m_inst)
    
    combined = trimesh.util.concatenate(instances)
    scene.add_geometry(combined)
    
    # 邊界檢測與變色
    b = combined.bounds
    is_over = (b[0][0] < -w/2 or b[1][0] > w/2 or b[0][1] < -d/2 or b[1][1] > d/2 or b[1][2] > h/2)
    box_color = [225, 29, 72, 255] if is_over else [148, 163, 184, 255]
    
    # 細線框 Wireframe (Requirement 3)
    v = np.array([[-w/2,-d/2,-h/2], [w/2,-d/2,-h/2], [w/2,d/2,-h/2], [-w/2,d/2,-h/2],
                  [-w/2,-d/2,h/2], [w/2,-d/2,h/2], [w/2,d/2,h/2], [-w/2,d/2,h/2]])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    for s, e in edges:
        line = trimesh.creation.cylinder(radius=0.15, segment=[v[s], v[e]])
        line.visual.face_colors = box_color
        scene.add_geometry(line)
        
    # 底部格子呈現 (Grid Floor)
    grid_size = 10.0 # 每格 10mm
    for i in np.arange(-w/2, w/2 + 1, grid_size):
        scene.add_geometry(trimesh.creation.cylinder(radius=0.05, segment=[[i, -d/2, -h/2], [i, d/2, -h/2]]))
    for j in np.arange(-d/2, d/2 + 1, grid_size):
        scene.add_geometry(trimesh.creation.cylinder(radius=0.05, segment=[[-w/2, j, -h/2], [w/2, j, -h/2]]))
        
    return base64.b64encode(scene.export(file_type='glb')).decode(), is_over

# --- 5. 左側選單介面 ---
with st.sidebar:
    st.title("PreForm 估價專家")
    
    with st.expander("⌨️ 手動輸入體積", expanded=False):
        m_unit = st.radio("選擇單位", ["mm³", "cm³ (ml)"], horizontal=True)
        manual_v = st.number_input("輸入體積值", min_value=0.0, step=100.0)
    
    with st.expander("📂 上傳檔案估價", expanded=True):
        up_file = st.file_uploader("上傳模型 STL", type=["stl"])
    
    st.divider()
    m_choice = st.selectbox("材料連動 (GitHub Data)", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("設備與框線大小", list(PRINTERS.keys()))
    qty = st.number_input("增加數量 (陣列同步)", min_value=1, value=1)
    markup = st.number_input("報價倍率 (Margin)", min_value=1.0, value=2.0)
    min_t_val = st.slider("最小薄度偵測 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 6. 報價與主操作區 ---
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
    
    # 價格與數據詳細資訊 (Requirement 7)
    st.markdown(f"""
    <div class="price-container">
        <div style="font-size: 14px; color: #64748b; font-weight: bold;">預估總報價</div>
        <div class="price-result">NT$ {total_price:,.0f}</div>
        <div class="data-row">
            <div class="data-item"><div class="data-label">選用材料</div><div class="data-value">{m_choice}</div></div>
            <div class="data-item"><div class="data-label">單件體積</div><div class="data-value">{calc_vol:,.1f} mm³</div></div>
            <div class="data-item"><div class="data-label">樹脂總消耗</div><div class="data-value">{calc_vol*qty/1000:,.2f} mL</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if up_file:
        st.divider()
        col_ctrl, col_view = st.columns([1, 3])
        
        with col_ctrl:
            st.write("🕹️ 操作零件 (左鍵邏輯)")
            if st.button("✨ 自動定位 (SLA 45° 斜角)"):
                # SLA 45度最佳化
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot)
                st.rerun()
            
            if st.button("🔴 執行薄度偵測"):
                tree = cKDTree(st.session_state.mesh.triangles_center)
                v_colors = np.full((len(st.session_state.mesh.vertices), 4), [0, 129, 255, 180], dtype=np.uint8)
                for i, (v, n) in enumerate(zip(st.session_state.mesh.vertices, st.session_state.mesh.vertex_normals)):
                    d, idx = tree.query(v, k=5)
                    for dist, f_idx in zip(d, idx):
                        if np.dot(n, st.session_state.mesh.face_normals[f_idx]) < -0.5 and dist < min_t_val:
                            v_colors[i] = [255, 0, 0, 255]
                            break
                st.session_state.mesh.visual.vertex_colors = v_colors
                st.success(f"完成偵測: {min_t_val}mm")

            st.write("📏 零件平移微調 (X/Y)")
            c1, c2 = st.columns(2)
            if c1.button("⬅️ X-"): st.session_state.offset[0] -= 10; st.rerun()
            if c2.button("➡️ X+"): st.session_state.offset[0] += 10; st.rerun()
            c3, c4 = st.columns(2)
            if c3.button("⬆️ Y+"): st.session_state.offset[1] += 10; st.rerun()
            if c4.button("⬇️ Y-"): st.session_state.offset[1] -= 10; st.rerun()
            if st.button("🔄 旋轉零件 45°"):
                st.session_state.mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(45), [0,0,1]))
                st.rerun()

        with col_view:
            glb_str, over = get_scene_glb(st.session_state.mesh, PRINTERS[p_choice], qty, 
                                          st.session_state.offset[0], st.session_state.offset[1])
            
            if over: st.error("⚠️ 警告：物件已越界！框線已變紅，請調整位置或機型。")
            
            # Model-viewer 深度模擬 (Requirement 6)
            st.components.v1.html(f"""
                <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                <model-viewer src="data:model/gltf-binary;base64,{glb_str}" 
                    camera-controls 
                    camera-orbit="45deg 75deg 105%" 
                    field-of-view="25deg"
                    style="width:100%; height:650px; background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px;">
                </model-viewer>
                <div style="font-size:11px; color:#64748b; text-align:right; margin-top:8px;">
                    等角視圖模式 | 右鍵：旋轉 3D 框線視角 | 左鍵控制盤：只移動零件位移 | 底部格子為 10x10mm
                </div>
            """, height=680)
else:
    st.info("👋 歡迎。請由左側執行「手動估價」或「模型上傳」以啟動 PreForm 專業模擬系統。")
