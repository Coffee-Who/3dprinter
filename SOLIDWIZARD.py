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
# State
# ---------------------------
if "dark" not in st.session_state:
    st.session_state.dark = True

if "mobile" not in st.session_state:
    st.session_state.mobile = False

# ---------------------------
# Sidebar 控制
# ---------------------------
st.sidebar.title("⚙️ 控制面板")

if st.sidebar.button("🌗 深色 / 淺色"):
    st.session_state.dark = not st.session_state.dark

if st.sidebar.button("📱 手機 / 電腦"):
    st.session_state.mobile = not st.session_state.mobile

dark = st.session_state.dark
mobile = st.session_state.mobile

# ---------------------------
# Theme
# ---------------------------
bg = "#0E1117" if dark else "#FFFFFF"
text = "white" if dark else "black"
card = "#1f1f1f" if dark else "#f2f2f2"

# ---------------------------
# CSS
# ---------------------------
st.markdown(f"""
<style>
.stApp {{
    background-color: {bg};
    color: {text};
}}

.card {{
    background-color: {card};
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    font-weight: 600;
    margin: 8px 0;
    transition: 0.2s;
}}

.card:hover {{
    transform: scale(1.02);
    opacity: 0.9;
}}

.title {{
    text-align:center;
    font-size:32px;
    font-weight:bold;
    margin-bottom:20px;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Title
# ---------------------------
st.markdown("<div class='title'>🏢 實威國際員工入口網站</div>", unsafe_allow_html=True)

# ---------------------------
# Card Function
# ---------------------------
def card(title, url):
    st.markdown(f"""
    <a href="{url}" target="_blank" style="text-decoration:none;">
        <div class="card">{title}</div>
    </a>
    """, unsafe_allow_html=True)

# ---------------------------
# Grid
# ---------------------------
def show(items, cols=3):
    if mobile:
        for t, u in items:
            card(t, u)
    else:
        c = st.columns(cols)
        for i, (t, u) in enumerate(items):
            with c[i % cols]:
                card(t, u)

# ---------------------------
# Internal
# ---------------------------
st.subheader("🔧 內部系統")

internal = [
    ("📊 CRM", "http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx"),
    ("📁 EIP", "http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx"),
    ("🔄 EASYFLOW", "http://192.168.100.85/efnet/"),
    ("📝 請假系統", "http://192.168.2.251/MotorWeb/CHIPage/Login.asp"),
]

show(internal, 2)

# ---------------------------
# Official
# ---------------------------
st.subheader("🌐 官方資源")

official = [
    ("🏢 官網", "https://www.swtc.com/zh-tw/"),
    ("🎬 YouTube", "https://www.youtube.com/@solidwizard"),
    ("🏭 智慧製造", "https://www.youtube.com/@SWTCIM"),
    ("📚 知識+", "https://www.youtube.com/@實威知識"),
]

show(official, 2)

# ---------------------------
# Products
# ---------------------------
st.subheader("🧩 產品入口")

with st.expander("SOLIDWORKS", expanded=False):
    show([
        ("SOLIDWORKS 官網", "https://www.solidworks.com/")
    ], 1)

with st.expander("Formlabs", expanded=False):
    show([
        ("Formlabs 官網", "https://formlabs.com/"),
        ("Support", "https://support.formlabs.com/s/?language=zh_CN")
    ], 1)

# ---------------------------
# Footer
# ---------------------------
st.markdown("<div style='text-align:center;opacity:0.5;margin-top:30px'>SWTC Internal Portal © 2026</div>", unsafe_allow_html=True)
