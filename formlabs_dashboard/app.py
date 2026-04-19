import streamlit as st

st.set_page_config(
    page_title="Formlabs Dashboard | 實威國際",
    page_icon="🖨️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

:root {
    --bg:      #08090f;
    --surf:    #0f1320;
    --surf2:   #161c30;
    --surf3:   #1e263a;
    --accent:  #ff4d00;
    --accent2: #ff7a35;
    --text:    #f0f2f8;
    --muted:   #8892a4;
    --border:  rgba(255,255,255,0.08);
    --radius:  12px;
    --green:   #22d3a0;
    --blue:    #60a5fa;
    --yellow:  #fbbf24;
    --red:     #ff4d00;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.25rem 2rem 80px !important; max-width: 100% !important; }
section[data-testid="stSidebar"],
button[data-testid="collapsedControl"] { display: none !important; }

/* ── nav bar ── */
.nav-bar {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.5rem; padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
.nav-logo {
    font-family: 'Syne', sans-serif; font-weight: 800; font-size: 1.25rem;
    color: var(--text); display: flex; align-items: center; gap: .5rem;
    letter-spacing: .02em;
}
.nav-logo span { color: var(--accent); }
.nav-badge {
    font-size: .75rem; font-weight: 600; padding: .25rem .75rem;
    border-radius: 20px; background: rgba(255,255,255,.08); color: var(--muted);
    margin-left: .6rem;
}
.nav-ts { font-size: .85rem; color: #ffffff; font-weight: 600; }

/* ── section headings ── */
.sec-title {
    font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800;
    color: #ffffff; margin-bottom: .2rem; letter-spacing: .01em;
}
.sec-sub { font-size: .88rem; color: var(--muted); margin-bottom: 1rem; }

/* ── cards ── */
.card {
    background: var(--surf); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.1rem 1.3rem;
    transition: border-color .2s;
}
.card:hover { border-color: rgba(255,77,0,.3); }

/* ── status pills ── */
.status-pill {
    display: inline-block; padding: .18rem .65rem;
    border-radius: 20px; font-size: .75rem; font-weight: 700;
    letter-spacing: .03em;
}
.pill-printing { background: rgba(34,211,160,.18); color: #22d3a0; }
.pill-finished { background: rgba(96,165,250,.18);  color: #60a5fa; }
.pill-idle     { background: rgba(107,114,128,.18); color: #9ca3af; }
.pill-error    { background: rgba(255,77,0,.18);    color: #ff6b35; }
.pill-paused   { background: rgba(251,191,36,.18);  color: #fbbf24; }
.pill-queued   { background: rgba(167,139,250,.18); color: #a78bfa; }

/* ── metrics ── */
div[data-testid="stMetric"] {
    background: var(--surf); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1rem 1.25rem;
}
div[data-testid="stMetric"] label {
    color: var(--muted) !important; font-size: .82rem !important; font-weight: 500 !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.9rem !important; color: #ffffff !important; font-weight: 800 !important;
}

/* ── table ── */
.data-table { width: 100%; border-collapse: collapse; font-size: .9rem; }
.data-table th {
    text-align: left; padding: .7rem .9rem;
    font-family: 'Syne', sans-serif; font-size: .75rem; font-weight: 800;
    letter-spacing: .08em; color: var(--accent2); text-transform: uppercase;
    border-bottom: 2px solid rgba(255,77,0,.25);
}
.data-table td {
    padding: .65rem .9rem;
    border-bottom: 1px solid rgba(255,255,255,.05);
    color: #e8edf5; font-size: .88rem;
}
.data-table tr:hover td { background: var(--surf2); }
.total-row td {
    background: rgba(255,77,0,.08) !important;
    border-top: 2px solid rgba(255,77,0,.4) !important;
    font-weight: 700; color: #ffffff !important; font-size: .9rem;
}

/* ── settings box ── */
.settings-box {
    background: rgba(255,77,0,.06); border: 1px solid rgba(255,77,0,.25);
    border-radius: var(--radius); padding: 1.3rem 1.5rem; margin-bottom: 1.25rem;
}

/* ── multiselect labels ── */
.stMultiSelect label, .stSelectbox label, .stRadio label {
    font-size: .9rem !important; font-weight: 600 !important; color: #c8d0e0 !important;
}
/* multiselect tags */
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(255,77,0,.25) !important;
    color: #ffffff !important; font-weight: 600 !important;
}

/* ── date input labels ── */
.stDateInput label { font-size: .88rem !important; color: #c8d0e0 !important; }

/* ── radio ── */
.stRadio [data-testid="stRadioLabel"] { font-size: .9rem !important; color: #e0e6f0 !important; }

/* ── buttons ── */
.stButton > button {
    font-size: .88rem !important; font-weight: 600 !important;
}

/* plotly */
.stPlotlyChart { border-radius: var(--radius); overflow: hidden; }
</style>
""", unsafe_allow_html=True)

import pages.dashboard as dashboard
dashboard.render()
