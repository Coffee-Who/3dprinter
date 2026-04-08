import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide")

# 2. 深度配色防護 CSS (解決手機版顯色異常)
st.markdown("""
    <style>
    /* 1. 強制鎖定全域背景與文字顏色 */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }

    /* 2. 手機版懸浮選單按鈕顏色鎖定 */
    [data-testid="stSidebarCollapseButton"] {
        position: fixed !important; top: 15px !important; left: 15px !important;
        z-index: 999999 !important; background-color: #1E40AF !important;
        color: #FFFFFF !important; border-radius: 50% !important;
        width: 48px !important; height: 48px !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.3) !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
    }
    [data-testid="stSidebarCollapseButton"] svg { fill: #FFFFFF !important; }

    /* 3. 上傳區塊：確保手機上也是白底黑字 */
    div[data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important; 
        color: #334155 !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 8px !important;
    }

    /* 4. 輸入框與下拉選單：強制深藍底白字 */
    div[data-testid="stNumberInput"] input, 
    div[data-baseweb="select"] > div {
        background-color: #1E40AF !important; 
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important; /* 防止手機瀏覽器改字色 */
        border-radius: 8px !important;
    }

    /* 5. 建議報價結果：黃底紅字鎖定 */
    .price-result {
        display: inline-block; 
        background-color: #FFFF00 !important;
        color: #E11D48 !important; 
        padding: 10px 20px;
        border-radius: 8px; 
        font-size: 38px !important;
        font-weight: 900 !important; 
        border: 3px solid #E11D48;
        margin: 10px 0;
    }

    /* 6. 導覽列與側邊欄文字顏色修正 */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
    }
    [data-testid="stSidebar"] * {
        color: #0F172A !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 登入邏輯
if "password_correct" not in st.session_state:
    st.markdown("<h2 style='text-align:center; color:#000000;'>實威國際 3D列印報價系統</h2>", unsafe_allow_html=True)
    pwd = st.text_input("請輸入密碼", type="password")
    if st.button("確認登入"):
        if pwd == "1234": 
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("密碼錯誤")
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
    choice = st.radio("功能選單", ["💰 自動估價系統", "📏 尺寸校正計算"])
    if st.button("登出"):
        del st.session_state["password_correct"]
        st.rerun()

if choice == "💰 自動估價系統":
    st.title("💰 專業 3D 列印自動報價")
    input_method = st.radio("體積來源", ["📤 上傳 STL", "⌨️ 手動輸入"], horizontal=True)
    
    vol_mm3 = 0
    if input_method == "📤 上傳 STL":
        up_file = st.file_uploader("Upload", type=["stl"], label_visibility="collapsed")
        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue()); t_path = tmp.name
            try:
                your_mesh = mesh.Mesh.from_file(t_path)
                vol_mm3 = int(abs(your_mesh.get_mass_properties()[0]))

                # --- 🎯 專業打光渲染 (這部分顏色是 3D 引擎控制，不隨系統變色) ---
                st.write("📦 **高解析度實體著色預覽**")
                points = your_mesh.points.reshape(-1, 3)
                v1, v2, v3 = points[::3], points[1::3], points[2::3]
                vertices = np.vstack([v1, v2, v3])
                n = len(v1)
                i, j, k = np.arange(n), np.arange(n) + n, np.arange(n) + 2*n
                mid_point = (vertices.max(axis=0) + vertices.min(axis=0)) / 2
                max_dim = np.max(vertices.max(axis=0) - vertices.min(axis=0))

                fig = go.Figure(data=[
                    go.Mesh3d(
                        x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
                        i=i, j=j, k=k,
                        color='#D1D5DB', 
                        flatshading=False, 
                        lighting=dict(ambient=0.1, diffuse=0.9, specular=1.5, roughness=0.1, fresnel=0.5),
                        lightposition=dict(x=mid_point[0]+max_dim, y=mid_point[1]+max_dim, z=mid_point[2]+max_dim),
                        showscale=False
                    )
                ])
                fig.update_layout(
                    scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                               aspectmode='data', bgcolor='#0F172A',
                               camera=dict(eye=dict(x=1.3, y=1.3, z=1.3))),
                    margin=dict(l=0, r=0, b=0, t=0), height=550
                )
                st.plotly_chart(fig, use_container_width=True)
            except: st.error("STL 解析失敗")
            finally: 
                if os.path.exists(t_path): os.remove(t_path)
    else:
        vol_mm3 = st.number_input("輸入體積 (mm³)", value=0, step=1, format="%d")

    if vol_mm3 > 0:
        st.write(f"**📐 當前模型體積:** {vol_mm3:,} mm³")
        col1, col2 = st.columns(2)
        with col1:
            m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
            u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每mm3成本"].values[0]
            st.info(f"💡 材料成本：NT$ {u_cost:.6f}/mm³")
        
        with col2:
            markup = st.slider("2. 利潤倍率調整", 0.5, 10.0, 1.0, 0.5)
            base_fee = st.number_input("3. 報價基本費 (NT$)", min_value=0, value=0, step=10, format="%d")

        mat_cost_total = vol_mm3 * u_cost
        total_price = (mat_cost_total * markup) + base_fee
        
        st.divider()
        st.write("### 建議報價總計")
        st.markdown(f'NT$ <span class="price-result">{total_price:,.1f}</span>', unsafe_allow_html=True)

elif choice == "📏 尺寸校正計算":
    st.title("📏 尺寸補償計算")
    d_size = st.number_input("CAD 設計尺寸 (mm)", value=20.0, step=0.1)
    a_size = st.number_input("實測成品尺寸 (mm)", value=19.8, step=0.1)
    if d_size > 0:
        res = (d_size / a_size) * 100
        st.write("### 建議縮放比例")
        st.markdown(f'<span class="price-result">{res:.2f}%</span>', unsafe_allow_html=True)
