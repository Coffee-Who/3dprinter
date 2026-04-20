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
  }import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
 
st.set_page_config(
    page_title="SOLIDWIZARD | 材料熱力圖",
    page_icon="🖨️",
    layout="wide"
)
 
st.markdown("""
<style>
  /* ── 全域 ── */
  .stApp, section[data-testid="stMain"] { background-color: #0d1117 !important; }
  #MainMenu, footer, header { visibility: hidden; }
  * { font-family: 'Segoe UI', system-ui, sans-serif; }
 
  /* ── 頁首 ── */
  .top-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0 6px 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 12px;
  }
  .top-bar-left { display: flex; align-items: center; gap: 12px; }
  .logo { color: #FFFFFF; font-size: 18px; font-weight: 800; letter-spacing: -0.5px; }
  .logo span { color: #00C853; }
  .subtitle { color: #8B949E; font-size: 12px; }
 
  /* ── Tab 頁籤 ── */
  .tab-bar {
    display: flex; gap: 4px; margin-bottom: 14px;
  }
  .tab-btn {
    background: transparent; border: 1px solid #21262d;
    color: #8B949E; font-size: 12px; font-weight: 600;
    padding: 5px 14px; border-radius: 20px; cursor: pointer;
    transition: all .15s; white-space: nowrap;
  }
  .tab-btn:hover { border-color: #00C853; color: #00C853; }
  .tab-btn.active { background: #00C853; color: #000; border-color: #00C853; }
 
  /* ── KPI 卡片列 ── */
  .kpi-row { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
  .kpi-card {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 8px; padding: 12px 16px; flex: 1; min-width: 120px;
  }
  .kpi-label { color: #8B949E; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .8px; margin-bottom: 4px; }
  .kpi-value { color: #FFFFFF; font-size: 20px; font-weight: 800; }
  .kpi-change { font-size: 11px; margin-top: 2px; }
  .up   { color: #00C853; }
  .down { color: #FF5252; }
  .flat { color: #8B949E; }
 
  /* ── 圖例列 ── */
  .legend-row {
    display: flex; align-items: center; gap: 16px;
    margin-bottom: 8px; flex-wrap: wrap;
  }
  .legend-item { display: flex; align-items: center; gap: 5px;
    font-size: 11px; color: #8B949E; }
  .legend-dot { width: 10px; height: 10px; border-radius: 2px; }
 
  /* ── Plotly 容器背景 ── */
  .stPlotlyChart { background: transparent !important; }
  .js-plotly-plot .plotly .bg { fill: #0d1117 !important; }
 
  /* ── Streamlit 元件深色化 ── */
  .stSelectbox > div > div,
  .stNumberInput input {
    background: #161b22 !important;
    color: #FFFFFF !important;
    border: 1px solid #21262d !important;
    border-radius: 6px !important;
  }
  label, .stSelectbox label { color: #8B949E !important; font-size: 11px !important; }
  .stDivider { border-color: #21262d !important; }
  .stAlert { background: #161b22 !important; border: 1px solid #21262d !important; }
 
  /* ── 報價區 ── */
  .quote-panel {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 10px; padding: 20px; margin-top: 12px;
  }
  .quote-title { color: #8B949E; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
  .quote-price { color: #00C853; font-size: 40px; font-weight: 900; margin-bottom: 4px; }
  .quote-sub { color: #8B949E; font-size: 12px; }
  .detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 14px; }
  .detail-cell { border-left: 2px solid #21262d; padding-left: 10px; }
  .detail-label { color: #8B949E; font-size: 10px; text-transform: uppercase; letter-spacing: .5px; }
  .detail-value { color: #FFFFFF; font-size: 13px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)
 
 
# ── 材料資料庫 ────────────────────────────────────────────
MATERIALS = [
    # name, category, price_per_L, density_g_cm3, shore/tensile, color_hex
    ("Clear Resin V4",       "Standard",   6900,  1.17, "透明/通用",    "#004D40"),
    ("Grey Resin V4",        "Standard",   6900,  1.17, "灰色/通用",    "#004D40"),
    ("White Resin V4",       "Standard",   6900,  1.17, "白色/通用",    "#004D40"),
    ("Black Resin V4",       "Standard",   6900,  1.17, "黑色/通用",    "#004D40"),
    ("Draft Resin V2",       "Standard",   6900,  1.10, "快速成型",     "#004D40"),
    ("Model Resin V3",       "Standard",   6900,  1.15, "精細模型",     "#004D40"),
    ("Tough 2000 Resin",     "Engineering",8500,  1.20, "韌性/高強度",  "#1565C0"),
    ("Tough 1500 Resin",     "Engineering",8500,  1.15, "韌性/彈性",    "#1565C0"),
    ("Durable Resin",        "Engineering",8500,  1.15, "耐磨/彈性",    "#1565C0"),
    ("Grey Pro Resin",       "Engineering",8500,  1.19, "工程灰/精準",  "#1565C0"),
    ("Rigid 10K Resin",      "Engineering",12000, 1.55, "超剛性/玻纖",  "#0D47A1"),
    ("Rigid 4000 Resin",     "Engineering",8500,  1.30, "剛性/玻纖",    "#1565C0"),
    ("Flexible 80A Resin",   "Flexible",   9500,  1.13, "Shore 80A",   "#1B5E20"),
    ("Elastic 50A Resin",    "Flexible",   9500,  1.10, "Shore 50A",   "#1B5E20"),
    ("High Temp Resin",      "Specialty",  11000, 1.25, "耐高溫 289°C", "#E65100"),
    ("Flame Retardant",      "Specialty",  12000, 1.30, "阻燃 UL94-V0","#B71C1C"),
    ("ESD Resin",            "Specialty",  12000, 1.22, "防靜電",       "#4A148C"),
    ("BioMed Clear",         "BioMed",     13500, 1.17, "生醫透明",     "#006064"),
    ("BioMed Amber",         "BioMed",     13500, 1.17, "生醫琥珀",     "#006064"),
    ("BioMed White",         "BioMed",     13500, 1.18, "生醫白色",     "#006064"),
    ("BioMed Black",         "BioMed",     13500, 1.18, "生醫黑色",     "#006064"),
    ("Castable Wax 40",      "Castable",   15000, 1.00, "失蠟鑄造",     "#F57F17"),
    ("Castable Wax",         "Castable",   15000, 1.00, "失蠟鑄造",     "#F57F17"),
    ("Silicone 40A",         "Specialty",  18000, 1.12, "矽膠 Shore 40A","#880E4F"),
    ("Alumina 4N Resin",     "Specialty",  25000, 2.40, "氧化鋁陶瓷",   "#37474F"),
]
 
df = pd.DataFrame(MATERIALS, columns=["name","category","price","density","spec","color"])
df["price_mL"] = df["price"] / 1000
 
 
# ── 色彩映射（依價格段）────────────────────────────────────
def price_color(p):
    if p <= 6900:  return "#004D40"   # 微漲 dark teal
    if p <= 8500:  return "#1565C0"   # 平盤 dark blue
    if p <= 10000: return "#1B5E20"   # 普通 dark green
    if p <= 13000: return "#E65100"   # 偏高 orange
    if p <= 16000: return "#B71C1C"   # 高   deep red
    return "#FF5252"                  # 最高 bright red
 
df["map_color"] = df["price"].apply(price_color)
 
 
# ── 頁首 ─────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
  <div class="top-bar-left">
    <div class="logo">SOLID<span>WIZARD</span></div>
    <div class="subtitle">Formlabs 材料報價熱力圖 · 實威國際</div>
  </div>
</div>
""", unsafe_allow_html=True)
 
# ── Tab 選擇（用 Streamlit radio 模擬膠囊 Tab）────────────
tab_options = ["全部材料", "Standard", "Engineering", "Flexible", "Specialty", "BioMed", "Castable"]
selected_tab = st.radio("", tab_options, horizontal=True, label_visibility="collapsed")
 
if selected_tab == "全部材料":
    df_view = df.copy()
else:
    df_view = df[df["category"] == selected_tab].copy()
 
# ── KPI 卡片 ─────────────────────────────────────────────
avg_price = df_view["price"].mean()
min_price = df_view["price"].min()
max_price = df_view["price"].max()
count     = len(df_view)
 
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-label">材料數量</div>
    <div class="kpi-value">{count}</div>
    <div class="kpi-change flat">種 Formlabs 材料</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">平均單價</div>
    <div class="kpi-value">NT$ {avg_price:,.0f}</div>
    <div class="kpi-change flat">每公升</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">最低單價</div>
    <div class="kpi-value up">NT$ {min_price:,}</div>
    <div class="kpi-change up">↓ 最優惠</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">最高單價</div>
    <div class="kpi-value down">NT$ {max_price:,}</div>
    <div class="kpi-change down">↑ 特殊材料</div>
  </div>
</div>
""", unsafe_allow_html=True)
 
# ── 圖例 ─────────────────────────────────────────────────
st.markdown("""
<div class="legend-row">
  <div class="legend-item"><div class="legend-dot" style="background:#004D40"></div> ≤ NT$6,900</div>
  <div class="legend-item"><div class="legend-dot" style="background:#1565C0"></div> ≤ NT$8,500</div>
  <div class="legend-item"><div class="legend-dot" style="background:#1B5E20"></div> ≤ NT$10,000</div>
  <div class="legend-item"><div class="legend-dot" style="background:#E65100"></div> ≤ NT$13,000</div>
  <div class="legend-item"><div class="legend-dot" style="background:#B71C1C"></div> ≤ NT$16,000</div>
  <div class="legend-item"><div class="legend-dot" style="background:#FF5252"></div> > NT$16,000</div>
</div>
""", unsafe_allow_html=True)
 
# ── TreeMap 熱力圖 ────────────────────────────────────────
col_map, col_quote = st.columns([3, 1], gap="medium")
 
with col_map:
    fig = go.Figure(go.Treemap(
        labels      = df_view["name"].tolist(),
        parents     = df_view["category"].tolist(),
        values      = df_view["price"].tolist(),
        customdata  = df_view[["price","price_mL","density","spec","category"]].values,
        marker=dict(
            colors     = df_view["map_color"].tolist(),
            line       = dict(width=2, color="#0d1117"),
            pad        = dict(t=20, l=3, r=3, b=3),
        ),
        texttemplate = "<b>%{label}</b><br>NT$ %{value:,}",
        textfont     = dict(color="#FFFFFF", size=11),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "單價：NT$ %{customdata[0]:,} / L<br>"
            "換算：NT$ %{customdata[1]:.2f} / mL<br>"
            "密度：%{customdata[2]} g/cm³<br>"
            "特性：%{customdata[3]}<br>"
            "分類：%{customdata[4]}"
            "<extra></extra>"
        ),
        root_color   = "#0d1117",
        branchvalues = "total",
    ))
 
    fig.update_layout(
        paper_bgcolor = "#0d1117",
        plot_bgcolor  = "#0d1117",
        margin        = dict(t=0, l=0, r=0, b=0),
        height        = 500,
        font          = dict(color="#FFFFFF"),
    )
 
    selected = st.plotly_chart(fig, use_container_width=True,
                               on_select="rerun", key="treemap")
 
# ── 報價計算區 ────────────────────────────────────────────
with col_quote:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
 
    # 從 TreeMap 點選或下拉選擇材料
    clicked_pts = (selected or {}).get("selection", {}).get("points", [])
    clicked_name = clicked_pts[0]["label"] if clicked_pts else None
 
    mat_names = df_view["name"].tolist()
    default_idx = mat_names.index(clicked_name) if clicked_name in mat_names else 0
    chosen = st.selectbox("選擇材料", mat_names, index=default_idx)
 
    row = df_view[df_view["name"] == chosen].iloc[0]
 
    st.markdown("---")
    vol   = st.number_input("列印體積 (mm³)", min_value=0.1, value=1000.0, step=100.0)
    sup   = st.slider("支撐材比例 (%)", 0, 50, 20)
    qty   = st.number_input("數量", min_value=1, value=1, step=1)
    fee   = st.number_input("後處理費/件 (NT$)", min_value=0, value=200, step=50)
    mark  = st.number_input("加成倍率", min_value=1.0, value=2.0, step=0.1)
 
    total_vol  = vol * (1 + sup / 100) * qty
    mat_cost   = (total_vol / 1000) * row["price_mL"]
    total_cost = (mat_cost + fee * qty) * mark
 
    # 顏色判斷
    price_lvl = row["price"]
    badge_color = price_color(price_lvl)
 
    st.markdown(f"""
    <div class="quote-panel">
      <div class="quote-title">⬡ 預估報價</div>
      <div class="quote-price">NT$ {total_cost:,.0f}</div>
      <div class="quote-sub">{chosen}</div>
      <div class="detail-grid">
        <div class="detail-cell">
          <div class="detail-label">材料消耗</div>
          <div class="detail-value">{total_vol/1000:.2f} mL</div>
        </div>
        <div class="detail-cell">
          <div class="detail-label">材料費</div>
          <div class="detail-value">NT$ {mat_cost*mark:,.0f}</div>
        </div>
        <div class="detail-cell">
          <div class="detail-label">單價</div>
          <div class="detail-value">NT$ {price_lvl:,} / L</div>
        </div>
        <div class="detail-cell">
          <div class="detail-label">密度</div>
          <div class="detail-value">{row['density']} g/cm³</div>
        </div>
        <div class="detail-cell">
          <div class="detail-label">特性</div>
          <div class="detail-value" style="font-size:11px">{row['spec']}</div>
        </div>
        <div class="detail-cell">
          <div class="detail-label">分類</div>
          <div class="detail-value" style="color:{badge_color}">{row['category']}</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
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
