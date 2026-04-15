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
# Theme (企業級優化 UI)
# ---------------------------
DARK_MODE = True

bg = "#0B1220" if DARK_MODE else "#F7F9FC"
text = "#FFFFFF" if DARK_MODE else "#1A1A1A"
muted = "#A0A0A0" if DARK_MODE else "#666666"
card_bg = "#111B2E" if DARK_MODE else "#FFFFFF"
card_shadow = "0px 4px 18px rgba(0,0,0,0.15)"

# ---------------------------
# CSS（企業級 UI 強化）
# ---------------------------
st.markdown(f"""
<style>
.stApp {{
    background-color: {bg};
    color: {text};
}}

/* 主標題 */
.title {{
    text-align: center;
    font-size: 36px;
    font-weight: 800;
    margin-top: 10px;
    margin-bottom: 5px;
    letter-spacing: 1px;
}}

.subtitle {{
    text-align: center;
    font-size: 14px;
    color: {muted};
    margin-bottom: 30px;
}}

/* 區塊標題 */
.section-title {{
    font-size: 20px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 12px;
    border-left: 4px solid #4F8BF9;
    padding-left: 10px;
}}

/* 卡片 */
.card {{
    background-color: {card_bg};
    padding: 18px;
    border-radius: 16px;
    text-align: center;
    font-weight: 600;
    margin: 10px 0;
    box-shadow: {card_shadow};
    transition: all 0.2s ease-in-out;
    border: 1px solid rgba(255,255,255,0.05);
}}

.card:hover {{
    transform: translateY(-3px);
    opacity: 0.95;
    border: 1px solid rgba(79,139,249,0.4);
}}

.card a {{
    text-decoration: none;
    color: inherit;
    display: block;
    font-size: 15px;
}}

/* Footer */
.footer {{
    text-align: center;
    margin-top: 40px;
    font-size: 12px;
    color: {muted};
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Title
# ---------------------------
st.markdown("<div class='title'>🏢 實威國際員工入口網站</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Internal Portal ｜ SWTC Digital Workspace</div>", unsafe_allow_html=True)

# ---------------------------
# Card Component
# ---------------------------
def card(title, url):
    st.markdown(f"""
    <a href=\"{url}\" target=\"_blank\">
        <div class='card'>{title}</div>
    </a>
    """, unsafe_allow_html=True)

# ---------------------------
# Grid Render（自動 RWD）
# ---------------------------
def show(items):
    cols = st.columns(3)
    for i, (t, u) in enumerate(items):
        with cols[i % 3]:
            card(t, u)

# ---------------------------
# 內部系統
# ---------------------------
st.markdown("<div class='section-title'>🔧 內部系統</div>", unsafe_allow_html=True)

internal = [
    ("📊 CRM 客戶管理系統", "http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx"),
    ("📁 EIP 企業入口平台", "http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx"),
    ("🔄 EASYFLOW 簽核系統", "http://192.168.100.85/efnet/"),
    ("📝 請假申請系統", "http://192.168.2.251/MotorWeb/CHIPage/Login.asp"),
]

show(internal)

# ---------------------------
# 官方系統
# ---------------------------
st.markdown("<div class='section-title'>🌐 官方資源</div>", unsafe_allow_html=True)

official = [
    ("🏢 實威國際官網", "https://www.swtc.com/zh-tw/"),
    ("🎬 官方 YouTube 頻道", "https://www.youtube.com/@solidwizard"),
    ("🏭 智慧製造 YouTube", "https://www.youtube.com/@SWTCIM"),
    ("📚 實威知識 +", "https://www.youtube.com/@實威知識"),
]

show(official)

# ---------------------------
# 產品入口（強化收合 UI）
# ---------------------------
st.markdown("<div class='section-title'>🧩 產品入口</div>", unsafe_allow_html=True)

with st.expander("🛠 SOLIDWORKS 產品線", expanded=False):
    show([
        ("SOLIDWORKS 官方網站", "https://www.solidworks.com/")
    ])

with st.expander("🖨 Formlabs 3D 列印", expanded=False):
    show([
        ("Formlabs 官方網站", "https://formlabs.com/"),
        ("Formlabs 技術支援", "https://support.formlabs.com/s/?language=zh_CN")
    ])

# ---------------------------
# Footer
# ---------------------------
st.markdown("<div class='footer'>SWTC Internal Portal © 2026 ｜ Built with Streamlit</div>", unsafe_allow_html=True)
