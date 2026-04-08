import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面基本配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide", page_icon="🖨️")

# 2. 登入介面專用 CSS (僅在未登入時強力隱藏所有元件)
def apply_login_style():
    st.markdown("""
        <style>
        [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stToolbar"] { 
            display: none !important; 
        }
        .stApp {
            background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%) !important;
        }
        [data-testid="stMainBlockContainer"] {
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            align-items: center !important;
            height: 100vh !important;
        }
        .stVerticalBlock { width: 100% !important; max-width: 420px !important; margin: auto !important; }
        .logo-box { display: flex !important; justify-content: center !important; margin-bottom: 25px !important; }
        .user-name { color: white !important; font-size: 28px !important; font-weight: 600 !important; text-align: center !important; margin-bottom: 35px !important; }
        div[data-baseweb="input"] { background-color: white !important; border-radius: 10px !important; }
        div.stButton button { width: 100% !important; height: 50px !important; background-color: #3B82F6 !important; color: white !important; border-radius: 10px !important; }
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({
            "Formlabs": ["一般樹脂", "Tough 2000", "Flexible 80A", "Rigid 10K"],
            "單價": [6500, 8500, 9500, 12000],
            "每cm3成本": [6.5, 8.5, 9.5, 12.0]
        })

# 3. 登入檢核邏輯
if "password_correct" not in st.session_state:
    apply_login_style()
    st.markdown('<div class="logo-box">', unsafe_allow_html=True)
    try:
        st.image("solidwizard_logo.png", width=250)
    except:
        st.markdown("<h2 style='color:white;'>SOLIDWIZARD</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="user-name">3D列印線上估價系統</div>', unsafe_allow_html=True)
    pwd = st.text_input("密碼", type="password", label_visibility="collapsed", placeholder="請輸入密碼")
    if st.button("進入系統"):
        if pwd == "1234":
            st.session_state["password_correct"] = True
            st.rerun()
        else: st.error("密碼錯誤")
    st.stop()

# 4. 主介面樣式 (登入後解鎖側邊欄並設定大字體)
st.markdown("""
    <style>
    /* 解鎖側邊欄與頁首，並恢復正常背景 */
    [data-testid="stHeader"], [data-testid="stSidebar"] { 
        display: block !important; 
    }
    .stApp { background-color: #F8FAFC !important; }
    
    /* 核心數據加大顯示 */
    [data-testid="stMetricValue"] { font-size: 42px !important; font-weight: 800 !important; color: #1E40AF !important; }

    /* 修正材料選擇框 (Selectbox) 的大字 */
    div[data-baseweb="select"] > div {
        font-size: 32px !important; font-weight: 800 !important; color: #1E40AF !important; height: 80px !important;
        display: flex !important; align-items: center !important;
    }
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        font-size: 32px !important; font-weight: 800 !important; color: #1E40AF !important;
    }

    /* 基本費輸入框樣式 */
    div[data-testid="stNumberInput"] input {
        font-size: 42px !important; font-weight: 800 !important; color: #1E40AF !important; height: 80px !important;
    }

    .result-container { background-color: #FFFFFF; padding: 30px; border-radius: 15px; border: 1px solid #E2E8F0; margin-top: 20px; }
    .big-font { font-size: 24px !important; font-weight: bold !important; color: #1E40AF !important; }
    </style>
""", unsafe_allow_html=True)

# 5. 側邊欄導覽 (現在會顯示了)
with st.sidebar:
    try: st.image("solidwizard_logo.png", use_container_width=True)
    except: st.write("### SOLIDWIZARD")
    st.subheader("🛠️ 功能選單")
    choice = st.radio("請選擇作業項目：", ["💰 自動估價系統", "📏 尺寸校正計算"])
    st.divider()
    if st.button("登出系統"):
        del st.session_state["password_correct"]
        st.rerun()

# 6. 主畫面邏輯
if choice == "💰 自動估價系統":
    st.title("💰 專業 3D 列印自動報價")
    df_m = load_materials()
    input_method = st.radio("選擇體積來源：", ["📤 上傳 STL 檔案", "⌨️ 手動輸入數值"], horizontal=True)
    st.divider()
    vol_cm3 = 0.0
    show_preview = False

    if input_method == "📤 上傳 STL 檔案":
        st.markdown('<span class="big-font">第一步：請上傳 STL 檔案</span>', unsafe_allow_html=True)
        up_file = st.file_uploader("Upload", type=["stl"], label_visibility="collapsed")
        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue()); t_path = tmp.name
            try:
                m_mesh = mesh.Mesh.from_file(t_path)
                v_val, _, _ = m_mesh.get_mass_properties()
                vol_cm3 = float(v_val) / 1000.0; show_preview = True
            except: st.error("STL 解析失敗")
            finally: 
                if os.path.exists(t_path): os.remove(t_path)
    else:
        st.markdown('<span class="big-font">第一步：請手動輸入模型體積 (cm³)</span>', unsafe_allow_html=True)
        col_in, col_ic = st.columns([1.5, 4])
        with col_in: vol_cm3 = st.number_input("體積", min_value=0.0, value=0.0, step=0.1, label_visibility="collapsed")
        with col_ic: st.image("估價01.jpg", width=50) if os.path.exists("估價01.jpg") else None

    if vol_cm3 > 0:
        if show_preview:
            vecs = m_mesh.vectors
            if len(vecs) > 30000: vecs = vecs[::(len(vecs)//30000)]
            p, q, r = vecs.shape; v = vecs.reshape(p*q, r); f = np.arange(p*q).reshape(p, q)
            fig = go.Figure(data=[go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2], color='#475569')])
            fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data'), height=450, margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.image("估價01.jpg", width=250) if os.path.exists("估價01.jpg") else None

        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.subheader("📊 報價參數設定")
        set1, set2, set3, set4 = st.columns([1.2, 2.0, 0.8, 1.0])
        with set1: st.metric("當前體積 (cm³)", f"{vol_cm3:.2f}")
        with set2:
            m_choice = st.selectbox("1. 選擇材料", df_m["Formlabs"].tolist())
            u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
            raw_p = df_m.loc[df_m["Formlabs"] == m_choice, "單價"].values[0]
            st.markdown(f'<p style="font-size:16px; font-weight:bold; color:#64748B; margin-top:5px;">單價: NT$ {int(raw_p):,}/L</p>', unsafe_allow_html=True)
        with set3: markup = st.slider("2. 倍率", 1.0, 10.0, 3.0, 0.1)
        with set4: base_fee = st.number_input("3. 基本費", value=150)
        st.divider()
        res1, res2 = st.columns([1, 5])
        with res1: st.image("估價01.jpg", width=100) if os.path.exists("估價01.jpg") else None
        with res2:
            total = (vol_cm3 * u_cost * markup) + base_fee
            st.markdown("### 建議報價總計")
            st.markdown(f"<h1 style='color:#E11D48; font-size:64px; margin-top:-10px;'>NT$ {int(total):,}</h1>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "📏 尺寸校正計算":
    st.title("📏 尺寸校正補償計算")
    st.divider()
    in1, in2, in3 = st.columns([1, 1, 2])
    with in1: d_size = st.number_input("CAD 設計尺寸 (mm)", value=20.0, step=0.01)
    with in2: a_size = st.number_input("實測成品尺寸 (mm)", value=19.8, step=0.01)
    with in3: st.image("尺寸調整.jpg", width=100) if os.path.exists("尺寸調整.jpg") else None
    if d_size > 0:
        factor = a_size / d_size
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        r1, r2 = st.columns([1, 2])
        with r1:
            st.metric("補償因子", f"{factor:.4f}")
            st.success(f"建議縮放比例：\n## **{(1/factor)*100:.2f}%**")
        with r2: st.image("尺寸調整.jpg", width=300) if os.path.exists("尺寸調整.jpg") else None
        st.markdown('</div>', unsafe_allow_html=True)
