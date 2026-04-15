import streamlit as st

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="實威國際員工入口網站", layout="wide", page_icon="🏢")

# ---------------------------
# Awwwards 圖像式 Portal（企業正式版）
# ---------------------------

DARK_MODE = True

bg = "#050713"
text = "#FFFFFF"
muted = "rgba(255,255,255,0.65)"
accent = "#6C8CFF"
card_bg = "rgba(255,255,255,0.04)"
border = "rgba(255,255,255,0.10)"

# ---------------------------
# Admin State
# ---------------------------
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "show_login" not in st.session_state:
    st.session_state.show_login = False

ADMIN_PASSWORD = "0000"

# ---------------------------
# Data
# ---------------------------
if "cards" not in st.session_state:
    st.session_state.cards = {
        "internal": [
            {"title": "CRM 客戶管理", "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71", "url": "http://192.168.100.85"},
            {"title": "EIP 企業入口", "img": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", "url": "http://192.168.100.89"},
            {"title": "EASYFLOW 簽核", "img": "https://images.unsplash.com/photo-1551836022-d5d88e9218df", "url": "http://192.168.100.85/efnet/"}
        ],
        "official": [
            {"title": "實威官網", "img": "https://images.unsplash.com/photo-1522071820081-009f0129c71c", "url": "https://www.swtc.com/zh-tw/"},
            {"title": "YouTube 官方", "img": "https://images.unsplash.com/photo-1611162616475-46b635cb6868", "url": "https://www.youtube.com/@solidwizard"}
        ],
        "products": [
            {"title": "SOLIDWORKS", "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158", "url": "https://www.solidworks.com/"},
            {"title": "Formlabs", "img": "https://images.unsplash.com/photo-1581090700227-1e37b190418e", "url": "https://formlabs.com/"}
        ]
    }

# ---------------------------
# CSS
# ---------------------------
st.markdown(f"""
<style>
.stApp {{ background:{bg}; color:{text}; }}

.hero {{ text-align:center; padding:60px 20px 30px 20px; }}
.hero h1 {{ font-size:46px; font-weight:800; }}
.hero p {{ color:{muted}; }}

.section {{ margin-top:40px; font-size:13px; letter-spacing:2px; color:{muted}; text-transform:uppercase; }}

.card {{
    border-radius:20px;
    overflow:hidden;
    background:{card_bg};
    border:1px solid {border};
    box-shadow:0 15px 40px rgba(0,0,0,0.35);
    transition:0.3s;
    margin-bottom:18px;
}}

.card:hover {{
    transform:translateY(-8px);
    border:1px solid {accent};
}}

.card img {{ width:100%; height:260px; object-fit:cover; }}

.card-title {{
    padding:14px;
    text-align:center;
    font-weight:700;
    font-size:15px;
}}

.topbar {{ display:flex; justify-content:space-between; align-items:center; }}

.footer {{ text-align:center; margin-top:50px; opacity:0.5; font-size:12px; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# TOP BAR
# ---------------------------
col1, col2, col3 = st.columns([2,6,2])

with col1:
    st.markdown("<div style='font-weight:800;font-size:18px'>SWTC Portal</div>", unsafe_allow_html=True)

with col3:
    if not st.session_state.is_admin:
        if st.button("管理員登入"):
            st.session_state.show_login = not st.session_state.show_login
    else:
        if st.button("登出管理員"):
            st.session_state.is_admin = False

# ---------------------------
# LOGIN
# ---------------------------
if st.session_state.show_login and not st.session_state.is_admin:
    st.subheader("管理員登入")
    pwd = st.text_input("輸入密碼", type="password")

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
st.markdown("<div class='hero'><h1>實威國際數位入口</h1><p>Awwwards Style Image Portal</p></div>", unsafe_allow_html=True)

# ---------------------------
# CARD
# ---------------------------
def card(item):
    st.markdown(f"<a href=\"{item['url']}\" target=\"_blank\"><div class='card'><img src=\"{item['img']}\"><div class='card-title'>{item['title']}</div></div></a>", unsafe_allow_html=True)

# ---------------------------
# GRID
# ---------------------------
def render(section):
    cols = st.columns(3)
    for i, item in enumerate(st.session_state.cards[section]):
        with cols[i % 3]:
            card(item)

# ---------------------------
# SECTIONS
# ---------------------------
st.markdown("<div class='section'>Internal Systems</div>", unsafe_allow_html=True)
render("internal")

st.markdown("<div class='section'>Official Resources</div>", unsafe_allow_html=True)
render("official")

st.markdown("<div class='section'>Products</div>", unsafe_allow_html=True)
render("products")

# ---------------------------
# ADMIN PANEL
# ---------------------------
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("管理員控制台")

    section = st.selectbox("區塊", ["internal", "official", "products"])

    title = st.text_input("標題")
    img = st.text_input("圖片URL")
    url = st.text_input("連結URL")

    if st.button("新增"):
        st.session_state.cards[section].append({"title": title, "img": img, "url": url})
        st.success("已新增")
        st.rerun()

    for i, item in enumerate(st.session_state.cards[section]):
        col1, col2 = st.columns([5,1])
        with col1:
            st.write(item["title"])
        with col2:
            if st.button(f"刪除{i}"):
                st.session_state.cards[section].pop(i)
                st.rerun()

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("<div class='footer'>SWTC Internal Portal © 2026</div>", unsafe_allow_html=True)
