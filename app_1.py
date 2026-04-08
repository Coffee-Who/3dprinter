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

# --- 2. 仿 Windows 登入畫面系統 (實威國際 Logo 版) ---
def check_password():
    if "password_correct" not in st.session_state:
        # 注入仿 Windows 登入畫面的 CSS
        st.markdown("""
            <style>
            /* 1. 隱藏預設元件，創造全螢幕感 */
            [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }
            
            /* 2. 全螢幕背景與漸層 */
            .stApp {
                background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%);
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            /* 3. 登入容器居中 */
            .login-container {
                text-align: center;
                color: white;
                max-width: 450px; /* 稍微放寬，適應 Logo 寬度 */
                margin: auto;
                padding-top: 10vh;
                display: flex;
                flex-direction: column;
                align-items: center;
            }

            /* 4. 實威國際 Logo 容器 */
            .user-logo {
                width: 200px; /* Logo 寬度 */
                margin: 0 auto 30px auto;
                background-color: transparent !important; /* 確保背景透明 */
            }
            .user-logo img {
                width: 100% !important;
                height: auto !important;
                object-fit: contain !important;
            }

            /* 5. 系統標題文字 (仿使用者名稱) */
            .user-name {
                font-size: 32px;
                font-weight: 500;
                margin-bottom: 30px;
                font-family: "Segoe UI", sans-serif;
            }

            /* 6. 【關鍵修正】縮短密碼輸入框與置中 */
            div[data-baseweb="input"] {
                background-color: rgba(255, 255, 255, 0.1) !important;
                border: 2px solid rgba(255, 255, 255, 0.3) !important;
                border-radius: 4px !important;
                width: 250px !important; /* 強制縮短輸入框寬度 */
                margin: 0 auto !important; /* 強制置中 */
            }
            input { color: white !important; text-align: center !important; }
            
            /* 7. 縮短登入按鈕 */
            button {
                width: 150px !important; /* 縮短按鈕 */
                background-color: rgba(255, 255, 255, 0.2) !important;
                color: white !important;
                border: none !important;
                margin-top: 10px !important;
            }
            </style>
            
            <div class="login-container">
                <div class="user-name">實威國際 3D列印線上估價</div>
            </div>
        """, unsafe_allow_html=True)

        # 8. 在 CSS 的 container 內嵌入 Logo 圖片 (使用您提供的圖片連結)
        # 備註：請確保這張圖片已上傳至 GitHub 倉庫根目錄，並將檔名改為 solidwizard_logo.png
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        try:
            # 嘗試使用本地上傳的 Logo 檔案
            st.image("solidwizard_logo.png", width=200, output_format="PNG")
        except:
            # 備援：如果找不到檔案，顯示佔位文字
            st.error("⚠️ 找不到 solidwizard_logo.png 檔案，請確認檔案已上傳至根目錄。")
        st.markdown("</div>", unsafe_allow_html=True)

        # 9. 登入輸入框 ( label_visibility="collapsed" 用來仿 placeholder)
        pwd = st.text_input("密碼", type="password", label_visibility="collapsed", placeholder="請輸入密碼")
        
        # 10. 按鈕置中
        colA, colB, colC = st.columns([1, 1, 1])
        with colB:
            if st.button("登入"):
                if pwd == "1234":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("密碼錯誤")
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
        # 備援資料
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 主程式執行 ---
if check_password():
    df_m = load_materials()
    
    # CSS：主內容區域間距優化 (側邊欄瘦身版)
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { width: 260px !important; min-width: 260px !important; }
        div[data-testid="stHorizontalBlock"] img { width: 40px !important; height: 40px !important; border-radius: 6px !important; }
        div[data-testid="stHorizontalBlock"] p { font-size: 10px !important; color: #64748B; font-weight: 600; }
        .main .block-container { padding-top: 1.5rem; padding-left: 2rem; padding-right: 2rem; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 控制面板")
        sel = image_select(
            label="選擇功能", 
            images=["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"], 
            captions=["自動估價", "尺寸校正"]
        )

    if "2953536" in sel:
        st.title("💰 專業 3D 列印自動報價")
        up_file = st.file_uploader("上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.8, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                st.subheader("📦 模型預覽 (80,000 面高精細度)")
                try:
                    m_mesh = mesh.Mesh.from_file(t_path)
                    vecs = m_mesh.vectors
                    if len(vecs) > 80000:
                        vecs = vecs[::(len(vecs)//80000)]
                    p, q, r = vecs.shape
                    v = vecs.reshape(p*q, r)
                    f = np.arange(p*q).reshape(p, q)
                    fig = go.Figure(data=[go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2], color='#334155', opacity=1.0, flatshading=False, lighting=dict(ambient=0.4, diffuse=0.8, specular=1.8, roughness=0.2, fresnel=1.2), contour=dict(show=True, color='white', width=1))])
                    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', bgcolor='white'), margin=dict(l=0, r=0, b=0, t=0), height=700)
                    st.plotly_chart(fig, use_container_width=True)
                    v_val, _, _ = m_mesh.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                except Exception as e:
                    st.error(f"渲染錯誤: {e}")
            
            with c2:
                st.subheader("📊 報價數據")
                st.metric("分析體積", f"{vol_cm3:.2f} cm³")
                m_choice = st.selectbox("選用樹脂", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                markup = st.slider("加成倍率", 1.0, 10.0, 3.0, 0.1)
                base_fee = st.number_input("上機費 (固定費)", value=150)
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                st.divider()
                st.markdown(f"### 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
            os.remove(t_path)
        else:
            st.info("👋 請上傳 STL 檔案開始分析。")
    else:
        st.title("📏 SLA 尺寸校正工具")
        ca = st.number_input("CAD 尺寸 (mm)", value=10.0)
        re = st.number_input("實測尺寸 (mm)", value=10.0)
        if ca > 0: st.metric("校正補償因子", f"{(re/ca):.4f}")
