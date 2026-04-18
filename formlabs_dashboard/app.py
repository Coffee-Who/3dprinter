import streamlit as st

# ── Page config (MUST be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Formlabs Dashboard | 實威國際",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Shared CSS injection ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:        #0a0d14;
    --surface:   #111520;
    --surface2:  #171d2e;
    --accent:    #ff4d00;
    --accent2:   #ff8c42;
    --text:      #e8eaf0;
    --muted:     #6b7280;
    --border:    rgba(255,255,255,0.07);
    --radius:    12px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* hide default streamlit chrome + sidebar */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
button[data-testid="collapsedControl"] { display: none !important; }

/* ── top nav bar ── */
.nav-bar {
    position: sticky; top: 0; z-index: 999;
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(10,13,20,0.92);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    height: 60px;
}
.nav-logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800; font-size: 1.1rem; letter-spacing: 0.04em;
    color: var(--text);
    display: flex; align-items: center; gap: 0.5rem;
}
.nav-logo span { color: var(--accent); }
.nav-links { display: flex; gap: 0.25rem; }
.nav-btn {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.82rem; font-weight: 500;
    padding: 0.4rem 1rem; border-radius: 6px;
    border: 1px solid transparent;
    cursor: pointer; transition: all .2s;
    background: transparent; color: var(--muted);
    text-decoration: none;
}
.nav-btn:hover  { background: var(--surface2); color: var(--text); }
.nav-btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }

/* ── bottom tab bar ── */
.bottom-bar {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 999;
    display: flex; justify-content: center; gap: 0;
    background: rgba(10,13,20,0.95);
    backdrop-filter: blur(16px);
    border-top: 1px solid var(--border);
    padding: 0.5rem 1rem;
}
.bottom-btn {
    display: flex; flex-direction: column; align-items: center; gap: 2px;
    padding: 0.4rem 1.5rem; border-radius: 8px;
    font-size: 0.7rem; font-weight: 500;
    cursor: pointer; transition: all .2s;
    border: none; background: transparent; color: var(--muted);
    min-width: 80px;
}
.bottom-btn .icon { font-size: 1.2rem; }
.bottom-btn:hover  { background: var(--surface2); color: var(--text); }
.bottom-btn.active { background: rgba(255,77,0,0.15); color: var(--accent); }

/* ── page wrapper ── */
.page-wrap { padding: 1.5rem 2rem 100px 2rem; }

/* ── cards ── */
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.25rem 1.5rem;
    transition: border-color .2s;
}
.card:hover { border-color: rgba(255,77,0,0.35); }
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem; font-weight: 600;
    color: var(--muted); text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.card-value {
    font-family: 'Syne', sans-serif;
    font-size: 2rem; font-weight: 800; color: var(--text);
    line-height: 1;
}
.card-sub { font-size: 0.78rem; color: var(--muted); margin-top: 0.3rem; }
.badge-ok   { color: #4ade80; }
.badge-warn { color: var(--accent2); }
.badge-err  { color: var(--accent); }

/* ── section heading ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem; font-weight: 800;
    color: var(--text); margin-bottom: 0.1rem;
}
.section-sub { font-size: 0.85rem; color: var(--muted); margin-bottom: 1.25rem; }

/* ── hero ── */
.hero {
    background: linear-gradient(135deg, #0d1322 0%, #1a0d00 100%);
    border-radius: 16px;
    padding: 3rem 3rem 2.5rem;
    margin-bottom: 2rem;
    position: relative; overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -80px; right: -80px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,77,0,0.18) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-eyebrow {
    font-size: 0.75rem; font-weight: 600; letter-spacing: 0.15em;
    color: var(--accent); text-transform: uppercase; margin-bottom: 0.75rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem,4vw,3.2rem); font-weight: 800;
    line-height: 1.05; color: var(--text); margin-bottom: 1rem;
}
.hero-title span { color: var(--accent); }
.hero-desc { font-size: 0.95rem; color: var(--muted); max-width: 520px; line-height: 1.7; }

/* ── feature grid ── */
.feat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 1rem; }
.feat-card {
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.25rem;
    transition: all .2s;
}
.feat-card:hover { border-color: rgba(255,77,0,0.4); transform: translateY(-2px); }
.feat-icon { font-size: 1.6rem; margin-bottom: 0.6rem; }
.feat-name {
    font-family: 'Syne', sans-serif; font-size: 0.9rem; font-weight: 700;
    color: var(--text); margin-bottom: 0.3rem;
}
.feat-desc { font-size: 0.78rem; color: var(--muted); line-height: 1.5; }

/* ── filter bar ── */
.filter-row {
    display: flex; flex-wrap: wrap; gap: 0.5rem;
    margin-bottom: 1.5rem; align-items: center;
}
.filter-label { font-size: 0.78rem; color: var(--muted); margin-right: 0.25rem; }

/* ── table ── */
.data-table { width: 100%; border-collapse: collapse; font-size: 0.83rem; }
.data-table th {
    text-align: left; padding: 0.6rem 0.8rem;
    font-family: 'Syne', sans-serif; font-size: 0.72rem;
    font-weight: 600; letter-spacing: 0.06em;
    color: var(--muted); text-transform: uppercase;
    border-bottom: 1px solid var(--border);
}
.data-table td {
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: var(--text);
}
.data-table tr:hover td { background: var(--surface2); }
.status-pill {
    display: inline-block; padding: 0.15rem 0.55rem;
    border-radius: 20px; font-size: 0.7rem; font-weight: 600;
}
.pill-printing  { background: rgba(74,222,128,0.15); color: #4ade80; }
.pill-finished  { background: rgba(96,165,250,0.15); color: #60a5fa; }
.pill-idle      { background: rgba(107,114,128,0.15); color: #9ca3af; }
.pill-error     { background: rgba(255,77,0,0.15);   color: var(--accent); }
.pill-paused    { background: rgba(251,191,36,0.15); color: #fbbf24; }

/* fix streamlit default table/chart backgrounds */
.stPlotlyChart { border-radius: var(--radius); overflow: hidden; }
div[data-testid="stMetric"] {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1rem 1.25rem;
}
div[data-testid="stMetric"] label { color: var(--muted) !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important; font-size: 1.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"

# ── Nav helper ────────────────────────────────────────────────────────────────
def set_page(p):
    st.session_state.page = p

# ── TOP NAV BAR ───────────────────────────────────────────────────────────────
p = st.session_state.page
home_cls  = "nav-btn active" if p == "home"      else "nav-btn"
dash_cls  = "nav-btn active" if p == "dashboard" else "nav-btn"

st.markdown(f"""
<div class="nav-bar">
  <div class="nav-logo">🖨️ FORMLABS<span>HUB</span></div>
  <div class="nav-links">
    <button class="{home_cls}"  onclick="window.location.href='?page=home'"     >🏠 首頁</button>
    <button class="{dash_cls}" onclick="window.location.href='?page=dashboard'" >📊 列印儀表板</button>
  </div>
</div>
""", unsafe_allow_html=True)

# handle query param navigation
qp = st.query_params.get("page", None)
if qp and qp != st.session_state.page:
    st.session_state.page = qp
    st.rerun()

# ── ROUTE ─────────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    import pages.home as home
    home.render()
else:
    import pages.dashboard as dashboard
    dashboard.render()

# ── BOTTOM TAB BAR ────────────────────────────────────────────────────────────
home_b = "bottom-btn active" if p == "home"      else "bottom-btn"
dash_b = "bottom-btn active" if p == "dashboard" else "bottom-btn"

st.markdown(f"""
<div class="bottom-bar">
  <a href="?page=home" style="text-decoration:none">
    <div class="{home_b}">
      <span class="icon">🏠</span>首頁
    </div>
  </a>
  <a href="?page=dashboard" style="text-decoration:none">
    <div class="{dash_b}">
      <span class="icon">📊</span>列印儀表板
    </div>
  </a>
</div>
""", unsafe_allow_html=True)
