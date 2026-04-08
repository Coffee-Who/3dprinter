import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面基本配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide", page_icon="🖨️")

# 2. 全域樣式優化
st.markdown("""
    <style>
    /* --- 登入頁面專用樣式 --- */
    /* 讓登入按鈕變成白底藍字 */
    div.stButton > button:first-child {
        background-color: #FFFFFF !important;
        color: #1E40AF !important;
        border: 2px solid #FFFFFF !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    
    /* --- 手機版懸浮選單按鈕 --- */
    [data-testid="stSidebarCollapseButton"] {
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        z-index: 999999 !important;
        background-color: #1E40AF !important;
        color: white !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3) !important;
    }
    [data-testid="stSidebarCollapseButton"] svg { fill: white !important; }

    /* 背景與基礎文字 */
    .stApp { background-color: #FFFFFF !important; }
    h1, h2, h3, p, span, label { color: #000000 !important; font-family: "Microsoft JhengHei", sans-serif; }

    /* --- 輸入框樣式 --- */
    /* Upload 區塊：白底黑字 */
    div[data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important; 
        color: #000000 !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 8px !important;
        max-width: 250px !important; 
    }

    /* 其餘輸入框 (數字、選單)：藍底白字且縮小 */
    div[data-testid="stNumberInput"], div[data-baseweb="select"] {
        max-width: 200px !important; 
    }
    div[data-testid="stNumberInput"] input, div[data-baseweb="select"] > div {
        background-color: #1E40AF !important; 
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    div[data-testid="stNumberInput"] input, div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        -webkit-text-fill-color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* 建議報價結果：黃底紅字 */
    .price-result {
        display: inline-block;
        background-color: #FFFF00 !important;
        color: #E11D48 !important;
        padding: 5px 15px;
        border-radius: 8px;
        font-size: 42px !important;
        font-weight: 900 !important;
        border: 3px solid #E11D48;
    }

    /* 分析內容區塊 */
    .analysis-box {
        background-color: #F8FAFC;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1E40AF;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 登入介面邏輯
if "password_correct" not in st.session_state:
    # 登入背景設定
    st.markdown("""
        <style>
        .stApp { background: radial-gradient(circle at center, #1E40AF 0%, #0F172A 100%) !important; }
        h2 { color: white !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>實威國際 3D列印報價系統</h2>", unsafe_allow_html=True)
    
    # 置中登入框
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        pwd = st.text_input("請輸入登入密碼", type="password")
        if st.button("確認登入"):
            if pwd == "1234":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("密碼錯誤，請重新輸入")
    st.stop()

# 4. 資料庫 (材料單價)
@st.cache_data
def load_materials():
    data = {
        "Formlabs": ["Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K"],
        "單價": [9975, 8500, 7500, 12000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df

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

# 6. 主程式內容
df_m = load_materials()

if choice == "💰 自動估價系統":
    st.title("💰 專業 3D 列印自動報價")
    input_method = st.radio("體積來源：", ["📤 上傳 STL", "⌨️ 手動輸入"], horizontal=True)
    st.divider()
    
    vol_mm3 = 0
    if input_method == "📤 上傳 STL":
        up_file = st.file_uploader("Upload", type=["stl"], label_visibility="collapsed")
        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue()); t_path = tmp.name
            try:
                m_mesh = mesh.Mesh.from_file(t_path)
                v_val, _, _ = m_mesh.get_mass_properties()
                vol_mm3 = int(v_val)
            except: st.error("STL 解析失敗")
            finally: 
                if os.path.exists(t_path): os.remove(t_path)
    else:
        vol_mm3 = st.number_input("手動輸入體積 (mm³)", min_value=0, value=0, step=1, format="%d")

    if vol_mm3 > 0:
        st.write(f"**📐 當前模型體積:** {vol_mm3:,} mm³")
        col1, col2 = st.columns(2)
        with col1:
            m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
            u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每mm3成本"].values[0]
            raw_p = df_m.loc[df_m["Formlabs"] == m_choice, "單價"].values[0]
            st.info(f"💡 材料成本：NT$ {u_cost:.6f}/mm³")
        
        with col2:
            markup = st.slider("2. 利潤倍率", 0.5, 10.0, 3.0, 0.5)
            base_fee = st.number_input("3. 基本報價費 (NT$)", min_value=0, value=0, step=10, format="%d")

        # 計算
        mat_cost_total = vol_mm3 * u_cost
        total_price = (mat_cost_total * markup) + base_fee
        profit = total_price - mat_cost_total
        profit_rate = (profit / total_price * 100) if total_price > 0 else 0

        st.divider()
        st.write("### 建議報價總計")
        st.markdown(f'NT$ <span class="price-result">{int(total_price):,}</span>', unsafe_allow_html=True)

        # 分析區塊
        st.markdown(f"""
            <div class="analysis-box">
                <h4>📊 報價結構分析</h4>
                <p>🧪 <b>純材料成本：</b> NT$ {mat_cost_total:,.2f}</p>
                <p>💵 <b>預估利潤 (含基本費)：</b> NT$ {profit:,.2f}</p>
                <p>📈 <b>利潤佔比：</b> {profit_rate:.1f}%</p>
                <p>⚙️ <b>計算方式：</b> (體積 × mm³成本 × 倍率) + 基本費</p>
            </div>
        """, unsafe_allow_html=True)

elif choice == "📏 尺寸校正計算":
    st.title("📏 尺寸補償計算")
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        d_size = st.number_input("CAD 設計尺寸 (mm)", min_value=0.01, value=20.00, step=0.01)
        a_size = st.number_input("實測成品尺寸 (mm)", min_value=0.01, value=19.80, step=0.01)
    
    if d_size > 0:
        factor = a_size / d_size
        suggested_scale = (1 / factor) * 100 if factor != 0 else 0
        st.write("### 補償結果")
        st.metric("補償因子 (Factor)", f"{factor:.4f}")
        st.markdown(f'建議比例：<span class="price-result">{suggested_scale:.2f}%</span>', unsafe_allow_html=True)
