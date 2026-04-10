import streamlit as st
import pandas as pd
import trimesh
import numpy as np
import io
import base64
import os
import tempfile
from scipy.spatial import cKDTree

# --- 1. 頁面配置與 CSS 風格 ---
st.set_page_config(page_title="實威國際 3D列印專業報價預檢系統", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    /* 專業按鈕樣式 */
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background-color: #1E40AF; color: white; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #1e3a8a; border: none; }
    /* 報價結果樣式 */
    .price-result { 
        display: inline-block; background-color: #FFFF00 !important; color: #E11D48 !important; 
        padding: 8px 16px; border-radius: 8px; font-size: 32px !important; font-weight: 900 !important; border: 3px solid #E11D48; 
    }
    /* 側邊欄縮小元件 */
    div[data-testid="stNumberInput"], div[data-baseweb="select"], .stSlider { 
        max-width: 100% !important; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 材料資料庫 ---
@st.cache_data
def load_materials():
    data = {
        "材料名稱": [
            "Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K", 
            "Flexible 80A", "Elastic 50A", "High Temp", "Draft Resin",
            "White Resin", "Grey Resin", "Black Resin", "Model Resin"
        ],
        "單價": [9975, 8500, 7500, 12000, 9500, 9500, 11000, 8000, 7500, 7500, 7500, 8500]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df
df_m = load_materials()

# --- 3. 核心邏輯：壁厚分析與支撐生成 ---
def analyze_thickness_robust(mesh, threshold):
    color_mesh = mesh.copy()
    base_color = [225, 225, 225, 255] # 淺灰
    red_color = [255, 0, 0, 255]      # 警示紅
    vertex_colors = np.full((len(color_mesh.vertices), 4), base_color, dtype=np.uint8)
    
    tree = cKDTree(color_mesh.triangles_center)
    for i, (vertex, v_normal) in enumerate(zip(color_mesh.vertices, color_mesh.vertex_normals)):
        dist, idx = tree.query(vertex, k=8)
        actual_thickness = 100.0
        found_back = False
        for d, f_idx in zip(dist, idx):
            if np.dot(v_normal, color_mesh.face_normals[f_idx]) < -0.3:
                actual_thickness = d
                found_back = True
                break
        if found_back and actual_thickness < threshold:
            vertex_colors[i] = red_color
    color_mesh.visual.vertex_colors = vertex_colors
    return color_mesh

def generate_supports(mesh, density, touch_size):
    z_min = mesh.bounds[0][2]
    raft_z_top = z_min - 5
    overhang_indices = np.where(mesh.face_normals[:, 2] < -0.5)[0]
    if len(overhang_indices) == 0: return None
    overhang_mesh = mesh.submesh([overhang_indices], append=True)
    points = overhang_mesh.sample(max(20, int(overhang_mesh.area * (density / 100))))
    supports = []
    for p in points:
        height = p[2] - raft_z_top
        cyl = trimesh.creation.cylinder(radius=touch_size/2, height=height)
        cyl.apply_translation([p[0], p[1], raft_z_top + height/2])
        cyl.visual.face_colors = [0, 102, 204, 120] # 半透明藍
        supports.append(cyl)
    return trimesh.util.concatenate(supports) if supports else None

# --- 4. 專業 3D 渲染器 ---
def render_3d_pro(mesh):
    glb_data = mesh.export(file_type='glb')
    b64 = base64.b64encode(glb_data).decode()
    return f"""
    <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
    <style> model-viewer {{ width: 100%; height: 600px; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }} </style>
    <model-viewer src="data:model/gltf-binary;base64,{b64}" camera-controls auto-rotate rotation-per-second="20deg" shadow-intensity="1.5" shadow-softness="0.5" exposure="1.3" environment-image="neutral" touch-action="pan-y"></model-viewer>
    """

# --- 5. 側邊欄與選單 ---
with st.sidebar:
    st.image("https://www.swtc.com/images/logo.png", width=200) # 假設的Logo
    st.header("🛠️ 系統功能")
    choice = st.radio("功能選單：", ["💰 自動估價與預檢", "📏 尺寸補償計算"])
    st.divider()
    if choice == "💰 自動估價與預檢":
        st.subheader("分析設定")
        min_wall_threshold = st.slider("最小壁厚警告門檻 (mm)", 0.1, 10.0, 0.6, 0.1)
        st.divider()
        st.subheader("支撐模擬")
        support_density = st.slider("支撐密度", 1.0, 5.0, 2.0)
        touchpoint_size = st.slider("接觸點直徑 (mm)", 0.3, 1.2, 0.6)

# --- 6. 主程式流程 ---
if choice == "💰 自動估價與預檢":
    st.title("💰 3D列印自動報價與專業預檢")
    
    input_method = st.radio("體積來源：", ["📤 上傳模型 (STL)", "⌨️ 手動輸入"], horizontal=True)
    vol_mm3 = 0
    
    if input_method == "📤 上傳模型 (STL)":
        up_file = st.file_uploader("Upload", type=["stl"], label_visibility="collapsed")
        if up_file:
            if 'raw_mesh' not in st.session_state or st.session_state.get('last_file') != up_file.name:
                with st.spinner("📦 幾何數據解析中..."):
                    raw = trimesh.load(io.BytesIO(up_file.read()), file_type='stl')
                    rot = trimesh.transformations.rotation_matrix(np.radians(45), [1, 0, 0])
                    raw.apply_transform(rot)
                    st.session_state.raw_mesh = raw
                    st.session_state.display_mesh = raw.copy()
                    st.session_state.last_file = up_file.name
            
            mesh = st.session_state.raw_mesh
            vol_mm3 = int(abs(mesh.volume))
            
            # --- 報價計算顯示 ---
            m_choice = st.selectbox("1. 選擇列印材料", df_m["材料名稱"].tolist())
            u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]
            pure_cost = vol_mm3 * u_cost
            
            col_m1, col_m2 = st.columns(2)
            markup = col_m1.slider("2. 利潤倍率", 0.5, 10.0, 2.0, 0.5)
            base_fee = col_m2.number_input("3. 基本費 (NT$)", min_value=0, value=200)
            
            total_price = (pure_cost * markup) + base_fee
            st.markdown(f'💸 建議報價：NT$ <span class="price-result">{total_price:,.1f}</span>', unsafe_allow_html=True)
            
            # --- 3D 預檢區 ---
            st.divider()
            col_b1, col_b2 = st.columns([1, 2])
            if col_b1.button("🔍 執行壁厚檢查 (紅色標示)"):
                with st.spinner("正在分析壁厚..."):
                    st.session_state.display_mesh = analyze_thickness_robust(mesh, min_wall_threshold)
            
            show_supp = st.checkbox("顯示模擬支撐架", value=True)
            preview_mesh = st.session_state.display_mesh.copy()
            if show_supp:
                supp = generate_supports(mesh, support_density, touchpoint_size)
                if supp: preview_mesh = trimesh.util.concatenate([preview_mesh, supp])
            
            st.components.v1.html(render_3d_pro(preview_mesh), height=620)
            
            # 數據看板
            c1, c2, c3 = st.columns(3)
            c1.metric("預估體積", f"{vol_mm3/1000:.2f} ml")
            c2.metric("材料成本", f"NT$ {pure_cost:,.1f}")
            c3.metric("結構狀態", "✅ 水密" if mesh.is_watertight else "⚠️ 破面")

    else:
        vol_mm3 = st.number_input("輸入模型體積 (mm³)：", min_value=0, step=100)
        if vol_mm3 > 0:
            m_choice = st.selectbox("1. 選擇列印材料", df_m["材料名稱"].tolist())
            u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]
            total_price = (vol_mm3 * u_cost * 2.0) + 200 # 預設倍率
            st.markdown(f'NT$ <span class="price-result">{total_price:,.1f}</span>', unsafe_allow_html=True)

else:
    st.title("📏 尺寸補償計算")
    d_size = st.number_input("設計尺寸 (mm)", min_value=0.1, value=20.0)
    a_size = st.number_input("實測尺寸 (mm)", min_value=0.1, value=19.8)
    res = (d_size / a_size) * 100
    st.write("### 建議縮放比例")
    st.markdown(f'<span class="price-result">{res:.2f}%</span>', unsafe_allow_html=True)
