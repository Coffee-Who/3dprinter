import streamlit as st

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="實威國際員工入口網站", layout="wide", page_icon="🏢")

# ---------------------------
# Session State
# ---------------------------
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "editing" not in st.session_state:
    st.session_state.editing = None

ADMIN_PASSWORD = "0000"

# ---------------------------
# WHITE AWWARDS THEME
# ---------------------------
bg = "#F7F8FA"
text = "#111111"
muted = "rgba(0,0,0,0.55)"
accent = "#2F6BFF"
border = "rgba(0,0,0,0.08)"
card_bg = "#FFFFFF"

# ---------------------------
# DATA
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
            {"title": "實威國際官網", "img": "https://images.unsplash.com/photo-1522071820081-009f0129c71c", "url": "https://www.swtc.com/zh-tw/"},
            {"title": "實威 YouTube", "img": "https://images.unsplash.com/photo-1611162616475-46b635cb6868", "url": "https://www.youtube.com/@solidwizard"},
            {"title": "智慧製造 YouTube", "img": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5", "url": "https://www.youtube.com/@SWTCIM"},
            {"title": "實威知識+", "img": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f", "url": "https://www.youtube.com/@實威知識"}
        ],
        "software": [
            {"title": "SOLIDWORKS", "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158", "url": "https://www.solidworks.com/"}
        ],
        "formlabs": [
            {"title": "Formlabs 原廠", "img": "https://images.unsplash.com/photo-1581090700227-1e37b190418e", "url": "https://formlabs.com/"},
            {"title": "Formlabs Support", "img": "https://images.unsplash.com/photo-1555949963-aa79dcee981c", "url": "https://support.formlabs.com/s/?language=zh_CN"}
        ]
    }

# ---------------------------
# CSS
# ---------------------------
st.markdown(f"""
<style>
.stApp {{ background:{bg}; color:{text}; }}

.hero {{ text-align:center; padding:50px 20px 10px 20px; }}
.hero h1 {{ font-size:48px; font-weight:800; }}
.hero p {{ color:{muted}; }}

.section {{ margin-top:40px; font-size:13px; letter-spacing:2px; color:{muted}; text-transform:uppercase; }}

.card {{
    border-radius:18px;
    overflow:hidden;
    background:{card_bg};
    border:1px solid {border};
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
    transition:0.25s;
}}

.card:hover {{ transform:translateY(-6px); border:1px solid {accent}; }}

.card img {{ width:100%; height:220px; object-fit:cover; }}

.card-title {{ padding:10px; font-weight:700; text-align:center; }}

.admin-actions {{ display:flex; justify-content:space-between; padding:0 10px 10px 10px; font-size:12px; }}

.btn {{ color:{accent}; cursor:pointer; font-weight:700; }}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# TOP BAR
# ---------------------------
col1, col2, col3 = st.columns([3,6,2])

with col1:
    st.markdown("<div style='font-size:18px;font-weight:800'>🏢 SWTC Portal</div>", unsafe_allow_html=True)

with col3:
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
st.markdown("<div class='hero'><h1>實威國際數位入口</h1><p>Awwwards Style Portal</p></div>", unsafe_allow_html=True)

# ---------------------------
# CARD RENDER
# ---------------------------
def render_card(section, idx, item):
    st.markdown(f"""
    <a href=\"{item['url']}\" target=\"_blank\">
        <div class='card'>
            <img src=\"{item['img']}\">
            <div class='card-title'>{item['title']}</div>
        </div>
    </a>
    """, unsafe_allow_html=True)

    if st.session_state.is_admin:
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"編輯-{section}-{idx}"):
                st.session_state.editing = (section, idx)
        with col2:
            if st.button(f"刪除-{section}-{idx}"):
                st.session_state.cards[section].pop(idx)
                st.rerun()

# ---------------------------
# GRID (5 columns)
# ---------------------------
def render(section):
    cols = st.columns(5)
    for i, item in enumerate(st.session_state.cards[section]):
        with cols[i % 5]:
            render_card(section, i, item)

# ---------------------------
# SECTIONS
# ---------------------------
st.markdown("<div class='section'>內部系統</div>", unsafe_allow_html=True)
render("internal")

st.markdown("<div class='section'>官方系統</div>", unsafe_allow_html=True)
render("official")

st.markdown("<div class='section'>軟體</div>", unsafe_allow_html=True)
render("software")

st.markdown("<div class='section'>Formlabs</div>", unsafe_allow_html=True)
render("formlabs")

# ---------------------------
# EDIT MODE
# ---------------------------
if st.session_state.editing:
    section, idx = st.session_state.editing
    item = st.session_state.cards[section][idx]

    st.markdown("---")
    st.subheader("編輯項目")

    new_title = st.text_input("標題", item['title'])
    new_img = st.text_input("圖片", item['img'])
    new_url = st.text_input("連結", item['url'])

    if st.button("儲存修改"):
        st.session_state.cards[section][idx] = {
            "title": new_title,
            "img": new_img,
            "url": new_url
        }
        st.session_state.editing = None
        st.rerun()

# ---------------------------
# FOOTER
# ---------------------------
st.markdown("<div style='text-align:center;margin-top:50px;opacity:0.5'>SWTC Portal © 2026</div>", unsafe_allow_html=True)
