import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
import hashlib
from scipy.spatial import cKDTree

# --- 1. PreForm 專業 UI 配置 ---
st.set_page_config(page_title="SOLIDWIZARD | PreForm AI", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e2e8f0; }
    .stButton>button { width: 100%; border-radius: 4px; font-weight: 600; background-color: #ffffff; border: 1px solid #cbd5e1; height: 38px; font-size: 13px; }
    .stButton>button:hover { background-color: #0081FF; color: white; border-color: #0081FF; }

    .price-container { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }
    .price-result { color: #1e293b; font-size: 32px; font-weight: 800; border-bottom: 2px solid #0081FF; display: inline-block; margin-bottom: 10px; }
    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
    .data-item { border-left: 3px solid #cbd5e1; padding-left: 10px; }
    .data-label { color: #64748b; font-size: 10px; font-weight: bold; text-transform: uppercase; }
    .data-value { color: #0f172a; font-size: 14px; font-weight: 700; }

    .cost-breakdown { background: #f8fafc; border-radius: 6px; padding: 12px 16px; margin-top: 12px; border: 1px solid #e2e8f0; }
    .cost-row { display: flex; justify-content: space-between; font-size: 12px; color: #475569; padding: 3px 0; }
    .cost-row.total { font-weight: 700; color: #0f172a; border-top: 1px solid #cbd5e1; margin-top: 6px; padding-top: 6px; font-size: 13px; }
    .priority-note { background: #eff6ff; color: #1d4ed8; border-left: 3px solid #3b82f6; padding: 8px 12px; font-size: 12px; border-radius: 0 4px 4px 0; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心狀態初始化 ---
if 'offset' not in st.session_state: st.session_state.offset = [0.0, 0.0]
if 'mesh' not in st.session_state: st.session_state.mesh = None
if 'mesh_hash' not in st.session_state: st.session_state.mesh_hash = ""
if 'thin_faces' not in st.session_state: st.session_state.thin_faces = None

# --- 3. 材料與設備規格定義 ---
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
        "單價": [6900, 6900, 6900, 6900, 6900, 6900, 8500, 8500, 8500, 8500, 12000, 8500,
                 9500, 9500, 11000, 12000, 12000, 13500, 13500, 13500, 13500, 13500, 13500,
                 8500, 15000, 15000, 18000, 25000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000
    return df

df_m = load_materials()

PRINTERS = {
    "Form 4":  {"w": 200.0, "d": 125.0, "h": 210.0, "layer_time_sec": 5.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0, "layer_time_sec": 6.0},
}


# --- 4. 3D 渲染核心：修復薄度顯示 + 效能優化地板 ---
def get_scene_glb(mesh, printer_box, qty, off_x, off_y, thin_faces=None):
    """
    thin_faces: set of face indices flagged as thin (red).
                Pass None for normal (blue) rendering.
    """
    w, d, h = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    cols = max(1, int(np.ceil(np.sqrt(qty))))
    spacing = mesh.extents[0] * 1.15

    instances = []
    for i in range(qty):
        m_inst = mesh.copy()

        # 修復：在 copy 後、加入 scene 前套用面顏色，確保薄度標記正確顯示
        if thin_faces is not None and len(thin_faces) > 0:
            face_colors = np.full((len(m_inst.faces), 4), [0, 129, 255, 220], dtype=np.uint8)
            valid_thin = [fi for fi in thin_faces if fi < len(m_inst.faces)]
            if valid_thin:
                face_colors[valid_thin] = [255, 50, 50, 255]
            m_inst.visual = trimesh.visual.ColorVisuals(mesh=m_inst, face_colors=face_colors)
        else:
            m_inst.visual.face_colors = [0, 129, 255, 200]

        r, c = divmod(i, cols)
        tx = (c - (cols - 1) / 2) * spacing + off_x
        ty = (r - (cols - 1) / 2) * spacing + off_y
        tz = -h / 2 - m_inst.bounds[0][2]
        m_inst.apply_translation([tx, ty, tz])
        instances.append(m_inst)

    combined = trimesh.util.concatenate(instances)
    scene.add_geometry(combined)

    # 邊界檢測
    b = combined.bounds
    is_over = (b[0][0] < -w/2 or b[1][0] > w/2 or
               b[0][1] < -d/2 or b[1][1] > d/2 or
               b[1][2] > h/2)
    box_color = [225, 29, 72, 255] if is_over else [156, 163, 175, 255]

    # 線框 Wireframe
    v = np.array([
        [-w/2, -d/2, -h/2], [w/2, -d/2, -h/2], [w/2,  d/2, -h/2], [-w/2,  d/2, -h/2],
        [-w/2, -d/2,  h/2], [w/2, -d/2,  h/2], [w/2,  d/2,  h/2], [-w/2,  d/2,  h/2]
    ])
    edges = [[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]]
    for s, e in edges:
        line = trimesh.creation.cylinder(radius=0.12, segment=[v[s], v[e]])
        line.visual.face_colors = box_color
        scene.add_geometry(line)

    # 修復：地板改用單一薄箱體取代大量圓柱，GLB 體積大幅縮小，渲染速度提升
    floor = trimesh.creation.box(extents=[w, d, 0.3])
    floor.apply_translation([0, 0, -h/2 - 0.15])
    floor.visual.face_colors = [226, 232, 240, 180]
    scene.add_geometry(floor)

    # 少量主要格線（固定 ≤ 14 條，不隨解析度爆炸）
    for xi in np.linspace(-w/2, w/2, 9):
        line = trimesh.creation.cylinder(radius=0.08, segment=[[xi, -d/2, -h/2], [xi, d/2, -h/2]])
        line.visual.face_colors = [203, 213, 225, 160]
        scene.add_geometry(line)
    for yi in np.linspace(-d/2, d/2, 7):
        line = trimesh.creation.cylinder(radius=0.08, segment=[[-w/2, yi, -h/2], [w/2, yi, -h/2]])
        line.visual.face_colors = [203, 213, 225, 160]
        scene.add_geometry(line)

    return base64.b64encode(scene.export(file_type='glb')).decode(), is_over


# --- 5. 左側導覽列 ---
with st.sidebar:
    st.image("https://formlabs.com/favicon.ico", width=20)
    st.title("PreForm 模擬報價")

    st.markdown('<div class="priority-note">📌 上傳 STL 優先；未上傳時使用手動體積估算。</div>', unsafe_allow_html=True)

    with st.container():
        st.subheader("⌨️ 手動估價")
        m_unit = st.radio("單位", ["mm³", "cm³"], horizontal=True)
        manual_v = st.number_input("體積值", min_value=0.0, step=100.0)

    with st.container():
        st.subheader("📂 上傳 STL 檔案")
        up_file = st.file_uploader("STL 檔案（優先使用）", type=["stl"])

    st.divider()
    m_choice = st.selectbox("Formlabs 材料選擇", df_m["材料名稱"].tolist())
    p_choice = st.selectbox("列印機型範圍", list(PRINTERS.keys()))
    qty = st.number_input("數量", min_value=1, value=1)
    markup = st.number_input("報價加成倍率", min_value=1.0, value=2.0)

    st.divider()
    st.subheader("⚙️ 進階設定")
    support_ratio = st.slider("支撐結構體積係數 (%)", 0, 50, 20, 5,
                               help="SLA 列印通常需要額外 15~30% 的支撐材料，會計入總用料與成本。")
    layer_thickness = st.selectbox("層厚 (mm)", [0.05, 0.1, 0.2], index=1)
    min_t_val = st.slider("薄度偵測閾值 (mm)", 0.0, 5.0, 0.5, 0.5)
    handling_fee = st.number_input("基本處理費 / 件 (NT$)", min_value=0, value=200, step=50,
                                    help="含清洗、後固化等後處理成本。")


# --- 6. 主畫面報價與 3D 交互 ---
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]
printer_spec = PRINTERS[p_choice]

# 修復：用 MD5 hash 判斷檔案是否真的改變，避免同名不同檔案的 bug
if up_file:
    file_bytes = up_file.read()
    file_hash = hashlib.md5(file_bytes).hexdigest()
    if st.session_state.mesh_hash != file_hash:
        st.session_state.mesh = trimesh.load(io.BytesIO(file_bytes), file_type='stl')
        st.session_state.mesh_hash = file_hash
        st.session_state.offset = [0.0, 0.0]
        st.session_state.thin_faces = None  # 新檔案清除舊偵測結果

use_stl = up_file and st.session_state.mesh is not None
use_manual = not use_stl and manual_v > 0

if use_stl or use_manual:
    if use_stl:
        model_vol = st.session_state.mesh.volume
    else:
        model_vol = manual_v if m_unit == "mm³" else manual_v * 1000

    # 修復：成本透明化，支撐結構、後處理費、加成分開顯示
    support_vol = model_vol * (support_ratio / 100)
    total_vol_per_unit = model_vol + support_vol
    material_cost_total = total_vol_per_unit * u_cost * qty
    handling_total = handling_fee * qty
    subtotal = material_cost_total + handling_total
    final_price = subtotal * markup

    # 列印時間估算（依零件高度 ÷ 層厚）
    if use_stl:
        model_h = st.session_state.mesh.extents[2]
    else:
        model_h = model_vol ** (1/3)  # 近似立方根高度
    n_layers = int(np.ceil(model_h / layer_thickness))
    print_time_min = (n_layers * printer_spec["layer_time_sec"]) / 60

    st.markdown(f"""
    <div class="price-container">
        <div style="font-size: 13px; color: #64748b; font-weight: bold; margin-bottom: 4px;">PREFORM 預估總列印成本</div>
        <div class="price-result">NT$ {final_price:,.0f}</div>
        <div class="data-grid">
            <div class="data-item"><div class="data-label">模型體積</div><div class="data-value">{model_vol:,.1f} mm³</div></div>
            <div class="data-item"><div class="data-label">使用材料</div><div class="data-value">{m_choice}</div></div>
            <div class="data-item"><div class="data-label">含支撐消耗 (mL)</div><div class="data-value">{total_vol_per_unit * qty / 1000:,.2f}</div></div>
            <div class="data-item"><div class="data-label">列印機型</div><div class="data-value">{p_choice}</div></div>
            <div class="data-item"><div class="data-label">預估列印時間</div><div class="data-value">≈ {print_time_min:.0f} 分鐘</div></div>
            <div class="data-item"><div class="data-label">層數（層厚 {layer_thickness}mm）</div><div class="data-value">{n_layers:,} 層</div></div>
        </div>
        <div class="cost-breakdown">
            <div class="cost-row">
                <span>材料費（模型 + 支撐 {support_ratio}%，共 {total_vol_per_unit/1000:.2f} mL/件）× {qty} 件</span>
                <span>NT$ {material_cost_total:,.0f}</span>
            </div>
            <div class="cost-row">
                <span>後處理基本費（NT$ {handling_fee}/件，含清洗＋後固化）× {qty} 件</span>
                <span>NT$ {handling_total:,.0f}</span>
            </div>
            <div class="cost-row"><span>小計</span><span>NT$ {subtotal:,.0f}</span></div>
            <div class="cost-row total"><span>× 加成倍率 {markup}x　→　最終報價</span><span>NT$ {final_price:,.0f}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- 3D 操作區（STL 模式才顯示）---
    if use_stl:
        st.divider()
        col_tool, col_view = st.columns([1, 3])

        with col_tool:
            st.write("🕹️ 零件操作")

            if st.button("✨ SLA 45° 擺放建議"):
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
                st.session_state.mesh.apply_transform(rot)
                st.session_state.thin_faces = None
                st.rerun()

            # 修復：偵測結果儲存於 session_state，渲染時才套用顏色，兩條流程互不干擾
            if st.button("🔴 薄度偵測分析"):
                mesh = st.session_state.mesh
                tree = cKDTree(mesh.triangles_center)
                thin_set = set()
                for fi, (center, normal) in enumerate(zip(mesh.triangles_center, mesh.face_normals)):
                    dists, idxs = tree.query(center, k=6)
                    for dist, neighbor_fi in zip(dists[1:], idxs[1:]):
                        if dist < min_t_val and np.dot(normal, mesh.face_normals[neighbor_fi]) < -0.5:
                            thin_set.add(fi)
                            break
                st.session_state.thin_faces = thin_set
                if len(thin_set) > 0:
                    st.warning(f"⚠️ 偵測到 {len(thin_set)} 個薄壁面（< {min_t_val}mm），已標紅。")
                else:
                    st.success(f"✅ 無薄壁問題（閾值 {min_t_val}mm）")

            if st.button("🔵 清除薄度標記"):
                st.session_state.thin_faces = None
                st.rerun()

            st.write("📏 X/Y 平面位置調整")
            c1, c2 = st.columns(2)
            if c1.button("⬅️ X-"): st.session_state.offset[0] -= 10; st.rerun()
            if c2.button("➡️ X+"): st.session_state.offset[0] += 10; st.rerun()
            c3, c4 = st.columns(2)
            if c3.button("⬆️ Y+"): st.session_state.offset[1] += 10; st.rerun()
            if c4.button("⬇️ Y-"): st.session_state.offset[1] -= 10; st.rerun()

            if st.button("🔄 旋轉物件 90°"):
                st.session_state.mesh.apply_transform(
                    trimesh.transformations.rotation_matrix(np.radians(90), [0, 0, 1])
                )
                st.session_state.thin_faces = None
                st.rerun()

            if st.button("🏠 重置位置"):
                st.session_state.offset = [0.0, 0.0]
                st.rerun()

        with col_view:
            thin_label = f"｜<span style='color:#ef4444;font-weight:600;'>🔴 薄壁標記顯示中（{len(st.session_state.thin_faces)} 面）</span>" \
                         if st.session_state.thin_faces else ""

            glb_b64, over = get_scene_glb(
                st.session_state.mesh,
                printer_spec,
                qty,
                st.session_state.offset[0],
                st.session_state.offset[1],
                thin_faces=st.session_state.thin_faces
            )
            if over:
                st.error("⚠️ 零件超出設備列印範圍！框線已標紅。")

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
                    等角方位視圖 | 滑鼠拖曳：旋轉視角 | 左側按鈕：操作零件移動{thin_label}
                </div>
            """, height=630)

else:
    st.info("💡 請上傳 STL 模型（左側），或手動輸入體積，開始 PreForm 專業模擬。")
    st.markdown("""
    **使用說明：**
    - 📂 **上傳 STL**：自動計算體積，支援 3D 排版與薄度偵測（優先使用）
    - ⌨️ **手動輸入**：僅輸入體積時使用，適合快速估算
    - ⚙️ **進階設定**：可調整支撐係數、層厚、後處理費用
    """)
