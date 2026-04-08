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

# --- 2. 仿 Windows 登入畫面系統 ---
def check_password():
    if "password_correct" not in st.session_state:
        # 注入仿 Windows 登入畫面的 CSS
        st.markdown("""
            <style>
            /* 隱藏預設元件 */
            [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }
            
            /* 全螢幕背景與漸層 */
            .stApp {
                background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%);
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            /* 登入容器居中 */
            .login-container {
                text-align: center;
                color: white;
                max-width: 400px;
                margin: auto;
                padding-top: 10vh;
            }

            /* 頭像圓形圖示 */
            .user-avatar {
                width: 150px;
                height: 150px;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 50%;
                margin: 0 auto 20px auto;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .user-avatar svg { width: 80px; fill: #64748B; }

            /* 使用者名稱文字 */
            .user-name {
                font-size: 32px;
                font-weight: 500;
                margin-bottom: 30px;
                font-family: "Segoe UI", sans-serif;
            }

            /* 修改 Streamlit 輸入框樣式 */
            div[data-baseweb="input"] {
                background-color: rgba(255, 255, 255, 0.1) !important;
                border: 2px solid rgba(255, 255, 255, 0.3) !important;
                border-radius: 4px !important;
            }
            input { color: white !important; text-align: center !important; }
            button { width: 100% !important; background-color: rgba(255, 255, 255, 0.2) !important; color: white !important; border: none !important; }
            </style>
            
            <div class="login-container">
                <div class="user-avatar">
                    <svg viewBox="0 0 24 24"><path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/></svg>
                </div>
                <div class="user-name">實威國際 3D列印線上估價</div>
            </div>
        """, unsafe_allow_html=True)

        # 登入輸入框
        pwd = st.text_input("密碼", type="password", label_visibility="collapsed", placeholder="請輸入密碼")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("登入"):
                if pwd == "1234":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("密碼錯誤，請重新輸入")
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

# --- 4. 主程式執行 ---
if check_password():
    df_m = load_materials()
    
    # 進入系統後的介面優化 (側邊欄縮小)
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] { width: 260px !important; min-width: 260px !important; }
        div[data-testid="stHorizontalBlock"] img { width: 40px !important; height: 40px !important; border-radius: 6px !important; }
        div[data-testid="stHorizontalBlock"] p { font-size: 10px !important; color: #64748B; font-weight: 600; }
        .main .block-container { padding-top: 1.5rem; padding-left: 2rem; padding-right: 2rem; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 功能選單")
        sel = image_select(
            label="請選擇功能", 
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png", 
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ], 
            captions=["自動估價", "尺寸校正"],
            index=0
        )

    if "2953536" in sel:
        st.title("💰 實威國際 - 3D列印自動估價")
        up_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.8, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                st.subheader("📦 模型預覽 (高解析 80,000 面)")
                try:
                    m_mesh = mesh.Mesh.from_file(t_path)
                    vecs = m_mesh.vectors
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
                    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', bgcolor='white'), margin=dict(l=0, r=0, b=0, t=0), height=700)
                    st.plotly_chart(fig, use_container_width=True)
                    v_val, _, _ = m_mesh.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                except Exception as e:
                    st.error(f"渲染錯誤: {e}")
            
            with c2:
                st.subheader("📊 報價數據分析")
                st.metric("分析體積", f"{vol_cm3:.2f} cm³")
                m_choice = st.selectbox("選用材料", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                markup = st.slider("報價加成倍率", 1.0, 10.0, 3.0, 0.1)
                base_fee = st.number_input("上機費 (NTD)", value=150)
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                st.divider()
                st.markdown(f"### 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
            os.remove(t_path)
    else:
        st.title("📏 SLA 尺寸校正工具")
        ca = st.number_input("CAD 原型尺寸 (mm)", value=10.0)
        re = st.number_input("實測尺寸 (mm)", value=10.0)
        if ca > 0: st.metric("校正補償因子", f"{(re/ca):.4f}")
