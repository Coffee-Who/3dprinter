import streamlit as st

st.set_page_config(
    page_title="Formlabs Dashboard | 實威國際",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg:      #0a0d14;
    --surface: #111520;
    --surf2:   #171d2e;
    --accent:  #ff4d00;
    --accent2: #ff8c42;
    --text:    #e8eaf0;
    --muted:   #6b7280;
    --border:  rgba(255,255,255,0.07);
    --radius:  12px;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 80px !important; max-width: 100% !important; }
section[data-testid="stSidebar"],
button[data-testid="collapsedControl"] { display: none !important; }

/* cards */
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.1rem 1.3rem;
    transition: border-color .2s;
}
.card:hover { border-color: rgba(255,77,0,.3); }

/* section headings */
.sec-title {
    font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800;
    color:var(--text); margin-bottom:.15rem;
}
.sec-sub { font-size:.82rem; color:var(--muted); margin-bottom:1rem; }

/* status pills */
.status-pill {
    display:inline-block; padding:.15rem .55rem;
    border-radius:20px; font-size:.68rem; font-weight:600;
}
.pill-printing { background:rgba(74,222,128,.15); color:#4ade80; }
.pill-finished { background:rgba(96,165,250,.15);  color:#60a5fa; }
.pill-idle     { background:rgba(107,114,128,.15); color:#9ca3af; }
.pill-error    { background:rgba(255,77,0,.15);    color:#ff4d00; }
.pill-paused   { background:rgba(251,191,36,.15);  color:#fbbf24; }
.pill-queued   { background:rgba(167,139,250,.15); color:#a78bfa; }

/* metrics */
div[data-testid="stMetric"] {
    background:var(--surface); border:1px solid var(--border);
    border-radius:var(--radius); padding:.9rem 1.1rem;
}
div[data-testid="stMetric"] label { color:var(--muted) !important; font-size:.78rem !important; }
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family:'Syne',sans-serif !important; font-size:1.6rem !important;
}

/* table */
.data-table { width:100%; border-collapse:collapse; font-size:.81rem; }
.data-table th {
    text-align:left; padding:.55rem .75rem;
    font-family:'Syne',sans-serif; font-size:.68rem; font-weight:700;
    letter-spacing:.07em; color:var(--muted); text-transform:uppercase;
    border-bottom:1px solid var(--border);
}
.data-table td {
    padding:.55rem .75rem;
    border-bottom:1px solid rgba(255,255,255,.04);
    color:var(--text);
}
.data-table tr:hover td { background:var(--surf2); }

/* plotly */
.stPlotlyChart { border-radius:var(--radius); overflow:hidden; }

/* settings expander */
.settings-box {
    background:rgba(255,77,0,.05);
    border:1px solid rgba(255,77,0,.2);
    border-radius:var(--radius); padding:1.2rem 1.4rem;
    margin-bottom:1.25rem;
}

/* nav bar */
.nav-bar {
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:1.5rem; padding-bottom:1rem;
    border-bottom:1px solid var(--border);
}
.nav-logo {
    font-family:'Syne',sans-serif; font-weight:800; font-size:1.15rem;
    color:var(--text); display:flex; align-items:center; gap:.4rem;
}
.nav-logo span { color:var(--accent); }
.nav-badge {
    font-size:.7rem; padding:.2rem .65rem; border-radius:20px;
    background:rgba(255,255,255,.07); color:var(--muted);
}
</style>
""", unsafe_allow_html=True)

# ── import dashboard (single page) ───────────────────────────────────────────
import pages.dashboard as dashboard
dashboard.render()
