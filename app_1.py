import streamlit as st
import pandas as pd
from stl import mesh
import trimesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面配置
st.set_page_config(page_title="實威國際 3D列印報價", layout="wide")

# 2. 登入狀態檢測與全域 CSS (黑底白字登入)
if "password_correct" not in st.session_state:
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A !important; }
        h2, p, label { color: #FFFFFF !important; }
        div[data-testid="stTextInput"] input {
            background-color: #1E293B !important; color: #FFFFFF !important;
            border: 2px solid #334155 !important; border-radius: 8px !important;
        }
        div.stButton > button {
            background-color: #1E40AF !important; color: #FFFFFF !important;
            width: 100% !important; height: 50px !important; font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>SOLIDWIZARD</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 6, 1])
    with col_m:
        pwd = st.text_input("管理員密碼", type="password")
        if st.button("確認登入"):
            if pwd == "1234": 
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("密碼錯誤")
    st.stop()

# --- 進入系統後的 CSS (白底 + 藍底上傳) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }
    div[data-testid="stNumberInput"], div[data-baseweb="select"], div[data-testid="stFileUploader"] { max-width: 280px !important; }
    div[data-testid="stFileUploader"] section { 
        background-color: #1E40AF !important; color: #FFFFFF !important; 
        border-radius: 10px !important; padding: 8px !important; 
    }
    div[data-testid="stFileUploader"] section * { color: #FFFFFF !important; fill: #FFFFFF !important; }
    div[data-testid="stMarkdownContainer"] p { color: #000000 !important; font-weight: 500 !important; }
    [data-testid="stSidebarCollapseButton"] { 
        position: fixed !important; top: 15px !important; left: 15px !important; 
        z-index: 999999 !important; background-color: #1E40AF !important; color: #FFFFFF !important; border-radius: 50% !important; 
    }
    div[data-testid="stNumberInput"] input, div[data-baseweb="select"] > div { 
        background-color: #1E40AF !important; color: #FFFFFF !important; 
        -webkit-text-fill-color: #FFFFFF !important; height: 38px !important; 
    }
    .price-result { 
        display: inline-block; background-color: #FFFF00 !important; color: #E11D48 !important; 
        padding: 8px 16px; border-radius: 8px; font-size: 32px !important; 
        font-weight: 900 !important; border: 3px solid #E11D48; 
    }
    </style>
""", unsafe_allow_html=True)

# 3. 資料庫與材料
@st.cache_data
def load_materials():
    data = {"Formlabs": ["Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K"], "單價": [9975, 8500, 7500, 12000]}
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df
df_m = load_materials()

# 4. 側邊欄
with st.sidebar:
    st.write("### SOLIDWIZARD")
    choice = st.radio("功能選單", ["💰 自動估價系統", "📏 尺寸校正計算"])
    if st.button("登出系統"):
        del st.session_state["password_correct"]
        st.rerun()

# 5. 主程式
if choice == "💰 自動估價系統":
    st.title("💰 3D列印報價")
    input_method = st.radio("體積來源", ["📤 上傳 STL/STEP", "⌨️ 手動輸入"], horizontal=True)
    
    vol_mm3 = 0
    if input_method == "📤 上傳 STL/STEP":
        up_file = st.file_uploader("Upload", type=["stl", "step", "stp"], label_visibility="collapsed")
        if up_file:
            ext = os.path.splitext(up_file.name)[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            try:
                if ext == ".stl":
                    your_mesh = mesh.Mesh.from_file(t_path)
                    vol_mm3 = int(abs(your_mesh.get_mass_properties()[0]))
                    vertices_raw = your_mesh.points.reshape(-1, 3)
                else:
                    # --- 💥 修正後的 STEP 讀取邏輯 ---
                    # 載入 STEP (依賴 cascadio)
                    loaded = trimesh.load(t_path)
                    
                    # 確保將 Scene 合併成單一 Mesh
                    if isinstance(loaded, trimesh.Scene):
                        full_mesh = loaded.dump(concatenate=True)
                    else:
                        full_mesh = loaded
                    
                    # 使用絕對值體積，解決法線反向問題
                    vol_mm3 = int(abs(full_mesh.volume))
                    
                    # 保底機制：若體積無效，嘗試凸包計算
                    if vol_mm3 <= 0:
                        vol_mm3 = int(full_mesh.convex_hull.volume)
                    
                    vertices_raw = full_mesh.vertices[full_mesh.faces].reshape(-1, 3)

                # 顯示預覽
                st.write(f"📦 **模型預覽 ({ext.upper()})**")
                v1, v2, v3 = vertices_raw[::3], vertices_raw[1::3], vertices_raw[2::3]
                vertices = np.vstack([v1, v2, v3])
                n = len(v1); i, j, k = np.arange(n), np.arange(n) + n, np.arange(n) + 2*n
                mid_point = (vertices.max(axis=0) + vertices.min(axis=0)) / 2
                max_dim = np.max(vertices.max(axis=0) - vertices.min(axis=0))

                fig = go.Figure(data=[go.Mesh3d(x=vertices[:,0], y=vertices[:,1], z=vertices[:,2], i=i, j=j, k=k, color='#D1D5DB', lighting=dict(ambient=0.1, diffuse=0.9, specular=1.5))])
                fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='#0F172A'), margin=dict(l=0, r=0, b=0, t=0), height=350)
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"解析失敗：{e}")
                st.info("💡 提示：讀取 STEP 需確保環境已安裝 'cascadio' 套件。")
            finally: 
                if os.path.exists(t_path): os.remove(t_path)
    else:
        vol_mm3 = st.number_input("輸入體積 (mm³)", value=0, step=1, format="%d")

    # 顯示估價區塊
    if vol_mm3 > 0:
        st.success(f"✅ 偵測體積：{vol_mm3:,} mm³")
        m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
        u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每mm3成本"].values[0]
        markup = st.slider("2. 利潤倍率", 0.5, 10.0, 1.0, 0.5)
        base_fee = st.number_input("3. 基本費 (NT$)", min_value=0, value=0, step=10, format="%d")

        total_price = (vol_mm3 * u_cost * markup) + base_fee
        st.divider()
        st.write("### 建議報價總計")
        st.markdown(f'NT$ <span class="price-result">{total_price:,.1f}</span>', unsafe_allow_html=True)

elif choice == "📏 尺寸校正計算":
    st.title("📏 尺寸補償")
    d_size = st.number_input("設計尺寸 (mm)", value=20.0, step=0.1)
    a_size = st.number_input("實測尺寸 (mm)", value=19.8, step=0.1)
    if d_size > 0:
        res = (d_size / a_size) * 100
        st.write("### 建議縮放比例")
        st.markdown(f'<span class="price-result">{res:.2f}%</span>', unsafe_allow_html=True)
