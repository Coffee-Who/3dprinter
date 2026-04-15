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
# 預設 Theme（可改這裡）
# ---------------------------
DARK_MODE = True

bg = "#0E1117" if DARK_MODE else "#FFFFFF"
text = "white" if DARK_MODE else "black"
card = "#1f1f1f" if DARK_MODE else "#f2f2f2"

# ---------------------------
# CSS
# ---------------------------
st.markdown(f"""
<style>
.stApp {{
    background-color: {bg};
    color: {text};
}}

.title {{
    text-align:center;
    font-size:34px;
    font-weight:bold;
    margin-bottom:20px;
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
# 自動 RWD 判斷
# Streamlit 會自動調整 columns → 手機=1欄 / 電腦=多欄
# ---------------------------
def show(items):
    cols = st.columns(3)
    for i, (t, u) in enumerate(items):
        with cols[i % 3]:
            card(t, u)

# ---------------------------
# 內部系統
# ---------------------------
st.subheader("🔧 內部系統")

internal = [
    ("📊 CRM", "http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx"),
    ("📁 EIP", "http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx"),
    ("🔄 EASYFLOW", "http://192.168.100.85/efnet/"),
    ("📝 請假系統", "http://192.168.2.251/MotorWeb/CHIPage/Login.asp"),
]

show(internal)

# ---------------------------
# 官方系統
# ---------------------------
st.subheader("🌐 官方資源")

official = [
    ("🏢 實威官網", "https://www.swtc.com/zh-tw/"),
    ("🎬 YouTube 官方", "https://www.youtube.com/@solidwizard"),
    ("🏭 智慧製造", "https://www.youtube.com/@SWTCIM"),
    ("📚 實威知識+", "https://www.youtube.com/@實威知識"),
]

show(official)

# ---------------------------
# 產品入口（收合）
# ---------------------------
st.subheader("🧩 產品入口")

with st.expander("SOLIDWORKS"):
    show([
        ("SOLIDWORKS 官網", "https://www.solidworks.com/")
    ])

with st.expander("Formlabs"):
    show([
        ("Formlabs 官網", "https://formlabs.com/"),
        ("Support", "https://support.formlabs.com/s/?language=zh_CN")
    ])

# ---------------------------
# Footer
# ---------------------------
st.markdown("""
<br><div style='text-align:center;opacity:0.5'>
SWTC Internal Portal © 2026
</div>
""", unsafe_allow_html=True)
