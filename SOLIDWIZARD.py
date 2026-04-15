import streamlit as st
import requests
import base64
import os
from datetime import datetime

# =========================
# 1. Page Config & CSS
# =========================
st.set_page_config(page_title="Digital Portal", layout="wide", page_icon="🏢")

st.markdown("""
<style>
    .stApp { background:#F7F8FA; color:#111; }
    .hero { text-align:center; padding:30px; }
    .hero h1 { font-size:40px; font-weight:800; color: #1A1A1A; }
    .card {
        background:#fff; border-radius:15px; overflow:hidden;
        box-shadow:0 8px 20px rgba(0,0,0,0.05); transition:0.3s;
        margin-bottom: 10px; border: 1px solid #EEE;
    }
    .card:hover { transform:translateY(-5px); box-shadow:0 12px 30px rgba(0,0,0,0.1); }
    .card img { width:100%; height:150px; object-fit:cover; }
    .card-title { padding:12px; font-weight:700; text-align:center; color: #333; font-size: 15px; }
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# =========================
# 2. Session State 初始化
# =========================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "cards" not in st.session_state:
    st.session_state.cards = {
        "常用系統": [
            {"title":"Google", "img":"https://images.unsplash.com/photo-1573804633927-bfcbcd909acd", "url":"https://google.com"},
        ]
    }
if "edit_info" not in st.session_state:
    st.session_state.edit_info = None

ADMIN_PASSWORD = "0000"

# =========================
# 3. GitHub 上傳工具函式
# =========================
def upload_to_github(uploaded_file):
    try:
        # 讀取 Secrets
        token = st.secrets["github"]["token"]
        owner = st.secrets["github"]["owner"]
        repo = st.secrets["github"]["repo"]
        branch = st.secrets["github"].get("branch", "main")
        
        # 轉換編碼
        encoded_content = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
        
        # 定義資料夾與檔名 (存放在 assets/portal_images/)
        file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
        path = f"assets/portal_images/{file_name}"
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
        data = {"message": f"Upload {file_name}", "content": encoded_content, "branch": branch}
        
        res = requests.put(url, headers=headers, json=data)
        if res.status_code == 201:
            return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
        else:
            st.error(f"GitHub API 錯誤: {res.json().get('message')}")
            return None
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

# =========================
# 4. UI 頂部控制列
# =========================
col_t1, col_t2 = st.columns([8, 2])
with col_t2:
    if not st.session_state.is_admin:
        if st.button("🔑 管理登入"):
            st.session_state.show_login = True
    else:
        if st.button("🚪 登出管理"):
            st.session_state.is_admin = False
            st.rerun()

if st.session_state.get("show_login") and not st.session_state.is_admin:
    with st.form("login_p"):
        p = st.text_input("密碼", type="password")
        if st.form_submit_button("登入"):
            if p == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("密碼錯誤")

st.markdown('<div class="hero"><h1>數位入口門戶</h1><p>Modern Portal Dashboard</p></div>', unsafe_allow_html=True)

# =========================
# 5. 編輯功能區塊
# =========================
if st.session_state.is_admin and st.session_state.edit_info:
    info = st.session_state.edit_info
    item = st.session_state.cards[info['cat']][info['idx']]
    
    with st.expander("🛠️ 編輯項目資料", expanded=True):
        with st.form("edit_form"):
            new_t = st.text_input("標題", value=item['title'])
            new_u = st.text_input("連結 URL", value=item['url'])
            new_i = st.text_input("圖片 URL", value=item['img'])
            c1, c2 = st.columns(2)
            if c1.form_submit_button("儲存修改"):
                st.session_state.cards[info['cat']][info['idx']] = {"title": new_t, "img": new_i, "url": new_u}
                st.session_state.edit_info = None
                st.rerun()
            if c2.form_submit_button("取消"):
                st.session_state.edit_info = None
                st.rerun()

# =========================
# 6. 核心渲染功能 (Fragment 優化)
# =========================
@st.fragment
def render_category(cat_name):
    items = st.session_state.cards.get(cat_name, [])
    for i in range(0, len(items), 5):
        cols = st.columns(5)
        chunk = items[i:i+5]
        for idx, item in enumerate(chunk):
            real_idx = i + idx
            with cols[idx]:
                # 卡片
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
                    if b1.button("✎", key=f"ed_{cat_name}_{real_idx}"):
                        st.session_state.edit_info = {"cat": cat_name, "idx": real_idx}
                        st.rerun()
                    if b2.button("✘", key=f"del_{cat_name}_{real_idx}"):
                        st.session_state.cards[cat_name].pop(real_idx)
                        st.rerun()

# =========================
# 7. 主程式循環
# =========================
for cat in list(st.session_state.cards.keys()):
    st.subheader(f"📂 {cat}")
    render_category(cat)
    
    # 新增項目區 (僅限管理員)
    if st.session_state.is_admin:
        with st.expander(f"➕ 在 {cat} 新增項目"):
            # 選項：上傳圖片到 GitHub
            up_file = st.file_uploader("上傳圖片至 GitHub (選填)", type=["jpg","png"], key=f"file_{cat}")
            gh_url = ""
            if up_file:
                if st.button("確認上傳圖片", key=f"up_btn_{cat}"):
                    with st.spinner("上傳中..."):
                        res_url = upload_to_github(up_file)
                        if res_url:
                            st.session_state[f"tmp_url_{cat}"] = res_url
                            st.success("GitHub 上傳成功！")
            
            # 正式新增表單
            with st.form(f"add_form_{cat}"):
                t = st.text_input("名稱")
                u = st.text_input("目標網址", value="https://")
                default_img = st.session_state.get(f"tmp_url_{cat}", "")
                i = st.text_input("圖片網址 (手動或自動帶入)", value=default_img)
                
                if st.form_submit_button("確認加入"):
                    if t and i and u:
                        st.session_state.cards[cat].append({"title":t, "img":i, "url":u})
                        if f"tmp_url_{cat}" in st.session_state: 
                            del st.session_state[f"tmp_url_{cat}"]
                        st.rerun()

# =========================
# 8. Footer
# =========================
st.markdown("---")
st.markdown("<div style='text-align:center; opacity:0.5;'>Digital Dashboard © 2026</div>", unsafe_allow_html=True)
