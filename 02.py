import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. 網頁配置 ---
st.set_page_config(page_title="實威國際 Pro SLA 整合系統", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1E40AF; color: white; }
    .price-result { background-color: #FFFF00; color: #E11D48; padding: 10px; border-radius: 8px; font-size: 28px; font-weight: 900; border: 2px solid #E11D48; }
    .over-limit { color: #FF0000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 材料資料 (根據 GitHub 檔案整理) ---
@st.cache_data
def load_materials():
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

# --- 3. 設備規格 ---
PRINTERS = {
    "Form 4": {"w": 200.0, "d": 125.0, "h": 210.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0}
}

# --- 4. 工具函數 ---
def create_wireframe_box(w, d, h, color):
    """建立細圓柱構成的線框 (Wireframe)"""
    v = np.array([
        [-w/2, -d/2, -h/2], [w/2, -d/2, -h/2], [w/2, d/2, -h/2], [-w/2, d/2, -h/2],
        [-w/2, -d/2, h/2], [w/2, -d/2, h/2], [w/2, d/2, h/2], [-w/2, d/2, h/2]
    ])
    edges = [[0,1], [1,2], [2,3], [3,0], [4,5], [5,6], [6,7], [7,4], [0,4], [1,5], [2,6], [3,7]]
    lines = []
    for s, e in edges:
        line = trimesh.creation.cylinder(radius=0.4, segment=[v[s], v[e]])
        line.visual.face_colors = color
        lines.append(line)
    return trimesh.util.concatenate(lines)

def render_3d_pro(mesh, printer_box, qty=1):
    w_limit, d_limit, h_limit = printer_box['w'], printer_box['d'], printer_box['h']
    scene = trimesh.Scene()
    
    # 複製並排列模型
    combined_mesh = []
    spacing = mesh.extents[0] + 10 # 模型間距
    
    for i in range(qty):
        m_copy = mesh.copy()
        # 簡單橫向排列
        m_copy.apply_translation([(i - (qty-1)/2) * spacing, 0, -m_copy.bounds[0][2] - h_limit/2])
        combined_mesh.append(m_copy)
    
    final_model = trimesh.util.concatenate(combined_mesh)
    scene.add_geometry(final_model)
    
    # 檢查是否超出範圍
    is_over = any(final_model.extents[i] > [w_limit, d_limit, h_limit][i] for i in range(3))
    box_color = [255, 0, 0, 255] if is_over else [150, 150, 150, 255]
    
    box_wire = create_wireframe_box(w_limit, d_limit, h_limit, box_color)
    scene.add_geometry(box_wire)
    
    glb = scene.export(file_type='glb')
    return base64.b64encode(glb).decode(), is_over

# --- 5. 主介面 ---
with st.sidebar:
    st.title("SOLIDWIZARD")
    menu = st.radio("功能選單", ["💰 模型上傳估價", "✏️ 手動輸入尺寸估價", "📏 尺寸補償"])
    st.divider()
    p_choice = st.selectbox("切換列印設備 (框線確認)", list(PRINTERS.keys()))
    m_choice = st.selectbox("選擇列印材料", df_m["材料名稱"].tolist())
    qty = st.number_input("數量", min_value=1, value=1)
    markup = st.number_input("利潤倍率", min_value=1.0, value=2.0, step=0.5)

# 獲取材料成本
u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]

if menu == "💰 模型上傳估價":
    st.title("📤 3D模型自動估價預檢")
    up_file = st.file_uploader("上傳 STL 檔案", type=["stl"])
    
    if up_file:
        if 'raw_mesh' not in st.session_state or st.session_state.get('last_file') != up_file.name:
            st.session_state.raw_mesh = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
            st.session_state.last_file = up_file.name
        
        mesh = st.session_state.raw_mesh
        
        # 擺放方向功能按鈕
        if st.button("✨ 建議列印擺放方向 (自動旋轉 45°)"):
            rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 1, 0])
            st.session_state.raw_mesh.apply_transform(rot)
            st.rerun()

        # 計算價格
        vol = mesh.volume
        total_price = (vol * u_cost * markup * qty) + (200 * qty)
        st.markdown(f"建議總報價：<span class='price-result'>NT$ {total_price:,.0f}</span>", unsafe_allow_html=True)
        
        # 3D 預覽
        b64_data, over = render_3d_pro(mesh, PRINTERS[p_choice], qty)
        if over: st.error(f"❌ 警告：模型排列已超出 {p_choice} 可列印空間！")
        
        html = f"""<script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
                   <model-viewer src="data:model/gltf-binary;base64,{b64_data}" camera-controls auto-rotate style="width:100%; height:500px;"></model-viewer>"""
        st.components.v1.html(html, height=520)

elif menu == "✏️ 手動輸入尺寸估價":
    st.title("✏️ 手動尺寸快速估價")
    c1, c2, c3 = st.columns(3)
    x = c1.number_input("長 (X) mm", 1.0)
    y = c2.number_input("寬 (Y) mm", 1.0)
    z = c3.number_input("高 (Z) mm", 1.0)
    
    vol = x * y * z
    total_price = (vol * u_cost * markup * qty) + (200 * qty)
    
    st.info(f"計算體積：{vol:,.0f} mm³")
    st.markdown(f"建議總報價：<span class='price-result'>NT$ {total_price:,.0f}</span>", unsafe_allow_html=True)
    
    # 空間檢查
    p = PRINTERS[p_choice]
    if x > p['w'] or y > p['d'] or z > p['h']:
        st.error(f"⚠️ 尺寸超過 {p_choice} 限制！")

else:
    st.title("📏 尺寸補償計算")
    d_size = st.number_input("設計尺寸", value=20.0)
    a_size = st.number_input("實測尺寸", value=19.8)
    st.success(f"建議縮放比例：{(d_size/a_size)*100:.2f} %")
