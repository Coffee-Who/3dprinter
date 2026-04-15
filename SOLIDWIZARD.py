import streamlit as st

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="實威國際員工入口網站",
    layout="wide",
    page_icon="🏢"
)

# ---------------------------
# Awwwards 風格 UI（企業級設計升級）
# ---------------------------
DARK_MODE = True

bg = "#070A12" if DARK_MODE else "#F6F7FB"
text = "#FFFFFF" if DARK_MODE else "#111111"
muted = "rgba(255,255,255,0.6)" if DARK_MODE else "rgba(0,0,0,0.6)"
card_bg = "rgba(255,255,255,0.06)" if DARK_MODE else "rgba(255,255,255,0.9)"
border = "rgba(255,255,255,0.12)" if DARK_MODE else "rgba(0,0,0,0.08)"
accent = "#6C8CFF"

# ---------------------------
# Global Style (Awwwards / Glassmorphism)
# ---------------------------
st.markdown(f"""
<style>
.stApp {{
    background: {bg};
    color: {text};
    font-family: 'Inter', sans-serif;
}}

/* HERO */
.hero {{
    text-align: center;
    padding: 60px 20px 30px 20px;
}}

.hero h1 {{
    font-size: 42px;
    font-weight: 800;
    letter-spacing: 1px;
    margin-bottom: 10px;
}}

.hero p {{
    color: {muted};
    font-size: 16px;
    margin-top: 0;
}}

/* SECTION TITLE */
.section {{
    margin-top: 40px;
    margin-bottom: 15px;
    font-size: 14px;
    letter-spacing: 2px;
    color: {muted};
    text-transform: uppercase;
}}

/* GLASS CARD */
.card {{
    background: {card_bg};
    border: 1px solid {border};
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 18px;
    padding: 18px;
    text-align: center;
    font-weight: 600;
    transition: all 0.25s ease;
    margin-bottom: 12px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}}

.card:hover {{
    transform: translateY(-6px);
    border: 1px solid {accent};
    box-shadow: 0 12px 40px rgba(108,140,255,0.25);
}}

.card a {{
    text-decoration: none;
    color: inherit;
    display: block;
}}

/* GRID SPACING */
.block {{
    margin-bottom: 20px;
}}

/* FOOTER */
.footer {{
    text-align: center;
    margin-top: 60px;
    font-size: 12px;
    color: {muted};
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# HERO SECTION
# ---------------------------
st.markdown(f"""
<div class='hero'>
    <h1>實威國際數位入口</h1>
    <p>SWTC Internal Digital Workspace ｜ Awwwards Style Portal</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# CARD COMPONENT
# ---------------------------
def card(title, url):
    st.markdown(f"""
    <a href=\"{url}\" target=\"_blank\">
        <div class='card'>{title}</div>
    </a>
    """, unsafe_allow_html=True)

# ---------------------------
# GRID (Awwwards spacing)
# ---------------------------
def grid(items):
    cols = st.columns(3)
    for i, (t, u) in enumerate(items):
        with cols[i % 3]:
            card(t, u)

# ---------------------------
# INTERNAL SYSTEM
# ---------------------------
st.markdown("<div class='section'>Internal Systems</div>", unsafe_allow_html=True)

internal = [
    ("CRM 客戶管理系統", "http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx"),
    ("EIP 企業入口平台", "http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx"),
    ("EASYFLOW 簽核系統", "http://192.168.100.85/efnet/"),
    ("請假管理系統", "http://192.168.2.251/MotorWeb/CHIPage/Login.asp"),
]

grid(internal)

# ---------------------------
# OFFICIAL
# ---------------------------
st.markdown("<div class='section'>Official Resources</div>", unsafe_allow_html=True)

official = [
    ("實威國際官網", "https://www.swtc.com/zh-tw/"),
    ("YouTube 官方頻道", "https://www.youtube.com/@solidwizard"),
    ("智慧製造 YouTube", "https://www.youtube.com/@SWTCIM"),
    ("實威知識+", "https://www.youtube.com/@實威知識"),
]

grid(official)

# ---------------------------
# PRODUCTS (Awwwards collapse style)
# ---------------------------
st.markdown("<div class='section'>Products</div>", unsafe_allow_html=True)

with st.expander("SOLIDWORKS Ecosystem", expanded=False):
    grid([
        ("SOLIDWORKS Official", "https://www.solidworks.com/")
    ])

with st.expander("Formlabs Ecosystem", expanded=False):
    grid([
        ("Formlabs Official", "https://formlabs.com/"),
        ("Support Center", "https://support.formlabs.com/s/?language=zh_CN")
    ])

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("""
<div class='footer'>
SWTC Internal Portal © 2026 ｜ Designed in Awwwards Style UI
</div>
""", unsafe_allow_html=True)
