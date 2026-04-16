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
# SAFE SECRETS（重點修正）
# =========================
# 不會再 KeyError
TOKEN = st.secrets.get("GITHUB_TOKEN", None)
GITHUB_REPO = st.secrets.get("GITHUB_REPO", None)

# debug 顯示（可刪）
if TOKEN is None:
    st.warning("⚠️ 未設定 GITHUB_TOKEN（目前使用本機模式）")

# =========================
# FULL HTML (你的 V2 Portal)
# =========================
html_code = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>實威國際入口網 V2</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">

<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#F4F5F8;
  --surface:#fff;
  --text:#111;
  --text2:#666;
  --accent:#2563EB;
  --border:#E5E7EB;
  --radius:16px;
}

body{
  font-family:'DM Sans','Noto Sans TC',sans-serif;
  background:var(--bg);
  color:var(--text);
}

.page{
  max-width:1200px;
  margin:0 auto;
  padding:20px;
}

.header{
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:10px 0;
  border-bottom:1px solid var(--border);
}

.logo{
  font-weight:800;
  font-size:18px;
}

.badge{
  background:var(--accent);
  color:#fff;
  padding:4px 10px;
  border-radius:999px;
  font-size:12px;
}

.grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(180px,1fr));
  gap:16px;
  margin-top:20px;
}

.card{
  background:var(--surface);
  border-radius:var(--radius);
  overflow:hidden;
  border:1px solid var(--border);
  transition:.2s;
  cursor:pointer;
  text-decoration:none;
  color:inherit;
}

.card:hover{
  transform:translateY(-4px);
}

.card img{
  width:100%;
  height:100px;
  object-fit:cover;
}

.card .title{
  padding:10px;
  font-size:14px;
  font-weight:600;
}

.section-title{
  margin-top:30px;
  font-size:16px;
  font-weight:700;
}
</style>
</head>

<body>
<div class="page">

  <div class="header">
    <div class="logo">實威國際 Portal V2</div>
    <div class="badge">企業入口</div>
  </div>

  <div class="section-title">內部系統</div>
  <div class="grid">

    <a class="card" href="http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx" target="_blank">
      <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=640">
      <div class="title">CRM</div>
    </a>

    <a class="card" href="http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx" target="_blank">
      <img src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=640">
      <div class="title">EIP</div>
    </a>

    <a class="card" href="http://192.168.100.85/efnet/" target="_blank">
      <img src="https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=640">
      <div class="title">EASYFLOW</div>
    </a>

    <a class="card" href="http://192.168.2.251/MotorWeb/CHIPage/Login.asp" target="_blank">
      <img src="https://images.unsplash.com/photo-1508385082359-f38ae991e8f2?w=640">
      <div class="title">請假系統</div>
    </a>

  </div>

  <div class="section-title">官方系統</div>
  <div class="grid">

    <a class="card" href="https://www.swtc.com/zh-tw/" target="_blank">
      <img src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=640">
      <div class="title">官網</div>
    </a>

    <a class="card" href="https://www.youtube.com/@solidwizard" target="_blank">
      <img src="https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=640">
      <div class="title">YouTube</div>
    </a>

  </div>

</div>
</body>
</html>
"""

# =========================
# RENDER
# =========================
components.html(html_code, height=900, scrolling=True)
