import streamlit as st

st.set_page_config(
    page_title="3D列印專業服務系統",
    page_icon="🖨️",
    layout="wide"
)

st.markdown("""
<style>
  .stApp { background-color: #0d1117; color: #FFFFFF; }
  #MainMenu, footer, header { visibility: hidden; }

  .stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #30363d;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #8B949E;
    border-radius: 6px 6px 0 0;
    padding: 8px 20px;
    font-size: 14px;
    font-weight: 500;
  }
  .stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 2px solid #00C853 !important;
    background: transparent !important;
  }

  .kpi-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    margin-top: 12px;
  }
  .kpi-label { color: #8B949E; font-size: 12px; letter-spacing: 1px; text-transform: uppercase; }
  .kpi-value { color: #00C853; font-size: 36px; font-weight: 700; margin: 8px 0; }
  .kpi-sub   { color: #8B949E; font-size: 12px; }

  .stNumberInput input, .stSelectbox select {
    background: #21262d !important;
    color: #FFFFFF !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
  }

  .page-header {
    padding: 20px 0 8px 0;
    border-bottom: 1px solid #30363d;
    margin-bottom: 24px;
  }
  .page-header h1 { font-size: 22px; font-weight: 700; margin: 0; }
  .page-header p  { color: #8B949E; font-size: 13px; margin: 4px 0 0 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
  <h1>🖨️ 3D 列印專業服務系統</h1>
  <p>實威國際 · 專業級製造解決方案</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💰 線上估價系統", "📏 尺寸校正助手"])

with tab1:
    col_input, col_result = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown("#### 輸入參數")
        material = st.selectbox(
            "列印材料",
            ["PLA", "PETG", "ABS", "TPU", "Resin"],
            help="不同材料單價不同"
        )
        weight = st.number_input("列印重量 (g)", min_value=0.1, value=10.0, step=0.5)
        hours  = st.number_input("列印時間 (hr)", min_value=0.1, value=1.0, step=0.5)
        support_rate = st.slider("支撐材比例 (%)", 0, 50, 10)

    with col_result:
        unit_map = {"PLA": 0.8, "PETG": 1.0, "ABS": 1.2, "TPU": 1.5, "Resin": 2.0}
        unit = unit_map[material]
        material_cost = weight * unit * (1 + support_rate / 100)
        machine_cost  = hours * 20
        subtotal      = material_cost + machine_cost
        total         = int(subtotal * 2)

        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">建議報價</div>
          <div class="kpi-value">NT$ {total:,}</div>
          <div class="kpi-sub">材料 NT${int(material_cost*2):,} ／ 機台 NT${int(machine_cost*2):,}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("📊 成本明細"):
            st.markdown(f"""
            | 項目 | 金額 |
            |------|------|
            | 材料費（含支撐材） | NT$ {int(material_cost*2):,} |
            | 機台費 | NT$ {int(machine_cost*2):,} |
            | **合計** | **NT$ {total:,}** |
            """)

with tab2:
    col_a, col_b = st.columns([1, 1], gap="large")

    with col_a:
        st.markdown("#### 輸入尺寸")
        cad      = st.number_input("CAD 設計尺寸 (mm)", min_value=0.01, value=10.0, step=0.01)
        measured = st.number_input("實際量測尺寸 (mm)", min_value=0.01, value=10.1, step=0.01)
        axis     = st.selectbox("校正軸向", ["X 軸", "Y 軸", "Z 軸"])

    with col_b:
        factor = measured / cad
        error  = abs(measured - cad)
        pct    = abs(factor - 1) * 100
        color  = "#00C853" if pct < 0.5 else "#FF5252" if pct > 2 else "#FFD700"

        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{axis} 校正因子</div>
          <div class="kpi-value" style="color:{color};">{factor:.4f}</div>
          <div class="kpi-sub">誤差 {error:.3f} mm（{pct:.2f}%）</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if pct < 0.5:
            st.success("✅ 精度優良，無需調整")
        elif pct < 2:
            st.warning(f"⚠️ 建議調整切片縮放比例至 {factor:.4f}")
        else:
            st.error(f"❌ 誤差過大（{pct:.1f}%），請檢查列印參數")
