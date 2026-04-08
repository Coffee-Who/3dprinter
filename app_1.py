import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面配置
st.set_page_config(page_title="3D列印專業報價系統", layout="wide", page_icon="🖨️")

# --- 2. 密碼驗證 ---
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

# --- 3. 讀取材料 ---
@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except Exception:
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 主程式 ---
if check_password():
    df_m = load_materials()
    
    # 【核心 CSS】縮小側邊欄與圖示
    st.markdown("""
        <style>
        /* 縮小側邊欄寬度 */
        section[data-testid="stSidebar"] {
            width: 260px !important;
            min-width: 260px !important;
        }
        
        /* 縮小選單圖示 (40px) */
        div[data-testid="stHorizontalBlock"] img {
            width: 40px !important;
            height: 40px !important;
            border-radius: 6px !important;
            object-fit: contain !important;
            border: 1px solid #E2E8F0;
            padding: 2px;
        }
        
        /* 縮小選單文字 */
        div[data-testid="stHorizontalBlock"] p {
            font-size: 10px !important;
            margin-top: 2px !important;
            color: #64748B;
            font-weight: 600;
        }

        /* 調整主畫面間距 */
        .main .block-container {
            padding-top: 2rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 控制面板")
        sel = image_select(
            label="選擇功能", 
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png", 
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ], 
            captions=["自動估價", "尺寸校正"],
            index=0
        )

    # --- 5. 自動估價 (高精細預覽版) ---
    if "2953536" in sel:
        st.title("💰 Formlabs 自動報價系統")
        up_file = st.file_uploader("上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.8, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                st.subheader("📦 高解析度模型預覽")
                try:
                    m_mesh = mesh.Mesh.from_file(t_path)
                    vecs = m_mesh.vectors
                    total_faces = len(vecs)
                    
                    # --- 網格顯示精細度翻倍邏輯 ---
                    # 門檻提高到 80,000 面，確保模型細節完整
                    if total_faces > 80000:
                        step = total_faces // 80000
                        vecs = vecs[::step]
                    
                    p, q, r = vecs.shape
                    v = vecs.reshape(p*q, r)
                    f = np.arange(p*q).reshape(p, q)
                    
                    fig = go.Figure(data=[
                        go.Mesh3d(
                            x=v[:,0], y=v[:,1], z=v[:,2],
                            i=f[:,0], j=f[:,1], k=f[:,2],
                            color='#334155', # 深灰色質感
                            opacity=1.0,
                            flatshading=False,
                            # 專業光學模擬
                            lighting=dict(
                                ambient=0.4, 
                                diffuse=0.8, 
                                specular=1.8, 
                                roughness=0.2,
                                fresnel=1.2
                            ),
                            # 增加細緻輪廓線
                            contour=dict(show=True, color='white', width=0.5)
                        )
                    ])
                    
                    fig.update_layout(
                        scene=dict(
                            xaxis_visible=False, 
                            yaxis_visible=False, 
                            zaxis_visible=False, 
                            aspectmode='data', 
                            bgcolor='white'
                        ),
                        margin=dict(l=0, r=0, b=0, t=0), height=700
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    v_val, _, _ = m_mesh.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                except Exception as e:
                    st.error(f"預覽失敗: {e}")
            
            with c2:
                st.subheader("📊 報價數據")
                st.metric("偵測體積", f"{vol_cm3:.2f} cm³")
                m_choice = st.selectbox("樹脂材料", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                markup = st.slider("報價倍率", 1.0, 10.0, 3.0, 0.1)
                base_fee = st.number_input("上機費", value=150)
                
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                st.divider()
                st.markdown(f"### 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
                
                with st.expander("🔍 報價組成明細"):
                    st.write(f"- 材料基本成本: NT$ {int(vol_cm3 * u_cost)}")
                    st.write(f"- 加工與利潤: NT$ {int(vol_cm3 * u_cost * (markup-1))}")
                    st.write(f"- 上機固定費: NT$ {base_fee}")
            os.remove(t_path)
        else:
            st.info("💡 請上傳 STL 檔案開始。")
    else:
        st.title("📏 尺寸校正助手")
        ca = st.number_input("CAD 尺寸 (mm)", value=10.0)
        re = st.number_input("實測尺寸 (mm)", value=10.0)
        if ca > 0:
            st.metric("應填入校正因子", f"{(re/ca):.4f}")
