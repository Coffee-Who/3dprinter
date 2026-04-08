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

# --- 3. 3D 預覽函數 ---
def show_3d_preview(file_path):
    try:
        m_data = mesh.Mesh.from_file(file_path)
        vecs = m_data.vectors
        if len(vecs) > 25000:
            step = len(vecs) // 25000
            vecs = vecs[::step]
        
        p, q, r = vecs.shape
        v = vecs.reshape(p*q, r)
        f = np.arange(p*q).reshape(p, q)
        
        fig = go.Figure(data=[go.Mesh3d(
            x=v[:,0], y=v[:,1], z=v[:,2], i=f[:,0], j=f[:,1], k=f[:,2],
            color='royalblue', opacity=1.0, flatshading=True,
            line=dict(color='black', width=1), showlegend=False
        )])
        fig.update_layout(
            scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data'),
            margin=dict(l=0, r=0, b=0, t=0), height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("⚠️ 預覽暫時無法載入")

# --- 4. 主程式 ---
if check_password():
    df_m = load_materials()
    with st.sidebar:
        sel = image_select(
            label="功能選單", 
            images=["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"], 
            captions=["自動估價", "尺寸校正"]
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
                st.subheader("📦 3D 網格結構分析")
                show_3d_preview(t_path)
            
            with c2:
                st.subheader("📊 數據分析與報價")
                try:
                    m = mesh.Mesh.from_file(t_path)
                    v_val, _, _ = m.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                    st.metric("偵測體積", f"{vol_cm3:.2f} cm³")
                except:
                    st.error("體積計算失敗")
                
                # 材料與單價
                m_choice = st.selectbox("樹脂型號 (來自 Excel)", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                
                # 計算設定
                markup = st.slider("報價倍率 (含利潤與損耗)", 1.0, 5.0, 1.0, step=0.1)
                base_fee = st.number_input("上機基本費 ", value=150)
                
                # 總價計算
                material_total = vol_cm3 * u_cost
                markup_total = material_total * (markup - 1)
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                
                st.divider()
                st.markdown(f"### 📢 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
                
                # --- 重新加入細項說明 ---
                with st.expander("🔍 查看報價組成細項"):
                    st.write(f"1. **材料原始成本**: NT$ {int(material_total)} ({vol_cm3:.2f} cm³ × {u_cost:.2f} 元)")
                    st.write(f"2. **加工與利潤加成**: NT$ {int(markup_total)} (倍率 x{markup})")
                    st.write(f"3. **固定費用**: NT$ {base_fee} 元")
                    st.info(f"計算公式: (體積 × 單價 × 倍率) + 固定費")
            
            os.remove(t_path)
        else:
            st.info("💡 請上傳 STL 檔案開始估價。")
    else:
        st.title("📏 SLA 尺寸校正助手")
        ca = st.number_input("CAD 設計尺寸 (mm)", value=10.0)
        re = st.number_input("實測尺寸 (mm)", value=10.0)
        if ca > 0:
            st.metric("Preform 校正因子", f"{(re/ca):.4f}")
