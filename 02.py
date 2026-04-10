import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
from scipy.spatial import cKDTree

# --- 1. 網頁配置與 CSS 風格 ---
st.set_page_config(page_title="實威國際 Pro SLA 系統", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background-color: #1E40AF; color: white; font-weight: bold; border: none;
    }
    .price-result { 
        display: inline-block; background-color: #FFFF00; color: #E11D48; 
        padding: 8px 16px; border-radius: 8px; font-size: 32px; font-weight: 900; border: 3px solid #E11D48; 
    }
    .over-limit { color: #FF0000; font-weight: bold; background-color: #FFEBEB; padding: 2px 5px; border-radius: 4px; }
    .safe-limit { color: #1E40AF; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 完整的 Formlabs 材料資料庫 ---
@st.cache_data
def load_materials():
    data = {
        "材料分類": ["標準", "標準", "標準", "標準", "工程", "工程", "工程", "工程", "工程", "工程", "醫療", "醫療", "珠寶", "矽膠"],
        "材料名稱": [
            "Clear Resin V4", "Grey Resin V4", "White Resin V4", "Black Resin V4",
            "Tough 2000", "Grey Pro", "Rigid 10K", "Flexible 80A", "Elastic 50A", "High Temp",
            "BioMed Clear", "BioMed Amber", "Castable Wax 40", "Silicone 40A"
        ],
        "單價": [6900, 6900, 6900, 6900, 8500, 7500, 12000, 9500, 9500, 11000, 13500, 13500, 15000, 18000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df

df_m = load_materials()

# --- 3. 設備規格資料 ---
PRINTERS = {
    "Form 4": {"w": 200.0, "d": 125.0, "h": 210.0},
    "Form 4L": {"w": 353.0, "d": 196.0, "h": 350.0}
}

# --- 4. 核心邏輯 ---
def analyze_thickness_robust(mesh, threshold):
    color_mesh = mesh.copy()
    vertex_colors = np.full((len(color_mesh.vertices), 4), [225, 225, 225, 255], dtype=np.uint8)
    tree = cKDTree(color_mesh.triangles_center)
    for i, (vertex, v_normal) in enumerate(zip(color_mesh.vertices, color_mesh.vertex_normals)):
        dist, idx = tree.query(vertex, k=5)
        for d, f_idx in zip(dist, idx):
            if np.dot(v_normal, color_mesh.face_normals[f_idx]) < -0.3:
                if d < threshold:
                    vertex_colors[i] = [255, 0, 0, 255]
                break
    color_mesh.visual.vertex_colors = vertex_colors
    return color_mesh

def render_3d_pro(mesh, printer_box, is_over_limit=False):
    # 建立設備空間線框
    w, d, h = printer_box['w'], printer_box['d'], printer_box['h']
    
    # 建立透明度極高的 Box 作為邊框參考
    box_color = [255, 0, 0, 40] if is_over_limit else [100, 100, 100, 30]
    box_geom = trimesh.creation.box(extents=[w, d, h])
    box_geom.visual.face_colors = box_color
    
    scene = trimesh.Scene()
    
    # 模型處理：置中並對齊底部
    mesh_copy = mesh.copy()
    mesh_bottom = mesh_copy.bounds[0][2]
    # 將模型移至 Box 的底平面中心 (Z 對齊 Box 底部)
    mesh_copy.apply_translation([-mesh_copy.centroid[0], -mesh_copy.centroid[1], -mesh_bottom - h/2])
    
    scene.add_geometry(mesh_copy)
    scene.add_geometry(box_geom, geom_name="printer_volume")
    
    glb_data = scene.export(file_type='glb')
    b64 = base64.b64encode(glb_data).decode()
    
    return f"""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <style> model-viewer {{ width: 100%; height: 600px; background-color: #ffffff; border-radius: 12px; }} </style>
    <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate shadow-intensity="1.5" exposure="1.3" environment-image="neutral" touch-action="pan-y"></model-viewer>
    """

# --- 5. 主程式頁面 ---
with st.sidebar:
    st.image("https://www.swtc.com/images/logo.png", width=180) # 示意用
    st.header("⚙️ 設備與預檢")
    p_choice = st.selectbox("切換列印空間確認", list(PRINTERS.keys()))
    min_wall_threshold = st.slider("最小壁厚警告門檻 (mm)", 0.1, 10.0, 0.6, 0.1)
    st.divider()
    menu = st.radio("選單", ["💰 自動估價報價", "📏 比例補償"])

if menu == "💰 自動估價報價":
    st.title(f"💰 {p_choice} 智慧報價系統")
    
    up_file = st.file_uploader("上傳 STL 檔案", type=["stl"])
    
    if up_file:
        if 'raw_mesh' not in st.session_state or st.session_state.get('last_file') != up_file.name:
            with st.spinner("模型載入中..."):
                raw = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
                # SLA 45度預設旋轉
                rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
                raw.apply_transform(rot)
                st.session_state.raw_mesh = raw
                st.session_state.display_mesh = raw.copy()
                st.session_state.last_file = up_file.name
        
        mesh = st.session_state.raw_mesh
        vol_mm3 = int(abs(mesh.volume))
        p_limit = PRINTERS[p_choice]
        
        # 1. 報價輸入區
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            m_selected = st.selectbox("1. 選擇 Formlabs 材料", df_m["材料名稱"].tolist())
        with c2:
            qty = st.number_input("2. 數量", min_value=1, value=1, step=1)
        with c3:
            markup = st.number_input("3. 利潤倍率", min_value=0.1, value=2.0, step=0.1)

        # 價格計算：(單件成本 * 數量 * 倍率) + (數量 * 處理費)
        u_cost = df_m.loc[df_m["材料名稱"] == m_selected, "每mm3成本"].values[0]
        total_price = (vol_mm3 * u_cost * qty * markup) + (200 * qty)
        
        st.markdown(f'💸 建議總報價：NT$ <span class="price-result">{total_price:,.0f}</span>', unsafe_allow_html=True)
        st.divider()

        # 2. 空間尺寸檢查
        bounds = mesh.extents # 獲取模型的寬、深、高
        is_over = any(bounds[i] > list(p_limit.values())[i] for i in range(3))
        
        st.subheader("📏 列印空間校驗")
        dim_cols = st.columns(3)
        dims = ['w', 'd', 'h']
        labels = ['寬 (X)', '深 (Y)', '高 (Z)']
        for i, d in enumerate(dims):
            val = bounds[i]
            limit = p_limit[d]
            style = "over-limit" if val > limit else "safe-limit"
            dim_cols[i].markdown(f"{labels[i]}: <span class='{style}'>{val:.1f} / {limit} mm</span>", unsafe_allow_html=True)
        
        if is_over:
            st.error(f"❌ 警告：模型尺寸超出 {p_choice} 的列印包絡範圍！")

        # 3. 3D 渲染
        if st.button("🔍 執行最小壁厚檢查"):
            with st.spinner("分析中..."):
                st.session_state.display_mesh = analyze_thickness_robust(mesh, min_wall_threshold)
        
        st.components.v1.html(render_3d_pro(st.session_state.display_mesh, p_limit, is_over), height=620)

else:
    st.title("📏 尺寸補償計算")
    # ... 比例補償代碼保持不變
