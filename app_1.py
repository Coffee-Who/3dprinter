import streamlit as st
from streamlit_image_select import image_select
from stl import mesh
import tempfile
import os

# --- 簡單的密碼驗證系統 ---
def check_password():
    def password_entered():
        if st.session_state["password"] == "1234": # 這裡改成你想要的密碼
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 驗證後刪除暫存密碼
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 第一次進入網頁，要求輸入密碼
        st.text_input("請輸入開啟密碼", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # 密碼打錯時
        st.text_input("密碼錯誤，請重新輸入", type="password", on_change=password_entered, key="password")
        st.error("😕 密碼不正確")
        return False
    else:
        # 密碼正確
        return True

# --- 程式主體判斷 ---
if check_password():
    # 這裡放你原本所有的程式碼 (st.title, selection, st.file_uploader 等等)
    st.success("解鎖成功！歡迎使用報價系統")
    # ...

st.set_page_config(page_title="3D列印專業助手", page_icon="🖨️", layout="wide")

# --- 側邊欄：功能導覽 (使用圖像選擇) ---
with st.sidebar:
    st.title("🛠️ 功能選單")
    selection = image_select(
        label="請選擇服務項目",
        images=[
            "https://cdn-icons-png.flaticon.com/512/2953/2953536.png",  # 估價圖示
            "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"   # 校正圖示
        ],
        captions=["自動估價系統", "SLA 尺寸校正"],
        index=0
    )

# --- 邏輯 A：自動估價系統 ---
if "2953536" in selection:
    st.title("💰 3D 列印自動估價系統")
    st.write("您可以上傳 STL 檔案自動計算體積，或手動輸入參數。")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. 檔案分析")
        uploaded_file = st.file_uploader("上傳 STL 檔案 (單位需為 mm)", type=["stl"])
        
        v_cm3 = 0.0
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            m = mesh.Mesh.from_file(tmp_path)
            vol, _, _ = m.get_mass_properties()
            os.remove(tmp_path)
            v_cm3 = vol / 1000
            st.success(f"✅ 偵測體積：{v_cm3:.2f} cm³")
        else:
            v_cm3 = st.number_input("手動輸入體積 (cm³)", min_value=0.0, value=0.0)

    with col2:
        st.subheader("2. 報價設定")
        price_per_cm3 = st.slider("每 cm³ 單價 (NT$)", 5, 50, 15)
        base_fee = st.number_input("上機固定費 (NT$)", value=100)
        
        total = (v_cm3 * price_per_cm3) + base_fee
        st.divider()
        st.header(f"建議總價：NT$ {int(total)}")

# --- 邏輯 B：尺寸校正助手 ---
else:
    st.title("📏 SLA 尺寸校正助手")
    st.info("參考 Formlabs SOP：量測前請確保物件已完全冷卻並靜置 15-30 分鐘。")
    
    # 這裡可以加入你之前上傳的 SOP 圖片
    # st.image("2026-04-07_17-45-09.png", caption="SOP 校正流程參考")
    
    c1, c2 = st.columns(2)
    with c1:
        cad_val = st.number_input("CAD 設計尺寸 (mm)", value=10.0)
    with c2:
        real_val = st.number_input("實際量測尺寸 (mm)", value=10.0)
    
    if cad_val > 0:
        factor = real_val / cad_val
        st.metric("應填入 Preform 的校正因子", f"{factor:.4f}")
        
        if abs(factor - 1.0) > 0.0015:
            st.warning("⚠️ 誤差較大，建議更新校正參數以確保精密件品質。")
        else:
            st.success("✅ 精度良好，微調即可。")
