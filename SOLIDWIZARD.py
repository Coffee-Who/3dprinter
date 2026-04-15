import streamlit as st

# ----------------------
# 基本設定
# ----------------------
st.set_page_config(page_title="實威國際入口網站", layout="wide")

# ----------------------
# 模式切換
# ----------------------
mode = st.sidebar.radio("🎨 顏色模式", ["深色模式", "白色模式"])
view = st.sidebar.radio("📱 顯示模式", ["手機版", "電腦版"])

# ----------------------
# 顏色設定
# ----------------------
if mode == "深色模式":
    bg_color = "#0E1117"
    text_color = "#FFFFFF"
    card_color = "#1E1E1E"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    card_color = "#F5F5F5"

# ----------------------
# CSS
# ----------------------
st.markdown(f"""
<style>
body {{
    background-color: {bg_color};
}}

.title {{
    text-align: center;
    font-size: 34px;
    font-weight: bold;
    color: {text_color};
}}

.section {{
    margin-top: 30px;
    margin-bottom: 10px;
    font-size: 24px;
    font-weight: bold;
    color: {text_color};
}}

.card {{
    background-color: {card_color};
    padding: 15px;
    border-radius: 12px;
    margin: 10px 0;
    text-align: center;
    font-size: 18px;
    font-weight: bold;
    color: {text_color};
    text-decoration: none;
    display: block;
}}

.card:hover {{
    transform: scale(1.03);
    opacity: 0.9;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------
# 標題
# ----------------------
st.markdown('<div class="title">🏢 實威國際員工入口網站</div>', unsafe_allow_html=True)

# ----------------------
# 建立按鈕函式
# ----------------------
def create_card(title, link):
    return f'<a href="{link}" target="_blank" class="card">{title}</a>'

# ----------------------
# 內部系統
# ----------------------
st.markdown('<div class="section">🔧 內部系統</div>', unsafe_allow_html=True)

systems = [
    ("📊 CRM 客戶管理", "http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx"),
    ("📁 EIP 企業平台", "http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx"),
    ("🔄 EASYFLOW 電子簽核", "http://192.168.100.85/efnet/"),
    ("📝 請假系統", "http://192.168.2.251/MotorWeb/CHIPage/Login.asp")
]

# ----------------------
# 外部連結
# ----------------------
st.markdown('<div class="section">🌐 官方與資源</div>', unsafe_allow_html=True)

links = [
    ("🌍 實威國際官網", "https://www.swtc.com/zh-tw/"),
    ("🎬 官方 YouTube", "https://www.youtube.com/@solidwizard"),
    ("🏭 智慧製造 YouTube", "https://www.youtube.com/@SWTCIM"),
    ("📚 實威知識+", "https://www.youtube.com/@實威知識")
]

# ----------------------
# 產品入口
# ----------------------
st.markdown('<div class="section">🧩 產品入口</div>', unsafe_allow_html=True)

products = [
    ("🛠 SOLIDWORKS 官網", "https://www.solidworks.com/"),
    ("🖨 Formlabs 官網", "https://formlabs.com/"),
    ("📖 Formlabs 技術支援", "https://support.formlabs.com/s/?language=zh_CN")
]

# ----------------------
# 顯示邏輯（手機 / 電腦）
# ----------------------
def render_section(items):
    if view == "手機版":
        for title, link in items:
            st.markdown(create_card(title, link), unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for i, (title, link) in enumerate(items):
            with cols[i % 3]:
                st.markdown(create_card(title, link), unsafe_allow_html=True)

render_section(systems)
render_section(links)
render_section(products)

# ----------------------
# Footer
# ----------------------
st.markdown("""
<br><br>
<div style='text-align:center; opacity:0.6;'>
SWTC Internal Portal © 2026
</div>
""", unsafe_allow_html=True)

