import streamlit as st

st.set_page_config(page_title="3D列印專業助手", page_icon="🖨️")

tabs = st.tabs(["💰 線上估價", "📏 尺寸校正"])

# --- 分頁 1：估價程式 ---
with tabs[0]:
    st.title("3D 列印快速估價")
    material = st.selectbox("材料", ["PLA", "PETG", "ABS", "TPU", "Resin"])
    weight = st.number_input("重量 (g)", value=10.0)
    hours = st.number_input("時間 (hr)", value=1.0)
    
    # 邏輯判斷
    if material == "PLA": unit = 0.8
    elif material == "PETG": unit = 1.0
    else: unit = 2.0
    
    total = (weight * unit) + (hours * 20)
    st.success(f"建議報價：NT$ {int(total * 2)}")

# --- 分頁 2：校正計算器 (SOP) ---
with tabs[1]:
    st.title("SLA 尺寸校正助手")
    st.info("參考 Formlabs SOP 操作")
    cad = st.number_input("CAD 設計尺寸 (mm)", value=10.0)
    measured = st.number_input("實際量測尺寸 (mm)", value=10.1)
    
    if cad > 0:
        factor = measured / cad
        st.metric("應填入 Preform 的校正因子", f"{factor:.4f}")
        st.warning("提醒：二次固化後請靜置 15-30 分鐘再量測。")
