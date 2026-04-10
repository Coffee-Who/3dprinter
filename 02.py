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
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; background-color: #1E40AF; color: white; border: none; }
    .stButton>button:hover { background-color: #3b82f6; }
    .price-result { display: inline-block; background-color: #FFFF00; color: #E11D48; padding: 12px 24px; border-radius: 8px; font-size: 34px; font-weight: 900; border: 3px solid #E11D48; }
    .data-label { color: #64748b; font-size: 14px; font-weight: bold; margin-top: 8px; }
    .data-value { color: #1E40AF; font-size: 18px; font-weight: 800; margin-bottom: 12px; }
    .sidebar-box { background-color: #f1f5f9; padding: 18px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #e2e8f0; }
    .control-label { font-size: 12px; color: #475569; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 完整材料資料庫 ---
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

# --- 3. 初始化 Session State ---
if 'offset' not in st.session_state: st.session_state.offset = [0.0, 0.0]
if 'rotation_y' not in st.session_state: st.session_state.rotation_y = 0.0

# --- 4. 核心 3D 邏輯 ---
def create_wireframe_box(w, d, h, color):
    v = np.array([[-w/2,-d/2,-h/2], [w/2,-d/2,-h/2], [w/2,d/2,-h/2], [-w/2,d/2,-h/2],
                  [-w/2,-d/2,h/2], [w/2,-d/2,h/2], [w/2,d/2,h/2], [-w/2,d/2,h/2]])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    cyls = [trimesh.creation.cylinder(radius=0.4, segment=[v[s], v[e]]) for s,e in edges]
    box = trimesh.util.concatenate(cyls)
    box.visual.face_colors = color
    return box

def render_scene(mesh, printer_box, qty, off_x, off_y):
    w_l, d_l, h_l = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.15
    
    items = []
    for i in range(qty):
        m_copy = mesh.copy()
        r, c = divmod(i, cols)
        tx = (c - (cols-1)/2) * spacing + off_x
        ty = (r - (cols-1)/2) * spacing + off_y
        tz = -h_l/2 - m_copy.bounds[0][2] # 底部對齊
        m_copy.apply_translation([tx, ty, tz])
        items.append(m_copy)
        
    final_mesh = trimesh.util.concatenate(items)
    scene.add_geometry(final_mesh)
    
    # 空間邊界檢查
    b = final_mesh.bounds
    is_over = (b[0][0] < -w_l/2 or b[1][0] > w_l/2 or b[0][1] < -d_l/2 or b[1][1] > d_l/2 or b[1][2] > h_l/2)
    
    box_color = [255, 0, 0, 255] if is_over else [100, 100, 100, 255]
    scene.add_geometry(create_wireframe_box(w_l, d_l, h_l, box_color))
    return base64.b64encode(scene.export(file_type='glb')).decode(), is_over

# --- 5. 左側側邊欄：功能選單 ---
with st.sidebar:
    st.title("🛡️ SOLIDWIZARD 專家選單")
    
    # 手動輸入估價
    st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
    st.subheader("⌨️ 手動輸入估價")
    m_unit = st.radio("單位", ["mm³", "cm³ (ml)"], horizontal=True)
    manual_v = st.number_input("輸入體積", min_value=0.0, step=10.0)
    st.markdown('</div>', unsafe_allow_html=True)

    # 上傳檔案估價
    st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
    st.subheader("📂 上傳檔案估價")
    up_file = st.file_uploader("選擇 STL 檔案", type=["stl"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    m_choice = st.selectbox("Formlabs 材料選擇", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("列印範圍 (機型)", list(PRINTERS.keys()))
    qty = st.number_input("列印數量 (陣列預覽)", min_value=1, value=1)
    markup = st.number_input("利潤加價倍率", min_value=1.0, value=2.0)
    min_t = st.slider("最小薄度偵測門檻 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 6. 主頁面報價與 3D 預覽 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

if manual_v > 0 or up_file:
    st.title("💰 SLA 自動報價與空間預檢")
    
    calc_vol = 0
    if up_file:
        if 'mesh' not in st.session_state or st.session_state.get('fname') != up_file.name:
            st.session_state.mesh = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
            st.session_state.fname = up_file.name
            st.session_state.offset = [0.0, 0.0]
        calc_vol = st.session_state.mesh.volume
    else:
        calc_vol = manual_v if m_unit == "mm³" else manual_v * 1000

    total_price = (calc_vol * u_cost * markup * qty) + (200 * qty)
    st.markdown(f"建議總報價：<span class='price-result'>NT$ {total_price:,.0f}</span>", unsafe_allow_html=True)
    
    # 資料顯示區
    d1, d2, d3 = st.columns(3)
    d1.markdown(f'<div class="data-label">單件體積</div><div class="data-value">{calc_vol:,.1f} mm³</div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="data-label">使用材料</div><div class="data-value">{m_choice}</div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="data-label">總消耗材料</div><div class="data-value">{calc_vol*qty/1000:,.2f} ml</div>', unsafe_allow_html=True)

    if up_file:
        st.divider()
        # PreForm 交互控制區
        c_auto, c_move = st.columns([1, 2])
        with c_auto:
            st.write("🤖 自動化工具")
            if st.button("✨ 最佳擺放方向 (45° 斜角)"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot)
                st.rerun()
            if st.button("🔴 執行薄度偵測"):
                tree = cKDTree(st.session_state.mesh.triangles_center)
                v_colors = np.full((len(st.session_state.mesh.vertices), 4), [220, 220, 220, 255], dtype=np.uint8)
                for i, (v, n) in enumerate(zip(st.session_state.mesh.vertices, st.session_state.mesh.vertex_normals)):
                    d, idx = tree.query(v, k=5)
                    for dist, f_idx in zip(d, idx):
                        if np.dot(n, st.session_state.mesh.face_normals[f_idx]) < -0.5 and dist < min_t:
                            v_colors[i] = [255, 0, 0, 255]
                            break
                st.session_state.mesh.visual.vertex_colors = v_colors
                st.success(f"低於 {min_t}mm 區域已標紅")

        with c_move:
            st.write("🕹️ PreForm 物件操控")
            mc1, mc2, mc3, mc4 = st.columns(4)
            if mc1.button("⬅️ X 軸左移"): st.session_state.offset[0] -= 10; st.rerun()
            if mc2.button("➡️ X 軸右移"): st.session_state.offset[0] += 10; st.rerun()
            if mc3.button("⬆️ Y 軸前移"): st.session_state.offset[1] += 10; st.rerun()
            if mc4.button("⬇️ Y 軸後移"): st.session_state.offset[1] -= 10; st.rerun()
            
            rc1, rc2 = st.columns(2)
            if rc1.button("🔄 水平旋轉 45°"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [0, 0, 1])
                st.session_state.mesh.apply_transform(rot); st.rerun()
            if rc2.button("🧹 重置位置"):
                st.session_state.offset = [0.0, 0.0]; st.rerun()

        # 3D 陣列同步預覽與框線
        b64, over = render_scene(st.session_state.mesh, PRINTERS[p_choice], qty, st.session_state.offset[0], st.session_state.offset[1])
        if over: st.error("❌ 警告：物件排列已超出列印範圍！(框線已變紅)")
        
        html_viewer = f"""
            <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate 
                exposure="1.2" shadow-intensity="1" style="width:100%; height:600px; background-color: #f8fafc; border-radius: 12px;"></model-viewer>
        """
        st.components.v1.html(html_viewer, height=620)
else:
    st.info("💡 請在左側側邊欄選擇「手動輸入體積」或「上傳 STL 檔案」來開始報價。")
