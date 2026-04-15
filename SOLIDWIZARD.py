import streamlit as st

# =========================
# Page Config
# =========================
st.set_page_config(page_title="實威國際員工入口網站", layout="wide", page_icon="🏢")

# =========================
# Session State
# =========================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "editing" not in st.session_state:
    st.session_state.editing = None

ADMIN_PASSWORD = "0000"

# =========================
# Awwwards 白底風格
# =========================
bg = "#F7F8FA"
text = "#111111"
muted = "rgba(0,0,0,0.55)"
accent = "#2F6BFF"
border = "rgba(0,0,0,0.08)"
card_bg = "#FFFFFF"

st.markdown(f"""
<style>
.stApp {{ background:{bg}; color:{text}; }}
.hero {{ text-align:center; padding:50px 20px 10px 20px; }}
.hero h1 {{ font-size:48px; font-weight:800; }}
.hero p {{ color:{muted}; }}
.section {{ margin-top:40px; font-size:13px; letter-spacing:2px; color:{muted}; text-transform:uppercase; }}
.card {{ border-radius:18px; overflow:hidden; background:{card_bg}; border:1px solid {border}; box-shadow:0 10px 30px rgba(0,0,0,0.08); transition:0.25s; }}
.card:hover {{ transform:translateY(-6px); border:1px solid {accent}; }}
.card img {{ width:100%; height:220px; object-fit:cover; }}
.card-title {{ padding:10px; font-weight:700; text-align:center; }}
</style>
""", unsafe_allow_html=True)

# =========================
# DATA
# =========================
if "cards" not in st.session_state:
    st.session_state.cards = {
        "internal": [
            {"title": "CRM", "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71", "url": "#"},
            {"title": "EIP", "img": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", "url": "#"},
            {"title": "EASYFLOW", "img": "https://images.unsplash.com/photo-1551836022-d5d88e9218df", "url": "#"},
            {"title": "請假系統", "img": "https://images.unsplash.com/photo-1508385082359-f38ae991e8f2", "url": "#"}
        ],
        "official": [
            {"title": "官網", "img": "https://images.unsplash.com/photo-1522071820081-009f0129c71c", "url": "#"},
            {"title": "YT", "img": "https://images.unsplash.com/photo-1611162616475-46b635cb6868", "url": "#"}
        ],
        "software": [
            {"title": "SOLIDWORKS", "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158", "url": "https://www.solidworks.com/"}
        ],
        "formlabs": [
            {"title": "Formlabs 原廠", "img": "https://images.unsplash.com/photo-1581090700227-1e37b190418e", "url": "https://formlabs.com/"},
            {"title": "Formlabs Support", "img": "https://images.unsplash.com/photo-1555949963-aa79dcee981c", "url": "https://support.formlabs.com/s/?language=zh_CN"}
        ]
    }

# =========================
# TOP BAR
# =========================
col1, col2, col3 = st.columns([3,6,2])
with col1:
    st.markdown("## 🏢 SWTC Portal")
with col3:
    if not st.session_state.is_admin:
        if st.button("管理員登入"):
            st.session_state.show_login = True
    else:
        if st.button("登出"):
            st.session_state.is_admin = False

# =========================
# LOGIN
# =========================
if st.session_state.show_login:
    pwd = st.text_input("輸入密碼", type="password")
    if st.button("登入"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.session_state.show_login = False
            st.success("登入成功")
        else:
            st.error("錯誤")

# =========================
# HERO
# =========================
st.markdown("<div class='hero'><h1>實威國際入口</h1><p>Awwwards Portal</p></div>", unsafe_allow_html=True)

# =========================
# ADD ITEM
# =========================
def add_form(section):
    if st.session_state.is_admin:
        st.markdown(f"### ➕ 新增 {section}")
        title = st.text_input("標題", key=f"t_{section}")
        img = st.text_input("圖片", key=f"i_{section}")
        url = st.text_input("連結", key=f"u_{section}")
        if st.button(f"新增-{section}"):
            st.session_state.cards[section].append({"title": title, "img": img, "url": url})
            st.rerun()

# =========================
# RENDER
# =========================
def render(section):
    items = st.session_state.cards.get(section, [])
    cols = st.columns(5)
    for i, item in enumerate(items):
        with cols[i % 5]:
            st.markdown(f"""
            <a href=\"{item['url']}\" target=\"_blank\">
                <div class='card'>
                    <img src=\"{item['img']}\">
                    <div class='card-title'>{item['title']}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

# =========================
# SECTIONS
# =========================
st.markdown("### 內部系統")
render("internal")
add_form("internal")

st.markdown("### 官方系統")
render("official")
add_form("official")

st.markdown("### 軟體")
render("software")
add_form("software")

st.markdown("### Formlabs")
render("formlabs")
add_form("formlabs")

# =========================
# FOOTER
# =========================
st.markdown("<div style='text-align:center;margin-top:50px;opacity:0.5'>SWTC Portal © 2026</div>", unsafe_allow_html=True)
