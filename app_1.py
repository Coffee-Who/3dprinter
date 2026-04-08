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

# --- 2. 仿 Windows 登入系統 (Logo 置中置頂版) ---
def check_password():
    if "password_correct" not in st.session_state:
        # 注入仿 Windows 登入畫面的 CSS
        st.markdown("""
            <style>
            /* 隱藏預設元件，創造沉浸式登入感 */
            [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }
            
            /* 全螢幕背景與 Windows 藍色漸層 */
            .stApp {
                background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%);
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            
            /* 登入容器佈局 */
            .login-box {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                width: 100%;
                max-width: 500px;
                margin-top: -10vh; /* 稍微往上提，視覺更平衡 */
            }

            /* 系統標題文字 */
            .user-name {
                color: white;
                font-size: 28px;
                font-weight: 500;
                margin-top: 20px;
                margin-bottom: 40px;
                font-family: "Segoe UI", "Microsoft JhengHei", sans-serif;
            }

            /* 密碼輸入框縮短樣式 */
            div[data-baseweb="input"] {
                background-color: rgba(255, 255, 255, 0.1) !important;
                border: 2px solid rgba(255, 255, 255, 0.3) !important;
                border-radius: 4px !important;
                width: 260px !important; /* 強制縮短寬度 */
                margin: 0 auto !important;
            }
            input { 
                color: white !important; 
                text-align: center !important; 
                font-size: 16px !important;
            }
            
            /* 登入按鈕樣式 */
            button[kind="secondary"], button[kind="primary"] {
                width: 120px !important;
                background-color: rgba(255, 255, 255, 0.2) !important;
                color: white !important;
                border: 1px solid rgba(255, 255, 255, 0.4) !important;
                margin-top: 20px !important;
                transition: 0.3s;
            }
            button:hover {
                background-color: rgba(255, 255, 255, 0.3) !important;
                border: 1px solid white !important;
            }
            
            /* 錯誤訊息優化 */
            .stAlert { 
                background-color: transparent !important; 
                color: #FDA4AF !important; 
                border: none !important; 
                text-align: center;
            }
            </style>
        """, unsafe_allow_html=True)

        # 開始構建登入畫面
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        
        # A. Logo 置頂置中
        try:
            # 請確保 solidwizard_logo.png 存在於 GitHub 根目錄
            st.image("solidwizard_logo.png", width=240)
        except:
            st.warning("⚠️ 檔案缺失: 請上傳 solidwizard_logo.png")

        # B. 標題文字
        st.markdown('<div class="user-name">實威國際 3D列印線上估價</div>', unsafe_allow_html=True)
        
        # C. 縮短的密碼框
        pwd = st.text_input("PW", type="password", label_visibility="collapsed", placeholder="輸入密碼")
        
        # D. 登入按鈕居中
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
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
    
    # 系統內部 UI 優化
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { width: 260px !important; min-width: 260px !important; }
        div[data-testid="stHorizontalBlock"] img { width: 42px !important; height: 42px !important; }
        .main .block-container { padding-top: 1.5rem; padding-left: 2.5rem; padding-right: 2.5rem; }
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
        up_file = st.file_uploader("請上傳您的 STL 模型檔案", type=["stl"])
        
        c1, c2 = st.columns([1.8, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                st.subheader("📦 高解析 3D 模型預覽")
                try:
                    m_mesh = mesh.Mesh.from_file(t_path)
                    vecs = m_mesh.vectors
                    # 網格精細度設定 (80,000 面)
                    if len(vecs) > 80000:
                        vecs = vecs[::(len(vecs)//80000)]
                    
                    p, q, r = vecs.shape
                    v = vecs.reshape(p*q, r)
                    f = np.arange(p*q).reshape(p, q)
                    
                    fig = go.Figure(data=[go.Mesh3d(
                        x=v[:,0], y=v[:,1], z=v[:,2],
                        i=f[:,0], j=f[:,1], k=f[:,2],
                        color='#334155', opacity=1.0, flatshading=False,
                        lighting=dict(ambient=0.4, diffuse=0.8, specular=1.8, roughness=0.2, fresnel=1.2),
                        contour=dict(show=True, color='white', width=1)
                    )])
                    fig.update_layout(
                        scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', bgcolor='white'),
                        margin=dict(l=0, r=0, b=0, t=0), height=700
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    v_val, _, _ = m_mesh.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                except Exception as e:
                    st.error(f"3D 渲染異常: {e}")
            
            with c2:
                st.subheader("📊 估價計算細節")
                st.metric("分析模型體積", f"{vol_cm3:.2f} cm³")
                m_choice = st.selectbox("請選擇材料型號", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                markup = st.slider("加成倍率 (工時/利潤)", 1.0, 10.0, 3.0, 0.1)
                base_fee = st.number_input("基本起鍋費 (NTD)", value=150)
                
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                st.divider()
                st.markdown(f"### 建議報價: <span style='color:red; font-size:42px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
                
                with st.expander("🔍 價格明細查看"):
                    st.write(f"- 材料基本成本: NT$ {int(vol_cm3 * u_cost)}")
                    st.write(f"- 加工服務費: NT$ {int(vol_cm3 * u_cost * (markup-1))}")
                    st.write(f"- 上機固定成本: NT$ {base_fee}")
            os.remove(t_path)
        else:
            st.info("💡 請上傳 STL 檔案以獲得精確報價。")
    else:
        st.title("📏 SLA 尺寸補償助手")
        c_a, c_b = st.columns(2)
        with c_a: design = st.number_input("CAD 原型尺寸 (mm)", value=10.0)
        with c_b: actual = st.number_input("列印實測尺寸 (mm)", value=10.0)
        if design > 0:
            st.divider()
            st.metric("Preform 校正因子", f"{(actual/design):.4f}")
