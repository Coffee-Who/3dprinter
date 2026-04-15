import streamlit as st
import requests
import base64
from datetime import datetime

# =========================
# 1. 頁面配置與 CSS
# =========================
st.set_page_config(page_title="實威國際入口網", layout="wide", page_icon="🏢")

st.markdown("""
<style>
    .stApp { background:#F7F8FA; color:#111; }
    .hero { text-align:center; padding:30px 0; }
    .hero h1 { font-size:40px; font-weight:800; color: #1A1A1A; }
    
    .card {
        background:#fff; border-radius:16px; overflow:hidden;
        box-shadow:0 8px 25px rgba(0,0,0,0.05); transition:0.3s;
        margin-bottom: 12px; border: 1px solid #F0F0F0;
        height: 250px; 
    }
    .card:hover { transform:translateY(-5px); box-shadow:0 12px 35px rgba(0,0,0,0.1); }
    .card img { width:100%; height:160px; object-fit:cover; }
    .card-title { padding:12px; font-weight:700; text-align:center; color: #333; font-size: 15px; }
    a { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# =========================
# 2. 初始化資料
# =========================
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
            {"title":"實威國際 YT", "img":"https://images.unsplash.com/photo-1611162616475-46b635cb6868", "url":"https://www.youtube.com/@solidwizard"}
        ],
        "軟體": [{"title":"SOLIDWORKS", "img":"https://images.unsplash.com/photo-1581092335397-9fa1f9a2d2a1", "url":"https://www.solidworks.com/"}],
        "Formlabs": [
            {"title":"Formlabs 原廠", "img":"https://images.unsplash.com/photo-1581090700227-1e37b190418e", "url":"https://formlabs.com/"},
            {"title":"Formlabs Support", "img":"https://images.unsplash.com/photo-1555949963-aa79dcee981c", "url":"https://support.formlabs.com/s/?language=zh_CN"}
        ]
    }

if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "edit_info" not in st.session_state: st.session_state.edit_info = None

# =========================
# 3. GitHub API 上傳邏輯
# =========================
def upload_to_github(uploaded_file):
    try:
        gh = st.secrets["github"]
        content = base64.b64encode(uploaded_file.getvalue()).decode()
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}"
        path = f"assets/images/{filename}"
        
        url = f"https://api.github.com/repos/{gh['owner']}/{gh['repo']}/contents/{path}"
        headers = {"Authorization": f"token {gh['token']}"}
        data = {"message": f"Upload {filename}", "content": content, "branch": gh.get("branch", "main")}
        
        res = requests.put(url, headers=headers, json=data)
        if res.status_code == 201:
            return f"https://raw.githubusercontent.com/{gh['owner']}/{gh['repo']}/{gh.get('branch', 'main')}/{path}"
    except Exception as e:
        st.error(f"GitHub 上傳失敗: {e}")
    return None

# =========================
# 4. 管理登入
# =========================
c_login, _ = st.columns([2, 8])
with c_login:
    if not st.session_state.is_admin:
        if st.button("🔑 管理登入"): st.session_state.show_login = True
    else:
        if st.button("🚪 登出系統"):
            st.session_state.is_admin = False
            st.rerun()

if st.session_state.get("show_login") and not st.session_state.is_admin:
    with st.form("login_f"):
        p = st.text_input("密碼", type="password")
        if st.form_submit_button("登入"):
            if p == "0000":
                st.session_state.is_admin = True
                st.session_state.show_login = False
                st.rerun()
            else: st.error("密碼錯誤")

st.markdown('<div class="hero"><h1>實威國際入口網</h1><p>以上傳圖片為主的管理模式</p></div>', unsafe_allow_html=True)

# =========================
# 5. 編輯面板 (改為上傳方式)
# =========================
if st.session_state.is_admin and st.session_state.edit_info:
    info = st.session_state.edit_info
    item = st.session_state.cards[info['cat']][info['idx']]
    
    with st.expander("🛠️ 編輯項目資料", expanded=True):
        # 編輯時的上傳器
        new_file = st.file_uploader("更換圖片 (上傳後自動更新網址)", type=["jpg","png"], key="edit_upload")
        if new_file:
            with st.spinner("正在上傳新圖片..."):
                uploaded_url = upload_to_github(new_file)
                if uploaded_url:
                    item['img'] = uploaded_url
                    st.success("圖片已自動更新！")

        with st.form("edit_form"):
            new_t = st.text_input("標題", value=item['title'])
            new_u = st.text_input("網址", value=item['url'])
            new_i = st.text_input("圖片網址 (手動微調)", value=item['img'])
            if st.form_submit_button("💾 儲存所有修改"):
                st.session_state.cards[info['cat']][info['idx']] = {"title": new_t, "img": new_i, "url": new_u}
                st.session_state.edit_info = None
                st.rerun()
            if st.button("取消編輯"):
                st.session_state.edit_info = None
                st.rerun()

# =========================
# 6. 分類渲染 (Fragment 優化)
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
# 7. 主迴圈渲染
# =========================
for cat in list(st.session_state.cards.keys()):
    st.subheader(f"📂 {cat}")
    render_category(cat)
    
    if st.session_state.is_admin:
        with st.expander(f"➕ 在「{cat}」新增項目"):
            # 上傳區域
            new_img_file = st.file_uploader("上傳封面圖片", type=["jpg","png"], key=f"add_up_{cat}")
            current_img_url = ""
            if new_img_file:
                with st.spinner("上傳中..."):
                    res_url = upload_to_github(new_img_file)
                    if res_url: 
                        current_img_url = res_url
                        st.success("圖片上傳成功！")

            # 資料表單
            with st.form(f"add_form_{cat}"):
                t = st.text_input("項目名稱")
                u = st.text_input("跳轉連結", value="https://")
                i = st.text_input("圖片網址 (上傳後會自動填入)", value=current_img_url)
                if st.form_submit_button("確認新增"):
                    if t and i:
                        st.session_state.cards[cat].append({"title": t, "img": i, "url": u})
                        st.rerun()

st.markdown("---")
st.markdown("<div style='text-align:center; opacity:0.3; padding:20px;'>SWTC Portal © 2026</div>", unsafe_allow_html=True)
