import streamlit as st

# =========================
# Page Config
# =========================
st.set_page_config(page_title="實威國際入口 Portal", layout="wide", page_icon="🏢")

# =========================
# Session State
# =========================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "show_login" not in st.session_state:
    st.session_state.show_login = False

if "edit_target" not in st.session_state:
    st.session_state.edit_target = None

ADMIN_PASSWORD = "0000"

# =========================
# Awwwards 白底風格
# =========================
st.markdown("""
<style>
.stApp { background:#F7F8FA; color:#111; }

.hero {
    text-align:center;
    padding:40px;
}

.hero h1 {
    font-size:44px;
    font-weight:800;
}

.section {
    margin-top:40px;
    font-weight:600;
    color:rgba(0,0,0,0.6);
    letter-spacing:2px;
}

.card {
    background:#fff;
    border-radius:18px;
    overflow:hidden;
    box-shadow:0 10px 30px rgba(0,0,0,0.08);
    transition:0.3s;
}

.card:hover {
    transform:translateY(-6px);
}

.card img {
    width:100%;
    height:200px;
    object-fit:cover;
}

.card-title {
    padding:10px;
    font-weight:700;
    text-align:center;
}

.btn {
    color:#2F6BFF;
    cursor:pointer;
    font-size:12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 初始化資料（完整分類）
# =========================
if "cards" not in st.session_state:
    st.session_state.cards = {
        "內部系統": [
            {"title":"CRM", "img":"https://images.unsplash.com/photo-1551288049-bebda4e38f71", "url":"#"},
            {"title":"EIP", "img":"https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", "url":"#"},
            {"title":"EASYFLOW", "img":"https://images.unsplash.com/photo-1551836022-d5d88e9218df", "url":"#"},
            {"title":"請假系統", "img":"https://images.unsplash.com/photo-1508385082359-f38ae991e8f2", "url":"#"}
        ],

        "官方系統": [
            {"title":"官網", "img":"https://images.unsplash.com/photo-1522071820081-009f0129c71c", "url":"#"},
            {"title":"YouTube", "img":"https://images.unsplash.com/photo-1611162616475-46b635cb6868", "url":"#"}
        ],

        "軟體": [
            {"title":"SOLIDWORKS", "img":"https://images.unsplash.com/photo-1581091226825-a6a2a5aee158",
             "url":"https://www.solidworks.com/"}
        ],

        "Formlabs": [
            {"title":"Formlabs 原廠", "img":"https://images.unsplash.com/photo-1581090700227-1e37b190418e",
             "url":"https://formlabs.com/"},
            {"title":"Formlabs Support", "img":"https://images.unsplash.com/photo-1555949963-aa79dcee981c",
             "url":"https://support.formlabs.com/s/?language=zh_CN"}
        ],

        "Scanology": [
            {"title":"Scanology 官網", "img":"https://images.unsplash.com/photo-1581092335397-9fa1f9a2d2a1", "url":"#"}
        ]
    }

# =========================
# 登入
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
st.markdown("""
<div class="hero">
<h1>實威國際數位入口</h1>
<p>Awwwards Portal</p>
</div>
""", unsafe_allow_html=True)

# =========================
# 新增 + 編輯
# =========================
def add_item(category):
    if st.session_state.is_admin:
        st.markdown(f"### ➕ 新增 {category}")

        t = st.text_input("標題", key=f"t_{category}")
        i = st.text_input("圖片", key=f"i_{category}")
        u = st.text_input("連結", key=f"u_{category}")

        if st.button(f"新增-{category}"):
            st.session_state.cards[category].append({"title": t, "img": i, "url": u})
            st.rerun()

# =========================
# render（安全版）
# =========================
def render(category):
    items = st.session_state.cards.get(category, [])
    cols = st.columns(5)

    for i, item in enumerate(items):
        with cols[i % 5]:
            st.markdown(f"""
            <a href="{item['url']}" target="_blank">
                <div class="card">
                    <img src="{item['img']}">
                    <div class="card-title">{item['title']}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

# =========================
# UI 主體
# =========================
for category in st.session_state.cards.keys():

    st.markdown(f"## {category}")

    render(category)
    add_item(category)

# =========================
# FOOTER
# =========================
st.markdown("<div style='text-align:center;opacity:0.5;margin-top:40px'>SWTC Portal © 2026</div>", unsafe_allow_html=True)
