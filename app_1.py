import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面基本配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide", page_icon="🖨️")

# 2. 登入介面專用 CSS (絕對置中樣式)
def apply_login_style():
    st.markdown("""
        <style>
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        .stApp {
            background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%) !important;
            height: 100vh !important; width: 100vw !important;
            display: flex !important; justify-content: center !important; align-items: center !important;
        }
        [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stMainBlockContainer"],
        .main .block-container, .stVerticalBlock {
            display: flex !important; flex-direction: column !important;
            align-items: center !important; justify-content: center !important;
            width: 100% !important; max-width: 100% !important; padding: 0 !important; margin: 0 !important;
        }
        .user-name {
            color: white !important; font-size: 32px !important; font-weight: 600 !important;
            margin: 20px 0 40px 0 !important; text-align: center !important; width: 100% !important;
        }
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 2px solid #3B82F6 !important; border-radius: 6px !important;
            width: 280px !important; margin: 0 auto !important;
        }
        input { color: #000000 !important; text-align: center !important; font-size: 18px !important; }
        div.stButton { display: flex !important; justify-content: center !important; width: 100% !important; margin-top: 25px !important; }
        .stButton button { width: 140px !important; height: 45px !important; background-color: rgba(255, 255, 255, 0.2) !important; color: white !important; }
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
            "每cm3成本": [6.5, 8.5, 9.5, 12.0]
        })

# 3. 登入邏輯
if "password_correct" not in st.session_state:
    apply_login_style()
    try:
        st.image("solidwizard_logo.png", width=250)
    except:
        st.write("🔧 **SolidWizard 3D Printing**")
    st.markdown('<div class="user-name">實威國際 3D列印線上估價</div>', unsafe_allow_html=True)
    pwd = st.text_input("PW", type="password", label_visibility="collapsed", placeholder="請輸入登入密碼")
    if st.button("進入系統"):
        if pwd == "1234":
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("密碼不正確")
    st.stop()

# 4. 登入成功後：系統主介面 (強力修正靠左貼邊)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #F8FAFC !important; }
    [data-testid="stMain"] { padding: 0 !important; margin: 0 !important; display: block !important; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0 !important; margin-left: 0 !important; }
    .main .block-container { max-width: 100% !important; padding: 2rem 3rem 2rem 2rem !important; margin-left: 0 !important; margin-right: auto !important; }
    .sidebar-title { font-size: 20px; font-weight: bold; color: #1E40AF; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 5. 左側功能選單 (Sidebar)
with st.sidebar:
    st.markdown('<div class="sidebar-title">🛠️ 功能選單</div>', unsafe_allow_html=True)
    choice = st.radio("請選擇作業項目：", ["💰 自動估價系統", "📏 尺寸校正計算"], index=0)
    st.divider()
    st.caption("實威國際 SolidWizard")
    st.caption("3D Printing Service Team")
    if st.button("登出系統"):
        del st.session_state["password_correct"]
        st.rerun()

# 6. 右側主畫面邏輯
if choice == "💰 自動估價系統":
    st.title("💰 專業 3D 列印自動報價")
    df_m = load_materials()
    
    # 新增：選擇輸入方式
    input_method = st.radio("選擇體積來源：", ["📤 上傳 STL 檔案", "⌨️ 手動輸入數值"], horizontal=True)
    st.divider()
    
    vol_cm3 = 0.0
    show_preview = False

    if input_method == "📤 上傳 STL 檔案":
        up_file = st.file_uploader("請上傳 STL 模型檔案", type=["stl"])
        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            try:
                m_mesh = mesh.Mesh.from_file(t_path)
                v_val, _, _ = m_mesh.get_mass_properties()
                vol_cm3 = float(v_val) / 1000.0
                show_preview = True
            except Exception as e:
                st.error(f"解析失敗: {e}")
            finally:
                if os.path.exists(t_path): os.remove(t_path)
    else:
        # 手動輸入模式
        vol_cm3 = st.number_input("請輸入模型總體積 (cm³ / ml)", min_value=0.0, value=0.0, step=0.1, help="請參考 PreForm 或其他軟體計算出的體積")

    # 報價計算區塊
    if vol_cm3 > 0:
        c1, c2 = st.columns([1.6, 1])
        
        with c1:
            if show_preview and input_method == "📤 上傳 STL 檔案":
                st.subheader("📦 模型 3D 預覽")
                vecs = m_mesh.vectors
                if len(vecs) > 40000: vecs = vecs[::(len(vecs)//40000)]
                p, q, r = vecs.shape
                v = vecs.reshape(p*q, r)
                f = np.arange(p*q).reshape(p, q)
                fig = go.Figure(data=[go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2], color='#475569')])
                fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data'), height=600, margin=dict(l=0,r=0,b=0,t=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ 目前為手動輸入模式，無 3D 預覽圖。")
                st.image("https://cdn-icons-png.flaticon.com/512/3563/3563437.png", width=200) # 顯示一個示意圖
        
        with c2:
            st.subheader("📊 報價設定")
            st.metric("當前計算體積", f"{vol_cm3:.2f} cm³")
            m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
            u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
            markup = st.slider("2. 利潤加成倍率", 1.0, 10.0, 3.0, 0.1)
            base_fee = st.number_input("3. 基本處理費 (NTD)", value=150)
            
            total = (vol_cm3 * u_cost * markup) + base_fee
            st.divider()
            st.markdown(f"### 建議報價總計")
            st.markdown(f"<h1 style='color:#E11D48; font-size:54px;'>NT$ {int(total):,}</h1>", unsafe_allow_html=True)
    else:
        st.info("💡 請上傳檔案或手動輸入體積以開始計算。")

elif choice == "📏 尺寸校正計算":
    # (維持不變)
    st.title("📏 尺寸校正補償計算")
    col_a, col_b = st.columns(2)
    with col_a:
        d_size = st.number_input("CAD 設計尺寸 (mm)", value=20.0)
        a_size = st.number_input("實測尺寸 (mm)", value=19.8)
    with col_b:
        if d_size > 0:
            factor = a_size / d_size
            st.metric("補償因子", f"{factor:.4f}")
            st.success(f"建議縮放比例: **{(1/factor)*100:.2f}%**")
