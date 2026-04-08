import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

st.set_page_config(page_title="3D列印專業服務系統", page_icon="🖨️", layout="wide")

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

# --- 3. 高品質 3D 預覽 (修正簡化過度問題) ---
def show_3d_preview(file_path):
    try:
        m_data = mesh.Mesh.from_file(file_path)
        vecs = m_data.vectors
        total_faces = len(vecs)
        
        # 動態調整：只有超過 60,000 面才會開始簡化，且最多保留到 40,000 面
        if total_faces > 60000:
            st.info(f"💡 原始模型面數較高 ({total_faces})，已自動進行輕量化優化。")
            target_faces = 40000
            step = total_faces // target_faces
            vecs = vecs[::step]
        
        p, q, r = vecs.shape
        v = vecs.reshape(p*q, r)
        f = np.arange(p*q).reshape(p, q)
        
        fig = go.Figure()

        # 實體面：使用較亮的藍色與更好的陰影
        fig.add_trace(go.Mesh3d(
            x=v[:,0], y=v[:,1], z=v[:,2], 
            i=f[:,0], j=f[:,1], k=f[:,2],
            color='#3B82F6', # 更亮的藍色
            opacity=1.0,
            flatshading=False,
            lighting=dict(ambient=0.4, diffuse=0.8, specular=0.2, roughness=0.5),
            name='實體'
        ))

        # 銳利黑線：大幅降低透明度，讓它看起來像淡淡的工程網格
        fig.add_trace(go.Mesh3d(
            x=v[:,0], y=v[:,1], z=v[:,2], 
            i=f[:,0], j=f[:,1], k=f[:,2],
            color='black',
            opacity=0.15, # 調淡黑線，避免干擾視覺
            wireframe=True,
            name='網格'
        ))

        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                aspectmode='data',
                bgcolor='white',
                camera=dict(eye=dict(x=1.2, y=1.2, z=1.2))
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=650
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"預覽生成失敗: {e}")

# --- 4. 主程式執行 ---
if check_password():
    df_m = load_materials()
    
    # CSS：精準縮小選單圖示
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] img {
            width: 45px !important;
            height: 45px !important;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        div[data-testid="stHorizontalBlock"] p {
            font-size: 11px !important;
            margin-top: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 功能選單")
        sel = image_select(
            label="請選擇服務", 
            images=["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"], 
            captions=["自動估價", "尺寸校正"]
        )

    if "2953536" in sel:
        st.title("💰 3D列印報價系統 (高品質預覽)")
        up_file = st.file_uploader("上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.6, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                show_3d_preview(t_path)
            
            with c2:
                st.subheader("📊 數據分析")
                try:
                    m = mesh.Mesh.from_file(t_path)
                    v_val, _, _ = m.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                    st.metric("模型總體積", f"{vol_cm3:.2f} cm³")
                except:
                    st.error("計算失敗")
                
                m_choice = st.selectbox("樹脂型號", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                markup = st.slider("報價倍率", 1.0, 10.0, 3.0, step=0.1)
                base_fee = st.number_input("上機費 (固定費)", value=150)
                
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                st.divider()
                st.markdown(f"### 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
                
                with st.expander("🔍 價格明細"):
                    cost_raw = vol_cm3 * u_cost
                    st.write(f"- 材料基本成本: NT$ {int(cost_raw)}")
                    st.write(f"- 倍率加成利潤: NT$ {int(cost_raw * (markup-1))}")
                    st.write(f"- 固定成本(上機費): NT$ {base_fee}")
            os.remove(t_path)
        else:
            st.info("💡 請上傳 STL 檔案開始分析。")
    else:
        st.title("📏 SLA 尺寸校正助手")
        ca = st.number_input("CAD 設計值", value=10.0)
        re = st.number_input("實測值", value=10.0)
        if ca > 0:
            st.metric("應填入校正因子", f"{(re/ca):.4f}")
