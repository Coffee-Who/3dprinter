import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np

# 1. 頁面基本配置
st.set_page_config(page_title="實威國際 3D列印線上估價", layout="wide", page_icon="🖨️")

# 2. 全域 CSS 樣式
st.markdown("""
    <style>
    /* 手機版懸浮選單按鈕 */
    [data-testid="stSidebarCollapseButton"] {
        position: fixed !important; top: 15px !important; left: 15px !important;
        z-index: 999999 !important; background-color: #1E40AF !important;
        color: white !important; border-radius: 50% !important;
        width: 48px !important; height: 48px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.4) !important;
    }
    
    .stApp { background-color: #FFFFFF !important; }
    
    /* 建議報價結果：黃底紅字 */
    .price-result {
        display: inline-block; background-color: #FFFF00 !important; color: #E11D48 !important;
        padding: 10px 20px; border-radius: 8px; font-size: 38px !important; font-weight: 900 !important;
        border: 3px solid #E11D48;
    }

    /* 藍底白字輸入框樣式 */
    div[data-testid="stNumberInput"] input, div[data-baseweb="select"] > div {
        background-color: #1E40AF !important; color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. 登入介面
if "password_correct" not in st.session_state:
    st.markdown("<style>.stApp { background: #0F172A !important; }</style>", unsafe_allow_html=True)
    st.markdown("<div style='height: 15vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:white;'>實威國際 3D列印報價系統</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        pwd = st.text_input("登入密碼", type="password")
        if st.button("確認登入"):
            if pwd == "1234":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("密碼錯誤")
    st.stop()

# 4. 資料庫
@st.cache_data
def load_materials():
    data = {
        "Formlabs": ["Clear Resin V4", "Tough 2000", "Grey Pro", "Rigid 10K"],
        "單價": [9975, 8500, 7500, 12000]
    }
    df = pd.DataFrame(data)
    df['每mm3成本'] = df['單價'] / 1000000 
    return df

# 5. 側邊欄
with st.sidebar:
    st.write("### SOLIDWIZARD")
    choice = st.radio("功能選單：", ["💰 自動估價系統", "📏 尺寸校正計算"])
    if st.button("登出系統"):
        del st.session_state["password_correct"]
        st.rerun()

# 6. 主程式
df_m = load_materials()

if choice == "💰 自動估價系統":
    st.title("💰 專業 3D 列印自動報價")
    input_method = st.radio("體積來源：", ["📤 上傳 STL", "⌨️ 手動輸入"], horizontal=True)
    st.divider()
    
    vol_mm3 = 0

    if input_method == "📤 上傳 STL":
        up_file = st.file_uploader("請選擇 STL 檔案", type=["stl"])
        
        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            try:
                m_mesh = mesh.Mesh.from_file(t_path)
                v_val, _, _ = m_mesh.get_mass_properties()
                vol_mm3 = int(abs(v_val)) # 確保體積為正值
                
                # --- 核心：高解析度著色渲染 ---
                st.write("📦 **高解析度模型預覽**")
                
                # 重新獲取頂點座標與面索引
                # 使用簡化的頂點提取方式以維持結構完整
                verts = m_mesh.vectors.reshape(-1, 3)
                
                # 動態調整點數：如果模型真的太巨大，才進行微量抽樣，否則保持原樣
                if len(verts) > 90000:
                    verts = verts[::3] 
                
                x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]
                i = np.arange(0, len(x), 3)
                j = i + 1
                k = i + 2

                fig = go.Figure(data=[
                    go.Mesh3d(
                        x=x, y=y, z=z,
                        i=i, j=j, k=k,
                        color='#D1D5DB', # 質感淺灰
                        opacity=1.0,
                        flatshading=False, # 關閉面著色，開啟平滑著色
                        lighting=dict(
                            ambient=0.5,
                            diffuse=0.9,
                            specular=0.5,
                            roughness=0.2,
                            fresnel=0.2
                        ),
                        lightposition=dict(x=1000, y=1000, z=1000)
                    )
                ])
                
                fig.update_layout(
                    scene=dict(
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False),
                        zaxis=dict(visible=False),
                        aspectmode='data',
                        bgcolor='#111827' # 深色背景，讓灰模型更醒目
                    ),
                    margin=dict(l=0, r=0, b=0, t=0),
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
            except Exception as e:
                st.error(f"模型解析失敗，請確認檔案格式。")
            finally: 
                if os.path.exists(t_path): os.remove(t_path)
    else:
        vol_mm3 = st.number_input("手動輸入體積 (mm³)", min_value=0, value=0)

    if vol_mm3 > 0:
        st.write(f"**📐 模型體積:** {vol_mm3:,} mm³")
        col1, col2 = st.columns(2)
        with col1:
            m_choice = st.selectbox("1. 選擇列印材料", df_m["Formlabs"].tolist())
            u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每mm3成本"].values[0]
        with col2:
            markup = st.slider("2. 利潤倍率", 0.5, 10.0, 1.0, 0.5)
            base_fee = st.number_input("3. 基本報價費 (NT$)", min_value=0, value=0)

        # 計算
        total_price = (vol_mm3 * u_cost * markup) + base_fee
        st.divider()
        st.write("### 建議報價總計")
        st.markdown(f'NT$ <span class="price-result">{total_price:,.1f}</span>', unsafe_allow_html=True)

        # 報價分析
        st.markdown(f"""
            <div class="analysis-box">
                <h4>📊 報價分析詳情</h4>
                <p>📏 <b>模型體積：</b> {vol_mm3:,} mm³</p>
                <p>🧪 <b>材料成本：</b> NT$ {vol_mm3 * u_cost:,.2f}</p>
                <p>📈 <b>利潤佔比：</b> {((total_price - vol_mm3*u_cost)/total_price*100):.1f}%</p>
            </div>
        """, unsafe_allow_html=True)

elif choice == "📏 尺寸校正計算":
    st.title("📏 尺寸補償計算")
    d_size = st.number_input("CAD 設計尺寸 (mm)", value=20.0, step=0.1)
    a_size = st.number_input("實測成品尺寸 (mm)", value=19.8, step=0.1)
    if d_size > 0:
        res = (1 / (a_size/d_size)) * 100
        st.write("### 建議補償比例")
        st.markdown(f'<span class="price-result">{res:.2f}%</span>', unsafe_allow_html=True)
