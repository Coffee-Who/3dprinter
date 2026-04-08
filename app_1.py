import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go # 引入 Plotly
import numpy as np

# ... (之前的密碼與材料讀取代碼保持不變) ...

# --- 新增一個 Plotly 預覽函數 ---
def show_stl_with_mesh(file_path):
    # 讀取 STL
    your_mesh = mesh.Mesh.from_file(file_path)
    
    # 提取頂點座標
    p, q, r = your_mesh.vectors.shape
    vertices = your_mesh.vectors.reshape(p*q, r)
    faces = np.arange(p*q).reshape(p, q)
    
    # 建立 Plotly 3D Mesh
    fig = go.Figure(data=[
        go.Mesh3d(
            x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
            i=faces[:,0], j=faces[:,1], k=faces[:,2],
            color='royalblue', # 模型顏色：藍色
            opacity=1.0,
            flatshading=True,
            line=dict(color='black', width=2), # 網格線顏色：黑色
            showlegend=False
        )
    ])
    
    fig.update_layout(
        scene=dict(aspectmode='data'),
        margin=dict(l=0, r=0, b=0, t=0),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 修改後的估價邏輯部分 ---
if "2953536" in selection:
    st.title("💰 3D列印專業估價 (藍色模型+黑網格)")
    
    uploaded_file = st.file_uploader("請上傳 STL", type=["stl"])
    
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
            
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader("📦 3D 結構分析預覽")
            # 呼叫剛才建立的 Plotly 預覽函數
            show_stl_with_mesh(tmp_path)
            
        with col2:
            # ... (原本的體積計算與報價邏輯) ...
            m = mesh.Mesh.from_file(tmp_path)
            vol, _, _ = m.get_mass_properties()
            v_cm3 = vol / 1000
            st.metric("偵測體積", f"{v_cm3:.2f} cm³")
            # ... (材料選擇與總價顯示) ...
            
        os.remove(tmp_path)
