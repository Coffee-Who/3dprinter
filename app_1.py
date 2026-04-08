import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 基礎頁面設定
st.set_page_config(page_title="3D列印專業服務系統", page_icon="🖨️", layout="wide")

# --- 2. 密碼驗證系統 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 內部系統存取限制")
        pwd = st.text_input("請輸入開啟密碼", type="password")
        if st.button("登入"):
            if pwd == "1234": # 這裡可以改你的密碼
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("密碼錯誤")
        return False
    return True

# --- 3. 讀取材料清單 ---
@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except Exception as e:
        st.error(f"找不到材料清單：{e}")
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. Plotly 藍色模型 + 黑色邊線預覽函數 ---
def show_stl_with_mesh(file_path):
    try:
        your_mesh = mesh.Mesh.from_file(file_path)
        p, q, r = your_mesh.vectors.shape
        vertices = your_mesh.vectors.reshape(p*q, r)
        faces = np.arange(p*q).reshape(p, q)
        
        fig = go.Figure(data=[
            go.Mesh3d(
                x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
                i=faces[:,0], j=faces[:,1], k=faces[:,2],
                color='royalblue', # 藍色主體
                opacity=1.0,
                flatshading=True,
                line=dict(color='black', width=1), # 黑色邊線
                showlegend=False
            )
        ])
        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='data'
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"預覽生成失敗: {e}")

# --- 5. 程式主體 (確保所有邏輯都在密碼通過後) ---
if check_password():
    df_materials = load_materials()
    
    # 側邊欄功能選擇
    with st.sidebar:
        st.title("🛠️ 功能選單")
        selection = image_select(
            label="請選擇服務項目",
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png",
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ],
            captions=["自動估價系統", "SLA 尺寸校正"],
            index=0
        )

    # 判斷功能 (所有的 if/else 都要縮排在 check_password 內)
    if "2953536" in selection:
        st.title("💰 Formlabs 自動估價與網格預覽")
        
        uploaded_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        col1, col2 = st.columns([1.5, 1])
        
        v_cm3 = 0.0
        
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            with col1:
                st.subheader("📦 3D 結構分析 (藍色主體/黑邊線)")
                show_stl_with_mesh(tmp_path)
            
            with col2:
                st.subheader("📊 數據分析")
                try:
                    m = mesh.Mesh.from_file(tmp_path)
                    vol, _, _ = m.get_mass_properties()
                    v_cm3 = float(vol) / 1000.0
                    st.metric("偵測體積", f"{v_cm3:.2f} cm³")
                except:
                    st.error("體積計算失敗")
                
                material_choice = st.selectbox("樹脂型號", df_materials["Formlabs"].tolist())
                cost_unit = df_materials.loc[df_materials["Formlabs"] == material_choice, "每cm3成本"].values[0]
                
                markup = st.slider("報價倍率", 1.0, 10.0,
