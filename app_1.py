import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

st.set_page_config(page_title="3D列印專業報價系統", page_icon="🖨️", layout="wide")

# --- 1. 密碼驗證 ---
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

# --- 2. 讀取材料 ---
@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 3. Trellis 風格預覽 (藍色主體 + 銳利黑色輪廓線) ---
def show_3d_preview(file_path):
    try:
        m_data = mesh.Mesh.from_file(file_path)
        vecs = m_data.vectors
        
        # 為了保持預覽流暢且清晰，適度抽樣
        if len(vecs) > 40000:
            step = len(vecs) // 40000
            vecs = vecs[::step]
        
        p, q, r = vecs.shape
        v = vecs.reshape(p*q, r)
        f = np.arange(p*q).reshape(p, q)
        
        fig = go.Figure()

        # 第一層：高品質藍色實體面 (加入環境光渲染)
        fig.add_trace(go.Mesh3d(
            x=v[:,0], y=v[:,1], z=v[:,2], 
            i=f[:,0], j=f[:,1], k=f[:,2],
            color='#1E40AF', # 深寶藍色
            opacity=1.0,
            flatshading=False, # 使用流暢法向量陰影
            lighting=dict(
                ambient=0.5,      # 環境光，讓陰影處不全黑
                diffuse=0.9,      # 漫反射，增加表面質感
                fresnel=0.5,      # 邊緣光感
                specular=1.2,     # 高光強度，讓邊角發亮
                roughness=0.2     # 表面粗糙度
            ),
            lightposition=dict(x=100, y=200, z=150),
            name='實體'
        ))

        # 第二層：黑色細線邊框 (這就是 Trellis 質感的來源)
        fig.add_trace(go.Mesh3d(
            x=v[:,0], y=v[:,1], z=v[:,2], 
            i=f[:,0], j=f[:,1], k=f[:,2],
            color='black',
            opacity=0.15,      # 線條要淡，才不會干擾視覺
            wireframe=True,
            name='網格線'
        ))

        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='data',
                bgcolor='#F8FAFC', # 使用 Trellis 常見的淺灰白背景
                camera=dict(
                    eye=dict(x=1.3, y=1.3, z=1.3),
                    up=dict(x=0, y=0, z=1)
                )
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=700 # 拉高顯示區域，更專業
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"預覽生成失敗: {e}")

# --- 4. 主程式執行 ---
if check_password():
    df_m = load_materials()
    
    # CSS：縮小選單圖示
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] img {
            width: 45px !important;
            height: 45px !important;
            border-radius: 8px;
            border: 1px solid #E2E8F0;
        }
        div[data-testid="stHorizontalBlock"] p {
            font-size: 11px !important;
            color: #64748B;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 服務控制面板")
        sel = image_select(
            label="選擇功能", 
            images=["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"], 
            captions=["自動報價", "尺寸校正"]
        )

    if "2953536" in sel:
        st.title("💎 高階 STL 在線報價系統")
        up_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.8, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                show_3d_preview(t_path)
            
            with c2:
                st.subheader("📊 結構與成本分析")
                try:
                    m = mesh.Mesh.from_file(t_path)
                    v_val, _, _ = m.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                    st.metric("偵測體積", f"{vol_cm3:.2f} cm³")
                except:
                    st.error("計算失敗")
                
                m_choice = st.selectbox("樹脂型號 (Formlabs)", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                markup = st.slider("報價加成倍率", 1.0, 10.0, 3.0, step=0.1)
                base_fee = st.number_input("上機費 (NTD)", value=150)
                
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                st.divider()
                st.markdown(f"### 📢 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
                
                with st.expander("🔍 報價詳細組成"):
                    cost_raw = vol_cm3 * u_cost
                    st.write(f"- 材料基本費用: NT$ {int(cost_raw)}")
                    st.write(f"- 工時利潤加成: NT$ {int(cost_raw * (markup-1))}")
                    st.write(f"- 上機固定費: NT$ {base_fee}")
            os.remove(t_path)
        else:
            st.info("💡 上傳 STL 檔案即可開啟 Trellis 風格 3D 預覽。")
    else:
        st.title("📏 尺寸補償計算機")
        ca = st.number_input("CAD 尺寸 (mm)", value=10.0)
        re = st.number_input("實測尺寸 (mm)", value=10.0)
        if ca > 0:
            st.metric("Preform 校正因子", f"{(re/ca):.4f}")
