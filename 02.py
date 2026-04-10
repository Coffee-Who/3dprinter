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
    .price-result { display: inline-block; background-color: #FFFF00; color: #E11D48; padding: 10px 20px; border-radius: 8px; font-size: 32px; font-weight: 900; border: 3px solid #E11D48; }
    .data-label { color: #475569; font-size: 14px; font-weight: bold; margin-top: 5px; }
    .data-value { color: #1E40AF; font-size: 18px; font-weight: 900; margin-bottom: 10px; }
    .sidebar-box { background-color: #f8fafc; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 完整材料資料庫 (連動 GitHub) ---
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

# --- 3. 核心 3D 邏輯 ---
def create_wireframe_box(w, d, h, color):
    v = np.array([[-w/2,-d/2,-h/2], [w/2,-d/2,-h/2], [w/2,d/2,-h/2], [-w/2,d/2,-h/2],
                  [-w/2,-d/2,h/2], [w/2,-d/2,h/2], [w/2,d/2,h/2], [-w/2,d/2,h/2]])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    cyls = [trimesh.creation.cylinder(radius=0.4, segment=[v[s], v[e]]) for s,e in edges]
    box = trimesh.util.concatenate(cyls)
    box.visual.face_colors = color
    return box

def render_preview(mesh, printer_box, qty, offset_x=0, offset_y=0):
    w_l, d_l, h_l = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    cols = int(np.ceil(np.sqrt(qty)))
    spacing = mesh.extents[0] * 1.15
    
    combined_items = []
    for i in range(qty):
        m_copy = mesh.copy()
        r, c = divmod(i, cols)
        # 預設底部中間放置 + 使用者手動位移
        tx = (c - (cols-1)/2) * spacing + offset_x
        ty = (r - (cols-1)/2) * spacing + offset_y
        tz = -h_l/2 - m_copy.bounds[0][2] # 貼齊底部
        m_copy.apply_translation([tx, ty, tz])
        combined_items.append(m_copy)
        
    final_mesh = trimesh.util.concatenate(combined_items)
    scene.add_geometry(final_mesh)
    
    # 空間檢查：檢查 Bounding Box 是否超出方框
    b = final_mesh.bounds
    is_over = (b[0][0] < -w_l/2 or b[1][0] > w_l/2 or
               b[0][1] < -d_l/2 or b[1][1] > d_l/2 or
               b[1][2] > h_l/2)
    
    box_color = [255, 0, 0, 255] if is_over else [150, 150, 150, 255]
    scene.add_geometry(create_wireframe_box(w_l, d_l, h_l, box_color))
    return base64.b64encode(scene.export(file_type='glb')).decode(), is_over

# --- 4. 左側側邊欄 ---
with st.sidebar:
    st.title("🛡️ SOLIDWIZARD 選單")
    
    # 手動輸入體積
    st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
    st.subheader("⌨️ 手動輸入估價")
    m_unit = st.radio("單位", ["mm³", "cm³ (ml)"], horizontal=True)
    manual_v = st.number_input("輸入體積", min_value=0.0, step=10.0)
    st.markdown('</div>', unsafe_allow_html=True)

    # 上傳檔案
    st.markdown('<div class="sidebar-box">', unsafe_allow_html=True)
    st.subheader("📂 上傳檔案估價")
    up_file = st.file_uploader("選擇 STL 檔案", type=["stl"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    m_choice = st.selectbox("選擇材料", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("列印設備", list(PRINTERS.keys()))
    qty = st.number_input("增加數量", min_value=1, value=1)
    markup = st.number_input("利潤倍率", min_value=1.0, value=2.0)
    min_t = st.slider("薄度偵測門檻 (mm)", 0.0, 5.0, 0.5, 0.5)

# --- 5. 主頁面邏輯 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

# 初始化 Offset
if 'offset' not in st.session_state:
    st.session_state.offset = [0.0, 0.0]

if manual_v > 0 or up_file:
    st.title("💰 SLA 報價預檢系統")
    
    calc_vol = 0
    if up_file:
        if 'mesh' not in st.session_state or st.session_state.get('fname') != up_file.name:
            st.session_state.mesh = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
            st.session_state.fname = up_file.name
            st.session_state.offset = [0.0, 0.0] # 重置位移
        calc_vol = st.session_state.mesh.volume
    else:
        calc_vol = manual_v if m_unit == "mm³" else manual_v * 1000

    total_price = (calc_vol * u_cost * markup * qty) + (200 * qty)
    st.markdown(f"建議總報價：<span class='price-result'>NT$ {total_price:,.0f}</span>", unsafe_allow_html=True)
    
    # 價格下方資料 (Requirement 7)
    d1, d2, d3 = st.columns(3)
    d1.markdown(f'<div class="data-label">單件體積</div><div class="data-value">{calc_vol:,.1f} mm³</div>', unsafe_allow_html=True)
    d2.markdown(f'<div class="data-label">使用材料</div><div class="data-value">{m_choice}</div>', unsafe_allow_html=True)
    d3.markdown(f'<div class="data-label">總消耗量</div><div class="data-value">{calc_vol*qty/1000:,.2f} ml</div>', unsafe_allow_html=True)

    if up_file:
        st.divider()
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("✨ 擺放建議 (45°旋轉)"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot)
                st.rerun()
        with c2:
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
                st.success("分析完成")
        
        with c3:
            st.write("🕹️ 模型位置微調")
            mc1, mc2, mc3 = st.columns(3)
            if mc1.button("⬅️ 左移"): st.session_state.offset[0] -= 10; st.rerun()
            if mc2.button("➡️ 右移"): st.session_state.offset[0] += 10; st.rerun()
            if mc3.button("🔄 旋轉 90°"):
                st.session_state.mesh.apply_transform(trimesh.transformations.rotation_matrix(np.radians(90), [0, 0, 1]))
                st.rerun()

        # 3D 渲染
        b64, over = render_preview(st.session_state.mesh, PRINTERS[p_choice], qty, st.session_state.offset[0], st.session_state.offset[1])
        if over: st.error("❌ 模型已超出列印範圍！框線已變紅。")
        
        html = f"""<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                   <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate style="width:100%; height:600px; background-color: #f1f5f9; border-radius: 12px;"></model-viewer>"""
        st.components.v1.html(html, height=620)
