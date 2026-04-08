import streamlit as st
import pandas as pd
from stl import mesh
import trimesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面配置
st.set_page_config(page_title="實威國際 3D列印報價", layout="wide", initial_sidebar_state="expanded")

# 2. 登入狀態檢測 (黑底白字)
if "password_correct" not in st.session_state:
    st.markdown("""
        <style>
        .stApp { background-color: #0F172A !important; }
        h2, p, label { color: #FFFFFF !important; }
        div[data-testid="stTextInput"] input {
            background-color: #1E293B !important; color: #FFFFFF !important;
            border: 2px solid #334155 !important; border-radius: 8px !important;
        }
        div.stButton > button {
            background-color: #1E40AF !important; color: #FFFFFF !important;
            width: 100% !important; height: 50px !important; font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>SOLIDWIZARD</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 6, 1])
    with col_m:
        pwd = st.text_input("管理員密碼", type="password")
        if st.button("確認登入"):
            if pwd == "1234": 
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("密碼錯誤")
    st.stop()

# --- 進入系統後的 CSS (強化手機版側邊欄開關) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    
    /* 強制顯示手機版的側邊欄開啟按鈕 (左上角) */
    [data-testid="stSidebarCollapseButton"] {
        background-color: #1E40AF !important;
        color: #FFFFFF !important;
        border-radius: 5px !important;
        left: 10px !important;
        top: 10px !important;
        display: block !important;
        z-index: 99999 !important;
    }
    
    /* 側邊欄內部的顏色調整 */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    /* 縮小元件寬度 */
    div[data-testid="stNumberInput"], div[data-baseweb="select"], div[data-testid="stFileUploader"], .stSlider { 
        max-width: 250px !important; 
    }

    /* 上傳區塊藍底白字 */
    div[data-testid="stFileUploader"] section { 
        background-color: #1E40AF !important; color: #FFFFFF !important; 
        border-radius: 10px !important; padding: 5px !important; 
    }
    div[data-testid="stFileUploader"] section * { color: #FFFFFF !important; }

    /* 報價結果樣式 */
    .price-result { 
        display: inline-block; background-color: #FFFF00 !important; color: #E11D48 !important; 
        padding: 8px 16px; border-radius: 8px; font-size: 32px !important; 
        font-weight: 900 !important; border: 3px solid #E11D48; 
    }
    </style>
""", unsafe_allow_html=True)

# 3. 資料庫
@st.cache_data
def load_materials():
    data = {"Formlabs": ["Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K"], "單價": [9975, 8500, 7500, 12000]}
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000
    return df
df_m = load_materials()

# 4. 側邊欄 (確定在登入後才定義)
with st.sidebar:
    st.markdown("### 🛠️ 系統功能")
    choice = st.radio("請選擇操作：", ["💰 自動估價系統", "📏 尺寸校正計算"])
    st.divider()
    if st.button("🚪 登出系統"):
        del st.session_state["password_correct"]
        st.rerun()

# 5. 主程式邏輯
if choice == "💰 自動估價系統":
    st.title("💰 3D列印自動報價")
    up_file = st.file_uploader("Upload", type=["stl", "step", "stp"], label_visibility="collapsed")
    
    vol_mm3 = 0
    mesh_for_viz = None

    if up_file:
        ext = os.path.splitext(up_file.name)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(up_file.getvalue()); t_path = tmp.name
        
        try:
            # 優先處理 STL
            if ext == ".stl":
                m = trimesh.load(t_path)
                vol_mm3 = int(abs(m.volume))
                mesh_for_viz = m
            else:
                # STEP 解析 (嘗試獲取預覽數據)
                try:
                    loaded = trimesh.load(t_path)
                    mesh_for_viz = loaded.dump(concatenate=True) if isinstance(loaded, trimesh.Scene) else loaded
                    vol_mm3 = int(abs(mesh_for_viz.volume))
                    if vol_mm3 <= 0: vol_mm3 = int(mesh_for_viz.convex_hull.volume)
                except:
                    vol_mm3 = 0
            
            # 顯示 3D 預覽
            if mesh_for_viz:
                st.write(f"📦 **模型預覽 ({ext.upper()})**")
                vertices = mesh_for_viz.vertices
                faces = mesh_for_viz.faces
                fig = go.Figure(data=[go.Mesh3d(x=vertices[:,0], y=vertices[:,1], z=vertices[:,2], i=faces[:,0], j=faces[:,1], k=faces[:,2], color='#D1D5DB', lighting=dict(ambient=0.1, diffuse=0.9, specular=1.5))])
                fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='#0F172A'), margin=dict(l=0, r=0, b=0, t=0), height=350)
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"解析失敗: {e}")
        finally:
            if os.path.exists(t_path): os.remove(t_path)

    # 報價顯示區
    if vol_mm3 > 0:
        st.success(f"✅ 偵測體積：{vol_mm3:,} mm³")
        m_choice = st.selectbox("1. 選擇材料", df_m["Formlabs"].tolist())
        u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每mm3成本"].values[0]
        markup = st.slider("2. 利潤倍率", 0.5, 10.0, 1.0, 0.5)
        base_fee = st.number_input("3. 基本費 (NT$)", min_value=0, value=0)

        total_price = (vol_mm3 * u_cost * markup) + base_fee
        st.divider()
        st.write("### 建議報價總計")
        st.markdown(f'NT$ <span class="price-result">{total_price:,.1f}</span>', unsafe_allow_html=True)
    elif up_file:
        st.info("💡 預覽已載入，但體積無法自動解析。請確認模型是否為密封實體，或改用 STL 格式。")

else:
    st.title("📏 尺寸補償計算")
    d_size = st.number_input("設計尺寸 (mm)", value=20.0, step=0.1)
    a_size = st.number_input("實測尺寸 (mm)", value=19.8, step=0.1)
    if d_size > 0 and a_size > 0:
        res = (d_size / a_size) * 100
        st.write("### 建議縮放比例")
        st.markdown(f'<span class="price-result">{res:.2f}%</span>', unsafe_allow_html=True)
