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

# --- 進入系統後的 CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebarCollapseButton"] {
        background-color: #1E40AF !important; color: #FFFFFF !important;
        left: 10px !important; top: 10px !important; display: block !important; z-index: 99999 !important;
    }
    div[data-testid="stNumberInput"], div[data-baseweb="select"], div[data-testid="stFileUploader"], .stSlider { 
        max-width: 280px !important; 
    }
    div[data-testid="stFileUploader"] section { 
        background-color: #1E40AF !important; color: #FFFFFF !important; border-radius: 10px !important; 
    }
    div[data-testid="stFileUploader"] section * { color: #FFFFFF !important; }
    div[data-testid="stNumberInput"] input { background-color: #1E40AF !important; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }
    
    .price-result { 
        display: inline-block; background-color: #FFFF00 !important; color: #E11D48 !important; 
        padding: 8px 16px; border-radius: 8px; font-size: 32px !important; font-weight: 900 !important; border: 3px solid #E11D48; 
    }
    
    /* 成本分析小卡樣式 */
    .analysis-card {
        background-color: #F1F5F9; border-left: 5px solid #64748B; padding: 10px; border-radius: 5px; margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 完整材料資料庫
@st.cache_data
def load_materials():
    data = {
        "材料名稱": [
            "Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K", 
            "Flexible 80A", "Elastic 50A", "High Temp", "Draft Resin",
            "White Resin", "Grey Resin", "Black Resin", "Model Resin"
        ],
        "單價": [9975, 8500, 7500, 12000, 9500, 9500, 11000, 8000, 7500, 7500, 7500, 8500]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df
df_m = load_materials()

# 4. 側邊欄
with st.sidebar:
    st.markdown("### 🛠️ 系統功能")
    choice = st.radio("請選擇：", ["💰 自動估價", "📏 尺寸補償"])
    st.divider()
    if st.button("🚪 登出系統"):
        del st.session_state["password_correct"]
        st.rerun()

# 5. 主程式
if choice == "💰 自動估價":
    st.title("💰 3D列印報價")
    
    input_method = st.radio("選擇體積來源：", ["📤 上傳模型", "⌨️ 手動輸入"], horizontal=True)
    
    vol_mm3 = 0
    mesh_for_viz = None

    if input_method == "📤 上傳模型":
        up_file = st.file_uploader("Upload STL/STEP", type=["stl", "step", "stp"], label_visibility="collapsed")
        if up_file:
            ext = os.path.splitext(up_file.name)[-1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(up_file.getvalue()); t_path = tmp.name
            
            try:
                loaded = trimesh.load(t_path)
                mesh_for_viz = loaded.dump(concatenate=True) if isinstance(loaded, trimesh.Scene) else loaded
                vol_mm3 = int(abs(mesh_for_viz.volume))
                if vol_mm3 <= 0: vol_mm3 = int(mesh_for_viz.convex_hull.volume)
                
                st.write(f"📦 **3D 預覽 ({ext.upper()})**")
                vertices = mesh_for_viz.vertices
                faces = mesh_for_viz.faces
                fig = go.Figure(data=[go.Mesh3d(x=vertices[:,0], y=vertices[:,1], z=vertices[:,2], i=faces[:,0], j=faces[:,1], k=faces[:,2], color='#D1D5DB')])
                fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), bgcolor='#0F172A'), margin=dict(l=0, r=0, b=0, t=0), height=300)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.warning("⚠️ 檔案解析失敗，體積偵測無效。")
            finally:
                if os.path.exists(t_path): os.remove(t_path)
    else:
        vol_mm3 = st.number_input("請輸入模型體積 (mm³)：", min_value=0, step=100)

    # 顯示報價區
    if vol_mm3 > 0:
        st.success(f"📍 當前計算體積：{vol_mm3:,} mm³")
        
        # 區塊 1: 材料選擇與初步成本分析
        m_choice = st.selectbox("1. 選擇列印材料", df_m["材料名稱"].tolist())
        u_cost = df_m.loc[df_m["材料名稱"] == m_choice, "每mm3成本"].values[0]
        pure_material_cost = vol_mm3 * u_cost
        
        st.markdown(f"""
            <div class="analysis-card">
                <b>📊 材料成本分析</b><br>
                單位體積成本: NT$ {u_cost:.6f} / mm³<br>
                <b>單件純材料消耗: NT$ {pure_material_cost:,.1f}</b>
            </div>
        """, unsafe_allow_html=True)
        
        # 區塊 2: 報價參數
        markup = st.slider("2. 利潤倍率", 0.5, 10.0, 1.0, 0.5)
        base_fee = st.number_input("3. 基本費 (NT$)", min_value=0, value=0)

        # 最終報價計算
        total_price = (pure_material_cost * markup) + base_fee
        estimated_profit = total_price - pure_material_cost
        
        st.divider()
        st.markdown(f'### 建議報價：NT$ <span class="price-result">{total_price:,.1f}</span>', unsafe_allow_html=True)
        
        # 區塊 3: 最終利潤成本分析
        st.markdown(f"""
            <div class="analysis-card" style="border-left-color: #10B981;">
                <b>📈 報價結構細節</b><br>
                材料成本佔比: { (pure_material_cost/total_price*100) if total_price > 0 else 0 :.1f}% (NT$ {pure_material_cost:,.1f})<br>
                基本費收入: NT$ {base_fee:,.0f}<br>
                預估毛利 (含基本費): <span style="color:#059669; font-weight:bold;">NT$ {estimated_profit:,.1f}</span>
            </div>
        """, unsafe_allow_html=True)

elif choice == "📏 尺寸補償":
    st.title("📏 尺寸補償計算")
    d_size = st.number_input("設計尺寸 (mm)", min_value=0.1, value=20.0)
    a_size = st.number_input("實測尺寸 (mm)", min_value=0.1, value=19.8)
    res = (d_size / a_size) * 100
    st.write("### 建議縮放比例")
    st.markdown(f'<span class="price-result">{res:.2f}%</span>', unsafe_allow_html=True)
