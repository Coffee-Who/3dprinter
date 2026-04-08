import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面基本設定
st.set_page_config(page_title="3D列印專業服務系統", page_icon="🖨️", layout="wide")

# --- 2. 密碼驗證系統 ---
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

# --- 3. 讀取材料資料 ---
@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 修正版 3D 預覽 (提高相容性) ---
def show_3d_preview(file_path):
    try:
        m_data = mesh.Mesh.from_file(file_path)
        vecs = m_data.vectors
        
        # 強制大幅抽樣以確保網頁不當掉
        max_faces = 12000
        if len(vecs) > max_faces:
            step = len(vecs) // max_faces
            vecs = vecs[::step]
        
        p, q, r = vecs.shape
        v = vecs.reshape(p*q, r)
        f = np.arange(p*q).reshape(p, q)
        
        # 使用 Mesh3d 同時渲染面與邊線
        fig = go.Figure(data=[
            go.Mesh3d(
                x=v[:,0], y=v[:,1], z=v[:,2], 
                i=f[:,0], j=f[:,1], k=f[:,2],
                color='royalblue', 
                opacity=1.0,
                flatshading=True,
                # 這裡強制開啟網格線條
                contour=dict(show=True, color='black', width=1),
                showlegend=False
            )
        ])
        
        fig.update_layout(
            scene=dict(
                xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, 
                aspectmode='data', bgcolor='white'
            ),
            margin=dict(l=0, r=0, b=0, t=0), height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"預覽生成失敗。原因: {e}")

# --- 5. 主程式執行 ---
if check_password():
    df_m = load_materials()
    
    # 強力版 CSS：縮小 image-select 圖示並修正跑位
    st.markdown("""
        <style>
        /* 鎖定所有 image-select 內的圖片容器 */
        div[data-testid="stHorizontalBlock"] div[style*="width"] img {
            width: 50px !important;
            height: 50px !important;
            max-width: 50px !important;
            object-fit: contain !important;
        }
        /* 縮小下方文字標題大小 */
        div[data-testid="stHorizontalBlock"] p {
            font-size: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 功能選單")
        # 這裡的圖示會被上方的 CSS 縮小
        sel = image_select(
            label="請選擇服務項目", 
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png", 
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ], 
            captions=["自動估價", "尺寸校正"],
            index=0
        )

    if "2953536" in sel:
        st.title("💰 3D列印自動估價系統")
        up_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.5, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                st.subheader("📦 3D 結構分析")
                show_3d_preview(t_path)
            
            with c2:
                st.subheader("📊 報價數據")
                try:
                    m = mesh.Mesh.from_file(t_path)
                    v_val, _, _ = m.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                    st.metric("偵測體積", f"{vol_cm3:.2f} cm³")
                except:
                    st.error("計算失敗")
                
                m_choice = st.selectbox("樹脂型號", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                
                markup = st.slider("報價倍率", 1.0, 10.0, 3.0, step=0.1)
                base_fee = st.number_input("起鍋費", value=150)
                
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                
                st.divider()
                st.markdown(f"### 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
                
                with st.expander("🔍 查看細項"):
                    st.write(f"- 材料成本: NT$ {int(vol_cm3 * u_cost)}")
                    st.write(f"- 倍率加成: x{markup}")
                    st.write(f"- 固定費用: NT$ {base_fee}")
            
            os.remove(t_path)
        else:
            st.info("💡 請上傳 STL 檔案。")

    else:
        st.title("📏 SLA 尺寸校正助手")
        ca = st.number_input("CAD 尺寸 (mm)", value=10.0)
        re = st.number_input("實測尺寸 (mm)", value=10.0)
        if ca > 0:
            st.metric("Preform 校正因子", f"{(re/ca):.4f}")
