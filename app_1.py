import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面基本配置
st.set_page_config(page_title="3D列印專業報價系統", layout="wide", page_icon="🖨️")

# --- 2. 密碼驗證系統 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 內部系統登入")
        pwd = st.text_input("請輸入開啟密碼", type="password")
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
    except Exception:
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 主程式邏輯 ---
if check_password():
    df_m = load_materials()
    
    # 【關鍵修正】CSS 強制縮小側邊欄與圖示
    st.markdown("""
        <style>
        /* 1. 縮小側邊欄整體寬度 */
        section[data-testid="stSidebar"] {
            width: 260px !important;
            min-width: 260px !important;
        }
        
        /* 2. 縮小側邊欄標題字體 */
        section[data-testid="stSidebar"] h1 {
            font-size: 1.2rem !important;
        }

        /* 3. 精確控制服務選單圖示大小 (40px) */
        div[data-testid="stHorizontalBlock"] img {
            width: 40px !important;
            height: 40px !important;
            border-radius: 6px !important;
            object-fit: contain !important;
            border: 1px solid #E2E8F0;
            padding: 2px;
        }
        
        /* 4. 縮小選單下方的文字 */
        div[data-testid="stHorizontalBlock"] p {
            font-size: 10px !important;
            margin-top: 2px !important;
            color: #64748B;
        }

        /* 5. 調整主內容區域，適應縮小的側邊欄 */
        .main .block-container {
            padding-left: 3rem;
            padding-right: 3rem;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 服務控制面板")
        # 這裡選擇服務的組件會受 CSS 影響縮小
        sel = image_select(
            label="選擇項目", 
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png", 
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ], 
            captions=["自動估價", "尺寸校正"],
            index=0
        )

    # --- 5. 自動估價與預覽 ---
    if "2953536" in sel:
        st.title("💰 Formlabs 自動估價系統")
        up_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.8, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                st.subheader("📦 3D 預覽")
                try:
                    m_mesh = mesh.Mesh.from_file(t_path)
                    vecs = m_mesh.vectors
                    if len(vecs) > 30000:
                        vecs = vecs[::(len(vecs)//30000)]
                    
                    p, q, r = vecs.shape
                    v = vecs.reshape(p*q, r)
                    f = np.arange(p*q).reshape(p, q)
                    
                    fig = go.Figure(data=[
                        go.Mesh3d(
                            x=v[:,0], y=v[:,1], z=v[:,2],
                            i=f[:,0], j=f[:,1], k=f[:,2],
                            color='#334155', opacity=1.0,
                            lighting=dict(ambient=0.4, diffuse=0.8, specular=1.5, roughness=0.2),
                            contour=dict(show=True, color='white', width=1)
                        )
                    ])
                    fig.update_layout(
                        scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', bgcolor='white'),
                        margin=dict(l=0, r=0, b=0, t=0), height=600
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    v_val, _, _ = m_mesh.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                except Exception as e:
                    st.error(f"預覽錯誤: {e}")
            
            with c2:
                st.subheader("📊 報價分析")
                st.metric("模型體積", f"{vol_cm3:.2f} cm³")
                m_choice = st.selectbox("選用樹脂", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                markup = st.slider("報價倍率", 1.0, 10.0, 3.0, 0.1)
                base_fee = st.number_input("基本費", value=150)
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                st
