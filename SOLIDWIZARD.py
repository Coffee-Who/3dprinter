import streamlit as st
import requests
import base64
from datetime import datetime

# =========================
# 1. Page Config & CSS
# =========================
st.set_page_config(page_title="Portal", layout="wide", page_icon="🏢")

st.markdown("""
<style>
    .stApp { background:#F7F8FA; color:#111; }
    .hero { text-align:center; padding:20px; }
    .card {
        background:#fff; border-radius:18px; overflow:hidden;
        box-shadow:0 10px 30px rgba(0,0,0,0.08); transition:0.3s;
        margin-bottom: 10px;
    }
    .card:hover { transform:translateY(-6px); }
    .card img { width:100%; height:180px; object-fit:cover; }
    .card-title { padding:10px; font-weight:700; text-align:center; }
    a { text-decoration: none; color: inherit; }
</style>
""", unsafe_allow_html=True)

# =========================
# 2. Session State 初始化
# =========================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "edit_info" not in st.session_state:
    st.session_state.edit_info = None  # 格式: {"cat": "分類名", "idx": 0}

if "cards" not in st.session_state:
    st.session_state.cards = {
        "內部系統": [
            {"title":"CRM", "img":"https://images.unsplash.com/photo-1551288049-bebda4e38f71", "url":"#"},
            {"title":"EIP", "img":"https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", "url":"#"}
        ]
    }

ADMIN_PASSWORD = "0000"

# =========================
# 3. GitHub 上傳工具 (選填，需配置 Secrets)
# =========================
def upload_to_github(uploaded_file):
    try:
        token = st.secrets["github"]["token"]
        owner = st.secrets["github"]["owner"]
        repo = st.secrets["github"]["repo"]
        path = f"assets/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
        
        encoded = base64.b64encode(uploaded_file.getvalue()).decode()
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {"Authorization": f"token {token}"}
        data = {"message": "upload", "content": encoded, "branch": "main"}
        
        res = requests.put(url, headers=headers, json=data)
        if res.status_code == 201:
            return f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
    except:
        pass
    return None

# =========================
# 4. 管理員登入與編輯面板
# =========================
col_login, _ = st.columns([1, 5])
with col_login:
    if not st.session_state.is_admin:
        if st.button("🔑 管理登入"):
            st.session_state.show_login = True
    else:
        if st.button("🚪 登出"):
            st.session_state.is_admin = False
            st.rerun()

if st.session_state.get("show_login") and not st.session_state.is_admin:
    pwd = st.text_input("輸入密碼", type="password")
    if st.button("確認"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.session_state.show_login = False
            st.rerun()

# --- 編輯面板 (當 edit_info 有值時顯示) ---
if st.session_state.is_admin and st.session_state.edit_info:
    info = st.session_state.edit_info
    item = st.session_state.cards[info['cat']][info['idx']]
    
    st.info(f"正在編輯: {item['title']}")
    with st.form("edit_form"):
        new_t = st.text_input("標題", value=item['title'])
        new_u = st.text_input("連結", value=item['url'])
        new_i = st.text_input("圖片連結", value=item['img'])
        c1, c2 = st.columns(2)
        if c1.form_submit_button("💾 儲存修改"):
            st.session_state.cards[info['cat']][info['idx']] = {"title": new_t, "img": new_i, "url": new_u}
            st.session_state.edit_info = None
            st.rerun()
        if c2.form_submit_button("❌ 取消"):
            st.session_state.edit_info = None
            st.rerun()

# =========================
# 5. 渲染函數 (Fragment 優化)
# =========================
@st.fragment
def render_category(category):
    items = st.session_state.cards.get(category, [])
    for i in range(0, len(items), 5):
        cols = st.columns(5)
        chunk = items[i:i+5]
        for idx, item in enumerate(chunk):
            real_idx = i + idx
            with cols[idx]:
                # 卡片 HTML
                st.markdown(f"""
                <a href="{item['url']}" target="_blank">
                    <div class="card">
                        <img src="{item['img']}">
                        <div class="card-title">{item['title']}</div>
                    </div>
                </a>
                """, unsafe_allow_html=True)
                
                # 管理按鈕
                if st.session_state.is_admin:
                    b1, b2 = st.columns(2)
                    if b1.button("✎", key=f"edit_{category}_{real_idx}"):
                        st.session_state.edit_info = {"cat": category, "idx": real_idx}
                        st.rerun()
                    if b2.button("✘", key=f"del_{category}_{real_idx}"):
                        st.session_state.cards[category].pop(real_idx)
                        st.rerun()

# =========================
# 6. 主程式
# =========================
st.markdown('<div class="hero"><h1>數位入口</h1></div>', unsafe_allow_html=True)

for category in list(st.session_state.cards.keys()):
    st.markdown(f"### {category}")
    render_category(category)
    
    # 新增功能
    if st.session_state.is_admin:
        with st.expander(f"➕ 新增項目到 {category}"):
            up_file = st.file_uploader("上傳圖片 (選填)", type=["jpg","png"], key=f"file_{category}")
            with st.form(f"add_{category}"):
                t = st.text_input("標題")
                u = st.text_input("網址")
                i = st.text_input("圖片連結 (若上傳請留空)")
                if st.form_submit_button("確認新增"):
                    final_img = i
                    if up_file: # 若有上傳則觸發 GitHub 上傳
                        final_img = upload_to_github(up_file) or i
                    st.session_state.cards[category].append({"title": t, "img": final_img, "url": u})
                    st.rerun()
