import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面基本配置
st.set_page_config(
    page_title="實威國際 3D列印線上估價", 
    layout="wide", 
    page_icon="🖨️"
)

# 2. 登入介面專用 CSS (維持絕對置中與黑色字體)
def apply_login_style():
    st.markdown("""
        <style>
        /* 登入時隱藏側邊欄與頁首 */
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
            "Formlabs": ["一般樹脂 (Clear/Grey/White)", "Tough 2000", "Flexible 80A", "Rigid 10K"],
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
            st.error("密碼不正確，請重新輸入。")
    st.stop()

# 4. 登入成功後：系統主介面樣式恢復
st.markdown("""
    <style>
    /* 恢復淺色背景與正常排版 */
    .stApp { background: #F8FAFC !important; align-items: flex-start !important; justify-content: flex-start !important; height: auto !important; }
    [data-testid="stAppViewContainer"], .main .block-container { 
        display: block !important; max-width: 1200px !important; margin: 0 auto !important; padding: 1.5rem 2rem !important; 
    }
    [data-testid="stSidebar"] { display: block !important; background-color: #FFFFFF !important; }
    [data-testid="stHeader"] { display: block !important; }
    
    /* 側邊欄標題樣式 */
    .sidebar-title { font-size: 20px; font-weight: bold; color: #1E40AF; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 5. 左側功能選單 (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-title">🛠️ 功能選單</div>', unsafe_allow_html=True)
    
    # 使用原生 radio 元件，保證切換穩定度
    choice = st.radio(
        "請選擇作業項目：",
        ["💰 自動估價系統", "📏 尺寸校正計算"],
        index=0,
        help="切換不同的 3D 列印工具"
    )
    
    st.divider()
    
    # 放置一些輔助資訊
    st.caption("實威國際 SolidWizard")
    st.caption("3D Printing Service Team")
    
    if st.button("登出系統"):
        del st.session_state["password_correct"]
        st.rerun()

# ==========================================
# 6. 右側主畫面邏輯
# ==========================================

# --- A. 自動估價系統 ---
if choice == "💰 自動估價系統":
    st.title("💰 專業 3D 列印自動報價")
    st.write("上傳您的 STL 檔案，系統將自動分析體積並提供建議售價。")
    st.divider()
    
    df_m = load_materials()
    up_file = st.file_uploader("第一步：請點擊或拖拽上傳 STL 模型檔案", type=["stl"])
    
    if up_file:
        c1, c2 = st.columns([1.6, 1])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
            tmp.write(up_file.getvalue())
            t_path = tmp.name
        
        try:
            m_mesh = mesh.Mesh.from_file(t_path)
            v_val, _, _ = m_mesh.get_mass_properties()
            vol_cm3 = float(v_val) / 1000.0
            
            with c1:
                st.subheader("📦 模型 3D 預覽")
                # 優化預覽效能
                vecs = m_mesh.vectors
                if len(vecs) > 40000: vecs = vecs[::(len(vecs)//40000)]
                p, q, r = vecs.shape
                v = vecs.reshape(p*q, r)
                f = np.arange(p*q).reshape(p, q)
                
                fig = go.Figure(data=[go.Mesh3d(
                    x=v[:,0], y=v[:,1], z=v[:,2], 
                    i=f[:,0], j=f[:,1], k=f[:,2], 
                    color='#475569', opacity=1.0,
                    flatshading=False
                )])
                fig.update_layout(
                    scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data'),
                    height=600, margin=dict(l=0,r=0,b=0,t=0)
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.subheader("📊 報價設定")
                st.metric("偵測模型體積", f"{vol_cm3:.2f} cm³")
                
                st.divider()
                m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                
                markup = st.slider("2. 利潤加成倍率 (Markup)", 1.0, 10.0, 3.0, 0.1)
                base_fee = st.number_input("3. 基本處理費 (NTD)", value=150)
                
                total = (vol_cm3 * u_cost * markup) + base_fee
                
                st.divider()
                st.markdown("### 建議報價總計")
                st.markdown(f"<h1 style='color:#E11D48; font-size:54px;'>NT$ {int(total):,}</h1>", unsafe_allow_html=True)
                st.caption("＊計算公式：(體積 × 單價 × 倍率) + 基本費")

        except Exception as e:
            st.error(f"模型解析失敗，請確認檔案是否為標準 STL 格式。錯誤訊息: {e}")
        finally:
            if os.path.exists(t_path): os.remove(t_path)
    else:
        st.info("💡 尚未上傳檔案，請先在上方區域上傳您的 3D 模型。")

# --- B. 尺寸校正計算 ---
elif choice == "📏 尺寸校正計算":
    st.title("📏 尺寸校正補償計算")
    st.write("根據實際列印出的成品尺寸與原設計尺寸，計算精確的收縮補償比例。")
    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📋 輸入參數")
        d_size = st.number_input("CAD 原設計尺寸 (mm)", value=20.0, min_value=0.1, step=0.1)
        a_size = st.number_input("列印成品實測尺寸 (mm)", value=19.8, min_value=0.1, step=0.1)
    
    with col_b:
        st.markdown("### 📐 計算結果")
        if d_size > 0:
            factor = a_size / d_size
            error_percent = (1 - factor) * 100
            
            st.metric("補償因子 (Scale Factor)", f"{factor:.4f}")
            st.metric("尺寸偏差率", f"{error_percent:.2f}%")
            
            st.divider()
            st.success(f"**建議解決方案：**\n\n請在 PreForm 或 CAD 軟體中將模型縮放設為：\n## **{(1/factor)*100:.2f}%**")
