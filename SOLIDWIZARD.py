import streamlit as st

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="實威國際員工入口網站", layout="wide", page_icon="🏢")

# ---------------------------
# Session State Init
# ---------------------------
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

ADMIN_PASSWORD = "0000"

# ---------------------------
# Theme Switch
# ---------------------------
def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

DARK = st.session_state.dark_mode

bg = "#050713" if DARK else "#F6F7FB"
text = "#FFFFFF" if DARK else "#111111"
muted = "rgba(255,255,255,0.65)" if DARK else "rgba(0,0,0,0.55)"
accent = "#6C8CFF"
card_bg = "rgba(255,255,255,0.04)" if DARK else "#FFFFFF"
border = "rgba(255,255,255,0.10)" if DARK else "rgba(0,0,0,0.08)"

# ---------------------------
# Data
# ---------------------------
if "cards" not in st.session_state:
    st.session_state.cards = {
        "internal": [
            {"title": "CRM 客戶管理", "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71", "url": "http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx"},
            {"title": "EIP 企業入口", "img": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", "url": "http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx"},
            {"title": "EASYFLOW 簽核", "img": "https://images.unsplash.com/photo-1551836022-d5d88e9218df", "url": "http://192.168.100.85/efnet/"},
            {"title": "請假系統", "img": "https://images.unsplash.com/photo-1508385082359-f38ae991e8f2", "url": "http://192.168.2.251/MotorWeb/CHIPage/Login.asp"}
        ],
        "official": [
            {"title": "實威官網", "img": "https://images.unsplash.com/photo-1522071820081-009f0129c71c", "url": "https://www.swtc.com/zh-tw/"},
            {"title": "實威 YouTube", "img": "https://images.unsplash.com/photo-1611162616475-46b635cb6868", "url": "https://www.youtube.com/@solidwizard"},
            {"title": "智慧製造", "img": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5", "url": "https://www.youtube.com/@SWTCIM"},
            {"title": "實威知識+", "img": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f", "url": "https://www.youtube.com/@實威知識"}
        ],
        "products": [
            {"title": "SOLIDWORKS", "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158", "url": "https://www.solidworks.com/"},
            {"title": "Formlabs", "img": "https://images.unsplash.com/photo-1581090700227-1e37b190418e", "url": "https://formlabs.com/"},
            {"title": "Support", "img": "https://images.unsplash.com/photo-1555949963-aa79dcee981c", "url": "https://support.formlabs.com/s/?language=zh_CN"}
        ]
    }

# ---------------------------
# CSS (Awwwards)
# ---------------------------
st.markdown(f"""
<style>
.stApp {{ background:{bg}; color:{text}; }}

.hero {{ text-align:center; padding:60px 20px 25px 20px; }}
.hero h1 {{ font-size:48px; font-weight:800; }}
.hero p {{ color:{muted}; }}

.section {{ margin-top:40px; font-size:13px; letter-spacing:2px; color:{muted}; text-transform:uppercase; }}

.card {{
    border-radius:22px;
    overflow:hidden;
    background:{card_bg};
    border:1px solid {border};
    box-shadow:0 18px 50px rgba(0,0,0,0.35);
    transition:0.3s;
}}

.card:hover {{ transform:translateY(-10px); border:1px solid {accent}; }}

.card img {{ width:100%; height:240px; object-fit:cover; display:block; }}

.card-title {{ padding:12px; text-align:center; font-weight:700; }}

.topbar {{ display:flex; justify-content:space-between; align-items:center; padding:5px 0; }}

.btn {{ cursor:pointer; color:{accent}; font-weight:700; }}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# TOP BAR
# ---------------------------
col1, col2, col3, col4 = st.columns([3,4,2,2])

with col1:
    st.markdown("<div style='font-size:18px;font-weight:800'>🏢 SWTC Portal</div>", unsafe_allow_html=True)

with col3:
    if st.button("🌗 切換模式"):
        toggle_theme()

with col4:
    if not st.session_state.is_admin:
        if st.button("管理員登入"):
            st.session_state.show_login = True
    else:
        if st.button("登出"):
            st.session_state.is_admin = False

# ---------------------------
# LOGIN
# ---------------------------
if st.session_state.show_login and not st.session_state.is_admin:
    st.subheader("管理員登入")
    pwd = st.text_input("請輸入密碼", type="password")

    if st.button("登入"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.session_state.show_login = False
            st.success("登入成功")
        else:
            st.error("密碼錯誤")

# ---------------------------
# HERO
# ---------------------------
st.markdown("""
<div class='hero'>
<h1>實威國際數位入口</h1>
<p>Awwwards Style Image Portal</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# RENDER GRID (5 columns)
# ---------------------------
def render(section):
    cols = st.columns(5)
    for i, item in enumerate(st.session_state.cards[section]):
        with cols[i % 5]:
            st.markdown(f"""
            <a href=\"{item['url']}\" target=\"_blank\">
                <div class='card'>
                    <img src=\"{item['img']}\">
                    <div class='card-title'>{item['title']}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

# ---------------------------
# SECTIONS
# ---------------------------
st.markdown("<div class='section'>內部系統</div>", unsafe_allow_html=True)
render("internal")

st.markdown("<div class='section'>官方系統</div>", unsafe_allow_html=True)
render("official")

st.markdown("<div class='section'>產品入口（點擊展開）</div>", unsafe_allow_html=True)
with st.expander("產品分類", expanded=False):
    render("products")

# ---------------------------
# ADMIN PANEL
# ---------------------------
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("管理員控制台")

    section = st.selectbox("分類", ["internal", "official", "products"])

    title = st.text_input("標題")
    img = st.text_input("圖片URL")
    url = st.text_input("連結URL")

    if st.button("新增項目"):
        st.session_state.cards[section].append({"title": title, "img": img, "url": url})
        st.success("新增成功")
        st.rerun()

    st.markdown("### 管理現有項目")
    for i, item in enumerate(st.session_state.cards[section]):
        col1, col2 = st.columns([5,1])
        with col1:
            st.write(item["title"])
        with col2:
            if st.button(f"刪除 {i}"):
                st.session_state.cards[section].pop(i)
                st.rerun()

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("<div style='text-align:center;margin-top:60px;opacity:0.5'>SWTC Internal Portal © 2026</div>", unsafe_allow_html=True)
