import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面基礎配置
st.set_page_config(page_title="3D列印專業報價系統", layout="wide", page_icon="🖨️")

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
        # 讀取您上傳的 Formlabs材料.csv
        df = pd.read_csv("Formlabs材料.csv")
        # 確保單價轉換為每cm3成本
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except Exception:
        # 備援資料：若檔案讀取失敗時顯示
        return pd.DataFrame({"Formlabs": ["標準樹脂 (Default)"], "每cm3成本": [10.0]})

# --- 4. 主程式執行 ---
if check_password():
    df_m = load_materials()
    
    # 【關鍵】注入 CSS 縮小功能選單圖示
    st.markdown("""
        <style>
        /* 縮小 image-select 的圖片容器 */
        div[data-testid="stHorizontalBlock"] img {
            width: 45px !important;
            height: 45px !important;
            border-radius: 8px !important;
            object-fit: contain !important;
            border: 1px solid #E2E8F0;
        }
        /* 調整選單文字大小 */
        div[data-testid="stHorizontalBlock"] p {
            font-size: 11px !important;
            margin-top: 5px !important;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 功能選單")
        sel = image_select(
            label="請選擇服務項目", 
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png", 
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ], 
            captions=["自動估價", "尺寸校正"],
            index=0
        )

    # --- 5. 自動估價功能 ---
    if "2953536" in sel:
        st.title("💰 專業 3D 列印自動估價")
        up_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])
        
        c1, c2 = st.columns([1.8, 1])
        vol_cm3 = 0.0

        if up_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                # --- 6. Trellis 風格 3D 預覽 (修正版) ---
                try:
                    m_mesh = mesh.Mesh.from_file(t_path)
                    vecs = m_mesh.vectors
                    
                    # 動態抽樣：避免網頁崩潰且維持清晰度
                    if len(vecs) > 40000:
                        step = len(vecs) // 40000
                        vecs = vecs[::step]
                    
                    p, q, r = vecs.shape
                    v = vecs.reshape(p*q, r)
                    f = np.arange(p*q).reshape(p, q)
                    
                    fig = go.Figure(data=[
                        go.Mesh3d(
                            x=v[:,0], y=v[:,1], z=v[:,2],
                            i=f[:,0], j=f[:,1], k=f[:,2],
                            color='#1E40AF', # 深寶藍
                            opacity=1.0,
                            flatshading=False,
                            # 強化光澤感
                            lighting=dict(ambient=0.5, diffuse=0.8, specular=1.5, roughness=0.2),
                            # 顯示輪廓線 (取代會報錯的 wireframe)
                            contour=dict(show=True, color='black', width=1)
                        )
                    ])
                    
                    fig.update_layout(
                        scene=dict(
                            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, 
                            aspectmode='data', bgcolor='white'
                        ),
                        margin=dict(l=0, r=0, b=0, t=0), height=650
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 計算體積
                    v_val, _, _ = m_mesh.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                    
                except Exception as e:
                    st.error(f"預覽生成失敗：{e}")
            
            with c2:
                st.subheader("📊 數據分析與報價")
                st.metric("偵測模型體積", f"{vol_cm3:.2f} cm³")
                
                m_choice = st.selectbox("樹脂型號 (依據 Excel)", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                
                markup = st.slider("報價倍率 (加工/利潤)", 1.0, 10.0, 3.0, step=0.1)
                base_fee = st.number_input("上機固定費", value=150)
                
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                
                st.divider()
                st.markdown(f"### 📢 建議報價: <span style='color:red; font-size:40px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
                
                with st.expander("🔍 查看報價組成細項"):
                    st.write(f"1. **材料原始成本**: NT$ {int(vol_cm3 * u_cost)}")
                    st.write(f"2. **加工與利潤加成**: NT$ {int(vol_cm3 * u_cost * (markup-1))}")
                    st.write(f"3. **上機固定費用**: NT$ {base_fee} 元")
            
            os.remove(t_path)
        else:
            st.info("💡 請上傳 STL 檔案以顯示預覽與計算報價。")

    # --- 7. 尺寸校正功能 ---
    else:
        st.title("📏 SLA 尺寸校正助手")
        ca = st.number_input("CAD 設計尺寸 (mm)", value=10.0)
        re = st.number_input("實測尺寸 (mm)", value=10.0)
        if ca > 0:
            st.metric("Preform 應填入校正因子", f"{(re/ca):.4f}")
