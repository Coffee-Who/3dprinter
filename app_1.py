import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide")

# 2. 全域 CSS 樣式
st.markdown("""
    <style>
    [data-testid="stSidebarCollapseButton"] {
        position: fixed !important; top: 15px !important; left: 15px !important;
        z-index: 999999 !important; background-color: #1E40AF !important;
        color: white !important; border-radius: 50% !important;
        width: 48px !important; height: 48px !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.4) !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
    }
    .stApp { background-color: #FFFFFF !important; }
    div[data-testid="stFileUploader"] section { background-color: #FFFFFF !important; border: 2px dashed #CBD5E1 !important; }
    div[data-testid="stNumberInput"] input, div[data-baseweb="select"] > div {
        background-color: #1E40AF !important; color: #FFFFFF !important;
    }
    .price-result {
        display: inline-block; background-color: #FFFF00 !important;
        color: #E11D48 !important; padding: 10px 20px;
        border-radius: 8px; font-size: 38px !important;
        font-weight: 900 !important; border: 3px solid #E11D48;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 登入邏輯
if "password_correct" not in st.session_state:
    pwd = st.text_input("請輸入密碼", type="password")
    if st.button("登入"):
        if pwd == "1234": st.session_state["password_correct"] = True; st.rerun()
        else: st.error("錯誤")
    st.stop()

# 4. 資料庫
@st.cache_data
def load_materials():
    data = {
        "Formlabs": ["Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K"],
        "單價": [9975, 8500, 7500, 12000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df

# 5. 主程式
df_m = load_materials()
with st.sidebar:
    st.write("### SOLIDWIZARD")
    choice = st.radio("選單", ["💰 自動估價系統", "📏 尺寸校正計算"])

if choice == "💰 自動估價系統":
    st.title("💰 專業 3D 列印自動報價")
    input_method = st.radio("來源", ["📤 上傳 STL", "⌨️ 手動輸入"], horizontal=True)
    
    vol_mm3 = 0
    if input_method == "📤 上傳 STL":
        up_file = st.file_uploader("Upload", type=["stl"], label_visibility="collapsed")
        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue()); t_path = tmp.name
            try:
                your_mesh = mesh.Mesh.from_file(t_path)
                vol_mm3 = int(abs(your_mesh.get_mass_properties()[0]))

                # --- 🎯 專業打光渲染 (強化陰影與立體感) ---
                st.write("📦 **高對比實體預覽**")
                
                points = your_mesh.points.reshape(-1, 3)
                v1, v2, v3 = points[::3], points[1::3], points[2::3]
                vertices = np.vstack([v1, v2, v3])
                
                n = len(v1)
                i, j, k = np.arange(n), np.arange(n) + n, np.arange(n) + 2*n

                # 計算模型大小以動態調整光源位置
                max_dim = np.max(vertices.max(axis=0) - vertices.min(axis=0))

                fig = go.Figure(data=[
                    go.Mesh3d(
                        x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
                        i=i, j=j, k=k,
                        color='#D1D5DB', # 使用稍亮的灰色作為底色
                        flatshading=True, # 保持專業面感
                        # 強化光影參數
                        lighting=dict(
                            ambient=0.3,   # 降低環境光，讓陰影更深
                            diffuse=0.9,   # 強化漫反射，亮部更明顯
                            specular=1.2,  # 提高鏡面高光，產生邊緣亮點
                            roughness=0.1, # 降低粗糙度，讓光影轉折更銳利
                            fresnel=0.5
                        ),
                        # 設定主光源方向 (斜上方)
                        lightposition=dict(x=max_dim*2, y=max_dim*2, z=max_dim*5),
                        showscale=False
                    )
                ])

                fig.update_layout(
                    scene=dict(
                        xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                        aspectmode='data', 
                        bgcolor='#0F172A', # 改用深藍黑背景，更能襯托出模型的陰影與光澤
                        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)) # 預設最佳觀看視角
                    ),
                    margin=dict(l=0, r=0, b=0, t=0), height=500
                )
                st.plotly_chart(fig, use_container_width=True)

            except: st.error("解析失敗")
            finally: 
                if os.path.exists(t_path): os.remove(t_path)
    else:
        vol_mm3 = st.number_input("輸入體積 (mm³)", value=0, step=1, format="%d")

    if vol_mm3 > 0:
        st.write(f"**📐 體積:** {vol_mm3:,} mm³")
        col1, col2 = st.columns(2)
        with col1:
            m_choice = st.selectbox("1. 材料", df_m["Formlabs"].tolist())
            u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每mm3成本"].values[0]
        with col2:
            markup = st.slider("2. 利潤倍率", 0.5, 10.0, 1.0, 0.5)
            base_fee = st.number_input("3. 基本報價費 (NT$)", value=0, step=10, format="%d")

        total = (vol_mm3 * u_cost * markup) + base_fee
        st.divider()
        st.write("### 建議報價總計")
        st.markdown(f'NT$ <span class="price-result">{total:,.1f}</span>', unsafe_allow_html=True)
