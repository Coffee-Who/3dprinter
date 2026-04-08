import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面設定
st.set_page_config(page_title="3D報價系統", layout="wide")

# 2. 密碼驗證
if "auth" not in st.session_state:
    st.title("🔒 系統登入")
    pwd = st.text_input("請輸入密碼", type="password")
    if st.button("登入"):
        if pwd == "1234":
            st.session_state["auth"] = True
            st.rerun()
        else: st.error("密碼錯誤")
    st.stop()

# 3. 讀取 CSV 資料
@st.cache_data
def load_data():
    try: return pd.read_csv("Formlabs材料.csv")
    except: return pd.DataFrame({"Formlabs": ["標準樹脂"], "單價": [10000]})

df_m = load_data()

# 4. 側邊欄 CSS 與 選單
st.markdown("<style>div[data-testid='stHorizontalBlock'] img {width:45px !important; height:45px !important; border-radius:5px;}</style>", unsafe_allow_html=True)
with st.sidebar:
    st.title("🛠️ 選單")
    sel = image_select("切換功能", ["https://cdn-icons-png.flaticon.com/512/2953/2953536.png", "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"], ["自動報價", "尺寸校正"])

# 5. 主程式邏輯
if "2953536" in sel: # 報價功能
    st.title("💰 3D列印自動報價 (高品質預覽)")
    f = st.file_uploader("請上傳 STL 檔案", type=["stl"])
    
    if f:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
            tmp.write(f.getvalue())
            path = tmp.name
        
        c1, c2 = st.columns([1.8, 1])
        # 讀取模型
        m = mesh.Mesh.from_file(path)
        vol = float(m.get_mass_properties()[0]) / 1000.0
        
        with c1:
            # --- 修正後的 3D 預覽邏輯 ---
            # 抽樣以維持效能
            v = m.vectors
            if len(v) > 30000: v = v[::(len(v)//30000)]
            
            # 轉換為 Plotly 格式
            p, q, r = v.shape
            pts = v.reshape(p*q, r)
            faces = np.arange(p*q).reshape(p, q)
            
            # 建立 Trellis 風格圖表
            fig = go.Figure()
            # 藍色主體
            fig.add_trace(go.Mesh3d(
                x=pts[:,0], y=pts[:,1], z=pts[:,2],
                i=faces[:,0], j=faces[:,1], k=faces[:,2],
                color='#1E40AF', opacity=1.0, flatshading=False,
                lighting=dict(ambient=0.5, diffuse=0.8, specular=1, roughness=0.3)
            ))
            # 銳利黑邊線 (不使用會報錯的 contour)
            fig.add_trace(go.Mesh3d(
                x=pts[:,0], y=pts[:,1], z=pts[:,2],
                i=faces[:,0], j=faces[:,1], k=faces[:,2],
                color='black', opacity=0.1, wireframe=True
            ))
            
            fig.update_layout(
                scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', bgcolor='white'),
                margin=dict(l=0, r=0, b=0, t=0), height=650
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.metric("偵測體積", f"{vol:.2f} cm³")
            mat = st.selectbox("材料型號", df_m["Formlabs"].tolist())
            u_p = df_m.loc[df_m["Formlabs"] == mat, "單價"].values[0] / 1000
            mark = st.slider("報價倍率", 1.0, 10.0, 3.0, 0.1)
            fee = st.number_input("上機費", value=150)
            
            total = (vol * u_p * mark) + fee
            st.divider()
            st.markdown(f"### 📢 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(total)}</span>", unsafe_allow_html=True)
            with st.expander("🔍 報價組成細項"):
                st.write(f"- 材料費: {int(vol * u_p)} 元")
                st.write(f"- 潤加工: {int(vol * u_p * (mark-1))} 元")
                st.write(f"- 上機費: {fee} 元")
        
        os.remove(path)
else: # 尺寸校正
    st.title("📏 尺寸校正助手")
    ca = st.number_input("CAD 尺寸 (mm)", value=10.0)
    re = st.number_input("實測尺寸 (mm)", value=10.0)
    if ca > 0:
        st.metric("校正因子 (填入 Preform)", f"{(re/ca):.4f}")
