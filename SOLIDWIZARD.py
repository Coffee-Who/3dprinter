import streamlit as st
import requests
import base64
from datetime import datetime

# =========================
# 1. 頁面配置
# =========================
st.set_page_config(page_title="實威國際入口網", layout="wide", page_icon="🏢")

# =========================
# 2. 初始化 Session State
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
            {"title":"EASYFLOW", "img":"https://images.unsplash.com/photo-1551836022-d5d88e9218df", "url":"http://192.168.100.85/efnet/"}
        ],
        "官方系統": [
            {"title":"實威官網", "img":"https://images.unsplash.com/photo-1522071820081-009f0129c71c", "url":"https://www.swtc.com/zh-tw/"}
        ]
    }

# =========================
# 3. 注入精務 CSS (修正 SyntaxError)
# =========================
# 使用 r''' ''' 原始字串來避免 Python 轉義符號問題
st.markdown(r'''
<style>
:root {
  --bg:#F4F5F8;
  --surface:#ffffff;
  --surface2:#F0F1F6;
  --text:#111111;
  --text2:#555566;
  --text3:#9999AA;
  --accent:#2563EB;
  --accent-hover:#1d4ed8;
  --accent-light:#EFF4FF;
  --accent-border:#BFDBFE;
  --border:#E2E4EC;
  --border2:#C8CBD8;
  --radius:16px;
  --radius-sm:10px;
  --radius-xs:7px;
  --shadow:0 2px 14px rgba(0,0,0,0.07);
  --shadow-md:0 4px 20px rgba(0,0,0,0.10);
  --shadow-lg:0 10px 40px rgba(0,0,0,0.14);
}

.card {
  background: var(--surface);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  border: 1px solid var(--border);
  transition: transform .2s, box-shadow .2s;
  display: flex;
  flex-direction: column;
  text-decoration: none;
  height: 250px;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border2);
}
.card-thumb {
  width: 100%; height: 160px; object-fit: cover; border-bottom: 1px solid var(--border);
}
.card-body { padding: 12px; flex: 1; }
.card-title { font-size: 14px; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.card-host { font-size: 11px; color: var(--text3); }

.hero { text-align: center; padding: 40px 0; }
.hero h1 { font-size: 42px; font-weight: 700; color: var(--text); letter-spacing: -1px; }
.hero h1 em { font-style: normal; color: var(--accent); }
</style>
''', unsafe_allow_html=True)

# =========================
# 4. GitHub 上傳功能
# =========================
def upload_to_github(uploaded_file):
    try:
        if "github" not in st.secrets:
            st.error("Secrets 中找不到 [github] 設定")
            return None
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
        st.error(f"上傳失敗: {e}")
    return None

# =========================
# 5. 管理功能 (登入與編輯)
# =========================
col_l, col_r = st.columns([2, 8])
with col_l:
    if not st.session_state.is_admin:
        if st.button("🔑 管理登入"):
            pwd = st.text_input("請輸入密碼", type="password")
            if pwd == "0000":
                st.session_state.is_admin = True
                st.rerun()
    else:
        if st.button("🚪 登出模式"):
            st.session_state.is_admin = False
            st.rerun()

# 編輯面板
if st.session_state.is_admin and st.session_state.edit_info:
    info = st.session_state.edit_info
    item = st.session_state.cards[info['cat']][info['idx']]
    with st.expander("🛠️ 編輯連結資訊", expanded=True):
        up_file = st.file_uploader("更換圖片", type=["jpg","png"], key="edit_up")
        if up_file:
            new_url = upload_to_github(up_file)
            if new_url: item['img'] = new_url
        
        with st.form("edit_form"):
            new_t = st.text_input("名稱", value=item['title'])
            new_u = st.text_input("網址", value=item['url'])
            new_i = st.text_input("圖片連結", value=item['img'])
            c1, c2 = st.columns(2)
            if c1.form_submit_button("儲存"):
                st.session_state.cards[info['cat']][info['idx']] = {"title":new_t, "url":new_u, "img":new_i}
                st.session_state.edit_info = None
                st.rerun()
            if c2.form_submit_button("取消"):
                st.session_state.edit_info = None
                st.rerun()

# =========================
# 6. 主介面渲染
# =========================
st.markdown('<div class="hero"><h1>實威國際<em>入口網站</em></h1><p>Digital Gateway Dashboard</p></div>', unsafe_allow_html=True)

for cat_name, items in st.session_state.cards.items():
    st.subheader(f"📂 {cat_name}")
    
    # 建立網格
    cols = st.columns(5)
    for idx, item in enumerate(items):
        with cols[idx % 5]:
            # 使用你提供的 HTML 結構
            st.markdown(f'''
            <a href="{item['url']}" target="_blank" class="card">
                <img src="{item['img']}" class="card-thumb">
                <div class="card-body">
                    <div class="card-title">{item['title']}</div>
                    <div class="card-host">{item['url'].split('/')[2] if '://' in item['url'] else ''}</div>
                </div>
            </a>
            ''', unsafe_allow_html=True)
            
            if st.session_state.is_admin:
                b1, b2 = st.columns(2)
                if b1.button("✎", key=f"e_{cat_name}_{idx}"):
                    st.session_state.edit_info = {"cat": cat_name, "idx": idx}
                    st.rerun()
                if b2.button("✕", key=f"d_{cat_name}_{idx}"):
                    st.session_state.cards[cat_name].pop(idx)
                    st.rerun()

    # 新增按鈕 (管理模式)
    if st.session_state.is_admin:
        with st.expander(f"➕ 在 {cat_name} 新增連結"):
            new_img_file = st.file_uploader("上傳圖片", type=["jpg","png"], key=f"add_{cat_name}")
            img_path = ""
            if new_img_file:
                img_path = upload_to_github(new_img_file)
            
            with st.form(f"f_{cat_name}"):
                nt = st.text_input("名稱")
                nu = st.text_input("網址", value="https://")
                ni = st.text_input("圖片網址", value=img_path)
                if st.form_submit_button("確認新增"):
                    st.session_state.cards[cat_name].append({"title":nt, "url":nu, "img":ni})
                    st.rerun()

st.markdown("---")
st.caption("SWTC Portal © 2026")
