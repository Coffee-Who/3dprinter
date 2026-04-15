import streamlit as st

st.set_page_config(page_title="SWTC Portal", layout="wide")

# =====================
# State
# =====================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "show_login" not in st.session_state:
    st.session_state.show_login = False

if "edit" not in st.session_state:
    st.session_state.edit = None
import streamlit as st

st.set_page_config(page_title="SWTC Portal", layout="wide")

# =====================
# State
# =====================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "show_login" not in st.session_state:
    st.session_state.show_login = False

if "edit" not in st.session_state:
    st.session_state.edit = None

ADMIN_PASSWORD = "0000"

# =====================
# UI
# =====================
st.markdown("""
<style>
.stApp { background:#F7F8FA; color:#111; }

.card {
    background:white;
    border-radius:16px;
    overflow:hidden;
    box-shadow:0 10px 25px rgba(0,0,0,0.08);
    margin-bottom:10px;
}

.card img {
    width:100%;
    height:180px;
    object-fit:cover;
}

.card-title {
    text-align:center;
    font-weight:700;
    padding:8px;
}

.btn { color:#2F6BFF; cursor:pointer; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# =====================
# DATA
# =====================
if "cards" not in st.session_state:
    st.session_state.cards = {
        "內部系統": [
            {"title":"CRM","img":"https://images.unsplash.com/photo-1551288049-bebda4e38f71","url":"#"},
            {"title":"EIP","img":"https://images.unsplash.com/photo-1454165804606-c3d57bc86b40","url":"#"},
        ],
        "軟體": [
            {"title":"SOLIDWORKS","img":"https://images.unsplash.com/photo-1581091226825-a6a2a5aee158","url":"https://www.solidworks.com/"}
        ]
    }

# =====================
# LOGIN
# =====================
col1, col2, col3 = st.columns([3,6,2])
with col3:
    if not st.session_state.is_admin:
        if st.button("管理員登入"):
            st.session_state.show_login = True
    else:
        if st.button("登出"):
            st.session_state.is_admin = False

if st.session_state.show_login:
    pwd = st.text_input("密碼", type="password")
    if st.button("登入"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.session_state.show_login = False
        else:
            st.error("錯誤")

# =====================
# HERO
# =====================
st.title("實威國際 Portal")

# =====================
# RENDER
# =====================
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

            if st.session_state.is_admin:
                c1, c2 = st.columns(2)

                # ================= EDIT =================
                with c1:
                    if st.button(f"編輯-{category}-{i}"):
                        st.session_state.edit = (category, i)

                # ================= DELETE =================
                with c2:
                    if st.button(f"刪-{category}-{i}"):
                        st.session_state.cards[category].pop(i)
                        st.rerun()

# =====================
# ADD ITEM
# =====================
def add_item(category):
    if st.session_state.is_admin:
        st.markdown(f"### ➕ 新增 {category}")

        t = st.text_input("標題", key=f"t_{category}")
        i = st.text_input("圖片", key=f"i_{category}")
        u = st.text_input("連結", key=f"u_{category}")

        if st.button(f"新增-{category}"):
            st.session_state.cards[category].append(
                {"title": t, "img": i, "url": u}
            )
            st.rerun()

# =====================
# EDIT PANEL（重點🔥）
# =====================
if st.session_state.edit:
    cat, idx = st.session_state.edit
    item = st.session_state.cards[cat][idx]

    st.markdown("## ✏️ 編輯項目")

    new_t = st.text_input("標題", item["title"])
    new_i = st.text_input("圖片", item["img"])
    new_u = st.text_input("連結", item["url"])

    if st.button("儲存修改"):
        st.session_state.cards[cat][idx] = {
            "title": new_t,
            "img": new_i,
            "url": new_u
        }
        st.session_state.edit = None
        st.rerun()

# =====================
# SECTIONS
# =====================
for category in st.session_state.cards.keys():
    st.markdown(f"## {category}")
    render(category)
    add_item(category)

# =====================
# FOOTER
# =====================
st.markdown("<div style='text-align:center;opacity:0.5;margin-top:40px'>SWTC Portal © 2026</div>", unsafe_allow_html=True)
ADMIN_PASSWORD = "0000"

# =====================
# UI
# =====================
st.markdown("""
<style>
.stApp { background:#F7F8FA; color:#111; }

.card {
    background:white;
    border-radius:16px;
    overflow:hidden;
    box-shadow:0 10px 25px rgba(0,0,0,0.08);
    margin-bottom:10px;
}

.card img {
    width:100%;
    height:180px;
    object-fit:cover;
}

.card-title {
    text-align:center;
    font-weight:700;
    padding:8px;
}

.btn { color:#2F6BFF; cursor:pointer; font-size:12px; }
</style>
""", unsafe_allow_html=True)

# =====================
# DATA
# =====================
if "cards" not in st.session_state:
    st.session_state.cards = {
        "內部系統": [
            {"title":"CRM","img":"https://images.unsplash.com/photo-1551288049-bebda4e38f71","url":"#"},
            {"title":"EIP","img":"https://images.unsplash.com/photo-1454165804606-c3d57bc86b40","url":"#"},
        ],
        "軟體": [
            {"title":"SOLIDWORKS","img":"https://images.unsplash.com/photo-1581091226825-a6a2a5aee158","url":"https://www.solidworks.com/"}
        ]
    }

# =====================
# LOGIN
# =====================
col1, col2, col3 = st.columns([3,6,2])
with col3:
    if not st.session_state.is_admin:
        if st.button("管理員登入"):
            st.session_state.show_login = True
    else:
        if st.button("登出"):
            st.session_state.is_admin = False

if st.session_state.show_login:
    pwd = st.text_input("密碼", type="password")
    if st.button("登入"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.session_state.show_login = False
        else:
            st.error("錯誤")

# =====================
# HERO
# =====================
st.title("實威國際 Portal")

# =====================
# RENDER
# =====================
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

            if st.session_state.is_admin:
                c1, c2 = st.columns(2)

                # ================= EDIT =================
                with c1:
                    if st.button(f"編輯-{category}-{i}"):
                        st.session_state.edit = (category, i)

                # ================= DELETE =================
                with c2:
                    if st.button(f"刪-{category}-{i}"):
                        st.session_state.cards[category].pop(i)
                        st.rerun()

# =====================
# ADD ITEM
# =====================
def add_item(category):
    if st.session_state.is_admin:
        st.markdown(f"### ➕ 新增 {category}")

        t = st.text_input("標題", key=f"t_{category}")
        i = st.text_input("圖片", key=f"i_{category}")
        u = st.text_input("連結", key=f"u_{category}")

        if st.button(f"新增-{category}"):
            st.session_state.cards[category].append(
                {"title": t, "img": i, "url": u}
            )
            st.rerun()

# =====================
# EDIT PANEL（重點🔥）
# =====================
if st.session_state.edit:
    cat, idx = st.session_state.edit
    item = st.session_state.cards[cat][idx]

    st.markdown("## ✏️ 編輯項目")

    new_t = st.text_input("標題", item["title"])
    new_i = st.text_input("圖片", item["img"])
    new_u = st.text_input("連結", item["url"])

    if st.button("儲存修改"):
        st.session_state.cards[cat][idx] = {
            "title": new_t,
            "img": new_i,
            "url": new_u
        }
        st.session_state.edit = None
        st.rerun()

# =====================
# SECTIONS
# =====================
for category in st.session_state.cards.keys():
    st.markdown(f"## {category}")
    render(category)
    add_item(category)

# =====================
# FOOTER
# =====================
st.markdown("<div style='text-align:center;opacity:0.5;margin-top:40px'>SWTC Portal © 2026</div>", unsafe_allow_html=True)
