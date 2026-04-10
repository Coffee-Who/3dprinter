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
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #1E40AF; color: white; font-weight: bold; }
    .price-result { display: inline-block; background-color: #FFFF00; color: #E11D48; padding: 10px 20px; border-radius: 8px; font-size: 30px; font-weight: 900; border: 3px solid #E11D48; }
    .metric-box { background-color: #F1F5F9; padding: 15px; border-radius: 10px; border-left: 5px solid #1E40AF; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 材料資料 (連動 GitHub 資料庫內容) ---
@st.cache_data
def load_materials():
    # 根據提供之 GitHub 內容整合
    data = {
        "材料名稱": [
            "Clear Resin V4", "Grey Resin V4", "White Resin V4", "Black Resin V4",
            "Tough 2000", "Grey Pro", "Rigid 10K", "Flexible 80A", "Elastic 50A", 
            "High Temp", "BioMed Clear", "BioMed Amber", "Castable Wax 40", "Silicone 40A"
        ],
        "單價": [6900, 6900, 6900, 6900, 8500, 7500, 12000, 9500, 9500, 11000, 13500, 13500, 15000, 18000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df

df_m = load_materials()

# --- 3. 設備與空間規格 ---
PRINTERS = {
    "Form 4": {"w": 200.0, "d": 125.0, "h": 210.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0}
}

# --- 4. 核心邏輯函數 ---

def create_wireframe_box(w, d, h, color):
    """建立精細線構框線，不遮擋物件"""
    v = np.array([
        [-w/2, -d/2, -h/2], [w/2, -d/2, -h/2], [w/2, d/2, -h/2], [-w/2, d/2, -h/2],
        [-w/2, -d/2, h/2], [w/2, -d/2, h/2], [w/2, d/2, h/2], [-w/2, d/2, h/2]
    ])
    edges = [[0,1], [1,2], [2,3], [3,0], [4,5], [5,6], [6,7], [7,4], [0,4], [1,5], [2,6], [3,7]]
    lines = []
    for s, e in edges:
        line = trimesh.creation.cylinder(radius=0.3, segment=[v[s], v[e]])
        line.visual.face_colors = color
        lines.append(line)
    return trimesh.util.concatenate(lines)

def analyze_thickness(mesh, threshold):
    """最小薄度偵測邏輯"""
    if threshold <= 0: return mesh
    color_mesh = mesh.copy()
    vertex_colors = np.full((len(color_mesh.vertices), 4), [220, 220, 220, 255], dtype=np.uint8)
    # 使用 KDTree 進行距離搜尋
    tree = cKDTree(color_mesh.triangles_center)
    for i, (vertex, v_normal) in enumerate(zip(color_mesh.vertices, color_mesh.vertex_normals)):
        dist, idx = tree.query(vertex, k=5)
        for d, f_idx in zip(dist, idx):
            if np.dot(v_normal, color_mesh.face_normals[f_idx]) < -0.4: # 對向面
                if d < threshold:
                    vertex_colors[i] = [255, 0, 0, 255] # 標示紅色
                break
    color_mesh.visual.vertex_colors = vertex_colors
    return color_mesh

def render_scene(mesh, printer_box, qty):
    """整合數量預覽與線構框線"""
    w_l, d_l, h_l = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    
    # 數量排列邏輯 (矩陣排列)
    spacing = mesh.extents[0] * 1.2
    combined = []
    for i in range(qty):
        m_copy = mesh.copy()
        # 簡單橫向排列展示
        offset = (i - (qty - 1) / 2) * spacing
        m_copy.apply_translation([offset, 0, -m_copy.bounds[0][2] - h_l/2])
        combined.append(m_copy)
    
    final_model = trimesh.util.concatenate(combined)
    scene.add_geometry(final_model)
    
    # 超限偵測
    is_over = any(final_model.extents[i] > [w_l, d_l, h_l][i] for i in range(3))
    box_color = [255, 0, 0, 255] if is_over else [100, 100, 100, 255]
    
    box_wire = create_wireframe_box(w_l, d_l, h_l, box_color)
    scene.add_geometry(box_wire)
    
    glb = scene.export(file_type='glb')
    return base64.b64encode(glb).decode(), is_over

# --- 5. 側邊欄 UI ---
with st.sidebar:
    st.image("https://www.swtc.com/images/logo.png", width=180) # 請換成實威 Logo
    st.header("⚙️ 全域設定")
    p_choice = st.selectbox("切換列印設備", list(PRINTERS.keys()))
    m_choice = st.selectbox("選擇 Formlabs 材料", df_m["材料名稱"].tolist())
    qty = st.number_input("列印數量", min_value=1, value=1)
    markup = st.number_input("利潤倍率", min_value=1.0, value=2.0, step=0.1)
    st.divider()
    st.subheader("📏 薄度偵測設定")
    min_thickness = st.slider("最小薄度門檻 (mm)", 0.0, 5.0, 0.5, 0.5)
    st.info("低於此數值之區域將在 3D 預覽中顯示為紅色。")

# --- 6. 主程式選單 ---
menu = st.tabs(["💰 模型上傳估價", "⌨️ 手動輸入估價", "📏 尺寸補償"])

u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

with menu[0]:
    st.title("📤 SLA 專家預檢報價")
    up_file = st.file_uploader("上傳 STL 檔案", type=["stl"])
    
    if up_file:
        if 'mesh' not in st.session_state or st.session_state.get('fname') != up_file.name:
            st.session_state.mesh = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
            st.session_state.fname = up_file.name

        c1, c2 = st.columns([1, 1])
        if c1.button("✨ 建議最佳擺放方向 (45° SLA)"):
            rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
            st.session_state.mesh.apply_transform(rot)
            st.rerun()
        
        if c2.button("🔍 執行最小薄度偵測"):
            st.session_state.mesh = analyze_thickness(st.session_state.mesh, min_thickness)
            st.success(f"薄度分析完成！(門檻: {min_thickness}mm)")

        # 報價與數據
        vol = st.session_state.mesh.volume
        total_price = (vol * u_cost * markup * qty) + (200 * qty)
        
        st.markdown(f"建議總報價：<span class='price-result'>NT$ {total_price:,.0f}</span>", unsafe_allow_html=True)
        
        # 3D 預覽
        b64, over = render_scene(st.session_state.mesh, PRINTERS[p_choice], qty)
        if over: st.error(f"⚠️ 警告：物件排列已超出 {p_choice} 空間！")
        
        html_code = f"""
            <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
            <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate shadow-intensity="1" exposure="1.2" style="width:100%; height:600px;"></model-viewer>
        """
        st.components.v1.html(html_code, height=620)

with menu[1]:
    st.title("⌨️ 尺寸快速估價")
    col_in = st.columns(3)
    dim_x = col_in[0].number_input("長 (X) mm", 1.0)
    dim_y = col_in[1].number_input("寬 (Y) mm", 1.0)
    dim_z = col_in[2].number_input("高 (Z) mm", 1.0)
    
    manual_vol = dim_x * dim_y * dim_z
    manual_price = (manual_vol * u_cost * markup * qty) + (200 * qty)
    
    st.markdown(f"手動估算總報價：<span class='price-result'>NT$ {manual_price:,.0f}</span>", unsafe_allow_html=True)
    
    # 簡單空間檢核
    p = PRINTERS[p_choice]
    if dim_x > p['w'] or dim_y > p['d'] or dim_z > p['h']:
        st.error(f"❌ 尺寸超過 {p_choice} 單次列印極限！")

with menu[2]:
    st.title("📏 尺寸補償計算")
    d_size = st.number_input("設計標稱尺寸 (mm)", value=20.0)
    a_size = st.number_input("實測列印尺寸 (mm)", value=19.8)
    if a_size > 0:
        ratio = (d_size / a_size) * 100
        st.success(f"建議縮放比例：{ratio:.2f} %")
