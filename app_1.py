import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide")

# 2. 登入狀態檢測與全域 CSS
if "password_correct" not in st.session_state:
    # --- 登入頁面專屬黑底 CSS ---
    st.markdown("""
        <style>
        .stApp {
            background-color: #0F172A !important; /* 深黑藍背景 */
        }
        h2, label, p {
            color: #FFFFFF !important; /* 白色文字 */
        }
        /* 登入輸入框樣式 */
        div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input {
            background-color: #1E293B !important;
            color: #FFFFFF !important;
            border: 1px solid #334155 !important;
            -webkit-text-fill-color: #FFFFFF !important;
        }
        /* 登入按鈕樣式 */
        button[kind="primary"] {
            background-color: #1E40AF !important;
            color: white !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>SOLIDWIZARD</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>3D列印線上估價系統</p>", unsafe_allow_html=True)
    
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        pwd = st.text_input("管理員密碼", type="password")
        if st.button("確認登入", kind="primary"):
            if pwd == "1234": 
                st.session_state["password_correct"] = True
                st.rerun()
            else: 
                st.error("密碼錯誤，請重新輸入")
    st.stop()

# --- 進入系統後的 CSS (白底 + 精簡輸入框) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; color: #000000 !important; }

    /* 縮小所有輸入框與選單的寬度 */
    div[data-testid="stNumberInput"], 
    div[data-baseweb="select"],
    div[data-testid="stFileUploader"] {
        max-width: 280px !important;
    }

    /* 上傳區塊：藍底白字 + 精簡尺寸 */
    div[data-testid="stFileUploader"] section {
        background-color: #1E40AF !important; 
        color: #FFFFFF !important;
        border: 2px solid #1E3A8A !important;
        border-radius: 10px !important;
        padding: 8px !important;
    }
    div[data-testid="stFileUploader"] section * { color: #FFFFFF !important; fill: #FFFFFF !important; }

    /* 單選按鈕文字：黑色 */
    div[data-testid="stMarkdownContainer"] p { color: #000000 !important; font-weight: 500 !important; }

    /* 手機懸浮選單按鈕 */
    [data-testid="stSidebarCollapseButton"] {
        position: fixed !important; top: 15px !important; left: 15px !important;
        z-index: 999999 !important; background-color: #1E40AF !important;
        color: #FFFFFF !important; border-radius: 50% !important;
        width: 48px !important; height: 48px !important;
    }

    /* 輸入框與選單：深藍底白字 + 緊湊高度 */
    div[data-testid="stNumberInput"] input, 
    div[data-baseweb="select"] > div {
        background-color: #1E40AF !important; 
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        height: 38px !important;
    }

    /* 建議報價結果：黃底紅字 */
    .price-result {
        display: inline-block; background-color: #FFFF00 !important;
        color: #E11D48 !important; padding: 8px 16px;
        border-radius: 8px; font-size: 32px !important;
        font-weight: 900 !important; border: 3px solid #E11D48;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 資料庫
@st.cache_data
def load_materials():
    data = {
        "Formlabs": ["Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K"],
        "單價": [9975, 8500, 7500, 12000]
    }
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
                
                st.write("📦 **模型預覽**")
                points = your_mesh.points.reshape(-1, 3)
                v1, v2, v3 = points[::3], points[1::3], points[2::3]
                vertices = np.vstack([v1, v2, v3])
                n = len(v1); i, j, k = np.arange(n), np.arange(n) + n, np.arange(n) + 2*n
                mid_point = (vertices.max(axis=0) + vertices.min(axis=0)) / 2
                max_dim = np.max(vertices.max(axis=0) - vertices.min(axis=0))

                fig = go.Figure(data=[
                    go.Mesh3d(
                        x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
                        i=i, j=j, k=k, color='#D1D5DB', flatshading=False, 
                        lighting=dict(ambient=0.1, diffuse=0.9, specular=1.5, roughness=0.1, fresnel=0.5),
                        lightposition=dict(x=mid_point[0]+max_dim, y=mid_point[1]+max_dim, z=mid_point[2]+max_dim),
                        showscale=False
                    )
                ])
                fig.update_layout(
                    scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                               aspectmode='data', bgcolor='#0F172A',
                               camera=dict(eye=dict(x=1.3, y=1.3, z=1.3))),
                    margin=dict(l=0, r=0, b=0, t=0), height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            except: st.error("STL 解析失敗")
            finally: 
                if os.path.exists(t_path): os.remove(t_path)
    else:
        vol_mm3 = st.number_input("輸入體積 (mm³)", value=0, step=1, format="%d")

    if vol_mm3 > 0:
        st.write(f"**📐 體積:** {vol_mm3:,} mm³")
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
