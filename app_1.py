import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面基本配置
st.set_page_config(
    page_title="實威國際 3D列印線上估價", 
    layout="wide", 
    page_icon="🖨️"
)

# 2. 深度穿透 CSS
def apply_login_style():
    st.markdown("""
        <style>
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .stApp {
            background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%) !important;
            height: 100vh !important;
            width: 100vw !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"],
        .main .block-container, .stVerticalBlock {
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important; 
            justify-content: center !important;
            width: 100% !important;
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        [data-testid="stImage"] {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin-bottom: 20px !important;
        }
        .user-name {
            color: white !important;
            font-size: 32px !important;
            font-weight: 600 !important;
            margin-bottom: 40px !important;
            text-align: center !important;
            width: 100% !important;
            font-family: "Segoe UI", "Microsoft JhengHei", sans-serif;
        }
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid #3B82F6 !important;
            border-radius: 6px !important;
            width: 280px !important;
            margin: 0 auto !important;
        }
        input { 
            color: #000000 !important; 
            text-align: center !important; 
            font-size: 18px !important;
        }
        div.stButton {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
            margin-top: 25px !important;
        }
        .stButton button {
            width: 140px !important;
            height: 45px !important;
            background-color: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
        }
        .stAlert {
            background: transparent !important;
            border: none !important;
            color: #FDA4AF !important;
            text-align: center !important;
        }
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({
            "Formlabs": ["一般樹脂 (Clear/Grey/White)", "Tough 2000", "Flexible 80A"],
            "每cm3成本": [6.5, 8.5, 9.5]
        })

# 3. 登入系統邏輯
if "password_correct" not in st.session_state:
    apply_login_style()
    
    # 確保這裡的每一行都有正確縮進
    try:
        st.image("solidwizard_logo.png", width=250)
    except:
        st.write("🔧 **SolidWizard 3D Printing**")

    st.markdown('<div class="user-name">實威國際 3D列印線上估價</div>', unsafe_allow_html=True)
    
    pwd = st.text_input("PW", type="password", label_visibility="collapsed", placeholder="請輸入登入密碼")
    
    if st.button("進入系統"):
        if pwd == "1234":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("密碼不正確，請聯繫管理員。")
    
    st.stop()

# 4. 登入成功後的內容
st.markdown("""
    <style>
    .stApp { background: #F8FAFC !important; align-items: flex-start !important; justify-content: flex-start !important; height: auto !important; }
    [data-testid="stAppViewContainer"], .main .block-container { 
        display: block !important; max-width: 1200px !important; margin: 0 auto !important; padding: 2rem !important; 
    }
    [data-testid="stSidebar"] { display: block !important; }
    [data-testid="stHeader"] { display: block !important; }
    </style>
""", unsafe_allow_html=True)

df_m = load_materials()

with st.sidebar:
    st.title("🛠️ 功能選單")
    sel = image_select(
        label="選擇服務項目", 
        images=["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"], 
        captions=["自動估價", "尺寸校正"]
    )
    st.divider()
    if st.button("登出系統"):
        del st.session_state["password_correct"]
        st.rerun()

if "2953536" in sel:
    st.title("💰 專業 3D 列印自動報價系統")
    up_file = st.file_uploader("第一步：請上傳您的模型檔案 (STL)", type=["stl"])
    
    if up_file:
        c1, c2 = st.columns([1.6, 1])
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
            tmp.write(up_file.getvalue())
            t_path = tmp.name
        
        try:
            m_mesh = mesh.Mesh.from_file(t_path)
            v_val, _, _ = m_mesh.get_mass_properties()
            vol_cm3 = float(v_val) / 1000.0
            
            with c1:
                st.subheader("📦 模型 3D 預覽")
                vecs = m_mesh.vectors
                if len(vecs) > 50000:
                    vecs = vecs[::(len(vecs)//50000)]
                p, q, r = vecs.shape
                v = vecs.reshape(p*q, r)
                f = np.arange(p*q).reshape(p, q)
                fig = go.Figure(data=[go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2], color='#475569', opacity=1.0)])
                fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data'), margin=dict(l=0, r=0, b=0, t=0), height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.subheader("📊 報價設定")
                st.info(f"檢測到體積: **{vol_cm3:.2f} cm³**")
                m_choice = st.selectbox("選擇使用材料", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                markup = st.slider("報價加成倍率", 1.0, 10.0, 3.0, 0.1)
                base_fee = st.number_input("基本處理費 (NTD)", value=150)
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                st.divider()
                st.markdown(f"<h1 style='color:#E11D48;'>NT$ {int(final_total):,}</h1>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"解析失敗: {e}")
        finally:
            if os.path.exists(t_path): os.remove(t_path)
else:
    st.title("📏 尺寸校正補償計算")
    d_size = st.number_input("設計尺寸 (mm)", value=20.0)
    a_size = st.number_input("實測尺寸 (mm)", value=19.8)
    if d_size > 0:
        st.metric("補償因子", f"{(a_size/d_size):.4f}")
