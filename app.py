import streamlit as st
from streamlit_image_select import image_select

st.set_page_config(page_title="3D列印專業助手", page_icon="🖨️")

st.title("🖨️ 3D 列印專業服務系統")

# --- 1. 圖像選擇區 ---
# 這裡你可以換成你自己上傳到 GitHub 的圖片檔名
selection = image_select(
    label="請選擇功能項目",
    images=[
        "https://cdn-icons-png.flaticon.com/512/2953/2953536.png",  # 估價圖示 (範例)
        "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"   # 校正圖示 (範例)
    ],
    captions=["💰 線上估價系統", "📏 尺寸校正助手"],
    use_container_width=False
)

st.divider()

# --- 2. 根據圖像選擇顯示內容 ---
if selection == "https://cdn-icons-png.flaticon.com/512/2953/2953536.png":
    st.subheader("💰 線上估價系統")
    # ... 這裡放你原本的估價程式碼 ...
    material = st.selectbox("材料", ["PLA", "PETG", "ABS", "TPU", "Resin"])
    weight = st.number_input("重量 (g)", value=10.0)
    hours = st.number_input("時間 (hr)", value=1.0)
    
    # 邏輯判斷
    if material == "PLA": unit = 0.8
    elif material == "PETG": unit = 1.0
    else: unit = 2.0
    
    total = (weight * unit) + (hours * 20)
    st.success(f"建議報價：NT$ {int(total * 2)}")

else:
    st.subheader("📏 尺寸校正助手")
    # ... 這裡放你原本的校正計算器程式碼 ...
    cad = st.number_input("CAD 尺寸 (mm)", value=10.0)
    measured = st.number_input("量測尺寸 (mm)", value=10.1)
    st.metric("校正因子", f"{measured/cad:.4f}")
