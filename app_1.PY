import streamlit as st
from streamlit_image_select import image_select

st.set_page_config(page_title="3D列印專業助手", page_icon="🖨️")

st.title("🖨️ 3D 列印專業服務系統")

# --- 1. 圖像選擇區 ---
# 這裡你可以換成你自己上傳到 GitHub 的圖片檔名
selection = image_select(
    label="請選擇功能項目",
    images=[
        "6954_6438b3654f0ad.png",  # 估價圖示 (範例)
        "https://cdn-icons-png.flaticon.com/512/3563/3563437.png"   # 校正圖示 (範例)
    ],
    captions=["💰 線上估價系統", "📏 尺寸校正助手"],
    use_container_width=False
)

st.divider()

# --- 2. 根據圖像選擇顯示內容 ---
if selection == "6954_6438b3654f0ad.png":
    st.subheader("💰 線上估價系統")
   # ... 這裡放STL上傳 ..
   from stl import mesh
import tempfile
import os

def get_stl_volume(file):
    # 建立暫存檔處理上傳數據
    with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as tmp:
        tmp.write(file.getvalue())
        tmp_path = tmp.name
    
    # 讀取 STL 並計算體積
    main_mesh = mesh.Mesh.from_file(tmp_path)
    volume, cog, inertia = main_mesh.get_mass_properties()
    
    os.remove(tmp_path)
    # STL 預設單位通常是 mm³，除以 1000 得到 cm³ (cc)
    return volume / 1000

st.title("📦 STL 體積自動計算報價")

uploaded_file = st.file_uploader("請上傳 STL 檔案", type=["stl"])

if uploaded_file is not None:
    # 執行計算
    v_cm3 = get_stl_volume(uploaded_file)
    
    # 顯示結果
    st.metric("偵測模型體積", f"{v_cm3:.2f} cm³ (cc)")
    
    st.divider()
    
    # 價格設定
    col1, col2 = st.columns(2)
    with col1:
        price_per_cm3 = st.number_input("每 cm³ 單價 (元)", value=15.0)
    with col2:
        base_fee = st.number_input("基本上機費 (元)", value=100)
    
    # 計算總價
    total_price = (v_cm3 * price_per_cm3) + base_fee
    
    st.header(f"💰 預估報價：NT$ {int(total_price)}")
    st.caption("註：此報價不含支撐材體積，建議依據實際切片結果微調。")
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
