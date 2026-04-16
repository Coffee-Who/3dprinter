import streamlit as st
import streamlit.components.v1 as components

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="實威國際 Portal V2",
    layout="wide"
)

# =========================
# SAFE SECRETS（避免 KeyError）
# =========================
def safe_get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return None

GITHUB_TOKEN = safe_get_secret("GITHUB_TOKEN")
GITHUB_REPO = safe_get_secret("GITHUB_REPO")

# =========================
# SIDEBAR STATUS
# =========================
with st.sidebar:
    st.title("⚙️ V2 System")

    st.write("GitHub 狀態：")

    if GITHUB_TOKEN:
        st.success("TOKEN 已設定")
    else:
        st.warning("未設定 GITHUB_TOKEN（可忽略，不影響 UI）")

    if GITHUB_REPO:
        st.success(GITHUB_REPO)
    else:
        st.warning("未設定 REPO")

    st.markdown("---")
    st.info("V2 = UI Portal + 安全 secrets + 可擴充 GitHub 同步")

# =========================
# FULL HTML PORTAL (你的完整 UI)
# =========================
html_code = r"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>實威國際入口網 V2</title>

<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">

<style>
/* ===== BASE ===== */
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:'DM Sans','Noto Sans TC',sans-serif;
  background:#0f1117;
  color:#eee;
}

/* ===== LAYOUT ===== */
.page-wrap{max-width:1200px;margin:auto;padding:20px}

/* ===== HEADER ===== */
.header{
  display:flex;justify-content:space-between;align-items:center;
  padding:16px 0;border-bottom:1px solid #2a2d3e;
}
.logo{font-size:18px;font-weight:700;color:#3b82f6}

/* ===== GRID ===== */
.grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(180px,1fr));
  gap:14px;
  margin-top:20px;
}

/* ===== CARD ===== */
.card{
  background:#1a1d27;
  border-radius:14px;
  overflow:hidden;
  text-decoration:none;
  color:white;
  transition:0.2s;
  border:1px solid #2a2d3e;
}
.card:hover{
  transform:translateY(-5px);
  border-color:#3b82f6;
}
.card img{
  width:100%;
  height:110px;
  object-fit:cover;
}
.card-body{
  padding:10px;
}
.card-title{
  font-size:14px;
  font-weight:600;
}
.card-sub{
  font-size:11px;
  color:#aaa;
  margin-top:3px;
}

/* ===== SECTION ===== */
.section-title{
  margin-top:30px;
  font-size:16px;
  color:#3b82f6;
  font-weight:700;
}

</style>
</head>

<body>

<div class="page-wrap">

  <div class="header">
    <div class="logo">實威國際 Portal V2</div>
  </div>

  <!-- SECTION -->
  <div class="section-title">A · 內部系統</div>
  <div class="grid">

    <a class="card" href="http://192.168.100.85/WebCRM" target="_blank">
      <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600">
      <div class="card-body">
        <div class="card-title">CRM</div>
        <div class="card-sub">Internal System</div>
      </div>
    </a>

    <a class="card" href="http://192.168.100.89/SWTCweb4.0" target="_blank">
      <img src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600">
      <div class="card-body">
        <div class="card-title">EIP</div>
        <div class="card-sub">Portal</div>
      </div>
    </a>

  </div>

  <!-- SECTION -->
  <div class="section-title">B · 官方系統</div>
  <div class="grid">

    <a class="card" href="https://www.swtc.com" target="_blank">
      <img src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600">
      <div class="card-body">
        <div class="card-title">官方網站</div>
        <div class="card-sub">SWTC</div>
      </div>
    </a>

    <a class="card" href="https://youtube.com" target="_blank">
      <img src="https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=600">
      <div class="card-body">
        <div class="card-title">YouTube</div>
        <div class="card-sub">Channel</div>
      </div>
    </a>

  </div>

</div>

</body>
</html>
"""

components.html(html_code, height=900, scrolling=True)
