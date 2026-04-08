import streamlit as st
import pandas as pd
from stl import mesh
import tempfile
import os
import plotly.graph_objects as go
import numpy as np
from streamlit_image_select import image_select

# 1. 頁面基本配置 (標題與寬度設定)
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
        df = pd.read_csv("Formlabs材料.csv")
        df['每cm3成本'] = df['單價'] / 1000
        return df
    except Exception:
        # 如果讀不到 CSV，提供預設選項
        return pd.DataFrame({"Formlabs": ["一般樹脂"], "每cm3成本": [10.0]})

# --- 4. 主程式邏輯 ---
if check_password():
    df_m = load_materials()
    
    # CSS 強制修正：縮小圖示並微調間距
    st.markdown("""
        <style>
        /* 縮小 image-select 的圖片容器 */
        div[data-testid="stHorizontalBlock"] img {
            width: 48px !important;
            height: 48px !important;
            border-radius: 8px !important;
            object-fit: cover !important;
            border: 1px solid #CBD5E1;
            padding: 2px;
        }
        /* 縮小文字標籤 */
        div[data-testid="stHorizontalBlock"] p {
            font-size: 11px !important;
            font-weight: 600 !important;
            color: #475569;
            margin-top: 4px !important;
        }
        /* 移除上傳組件多餘空白 */
        .stFileUploader { padding-bottom: 2rem; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("🛠️ 服務控制面板")
        # 圖示會被上方的 CSS 縮小到 48px
        sel = image_select(
            label="選擇服務項目", 
            images=[
                "https://cdn-icons-png.flaticon.com/512/2953/2953536.png", 
                "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"
            ], 
            captions=["自動估價", "尺寸校正"],
            index=0
        )

    # --- 5. 自動估價與高品質預覽 ---
    if "2953536" in sel:
        st.title("💰 Formlabs 自動估價系統")
        up_file = st.file_uploader("請上傳 STL 檔案進行分析", type=["stl"])
        
        c1, c2 = st.columns([1.8, 1])
        vol_cm3 = 0.0

        if up_file:
            # 建立暫存檔以讀取
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(up_file.getvalue())
                t_path = tmp.name
            
            with c1:
                st.subheader("📦 3D 結構視覺化 (模擬 Magic3D 質感)")
                try:
                    m_mesh = mesh.Mesh.from_file(t_path)
                    vecs = m_mesh.vectors
                    
                    # 效能優化：如果面數太多則進行抽樣
                    if len(vecs) > 35000:
                        step = len(vecs) // 35000
                        vecs = vecs[::step]
                    
                    # 展開頂點資料
                    p, q, r = vecs.shape
                    v = vecs.reshape(p*q, r)
                    f = np.arange(p*q).reshape(p, q)
                    
                    # 使用 PBR 模擬光學參數
                    fig = go.Figure(data=[
                        go.Mesh3d(
                            x=v[:,0], y=v[:,1], z=v[:,2],
                            i=f[:,0], j=f[:,1], k=f[:,2],
                            color='#334155', # 專業深灰色 (類似 Magic3D 預設)
                            opacity=1.0,
                            flatshading=False,
                            # 強化材質感：模擬拋光樹脂
                            lighting=dict(
                                ambient=0.4, 
                                diffuse=0.8, 
                                specular=1.8, # 強力高光
                                roughness=0.2, # 低粗糙度
                                fresnel=1.2    # 邊緣反射
                            ),
                            # 增加輪廓線條 (取代 wireframe 以防報錯)
                            contour=dict(show=True, color='#F8FAFC', width=1)
                        )
                    ])
                    
                    fig.update_layout(
                        scene=dict(
                            xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, 
                            aspectmode='data', bgcolor='white' # 純白背景
                        ),
                        margin=dict(l=0, r=0, b=0, t=0), height=680
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 計算體積
                    v_val, _, _ = m_mesh.get_mass_properties()
                    vol_cm3 = float(v_val) / 1000.0
                    
                except Exception as e:
                    st.error(f"3D 預覽載入失敗：{e}")
            
            with c2:
                st.subheader("📊 報價數據分析")
                st.metric("偵測體積 (Volume)", f"{vol_cm3:.2f} cm³")
                
                # 選取材料與計算
                m_choice = st.selectbox("選用樹脂材料", df_m["Formlabs"].tolist())
                u_cost = df_m.loc[df_m["Formlabs"] == m_choice, "每cm3成本"].values[0]
                
                markup = st.slider("報價加成倍率", 1.0, 10.0, 3.0, step=0.1)
                base_fee = st.number_input("基本起鍋費 (NTD)", value=150)
                
                final_total = (vol_cm3 * u_cost * markup) + base_fee
                
                st.divider()
                st.markdown(f"### 📢 建議報價: <span style='color:red; font-size:42px;'>NT$ {int(final_total)}</span>", unsafe_allow_html=True)
                
                with st.expander("🔍 價格細項拆解"):
                    st.write(f"- 樹脂材料成本: NT$ {int(vol_cm3 * u_cost)}")
                    st.write(f"- 加工與潤收: NT$ {int(vol_cm3 * u_cost * (markup-1))}")
                    st.write(f"- 固定成本 (洗機/耗材): NT$ {base_fee}")
            
            # 刪除暫存檔
            os.remove(t_path)
        else:
            st.info("👋 您好！請在左側上傳 STL 檔案，系統將自動分析結構並提供即時報價。")

    # --- 6. 尺寸校正系統 ---
    else:
        st.title("📏 SLA 尺寸補償計算機")
        colA, colB = st.columns(2)
        with colA:
            ca = st.number_input("CAD 設計理想尺寸 (mm)", value=10.0)
        with colB:
            re = st.number_input("列印實測尺寸 (mm)", value=10.0)
        
        if ca > 0:
            factor = re / ca
            st.divider()
            st.subheader("校正結果")
            st.markdown(f"請在 Preform 中輸入校正因子： **{factor:.4f}**")
            st.info("💡 公式：實測尺寸 ÷ 設計尺寸 = 校正比例")
