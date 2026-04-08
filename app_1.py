import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

st.set_page_config(page_title="3D列印專業服務系統", page_icon="🖨️", layout="wide")

# --- 密碼驗證 ---
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

# --- 讀取材料 ---
@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 3D 預覽 (藍色模型+黑色網格) ---
def show_3d_preview(file_path):
    try:
        m_data = mesh.Mesh.from_file(file_path)
        # 簡易抽樣避免大檔案卡死
        vecs = m_data.vectors
        if len(vecs) > 40000:
            vecs = vecs[np.random.choice(len(vecs), 40000, replace=False)]
        
        p, q, r = vecs.shape
        v = vecs.reshape(p*q, r)
        f = np.arange(p*q).reshape(p, q)
        
        fig = go.Figure(data=[go.Mesh3d(
            x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2],
            color='royalblue', opacity=1.0, flatshading=True,
            line=dict(color='black', width=1), showlegend=False
        )])
        fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data'),
                          margin=dict(l=0, r=0, b=0, t=0), height=500)
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("預覽載入跳過")

# --- 主程式 ---
if check_password():
    df_m = load_materials()
    with st.sidebar:
        sel = image_select(label="功能", images=["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn
