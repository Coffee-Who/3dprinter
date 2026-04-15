import streamlit as st

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Portal", layout="wide", page_icon="🏢")

# =========================
# Session State
# =========================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False
# 用來記錄目前正在編輯哪個分類的第幾個項目: {"cat": "分類名", "idx": 0}
if "edit_info" not in st.session_state:
    st.session_state.edit_info = None

ADMIN_PASSWORD = "0000"

# =========================
# Awwwards 風格 CSS
# =========================
st.markdown("""
<style>
.stApp { background:#F7F8FA; color:#111; }
.hero { text-align:center; padding:20px 40px 40px 40px; }
.hero h1 { font-size:44px; font-weight:800; margin-bottom:0; }
.card {
    background:#fff; border-radius:18px; overflow:hidden;
    box-shadow:0 10px 30px rgba(0,0,0,0.08); transition:0.3s;
    margin-bottom: 10px;
}
.card:hover { transform:translateY(-6px); }
.card img { width:100%; height:160px; object-fit:cover; }
.card-title { padding:10px; font-weight:700; text-align:center; color: #333; }
a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# =========================
# 初始化資料
# =========================
if "cards" not in st.session_state:
    st.session_state.cards = {
        "內部系統": [
            {"title":"CRM", "img":"https://images.unsplash.com/photo-1551288049-bebda4e38f71", "url":"#"},
            {"title":"EIP", "img":"https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", "url":"#"}
        ],
        "官方系統": [
            {"title":"官網", "img":"https://images.unsplash.com/photo-1522071820081-009f0129c71c", "url":"#"}
        ]
    }

# =========================
# 頂部列 (登入/登出)
# =========================
l_col, r_col = st.columns([8, 2])
with r_col:
    if not st.session_state.is_admin:
        if st.button("管理員登入"):
            st.session_state.show_login = True
    else:
        if st.button("登出管理模式"):
            st.session_state.is_admin = False
            st.session_state.edit_info = None
            st.rerun()

if st.session_state.show_login and not st.session_state.is_admin:
    with st.form("login_form"):
        pwd = st.text_input("輸入密碼", type="password")
        if st.form_submit_button("送出"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("密碼錯誤")

# =========================
# HERO 區塊
# =========================
st.markdown("""
<div class="hero">
<h1>數位入口網</h1>
<p>Modern Dashboard</p>
</div>
""", unsafe_allow_html=True)

# =========================
# 編輯功能邏輯區
# =========================
if st.session_state.is_admin and st.session_state.edit_info:
    cat = st.session_state.edit_info["cat"]
    idx = st.session_state.edit_info["idx"]
    item = st.session_state.cards[cat][idx]
    
    st.info(f"正在編輯：{cat} - {item['title']}")
    with st.form("edit_form"):
        new_t = st.text_input("新標題", value=item['title'])
        new_i = st.text_input("新圖片 URL", value=item['img'])
        new_u = st.text_input("新連結 URL", value=item['url'])
        c1, c2 = st.columns(2)
        if c1.form_submit_button("儲存修改"):
            st.session_state.cards[cat][idx] = {"title": new_t, "img": new_i, "url": new_u}
            st.session_state.edit_info = None
            st.rerun()
        if c2.form_submit_button("取消編輯"):
            st.session_state.edit_info = None
            st.rerun()

# =========================
# 渲染函數 (含刪除與編輯按鈕)
# =========================
def render_section(category):
    items = st.session_state.cards.get(category, [])
    if not items:
        st.write("目前沒有項目")
        return

    # 每行顯示 5 個
    for i in range(0, len(items), 5):
        cols = st.columns(5)
        chunk = items[i : i + 5]
        for sub_idx, item in enumerate(chunk):
            real_idx = i + sub_idx
            with cols[sub_idx]:
                # 卡片本體
                st.markdown(f"""
                <a href="{item['url']}" target="_blank">
                    <div class="card">
                        <img src="{item['img']}">
                        <div class="card-title">{item['title']}</div>
                    </div>
                </a>
                """, unsafe_allow_html=True)
                
                # 管理員按鈕
                if st.session_state.is_admin:
                    btn_col1, btn_col2 = st.columns(2)
                    if btn_col1.button("✎", key=f"edit_{category}_{real_idx}", help="編輯"):
                        st.session_state.edit_info = {"cat": category, "idx": real_idx}
                        st.rerun()
                    if btn_col2.button("✘", key=f"del_{category}_{real_idx}", help="刪除"):
                        st.session_state.cards[category].pop(real_idx)
                        st.rerun()

def add_new_section(category):
    if st.session_state.is_admin:
        with st.expander(f"➕ 新增 {category} 項目"):
            with st.form(f"add_{category}"):
                t = st.text_input("標題")
                i = st.text_input("圖片 URL")
                u = st.text_input("連結 URL")
                if st.form_submit_button("確認新增"):
                    if t and i and u:
                        st.session_state.cards[category].append({"title": t, "img": i, "url": u})
                        st.rerun()

# =========================
# 主畫面循環
# =========================
for category in list(st.session_state.cards.keys()):
    st.markdown(f"### {category}")
    render_section(category)
    add_new_section(category)
    st.markdown("---")

# =========================
# FOOTER
# =========================
st.markdown("<div style='text-align:center;opacity:0.3;padding:20px'>Portal © 2026</div>", unsafe_allow_html=True)
