import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面基本配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide", page_icon="🖨️")

# 2. 登入介面專用 CSS
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
            padding: 0 !important;
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

# 4. 主介面樣式 (強制文字黑色以解決手機版看不見的問題)
st.markdown("""
    <style>
    [data-testid="stHeader"], [data-testid="stSidebar"] { display: block !important; }
    .stApp { background-color: #FFFFFF !important; }
    
    /* 強制主畫面標題與一般文字為黑色 */
    h1, h2, h3, p, span, label, div { color: #000000 !important; }

    /* 單選框與 Widget 標籤文字顏色修正 */
    [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }

    /* 當前體積數字顏色 */
    [data-testid="stMetricValue"] { font-size: 42px !important; font-weight: 800 !important; color: #000000 !important; }

    /* 輸入框與選擇框內容文字 */
    div[data-baseweb="select"] > div, div[data-testid="stNumberInput"] input {
        font-size: 28px !important; font-weight: 800 !important; color: #000000 !important;
    }

    /* 容器樣式 */
    .result-container { background-color: #F8FAFC; padding: 20px; border-radius: 15px; border: 1px solid #CBD5E1; }
    
    /* 黃底紅字報價區 (置底顯示) */
    .total-price-box {
        text-align: center; 
        background-color: #FFFF00 !important; 
        padding: 30px; 
        border-radius: 15px;
        border: 5px solid #E11D48;
        margin-top: 30px;
    }
    .total-price-box h1 { color: #E11D48 !important; font-size: 64px !important; margin: 0 !important; font-weight: 900 !important; }
    .total-price-box h3 { color: #000000 !important; margin-bottom: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# 5. 側邊欄導覽
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
        st.write("### 第一步：請上傳 STL 檔案")
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
        st.write("### 第一步：請手動輸入模型體積 (cm³)")
        vol_cm3 = st.number_input("體積", min_value=0.0, value=0.0, step=0.1, label_visibility="collapsed")

    if vol_cm3 > 0:
        # 顯示 3D 預覽或圖片
        if show_preview:
            vecs = m_mesh.vectors
            if len(vecs) > 30000: vecs = vecs[::(len(vecs)//30000)]
            p, q, r = vecs.shape; v = vecs.reshape(p*q, r); f = np.arange(p*q).reshape(p, q)
            fig = go.Figure(data=[go.Mesh3d(x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2], color='#475569')])
            fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data'), height=350, margin=dict(l=0,r=0,b=0,t=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.image("估價01.jpg", width=150) if os.path.exists("估價01.jpg") else None

        # 報價設定區塊
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.subheader("📏 當前體積 (cm³)")
        st.metric("", f"{vol_cm3:.2f}")
        
        st.write("---")
        
        # 1. 材料選擇
        m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
        u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
        raw_p = df_m.loc[df_m["Formlabs"] == m_choice, "單價"].values[0]
        st.write(f"材料單價: NT$ {int(raw_p):,}/L")
        
        # 2. 倍率
        markup = st.slider("2. 利潤倍率調整", 1.0, 10.0, 3.0, 0.1)
        
        # 3. 基本費
        base_fee = st.number_input("3. 報價基本費 (NT$)", value=150)
        
        # 最底部：建議報價總計 (黃底紅字)
        total = (vol_cm3 * u_cost * markup) + base_fee
        st.markdown(f"""
            <div class="total-price-box">
                <h3>建議報價總計</h3>
                <h1>NT$ {int(total):,}</h1>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif choice == "📏 尺寸校正計算":
    st.title("📏 尺寸校正補償計算")
    st.divider()
    d_size = st.number_input("CAD 設計尺寸 (mm)", value=20.0, step=0.01)
    a_size = st.number_input("實測成品尺寸 (mm)", value=19.8, step=0.01)
    
    if d_size > 0:
        factor = a_size / d_size
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.metric("補償因子", f"{factor:.4f}")
        st.success(f"建議縮放比例：{(1/factor)*100:.2f}%")
        st.image("尺寸調整.jpg", use_container_width=True) if os.path.exists("尺寸調整.jpg") else None
        st.markdown('</div>', unsafe_allow_html=True)
