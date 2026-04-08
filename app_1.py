import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide", page_icon="🖨️")

# --- 2. 仿 Windows 登入與全站強效置中 CSS ---
def apply_ultra_center_css():
    st.markdown("""
        <style>
        /* A. 全站背景與強效置中佈局 */
        .stApp {
            background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%);
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }

        /* B. 移除 Streamlit 預設邊距，強制容器置中 */
        [data-testid="stAppViewContainer"] {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        
        .main .block-container {
            max-width: 600px !important; /* 縮小容器寬度，讓對齊更精準 */
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            text-align: center !important;
        }

        /* C. 強制圖片 (Logo) 置中 */
        [data-testid="stImage"] {
            display: flex !important;
            justify-content: center !important;
            margin: 0 auto !important;
        }

        /* D. 系統標題 */
        .user-name {
            color: white;
            font-size: 28px;
            font-weight: 500;
            margin: 20px 0 30px 0;
            font-family: "Segoe UI", "Microsoft JhengHei", sans-serif;
        }

        /* E. 密碼框樣式與寬度 */
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 2px solid rgba(255, 255, 255, 0.3) !important;
            border-radius: 4px !important;
            width: 260px !important;
            margin: 0 auto !important;
        }
        input { color: white !important; text-align: center !important; }
        
        /* F. 【關鍵修正】強制登入按鈕置中 */
        [data-testid="stBaseButton-secondary"], 
        [data-testid="stBaseButton-primary"],
        .stButton button {
            display: block !important;
            margin: 20px auto 0 auto !important; /* 水平自動邊距強制置中 */
            width: 120px !important;
            background-color: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
        }
        
        /* 隱藏頂部 Header */
        [data-testid="stHeader"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. 密碼驗證邏輯 ---
def check_password():
    if "password_correct" not in st.session_state:
        apply_ultra_center_css()
        
        # 1. Logo (確保檔案 solidwizard_logo.png 存在)
        try:
            st.image("solidwizard_logo.png", width=240)
        except:
            st.warning("⚠️ 檔案缺失: solidwizard_logo.png")

        # 2. 標題
        st.markdown('<div class="user-name">實威國際 3D列印線上估價</div>', unsafe_allow_html=True)
        
        # 3. 密碼框
        pwd = st.text_input("PW", type="password", label_visibility="collapsed", placeholder="輸入密碼")
        
        # 4. 登入按鈕 (直接放置，不再使用 columns，靠 CSS 強制居中)
        if st.button("登入"):
            if pwd == "1234":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("密碼錯誤")
        return False
    return True

# --- 4. 讀取材料 ---
@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({"Formlabs": ["預設一般樹脂"], "每cm3成本": [10.0]})

# --- 5. 主程式 ---
if check_password():
    df_m = load_materials()
    
    # 登入後的佈局調整
    st.markdown("""
        <style>
        .stApp { background: white !important; align-items: flex-start !important; }
        section[data-testid="stSidebar"] { width: 260px !important; min-width: 260px !important; }
        .main .block-container { 
            max-width: 1200px !important; 
            padding-top: 3rem !important; 
            align-items: flex-start !important;
            text-align: left !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 功能選單")
        sel = image_select(
            label="選擇服務項目", 
            images=["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"], 
            captions=["自動估價", "尺寸校正"]
        )

    if "2953536" in sel:
        st.title("💰 專業 3D 列印自動報價")
        up_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        if up_file:
            c1, c2 = st.columns([1.5, 1])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            try:
                m_mesh = mesh.Mesh.from_file(t_path)
                v_val, _, _ = m_mesh.get_mass_properties()
                vol_cm3 = float(v_val) / 1000.0
                
                with c1:
                    st.subheader("📦 模型預覽")
                    vecs = m_mesh.vectors
                    if len(vecs) > 80000:
                        vecs = vecs[::(len(vecs)//80000)]
                    p, q, r = vecs.shape
                    v = vecs.reshape(p*q, r)
                    f = np.arange(p*q).reshape(p, q)
                    fig = go.Figure(data=[go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2], color='#334155', opacity=1.0, flatshading=False, lighting=dict(ambient=0.4, diffuse=0.8, specular=1.8, roughness=0.2, fresnel=1.2), contour=dict(show=True, color='white', width=1))])
                    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', bgcolor='#F8FAFC'), margin=dict(l=0, r=0, b=0, t=0), height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                with c2:
                    st.subheader("📊 價格明細")
                    st.metric("分析體積", f"{vol_cm3:.2f} cm³")
                    m_choice = st.selectbox("樹脂型號", df_m["Formlabs"].tolist())
                    u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                    markup = st.slider("報價倍率", 1.0, 10.0, 3.0, 0.1)
                    base_fee = st.number_input("上機費 (NTD)", value=150)
                    total = (vol_cm3 * u_cost * markup) + base_fee
                    st.divider()
                    st.markdown(f"### 建議報價")
                    st.markdown(f"<h1 style='color:red;'>NT$ {int(total)}</h1>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"渲染錯誤: {e}")
            os.remove(t_path)
