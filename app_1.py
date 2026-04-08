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

# --- 3. 讀取材料資料 (依據上傳的 CSV) ---
@st.cache_data
def load_materials():
    try:
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except:
        # 備援資料
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 終極穩定 3D 預覽 (藍色主體 + 黑色輪廓) ---
def show_3d_preview(file_path):
    try:
        m_data = mesh.Mesh.from_file(file_path)
        vecs = m_data.vectors
        
        # 極限限制：如果超過 30,000 面就抽樣，這能解決 99% 的載入問題
        if len(vecs) > 30000:
            step = len(vecs) // 30000
            vecs = vecs[::step]
        
        p, q, r = vecs.shape
        v = vecs.reshape(p*q, r)
        f = np.arange(p*q).reshape(p, q)
        
        # 使用最輕量的 Mesh3d 設定
        fig = go.Figure(data=[
            go.Mesh3d(
                x=v[:,0], y=v[:,1], z=v[:,2], 
                i=f[:,0], j=f[:,1], k=f[:,2],
                color='royalblue',
                opacity=1.0,
                flatshading=True,
                # 使用 contours 代替雙層 Mesh，減輕一半負擔
                contour=dict(show=True, color='black', width=1),
                lighting=dict(ambient=0.5, diffuse=0.8, specular=0.1),
                showlegend=False
            )
        ])
        
        fig.update_layout(
            scene=dict(
                xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, 
                aspectmode='data', bgcolor='white'
            ),
            margin=dict(l=0, r=0, b=0, t=0), 
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"預覽失敗：{e}")
        st.info("💡 建議嘗試上傳較小的 STL 檔案，或檢查瀏覽器是否支援 WebGL。")

# --- 5. 主程式 ---
if check_password():
    df_m = load_materials()
    
    # 強制 CSS：縮小 image-select 圖示
    st.markdown("""
        <style>
        /* 強制縮小圖片容器 */
        div[data-testid="stHorizontalBlock"] img {
            width: 45px !important;
            height: 45px !important;
            object-fit: contain !important;
        }
        /* 縮小下方文字 */
        div[data-testid="stHorizontalBlock"] p {
            font-size: 11px !important;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 功能選單")
        sel = image_select(
            label="選擇服務", 
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png", 
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ], 
            captions=["自動估價", "尺寸校正"],
            index=0
        )

    if "2953536" in sel:
        st.title("💰 Formlabs 自動估價系統")
        up_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.6, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                st.subheader("📦 3D 結構預覽")
                show_3d_preview(t_path)
            
            with c2:
                st.subheader("📊 數據分析")
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
                base_fee = st.number_input("上機費", value=150)
                
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                st.divider()
                st.markdown(f"### 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
                
                with st.expander("🔍 報價組成明細"):
                    st.write(f"- 材料成本: NT$ {int(vol_cm3 * u_cost)}")
                    st.write(f"- 工時利潤: NT$ {int(vol_cm3 * u_cost * (markup-1))}")
                    st.write(f"- 固定費用: NT$ {base_fee}")
            os.remove(t_path)
        else:
            st.info("💡 請上傳 STL 檔案開始。")
    else:
        st.title("📏 SLA 尺寸校正助手")
        ca = st.number_input("CAD 尺寸", value=10.0)
        re = st.number_input("實測尺寸", value=10.0)
        if ca > 0:
            st.metric("應填入校正因子", f"{(re/ca):.4f}")
