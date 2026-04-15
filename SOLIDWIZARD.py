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
# Awwwards + 圖像化 Portal（企業正式版）
# ---------------------------

DARK_MODE = True

bg = "#070A12" if DARK_MODE else "#F6F7FB"
text = "#FFFFFF" if DARK_MODE else "#111111"
muted = "rgba(255,255,255,0.6)" if DARK_MODE else "rgba(0,0,0,0.6)"
card_bg = "rgba(255,255,255,0.06)" if DARK_MODE else "rgba(255,255,255,0.9)"
border = "rgba(255,255,255,0.12)" if DARK_MODE else "rgba(0,0,0,0.08)"
accent = "#6C8CFF"

# ---------------------------
# Admin State
# ---------------------------
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "show_login" not in st.session_state:
    st.session_state.show_login = False

ADMIN_PASSWORD = "0000"

# ---------------------------
# Top Bar
# ---------------------------
col1, col2, col3 = st.columns([2, 6, 2])

with col1:
    st.markdown("<h3>🏢 實威入口</h3>", unsafe_allow_html=True)

with col3:
    if not st.session_state.is_admin:
        if st.button("管理員登入"):
            st.session_state.show_login = not st.session_state.show_login
    else:
        if st.button("登出管理員"):
            st.session_state.is_admin = False
            st.success("已登出")

# ---------------------------
# Login Panel (Top Area)
# ---------------------------
if st.session_state.show_login and not st.session_state.is_admin:
    st.markdown("---")
    st.subheader("🔐 管理員登入")

    pwd = st.text_input("請輸入密碼", type="password")

    if st.button("確認登入"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.session_state.show_login = False
            st.success("登入成功")
        else:
            st.error("密碼錯誤")

# ---------------------------
# Initial Data
# ---------------------------
if "cards" not in st.session_state:
    st.session_state.cards = {
        "internal": [
            {"title": "CRM 客戶管理", "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71", "url": "http://192.168.100.85"},
            {"title": "EIP 企業入口", "img": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", "url": "http://192.168.100.89"},
            {"title": "EASYFLOW 簽核", "img": "https://images.unsplash.com/photo-1551836022-d5d88e9218df", "url": "http://192.168.100.85/efnet/"},
        ],
        "official": [
            {"title": "實威官網", "img": "https://images.unsplash.com/photo-1522071820081-009f0129c71c", "url": "https://www.swtc.com/zh-tw/"},
            {"title": "YouTube 官方", "img": "https://images.unsplash.com/photo-1611162616475-46b635cb6868", "url": "https://www.youtube.com/@solidwizard"},
        ],
        "products": [
            {"title": "SOLIDWORKS", "img": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158", "url": "https://www.solidworks.com/"},
            {"title": "Formlabs", "img": "https://images.unsplash.com/photo-1581090700227-1e37b190418e", "url": "https://formlabs.com/"},
        ]
    }

# ---------------------------
# Theme Style
# ---------------------------
st.markdown(f"""
<style>
.stApp {{ background:{bg}; color:{text}; }}

.hero {{ text-align:center; padding:50px 20px; }}
.hero h1 {{ font-size:44px; font-weight:800; }}
.hero p {{ color:{muted}; }}

.section {{
    margin-top:40px;
    font-size:14px;
    letter-spacing:2px;
    text-transform:uppercase;
    color:{muted};
}}

.card {{
    border-radius:18px;
    overflow:hidden;
    background:{card_bg};
    border:1px solid {border};
    box-shadow:0 10px 30px rgba(0,0,0,0.25);
    transition:0.3s;
    margin-bottom:15px;
}}

.card:hover {{
    transform:translateY(-6px);
    border:1px solid {accent};
}}

.card-title {{
    padding:12px;
    text-align:center;
    font-weight:600;
}}

img {{ width:100%; height:160px; object-fit:cover; }}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# Hero
# ---------------------------
st.markdown("""
<div class='hero'>
<h1>實威國際數位入口</h1>
<p>Awwwards Style Image Portal ｜ Internal Workspace</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------
# Card Function
# ---------------------------
def image_card(item):
    st.markdown(f"""
    <a href=\"{item['url']}\" target=\"_blank\">
        <div class='card'>
            <img src=\"{item['img']}\">
            <div class='card-title'>{item['title']}</div>
        </div>
    </a>
    """, unsafe_allow_html=True)

# ---------------------------
# Grid
# ---------------------------
def render(section):
    cols = st.columns(3)
    for i, item in enumerate(st.session_state.cards[section]):
        with cols[i % 3]:
            image_card(item)

# ---------------------------
# Sections
# ---------------------------
st.markdown("<div class='section'>Internal Systems</div>", unsafe_allow_html=True)
render("internal")

st.markdown("<div class='section'>Official Resources</div>", unsafe_allow_html=True)
render("official")

st.markdown("<div class='section'>Products</div>", unsafe_allow_html=True)
render("products")

# ---------------------------
# Admin Panel
# ---------------------------
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("🛠 管理員編輯模式")

    section = st.selectbox("選擇區塊", ["internal", "official", "products"])

    new_title = st.text_input("標題")
    new_img = st.text_input("圖片URL")
    new_url = st.text_input("連結URL")

    if st.button("新增卡片"):
        st.session_state.cards[section].append({
            "title": new_title,
            "img": new_img,
            "url": new_url
        })
        st.success("已新增卡片")

    st.write("現有卡片")
    for i, item in enumerate(st.session_state.cards[section]):
        col1, col2 = st.columns([4,1])
        with col1:
            st.write(item["title"])
        with col2:
            if st.button(f"刪除 {i}"):
                st.session_state.cards[section].pop(i)
                st.rerun()

# ---------------------------
# Footer
# ---------------------------
st.markdown("<div style='text-align:center;margin-top:50px;opacity:0.5'>SWTC Internal Portal © 2026</div>", unsafe_allow_html=True)
