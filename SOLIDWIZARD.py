import streamlit as st
import requests
import base64
from datetime import datetime

# =========================
# 1. 頁面配置 (必須是第一行指令)
# =========================
st.set_page_config(page_title="實威國際入口網", layout="wide", page_icon="🏢")

# =========================
# 2. 初始化 Session State (防止報錯)
# =========================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if "show_login" not in st.session_state:
    st.session_state.show_login = False

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
            {"title":"智慧製造 YT", "img":"https://images.unsplash.com/photo-1581091226825-a6a2a5aee158", "url":"https://www.youtube.com/@SWTCIM"},
            {"title":"實威知識+", "img":"https://images.unsplash.com/photo-1532012197267-da84d127e765", "url":"https://www.youtube.com/@%E5%AF%A6%E5%A8%81%E7%9F%A5%E8%AD%98"}
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
# 3. 自定義 CSS (Awwwards 風格)
# =========================
st.markdown("""
<style>
    .stApp { background:#F7F8FA; color:#111; }
    .hero { text-align:center; padding:30px 0; }
    .hero h1 { font-size:42px; font-weight:800; }
    .card {
        background:#fff; border-radius:18px; overflow:hidden;
        box-shadow:0 10px 30px rgba(0,0,0,0.06); transition:0.3s;
        margin-bottom: 12px; height: 250px;
    }
    .card:hover { transform:translateY(-5px); box-shadow:0 15px 40px rgba(0,0,0,0.12); }
    .card img { width:100%; height:160px; object-fit:cover; }
    .card-title { padding:12px; font-weight:700; text-align:center; color: #333; font-size: 15px; }
    a { text-decoration: none; color: inherit; }
</style>
""", unsafe_allow_html=True)

# =========================
# 4. 工具函式: GitHub 上傳
# =========================
def upload_to_github(uploaded_file):
    try:
        conf = st.secrets["github"]
        content = base64.b64encode(uploaded_file.getvalue()).decode()
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
        path = f"assets/images/{filename}"
        
        url = f"https://api.github.com/repos/{conf['owner']}/{conf['repo']}/contents/{path}"
        headers = {"Authorization": f"token {conf['token']}"}
        data = {"message": f"Upload {filename}", "content": content, "branch": conf.get("branch", "main")}
        
        res = requests.put(url, headers=headers, json=data)
        if res.status_code == 201:
            return f"https://raw.githubusercontent.com/{conf['owner']}/{conf['repo']}/{conf.get('branch', 'main')}/{path}"
    except Exception as e:
        st.error(f"GitHub 上傳失敗: {e}")
    return None

# =========================
# 5. 管理員登入邏輯
# =========================
col_login, _ = st.columns([2, 8])
with col_login:
    if not st.session_state.is_admin:
        if st.button("🔑 管理登入"): st.session_state.show_login = True
    else:
        if st.button("🚪 登出管理"):
            st.session_state.is_admin = False
            st.rerun()

if st.session_state.get("show_login") and not st.session_state.is_admin:
    with st.form("login_form"):
        pwd = st.text_input("密碼", type="password")
        if st.form_submit_button("登入"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.session_state.show_login = False
                st.rerun()
            else: st.error("密碼錯誤")

# =========================
# 6. 編輯面板 (修正後的表單)
# =========================
if st.session_state.is_admin and st.session_state.edit_info:
    info = st.session_state.edit_info
    item = st.session_state.cards[info['cat']][info['idx']]
    
    with st.expander("🛠️ 正在編輯項目", expanded=True):
        new_file = st.file_uploader("上傳新圖片更換", type=["jpg","png"], key="edit_up")
        if new_file:
            with st.spinner("上傳中..."):
                new_url = upload_to_github(new_file)
                if new_url:
                    item['img'] = new_url
                    st.success("圖片網址已更新！")

        with st.form("edit_submit_form"):
            et = st.text_input("標題", value=item['title'])
            eu = st.text_input("跳轉網址", value=item['url'])
            ei = st.text_input("圖片連結 (可手動修改)", value=item['img'])
            
            c1, c2 = st.columns(2)
            if c1.form_submit_button("💾 儲存修改"):
                st.session_state.cards[info['cat']][info['idx']] = {"title": et, "img": ei, "url": eu}
                st.session_state.edit_info = None
                st.rerun()
            if c2.form_submit_button("❌ 取消編輯"):
                st.session_state.edit_info = None
                st.rerun()

# =========================
# 7. 渲染分類區塊
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
                    if b1.button("✎", key=f"edit_{cat_name}_{real_idx}"):
                        st.session_state.edit_info = {"cat": cat_name, "idx": real_idx}
                        st.rerun()
                    if b2.button("✘", key=f"del_{cat_name}_{real_idx}"):
                        st.session_state.cards[cat_name].pop(real_idx)
                        st.rerun()

# =========================
# 8. 主畫面佈局
# =========================
st.markdown('<div class="hero"><h1>實威國際入口網</h1><p>Digital Portal Dashboard</p></div>', unsafe_allow_html=True)

for cat in list(st.session_state.cards.keys()):
    st.subheader(f"📂 {cat}")
    render_section(cat)
    
    if st.session_state.is_admin:
        with st.expander(f"➕ 在 {cat} 新增項目"):
            add_file = st.file_uploader("上傳封面圖片", type=["jpg","png"], key=f"add_up_{cat}")
            img_val = ""
            if add_file:
                with st.spinner("圖片上傳 GitHub 中..."):
                    res = upload_to_github(add_file)
                    if res: 
                        img_val = res
                        st.success("上傳成功！")

            with st.form(f"add_form_{cat}"):
                nt = st.text_input("名稱")
                nu = st.text_input("網址", value="https://")
                ni = st.text_input("圖片網址 (自動帶入)", value=img_val)
                if st.form_submit_button("確認加入"):
                    if nt and ni:
                        st.session_state.cards[cat].append({"title":nt, "img":ni, "url":nu})
                        st.rerun()

st.markdown("---")
st.markdown("<div style='text-align:center; opacity:0.3; padding:20px;'>SWTC Portal © 2026</div>", unsafe_allow_html=True)
