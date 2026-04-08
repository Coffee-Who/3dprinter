import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面基本設定
st.set_page_config(page_title="3D列印專業服務系統", page_icon="🖨️", layout="wide")

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

# --- 3. 讀取材料資料 ---
@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except Exception as e:
        st.warning(f"材料清單讀取異常，請檢查 GitHub 檔案。")
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 優化後的 Plotly 預覽 (藍色主體 + 黑色網格線) ---
def show_3d_preview(file_path):
    try:
        # 讀取 STL 模型
        m_data = mesh.Mesh.from_file(file_path)
        
        # 限制預覽的面數，避免網頁崩潰 (如果面數超過 50,000 則抽樣顯示)
        max_faces = 50000
        if len(m_data.vectors) > max_faces:
            st.warning("⚠️ 模型面數過高，預覽已自動進行簡化以加速載入。")
            indices = np.random.choice(len(m_data.vectors), max_faces, replace=False)
            vectors = m_data.vectors[indices]
        else:
            vectors = m_data.vectors

        p, q, r = vectors.shape
        vertices = vectors.reshape(p*q, r)
        faces = np.arange(p*q).reshape(p, q)
        
        fig = go.Figure(data=[
            go.Mesh3d(
                x=vertices[:,0], y=vertices[:,1], z=vertices[:,2],
                i=faces[:,0], j=faces[:,1], k=faces[:,2],
                color='royalblue',      # 藍色模型
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
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"❌ 3D 預覽載入失敗。原因: {e}")
        st.info("💡 這可能是因為模型檔案結構特殊，但不影響體積計算。")

# --- 5. 主程式執行 ---
if check_password():
    df_materials = load_materials()
    
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

    if "2953536" in selection:
        st.title("💰 Formlabs 自動估價系統")
        uploaded_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        col1, col2 = st.columns([1.5, 1])
        v_cm3 = 0.0

        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            with col1:
                st.subheader("📦 3D 網格結構預覽")
                show_3d_preview(tmp_path)
            
            with col2:
                st.subheader("📊 分析與報價")
                try:
                    m_calc = mesh.Mesh.from_file(tmp_path)
                    vol, _, _ = m_calc.get_mass_properties()
                    v_cm3 = float(vol) / 1000.0
                    st.metric("偵測體積 (ml)", f"{v_cm3:.2f} cm³")
                except:
                    st.error("體積計算
