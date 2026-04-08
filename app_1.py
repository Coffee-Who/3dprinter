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

# --- 2. 仿 Windows 登入系統 (強制全置中版) ---
def check_password():
    if "password_correct" not in st.session_state:
        # 注入強效置中 CSS
        st.markdown("""
            <style>
            /* 隱藏預設元件 */
            [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }
            
            /* 背景與全畫面置中 */
            .stApp {
                background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%);
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            /* 覆寫 Streamlit 預設容器，讓它在畫面正中間 */
            .main .block-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 0 !important;
            }

            .login-box {
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }

            .user-name {
                color: white;
                font-size: 28px;
                font-weight: 500;
                margin-top: 20px;
                margin-bottom: 40px;
                font-family: "Segoe UI", "Microsoft JhengHei", sans-serif;
            }

            /* 密碼輸入框縮短且置中 */
            div[data-baseweb="input"] {
                background-color: rgba(255, 255, 255, 0.1) !important;
                border: 2px solid rgba(255, 255, 255, 0.3) !important;
                border-radius: 4px !important;
                width: 260px !important;
                margin: 0 auto !important;
            }
            input { color: white !important; text-align: center !important; }
            
            /* 按鈕置中 */
            button {
                width: 120px !important;
                background-color: rgba(255, 255, 255, 0.2) !important;
                color: white !important;
                border: 1px solid rgba(255, 255, 255, 0.4) !important;
                margin-top: 20px !important;
            }
            </style>
        """, unsafe_allow_html=True)

        # 構建登入畫面
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        try:
            st.image("solidwizard_logo.png", width=240)
        except:
            st.warning("請上傳 solidwizard_logo.png")

        st.markdown('<div class="user-name">實威國際 3D列印線上估價</div>', unsafe_allow_html=True)
        
        pwd = st.text_input("PW", type="password", label_visibility="collapsed", placeholder="輸入密碼")
        
        if st.button("登入"):
            if pwd == "1234":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("密碼錯誤")
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

# --- 3. 讀取材料資料 ---
@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 主程式邏輯 ---
if check_password():
    df_m = load_materials()
    
    # 系統內部全置中 CSS
    st.markdown("""
        <style>
        /* 側邊欄寬度 */
        section[data-testid="stSidebar"] { width: 260px !important; min-width: 260px !important; }
        
        /* 內容區塊置中 */
        .main .block-container {
            max-width: 1200px;
            padding-top: 2rem;
            margin: 0 auto; /* 水平置中 */
            text-align: center;
        }

        /* 讓選單圖片置中 */
        div[data-testid="stHorizontalBlock"] {
            justify-content: center;
        }
        
        /* 修正 3D 預覽容器居中 */
        .stPlotlyChart {
            display: flex;
            justify-content: center;
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
        # 讓上傳按鈕置中
        up_file = st.file_uploader("請上傳您的 STL 模型檔案", type=["stl"])
        
        if up_file:
            # 建立左右兩欄，維持內容平衡
            c1, c2 = st.columns([1.8, 1])
            vol_cm3 = 0.0

            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            try:
                m_mesh = mesh.Mesh.from_file(t_path)
                v_val, _, _ = m_mesh.get_mass_properties()
                vol_cm3 = float(v_val) / 1000.0
                
                with c1:
                    st.subheader("📦 3D 模型預覽")
                    vecs = m_mesh.vectors
                    if len(vecs) > 80000:
                        vecs = vecs[::(len(vecs)//80000)]
                    p, q, r = vecs.shape
                    v = vecs.reshape(p*q, r)
                    f = np.arange(p*q).reshape(p, q)
                    fig = go.Figure(data=[go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2], color='#334155', opacity=1.0, flatshading=False, lighting=dict(ambient=0.4, diffuse=0.8, specular=1.8, roughness=0.2, fresnel=1.2), contour=dict(show=True, color='white', width=1))])
                    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', bgcolor='white'), margin=dict(l=0, r=0, b=0, t=0), height=600)
                    st.plotly_chart(fig, use_container_width=True)
                
                with c2:
                    st.subheader("📊 數據分析")
                    st.metric("模型體積", f"{vol_cm3:.2f} cm³")
                    m_choice = st.selectbox("樹脂型號", df_m["Formlabs"].tolist())
                    u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                    markup = st.slider("報價加成", 1.0, 10.0, 3.0, 0.1)
                    base_fee = st.number_input("上機費 (NTD)", value=150)
                    final_total = (vol_cm3 * u_cost * markup) + base_fee
                    st.divider()
                    st.markdown(f"### 建議報價")
                    st.markdown(f"<h1 style='color:red; text-align:center;'>NT$ {int(final_total)}</h1>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"渲染異常: {e}")
            os.remove(t_path)
        else:
            st.info("💡 請點擊上方按鈕上傳檔案。")
    else:
        st.title("📏 尺寸校正助手")
        # 讓輸入框在中間
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            design = st.number_input("CAD 尺寸 (mm)", value=10.0)
            actual = st.number_input("列印實測 (mm)", value=10.0)
            if design > 0:
                st.metric("Preform 校正因子", f"{(actual/design):.4f}")
