import streamlit as st
import requests
import base64
from datetime import datetime

# =========================
# 1. 頁面配置與極簡 CSS
# =========================
st.set_page_config(page_title="實威國際入口網", layout="wide", page_icon="🏢")

st.markdown("""
<style>
    .stApp { background:#F7F8FA; color:#111; }
    .hero { text-align:center; padding:30px 0; }
    .hero h1 { font-size:42px; font-weight:800; color: #1A1A1A; margin-bottom: 10px; }
    .card {
        background:#fff; border-radius:16px; overflow:hidden;
        box-shadow:0 8px 25px rgba(0,0,0,0.05); transition:0.3s;
        margin-bottom: 12px; border: 1px solid #F0F0F0;
    }
    .card:hover { transform:translateY(-5px); box-shadow:0 12px 35px rgba(0,0,0,0.1); }
    .card img { width:100%; height:160px; object-fit:cover; }
    .card-title { padding:12px; font-weight:700; text-align:center; color: #333; font-size: 15px; }
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# =========================
# 2. Session State 初始化資料
# =========================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "edit_info" not in st.session_state:
    st.session_state.edit_info = None

if "cards" not in st.session_state:
    st.session_state.cards = {
        "內部系統": [
            {"title":"CRM", "img":"https://images.unsplash.com/photo-1551288049-bebda4e38f71", "url":"http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx"},
            {"title":"EIP", "img":"https://images.unsplash.com/photo-1454165804606-c3d57bc86b40", "url":"http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx"},
            {"title":"EASYFLOW", "img":"https://images.unsplash.com/photo-1551836022-d5d88e9218df", "url":"http://192.168.100.85/efnet/"},
            {"title":"請假系統", "img":"https://images.unsplash.com/photo-1508385082359-f38ae991e8f2", "url":"http://192.168.2.251/MotorWeb/CHIPage/Login.asp"}
        ],
        "官方系統": [
            {"title":"實威國際官網", "img":"https://images.unsplash.com/photo-1522071820081-009f0129c71c", "url":"https://www.swtc.com/zh-tw/"},
            {"title":"實威國際 YT", "img":"https://images.unsplash.com/photo-1611162616475-46b635cb6868", "url":"https://www.youtube.com/@solidwizard"},
            {"title":"實威國際 智慧製造 YT", "img":"https://images.unsplash.com/photo-1581091226825-a6a2a5aee158", "url":"https://www.youtube.com/@SWTCIM"},
            {"title":"實威知識+", "img":"https://images.unsplash.com/photo-1532012197267-da84d127e765", "url":"https://www.youtube.com/@實威知識"}
        ],
        "軟體": [
            {"title":"SOLIDWORKS", "img":"https://images.unsplash.com/photo-1581092335397-9fa1f9a2d2a1", "url":"https://www.solidworks.com/"}
        ],
        "Formlabs": [
            {"title":"Formlabs 原廠", "img":"https://images.unsplash.com/photo-1581090700227-1e37b190418e", "url":"https://formlabs.com/"},
            {"title":"Formlabs Support", "img":"https://images.unsplash.com/photo-1555949963-aa79dcee981c", "url":"https://support.formlabs.com/s/?language=zh_CN"}
        ]
    }

ADMIN_PASSWORD = "0000"

# =========================
# 3. GitHub API 上傳邏輯
# =========================
def upload_to_github(uploaded_file):
    try:
        conf = st.secrets["github"]
        encoded = base64.b64encode(uploaded_file.getvalue()).decode()
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
        path = f"assets/portal_images/{filename}"
        
        url = f"https://api.github.com/repos/{conf['owner']}/{conf['repo']}/contents/{path}"
        headers = {"Authorization": f"token {conf['token']}"}
        payload = {"message": f"Upload {filename}", "content": encoded, "branch": conf.get("branch", "main")}
        
        res = requests.put(url, headers=headers, json=payload)
        if res.status_code == 201:
            return f"https://raw.githubusercontent.com/{conf['owner']}/{conf['repo']}/{conf.get('branch', 'main')}/{path}"
    except Exception as e:
        st.error(f"GitHub 上傳失敗: {e}")
    return None

# =========================
# 4. 頂部導航與登入
# =========================
t_col1, t_col2 = st.columns([8, 2])
with t_col2:
    if not st.session_state.is_admin:
        if st.button("🔑 管理員登入"):
            st.session_state.show_login = True
    else:
        if st.button("🚪 登出系統"):
            st.session_state.is_admin = False
            st.rerun()

if st.session_state.get("show_login") and not st.session_state.is_admin:
    with st.form("login_panel"):
        pwd = st.text_input("請輸入管理密碼", type="password")
        if st.form_submit_button("登入"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("密碼不正確")

st.markdown('<div class="hero"><h1>實威國際入口網</h1><p>Modern Service Portal</p></div>', unsafe_allow_html=True)

# =========================
# 5. 編輯表單 (懸浮展開)
# =========================
if st.session_state.is_admin and st.session_state.edit_info:
    info = st.session_state.edit_info
    item = st.session_state.cards[info['cat']][info['idx']]
    with st.expander("🛠️ 正在編輯項目", expanded=True):
        with st.form("edit_item_form"):
            et = st.text_input("標題", value=item['title'])
            eu = st.text_input("網址", value=item['url'])
            ei = st.text_input("圖片連結", value=item['img'])
            c1, c2 = st.columns(2)
            if c1.form_submit_button("💾 儲存修改"):
                st.session_state.cards[info['cat']][info['idx']] = {"title": et, "img": ei, "url": eu}
                st.session_state.edit_info = None
                st.rerun()
            if c2.form_submit_button("取消"):
                st.session_state.edit_info = None
                st.rerun()

# =========================
# 6. 分類渲染 (Fragment 優化)
# =========================
@st.fragment
def render_section(cat_name):
    items = st.session_state.cards.get(cat_name, [])
    for i in range(0, len(items), 5):
        cols = st.columns(5)
        chunk = items[i:i+5]
        for idx, item in enumerate(chunk):
            real_idx = i + idx
            with cols[idx]:
                st.markdown(f"""
                <a href="{item['url']}" target="_blank">
                    <div class="card">
                        <img src="{item['img']}">
                        <div class="card-title">{item['title']}</div>
                    </div>
                </a>
                """, unsafe_allow_html=True)
                
                if st.session_state.is_admin:
                    b1, b2 = st.columns(2)
                    if b1.button("✎", key=f"e_{cat_name}_{real_idx}"):
                        st.session_state.edit_info = {"cat": cat_name, "idx": real_idx}
                        st.rerun()
                    if b2.button("✘", key=f"d_{cat_name}_{real_idx}"):
                        st.session_state.cards[cat_name].pop(real_idx)
                        st.rerun()

# =========================
# 7. 主迴圈
# =========================
for cat in list(st.session_state.cards.keys()):
    st.subheader(f"📂 {cat}")
    render_section(cat)
    
    if st.session_state.is_admin:
        with st.expander(f"➕ 新增項目到 {cat}"):
            up_file = st.file_uploader("上傳圖片到 GitHub (選填)", type=["jpg","png"], key=f"up_{cat}")
            if up_file and st.button("確認上傳", key=f"btn_up_{cat}"):
                with st.spinner("上傳至 GitHub..."):
                    res_url = upload_to_github(up_file)
                    if res_url: 
                        st.session_state[f"tmp_{cat}"] = res_url
                        st.success("上傳成功！")
            
            with st.form(f"add_form_{cat}"):
                new_title = st.text_input("名稱")
                new_url = st.text_input("連結", value="https://")
                img_default = st.session_state.get(f"tmp_{cat}", "")
                new_img = st.text_input("圖片網址", value=img_default)
                if st.form_submit_button("加入系統"):
                    if new_title and new_img:
                        st.session_state.cards[cat].append({"title": new_title, "img": new_img, "url": new_url})
                        if f"tmp_{cat}" in st.session_state: del st.session_state[f"tmp_{cat}"]
                        st.rerun()

st.markdown("---")
st.markdown("<div style='text-align:center; opacity:0.3;'>Portal © 2026</div>", unsafe_allow_html=True)
