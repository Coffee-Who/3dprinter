import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. 網頁配置與 Preform 風格美化 ---
st.set_page_config(page_title="SOLIDWIZARD Pro SLA 專家系統", layout="wide")

st.markdown("""
    <style>
    /* Preform 藍色風格按鈕 */
    .stButton>button { width: 100%; border-radius: 4px; font-weight: bold; background-color: #0081FF; color: white; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #0056b3; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    /* 價格大字顯示 */
    .price-result { display: inline-block; background-color: #FFFF00; color: #E11D48; padding: 15px 30px; border-radius: 8px; font-size: 36px; font-weight: 900; border: 3px solid #E11D48; box-shadow: 5px 5px 0px #000; }
    /* 數據面板 */
    .data-card { background-color: #ffffff; padding: 10px; border-left: 5px solid #0081FF; margin-bottom: 5px; }
    .data-label { color: #64748b; font-size: 13px; font-weight: bold; }
    .data-value { color: #1E293B; font-size: 18px; font-weight: 800; }
    /* 側邊欄區塊 */
    .sidebar-box { background-color: #f8fafc; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化 Session State (穩定核心) ---
if 'offset' not in st.session_state: st.session_state.offset = [0.0, 0.0]
if 'mesh' not in st.session_state: st.session_state.mesh = None
if 'fname' not in st.session_state: st.session_state.fname = ""

# --- 3. 完整材料連動 (GitHub 資料庫) ---
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

# --- 4. 核心 3D 處理引擎 ---
def create_preform_wireframe(w, d, h, is_over):
    """建立 Preform 風格的細線架構"""
    v = np.array([[-w/2,-d/2,-h/2], [w/2,-d/2,-h/2], [w/2,d/2,-h/2], [-w/2,d/2,-h/2],
                  [-w/2,-d/2,h/2], [w/2,-d/2,h/2], [w/2,d/2,h/2], [-w/2,d/2,h/2]])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    color = [255, 0, 0, 255] if is_over else [180, 180, 180, 255]
    lines = [trimesh.creation.cylinder(radius=0.3, segment=[v[s], v[e]]) for s,e in edges]
    box = trimesh.util.concatenate(lines)
    box.visual.face_colors = color
    return box

def render_preform_scene(mesh, printer_box, qty, off_x, off_y):
    w_l, d_l, h_l = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.1 # Preform 自動排列間距
    
    combined_list = []
    for i in range(qty):
        m_copy = mesh.copy()
        r, c = divmod(i, cols)
        tx = (c - (cols-1)/2) * spacing + off_x
        ty = (r - (cols-1)/2) * spacing + off_y
        # 底部對齊 (Bottom Center)
        tz = -h_l/2 - m_copy.bounds[0][2] 
        m_copy.apply_translation([tx, ty, tz])
        combined_list.append(m_copy)
        
    final_mesh = trimesh.util.concatenate(combined_list)
    scene.add_geometry(final_mesh)
    
    # 邊界檢核邏輯
    b = final_mesh.bounds
    is_over = (b[0][0] < -w_l/2 or b[1][0] > w_l/2 or b[0][1] < -d_l/2 or b[1][1] > d_l/2 or b[1][2] > h_l/2)
    
    scene.add_geometry(create_preform_wireframe(w_l, d_l, h_l, is_over))
    return base64.b64encode(scene.export(file_type='glb')).decode(), is_over

# --- 5. 左側 Preform 控制面板 ---
with st.sidebar:
    st.image("https://formlabs.com/favicon.ico", width=30)
    st.title("Preform 專家模式")
    
    # 功能 4 & 5: 輸入與上傳
    with st.container():
        st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
        st.subheader("⌨️ 手動估價")
        m_unit = st.radio("單位", ["mm³", "cm³ (ml)"], horizontal=True)
        manual_v = st.number_input("輸入體積值", min_value=0.0, step=100.0)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
        st.subheader("📂 上傳 STL")
        up_file = st.file_uploader("選擇模型", type=["stl"])
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    m_choice = st.selectbox("Formlabs 材料", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("列印機型", list(PRINTERS.keys()))
    qty = st.number_input("副本數量 (Array)", min_value=1, value=1)
    markup = st.number_input("報價倍率 (Margin)", min_value=1.0, value=2.0)
    min_t = st.slider("薄度偵測門檻 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 6. 主頁面：報價與 Preform 交互 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

if manual_v > 0 or up_file:
    st.title("💰 SLA 報價預檢終端")
    
    # 體積計算基準
    calc_vol = 0
    if up_file:
        if st.session_state.fname != up_file.name:
            st.session_state.mesh = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
            st.session_state.fname = up_file.name
            st.session_state.offset = [0.0, 0.0]
        calc_vol = st.session_state.mesh.volume
    else:
        calc_vol = manual_v if m_unit == "mm³" else manual_v * 1000

    # 價格計算
    total_price = (calc_vol * u_cost * markup * qty) + (200 * qty)
    st.markdown(f"建議報價：<span class='price-result'>NT$ {total_price:,.0f}</span>", unsafe_allow_html=True)
    
    # 價格下方數據細節 (Requirement 7)
    d1, d2, d3 = st.columns(3)
    with d1: st.markdown(f'<div class="data-card"><div class="data-label">單件體積</div><div class="data-value">{calc_vol:,.1f} mm³</div></div>', unsafe_allow_html=True)
    with d2: st.markdown(f'<div class="data-card"><div class="data-label">材料連動</div><div class="data-value">{m_choice}</div></div>', unsafe_allow_html=True)
    with d3: st.markdown(f'<div class="data-card"><div class="data-label">材料消耗</div><div class="data-value">{calc_vol*qty/1000:,.2f} ml</div></div>', unsafe_allow_html=True)

    if up_file:
        st.divider()
        # Preform 操作工具欄 (Requirement 5)
        st.subheader("🕹️ Preform 操作介面")
        t_col1, t_col2 = st.columns([1, 2])
        
        with t_col1:
            if st.button("✨ 自動最佳擺放 (SLA 45°)"):
                # SLA 最佳 45 度擺放減少拉力
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot)
                st.rerun()
            if st.button("🔴 執行最小薄度偵測"):
                tree = cKDTree(st.session_state.mesh.triangles_center)
                v_colors = np.full((len(st.session_state.mesh.vertices), 4), [200, 200, 200, 255], dtype=np.uint8)
                for i, (v, n) in enumerate(zip(st.session_state.mesh.vertices, st.session_state.mesh.vertex_normals)):
                    d, idx = tree.query(v, k=5)
                    for dist, f_idx in zip(d, idx):
                        if np.dot(n, st.session_state.mesh.face_normals[f_idx]) < -0.5 and dist < min_t:
                            v_colors[i] = [255, 0, 0, 255]
                            break
                st.session_state.mesh.visual.vertex_colors = v_colors
                st.success(f"低於 {min_t}mm 區域已標示紅色")

        with t_col2:
            st.caption("手動操控：移動物件與旋轉")
            ctrl_c1, ctrl_c2, ctrl_c3, ctrl_c4, ctrl_c5 = st.columns(5)
            if ctrl_c1.button("⬅️ X-"): st.session_state.offset[0] -= 10; st.rerun()
            if ctrl_c2.button("➡️ X+"): st.session_state.offset[0] += 10; st.rerun()
            if ctrl_c3.button("⬆️ Y+"): st.session_state.offset[1] += 10; st.rerun()
            if ctrl_c4.button("⬇️ Y-"): st.session_state.offset[1] -= 10; st.rerun()
            if ctrl_c5.button("🔄 旋轉"): 
                st.session_state.mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(45), [0, 0, 1]))
                st.rerun()

        # 3D 同步預覽渲染
        b64, over = render_preform_scene(st.session_state.mesh, PRINTERS[p_choice], qty, 
                                         st.session_state.offset[0], st.session_state.offset[1])
        
        if over: st.error("⚠️ 警告：物件已超出列印邊框！請調整位置或減少數量。")
        
        html_viewer = f"""
            <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate 
                exposure="1.0" shadow-intensity="2" environment-image="neutral"
                style="width:100%; height:600px; background-color: #f1f5f9; border-radius: 12px; border: 1px solid #cbd5e1;">
            </model-viewer>
        """
        st.components.v1.html(html_viewer, height=620)
else:
    st.info("💡 請在左側選單執行「手動體積輸入」或「模型上傳」以獲取專業報價。")
