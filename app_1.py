import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

st.set_page_config(page_title="3D列印專業服務系統", page_icon="🖨️", layout="wide")

# --- 1. 密碼驗證 ---
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

# --- 2. 讀取材料 ---
@st.cache_data
def load_materials():
    try:
        # 優先讀取您上傳的 Formlabs材料.csv
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 3. 強化版 3D 預覽 (解決跳過問題) ---
def show_3d_preview(file_path):
    try:
        m_data = mesh.Mesh.from_file(file_path)
        vecs = m_data.vectors
        
        # 核心優化：如果模型太大，強制大幅抽樣
        if len(vecs) > 20000:
            step = len(vecs) // 20000
            vecs = vecs[::step]
        
        # 提取頂點
        p, q, r = vecs.shape
        v = vecs.reshape(p*q, r)
        f = np.arange(p*q).reshape(p, q)
        
        # 建立藍色 Mesh，並加上黑色邊線
        fig = go.Figure(data=[go.Mesh3d(
            x=v[:,0], y=v[:,1], z=v[:,2], 
            i=f[:,0], j=f[:,1], k=f[:,2],
            color='royalblue', 
            opacity=0.9,
            flatshading=True,
            line=dict(color='black', width=1), # 黑色三角網格線
            showlegend=False
        )])
        
        fig.update_layout(
            scene=dict(
                xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, 
                aspectmode='data',
                bgcolor='white'
            ),
            margin=dict(l=0, r=0, b=0, t=0), 
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        # 如果 Mesh 失敗，嘗試最簡單的點雲預覽
        st.warning(f"正在嘗試輕量化預覽...")
        try:
            m_data = mesh.Mesh.from_file(file_path)
            v = m_data.vectors.reshape(-1, 3)
            if len(v) > 5000: v = v[::(len(v)//5000)]
            fig = go.Figure(data=[go.Scatter3d(
                x=v[:,0], y=v[:,1], z=v[:,2],
                mode='markers',
                marker=dict(size=1, color='royalblue')
            )])
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.error("此 STL 檔案格式損壞或過大，無法顯示預覽。")

# --- 4. 主程式 ---
if check_password():
    df_m = load_materials()
    with st.sidebar:
        sel = image_select(
            label="功能選單", 
            images=["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"], 
            captions=["自動估價", "尺寸校正"]
        )

    if "2953536" in sel:
        st.title("💰 3D列印自動估價系統")
        up_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.5, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                st.subheader("📦 3D 網格結構分析")
                show_3d_preview(t_path)
            
            with c2:
                st.subheader("📊 報價詳情")
                try:
                    m = mesh.Mesh.from_file(t_path)
                    v_val, _, _ = m.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                    st.metric("偵測體積", f"{vol_cm3:.2f} cm³")
                except:
                    st.error("體積計算失敗，請確認檔案。")
                
                m_choice = st.selectbox("樹脂型號 (來自 Excel)", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                
                markup = st.slider("報價利潤倍率", 1.0, 10.0, 3.0, step=0.1)
                base = st.number_input("上機固定費 (起鍋費)", value=150)
                
                total = (vol_cm3 * u_cost * markup) + base
                st.divider()
                st.markdown(f"### 📢 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(total)}</span>", unsafe_allow_html=True)
                st.caption(f"公式: ({vol_cm3:.1f}cm³ x {u_cost:.1f}單價 x {markup}倍) + {base}")
            
            os.remove(t_path)
        else:
            st.info("💡 請上傳檔案來開始 3D 分析與報價。")
    else:
        st.title("📏 SLA 尺寸校正助手")
        # 校正邏輯...
        ca = st.number_input("CAD 設計尺寸 (mm)", value=10.0)
        re = st.number_input("實測尺寸 (mm)", value=10.0)
        if ca > 0:
            st.metric("Preform 校正因子", f"{(re/ca):.4f}")
