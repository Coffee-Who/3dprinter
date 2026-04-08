import streamlit as st
import pandas as pd
from stl import mesh
import trimesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面配置
st.set_page_config(page_title="實威國際 3D列印報價", layout="wide")

# 2. 登入狀態檢測 (黑底白字)
if "password_correct" not in st.session_state:
    st.markdown("<style>.stApp { background-color: #0F172A !important; } h2, p, label { color: #FFFFFF !important; } div.stButton > button { background-color: #1E40AF !important; color: #FFFFFF !important; width: 100% !important; height: 50px !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15vh;'></div><h2 style='text-align:center;'>SOLIDWIZARD</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 6, 1])
    with col_m:
        pwd = st.text_input("管理員密碼", type="password")
        if st.button("確認登入"):
            if pwd == "1234": st.session_state["password_correct"] = True; st.rerun()
            else: st.error("密碼錯誤")
    st.stop()

# --- 進入系統後的 CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    div[data-testid="stNumberInput"], div[data-baseweb="select"], div[data-testid="stFileUploader"] { max-width: 280px !important; }
    div[data-testid="stFileUploader"] section { background-color: #1E40AF !important; color: #FFFFFF !important; border-radius: 10px !important; }
    div[data-testid="stFileUploader"] section * { color: #FFFFFF !important; }
    div[data-testid="stNumberInput"] input { background-color: #1E40AF !important; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }
    .price-result { display: inline-block; background-color: #FFFF00 !important; color: #E11D48 !important; padding: 8px 16px; border-radius: 8px; font-size: 32px !important; font-weight: 900 !important; border: 3px solid #E11D48; }
    </style>
""", unsafe_allow_html=True)

# 3. 資料庫
@st.cache_data
def load_materials():
    data = {"Formlabs": ["Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K"], "單價": [9975, 8500, 7500, 12000]}
    df = pd.DataFrame(data); df['每mm3成本'] = df['單價'] / 1000000
    return df
df_m = load_materials()

# 4. 側邊欄
with st.sidebar:
    st.write("### SOLIDWIZARD")
    if st.button("登出系統"): del st.session_state["password_correct"]; st.rerun()

# 5. 主程式
st.title("💰 3D列印自動報價")
input_method = st.radio("選擇體積來源", ["📤 上傳模型 (STL/STEP)", "⌨️ 手動輸入體積"], horizontal=True)

vol_mm3 = 0

if input_method == "📤 上傳模型 (STL/STEP)":
    up_file = st.file_uploader("Upload", type=["stl", "step", "stp"], label_visibility="collapsed")
    if up_file:
        ext = os.path.splitext(up_file.name)[-1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(up_file.getvalue()); t_path = tmp.name
        
        try:
            # 優先處理 STL
            if ext == ".stl":
                your_mesh = mesh.Mesh.from_file(t_path)
                vol_mm3 = int(abs(your_mesh.get_mass_properties()[0]))
            else:
                # 嘗試處理 STEP (Trimesh 邏輯)
                try:
                    loaded = trimesh.load(t_path)
                    m = loaded.dump(concatenate=True) if isinstance(loaded, trimesh.Scene) else loaded
                    vol_mm3 = int(abs(m.volume))
                    if vol_mm3 <= 0: vol_mm3 = int(m.convex_hull.volume)
                except:
                    st.warning("⚠️ STEP 自動解析失敗（環境限制）。請參考下方的 3D 軟體數據手動輸入體積。")
                    vol_mm3 = 0
            
            if vol_mm3 > 0:
                st.success(f"✅ 成功偵測體積：{vol_mm3:,} mm³")
            else:
                vol_mm3 = st.number_input("請手動輸入模型體積 (mm³)", min_value=0, step=100)

        except Exception as e:
            st.error(f"解析出錯：{e}")
        finally:
            if os.path.exists(t_path): os.remove(t_path)
else:
    vol_mm3 = st.number_input("請輸入體積 (mm³)", min_value=0, step=100)

# 顯示估價區塊
if vol_mm3 > 0:
    m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
    u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每mm3成本"].values[0]
    markup = st.slider("2. 利潤倍率", 0.5, 10.0, 1.0, 0.5)
    base_fee = st.number_input("3. 基本費 (NT$)", min_value=0, value=0)

    total_price = (vol_mm3 * u_cost * markup) + base_fee
    st.divider()
    st.write("### 建議報價總計")
    st.markdown(f'NT$ <span class="price-result">{total_price:,.1f}</span>', unsafe_allow_html=True)
