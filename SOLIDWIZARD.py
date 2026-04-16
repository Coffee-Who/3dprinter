<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>實威國際入口網</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
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
  --danger-bg:#FFF1F1;
  --danger-border:#FCA5A5;
  --danger-text:#B91C1C;
  --radius:16px;
  --radius-sm:10px;
  --radius-xs:7px;
  --shadow:0 2px 14px rgba(0,0,0,0.07);
  --shadow-md:0 4px 20px rgba(0,0,0,0.10);
  --shadow-lg:0 10px 40px rgba(0,0,0,0.14);
}

/* DARK MODE */
@media (prefers-color-scheme: dark) {
  :root{
    --bg:#0F1117;
    --surface:#1A1D27;
    --surface2:#242736;
    --text:#EEEEF3;
    --text2:#9090A8;
    --text3:#55556A;
    --accent:#3B82F6;
    --accent-hover:#2563EB;
    --accent-light:#1E2A45;
    --accent-border:#1E3A6B;
    --border:#2A2D3E;
    --border2:#3A3D52;
    --danger-bg:#2A1515;
    --danger-border:#7F2A2A;
    --danger-text:#FCA5A5;
    --shadow:0 2px 14px rgba(0,0,0,0.3);
    --shadow-md:0 4px 20px rgba(0,0,0,0.4);
    --shadow-lg:0 10px 40px rgba(0,0,0,0.5);
  }
}

html{scroll-behavior:smooth}

body{
  font-family:'DM Sans','Noto Sans TC',sans-serif;
  background:var(--bg);
  color:var(--text);
  min-height:100vh;
  line-height:1.5;
}

/* ===== LAYOUT ===== */
.page-wrap{max-width:1240px;margin:0 auto;padding:0 20px 80px}

/* ===== HEADER ===== */
.header{
  display:flex;align-items:center;justify-content:space-between;
  padding:18px 0 14px;
  border-bottom:1px solid var(--border);
  margin-bottom:8px;
  flex-wrap:wrap;gap:10px;
}
.header-logo{display:flex;align-items:center;gap:10px;text-decoration:none}
.logo-mark{
  width:34px;height:34px;border-radius:9px;
  background:var(--accent);
  display:flex;align-items:center;justify-content:center;
  flex-shrink:0;
}
.logo-mark svg{width:18px;height:18px;fill:none;stroke:#fff;stroke-width:2}
.logo-text{font-size:16px;font-weight:700;letter-spacing:-0.4px;color:var(--text)}
.logo-text small{font-weight:400;color:var(--text3);font-size:13px;margin-left:5px}
.header-right{display:flex;align-items:center;gap:8px;flex-wrap:wrap}

/* ===== BADGES ===== */
.badge{
  display:inline-flex;align-items:center;gap:5px;
  font-size:12px;font-weight:600;
  padding:4px 10px;border-radius:20px;
  background:var(--accent-light);color:var(--accent);
  border:1px solid var(--accent-border);
}

/* ===== BUTTONS ===== */
.btn{
  display:inline-flex;align-items:center;gap:6px;
  padding:8px 16px;border-radius:var(--radius-xs);
  font-size:13px;font-weight:500;
  cursor:pointer;border:1.5px solid var(--border);
  background:var(--surface);color:var(--text);
  transition:background .15s,border-color .15s,transform .1s;
  font-family:inherit;white-space:nowrap;
}
.btn:hover{background:var(--surface2);border-color:var(--border2)}
.btn:active{transform:scale(0.97)}
.btn.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.primary:hover{background:var(--accent-hover);border-color:var(--accent-hover)}
.btn.danger{background:var(--danger-bg);color:var(--danger-text);border-color:var(--danger-border)}
.btn.danger:hover{filter:brightness(0.95)}
.btn.sm{padding:5px 11px;font-size:12px}
.btn.icon{padding:7px;border-radius:8px}
.btn:disabled{opacity:0.5;cursor:not-allowed}

/* ===== HERO ===== */
.hero{
  text-align:center;
  padding:40px 0 30px;
}
.hero-eyebrow{
  display:inline-flex;align-items:center;gap:6px;
  font-size:12px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;
  color:var(--accent);margin-bottom:14px;
}
.hero-eyebrow::before,.hero-eyebrow::after{content:'';width:24px;height:1px;background:var(--accent);opacity:0.5}
.hero h1{
  font-size:clamp(28px,5vw,48px);
  font-weight:700;
  letter-spacing:-1.5px;
  line-height:1.1;
  color:var(--text);
}
.hero h1 em{font-style:normal;color:var(--accent)}
.hero p{color:var(--text2);font-size:15px;margin-top:10px;letter-spacing:0.2px}

/* ===== ADMIN NOTICE ===== */
.admin-notice{
  background:var(--accent-light);
  border:1px solid var(--accent-border);
  border-radius:var(--radius-sm);
  padding:10px 16px;
  font-size:13px;color:var(--accent);font-weight:500;
  margin-bottom:24px;
  display:flex;align-items:center;gap:8px;
  flex-wrap:wrap;
}
.admin-notice::before{content:'✦';font-size:10px}

/* ===== SECTIONS ===== */
.section{margin-bottom:40px;animation:fadeUp .3s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}

.section-header{
  display:flex;align-items:center;justify-content:space-between;
  margin-bottom:16px;flex-wrap:wrap;gap:10px;
}
.section-label{display:flex;align-items:center;gap:10px}
.section-tag{
  font-size:10px;font-weight:700;letter-spacing:1.2px;
  text-transform:uppercase;
  background:var(--accent-light);color:var(--accent);
  padding:4px 10px;border-radius:20px;
  border:1px solid var(--accent-border);
  flex-shrink:0;
}
.section-label h2{
  font-size:17px;font-weight:700;
  letter-spacing:-0.3px;color:var(--text);
}
.section-actions{display:flex;gap:6px}

/* ===== CARDS GRID ===== */
.cards-grid{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(170px,1fr));
  gap:16px;
}
@media(max-width:600px){
  .cards-grid{grid-template-columns:repeat(2,1fr);gap:12px}
}
@media(max-width:360px){
  .cards-grid{grid-template-columns:1fr}
}

/* ===== CARD ===== */
.card{
  background:var(--surface);
  border-radius:var(--radius);
  overflow:hidden;
  box-shadow:var(--shadow);
  border:1px solid var(--border);
  transition:transform .2s,box-shadow .2s,border-color .2s;
  display:flex;flex-direction:column;
}
a.card{text-decoration:none;cursor:pointer}
a.card:hover,.card.clickable:hover{
  transform:translateY(-5px);
  box-shadow:var(--shadow-lg);
  border-color:var(--border2);
}
.card-thumb{
  width:100%;aspect-ratio:16/9;
  object-fit:cover;display:block;
  background:var(--surface2);
  flex-shrink:0;
}
.card-placeholder{
  width:100%;aspect-ratio:16/9;
  background:var(--surface2);
  display:flex;align-items:center;justify-content:center;
  font-size:32px;
  flex-shrink:0;
}
.card-body{padding:11px 13px 14px;flex:1}
.card-title{
  font-size:13px;font-weight:600;color:var(--text);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}
.card-host{
  font-size:11px;color:var(--text3);
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  margin-top:3px;
}
.card-admin-bar{
  display:flex;gap:5px;
  padding:0 10px 10px;
}
.card-edit-btn{
  flex:1;font-size:11px;font-weight:500;
  padding:5px 0;border-radius:6px;
  border:1px solid var(--border);
  background:var(--surface2);
  cursor:pointer;color:var(--text2);
  transition:.15s;font-family:inherit;
}
.card-edit-btn:hover{
  background:var(--accent-light);
  color:var(--accent);border-color:var(--accent-border);
}
.card-del-btn{
  font-size:11px;font-weight:500;
  padding:5px 9px;border-radius:6px;
  border:1px solid var(--danger-border);
  background:var(--danger-bg);
  cursor:pointer;color:var(--danger-text);
  transition:.15s;font-family:inherit;
}
.card-del-btn:hover{filter:brightness(0.93)}

/* empty state */
.empty-state{
  grid-column:1/-1;
  text-align:center;padding:32px;
  color:var(--text3);font-size:14px;
  border:2px dashed var(--border);
  border-radius:var(--radius);
}

/* ===== MODAL OVERLAY ===== */
.overlay{
  display:none;position:fixed;inset:0;
  background:rgba(0,0,0,0.5);
  z-index:9000;
  align-items:center;justify-content:center;
  padding:16px;
  backdrop-filter:blur(3px);
  -webkit-backdrop-filter:blur(3px);
}
.overlay.open{display:flex}

/* ===== MODAL ===== */
.modal{
  background:var(--surface);
  border-radius:20px;
  width:100%;max-width:480px;
  box-shadow:var(--shadow-lg);
  border:1px solid var(--border);
  overflow:hidden;
  animation:modalIn .2s ease both;
  max-height:90vh;
  display:flex;flex-direction:column;
}
@keyframes modalIn{from{opacity:0;transform:scale(0.96) translateY(8px)}to{opacity:1;transform:scale(1) translateY(0)}}

.modal-header{
  padding:18px 20px 15px;
  border-bottom:1px solid var(--border);
  display:flex;justify-content:space-between;align-items:center;
  flex-shrink:0;
}
.modal-header h3{font-size:16px;font-weight:700;color:var(--text)}
.modal-close{
  background:none;border:none;
  font-size:16px;cursor:pointer;
  color:var(--text3);
  width:28px;height:28px;
  border-radius:7px;
  display:flex;align-items:center;justify-content:center;
  transition:.15s;
}
.modal-close:hover{background:var(--surface2);color:var(--text)}

.modal-body{
  padding:20px;
  overflow-y:auto;
  flex:1;
}
.modal-body .field{margin-bottom:16px}
.modal-body label{
  display:block;
  font-size:11px;font-weight:700;
  color:var(--text2);
  margin-bottom:6px;
  text-transform:uppercase;letter-spacing:.6px;
}
.modal-body input[type=text],
.modal-body input[type=url],
.modal-body input[type=password]{
  width:100%;
  padding:10px 13px;
  border:1.5px solid var(--border);
  border-radius:var(--radius-xs);
  font-size:14px;
  font-family:inherit;
  color:var(--text);
  background:var(--surface);
  transition:.2s;
  -webkit-appearance:none;
}
.modal-body input:focus{
  outline:none;
  border-color:var(--accent);
  box-shadow:0 0 0 3px rgba(37,99,235,.12);
}

/* IMAGE UPLOAD */
.img-preview{
  width:100%;aspect-ratio:16/9;
  object-fit:cover;
  border-radius:10px;
  border:1.5px solid var(--border);
  display:none;margin-bottom:8px;
}
.img-preview.show{display:block}

.upload-zone{
  width:100%;aspect-ratio:16/9;
  border:2px dashed var(--border);
  border-radius:10px;
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  gap:8px;cursor:pointer;
  transition:.2s;
  background:var(--surface2);
}
.upload-zone:hover{border-color:var(--accent);background:var(--accent-light)}
.upload-zone.hidden{display:none}
.upload-zone svg{width:30px;height:30px;stroke:var(--text3);fill:none;stroke-width:1.5}
.upload-zone span{font-size:13px;color:var(--text2);font-weight:500}
.upload-zone small{font-size:11px;color:var(--text3)}
.img-change-row{display:none;margin-top:6px}
.img-change-row.show{display:block}

.modal-footer{
  padding:14px 20px;
  border-top:1px solid var(--border);
  display:flex;justify-content:flex-end;gap:8px;
  flex-shrink:0;
}

/* ===== LOGIN MODAL ===== */
.login-box{
  background:var(--surface);
  border-radius:20px;
  width:100%;max-width:340px;
  box-shadow:var(--shadow-lg);
  border:1px solid var(--border);
  padding:32px 28px;
  text-align:center;
  animation:modalIn .2s ease both;
}
.login-box .lock-icon{
  width:52px;height:52px;
  background:var(--accent-light);
  border-radius:14px;
  display:flex;align-items:center;justify-content:center;
  margin:0 auto 16px;
}
.login-box .lock-icon svg{width:24px;height:24px;stroke:var(--accent);fill:none;stroke-width:2}
.login-box h3{font-size:19px;font-weight:700;margin-bottom:4px;color:var(--text)}
.login-box p{font-size:13px;color:var(--text2);margin-bottom:20px}
.login-box input{
  width:100%;padding:11px 14px;
  border:1.5px solid var(--border);border-radius:var(--radius-xs);
  font-size:15px;text-align:center;
  letter-spacing:6px;font-family:monospace;
  color:var(--text);background:var(--surface);
  margin-bottom:10px;-webkit-appearance:none;
}
.login-box input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(37,99,235,.12)}
.login-err{font-size:12px;color:var(--danger-text);min-height:16px;margin-bottom:8px;display:block}

/* ===== CATEGORY LIST MODAL ===== */
.cat-row{
  display:flex;align-items:center;gap:10px;
  padding:10px 0;
  border-bottom:1px solid var(--border);
}
.cat-row:last-child{border-bottom:none}
.cat-row-name{flex:1;font-size:14px;font-weight:500;color:var(--text)}
.cat-row-count{font-size:12px;color:var(--text3);margin-right:4px}
.new-cat-row{display:flex;gap:8px;margin-top:14px;padding-top:14px;border-top:1px solid var(--border)}
.new-cat-row input{
  flex:1;padding:9px 12px;
  border:1.5px solid var(--border);border-radius:var(--radius-xs);
  font-size:14px;font-family:inherit;color:var(--text);background:var(--surface);
}
.new-cat-row input:focus{outline:none;border-color:var(--accent)}
.emoji-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.emoji-btn{
  width:32px;height:32px;font-size:16px;border-radius:7px;
  border:1.5px solid var(--border);background:var(--surface2);
  cursor:pointer;display:flex;align-items:center;justify-content:center;
  transition:.15s;
}
.emoji-btn:hover,.emoji-btn.selected{border-color:var(--accent);background:var(--accent-light)}

/* ===== FOOTER ===== */
.footer{
  text-align:center;
  padding:24px;
  font-size:12px;
  color:var(--text3);
  border-top:1px solid var(--border);
  margin-top:16px;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--text3)}

/* ===== RESPONSIVE ===== */
@media(max-width:640px){
  .page-wrap{padding:0 12px 60px}
  .hero h1{letter-spacing:-0.8px}
}
</style>
</head>
<body>

<div class="page-wrap">

  <!-- HEADER -->
  <header class="header">
    <div class="header-logo">
      <div class="logo-mark">
        <svg viewBox="0 0 20 20"><rect x="2" y="2" width="7" height="7" rx="1.5"/><rect x="11" y="2" width="7" height="7" rx="1.5"/><rect x="2" y="11" width="7" height="7" rx="1.5"/><rect x="11" y="11" width="7" height="7" rx="1.5"/></svg>
      </div>
      <span class="logo-text">實威國際<small>Portal</small></span>
    </div>
    <div class="header-right">
      <span class="badge" id="admin-badge" style="display:none">管理員模式</span>
      <button class="btn sm" id="cat-manage-btn" style="display:none" onclick="openCatModal()">
        <svg width="13" height="13" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
        分類管理
      </button>
      <button class="btn sm danger" id="logout-btn" style="display:none" onclick="doLogout()">登出</button>
      <button class="btn sm" id="login-btn" onclick="openLogin()">
        <svg width="13" height="13" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="14" height="8" rx="2"/><path d="M7 11V7a3 3 0 016 0v4"/></svg>
        管理登入
      </button>
    </div>
  </header>

  <!-- HERO -->
  <section class="hero">
    <div class="hero-eyebrow">SWTC Digital Portal</div>
    <h1>實威國際<em>入口網站</em></h1>
    <p>統一管理所有系統入口・Digital Gateway Dashboard</p>
  </section>

  <!-- ADMIN NOTICE -->
  <div class="admin-notice" id="admin-notice" style="display:none">
    管理員模式已啟用：可新增、編輯、刪除連結與分類，圖片上傳後自動裁切為 16:9
  </div>

  <!-- SECTIONS -->
  <div id="sections-container"></div>

  <!-- FOOTER -->
  <footer class="footer">
    SWTC Portal &copy; 2026 &nbsp;·&nbsp; 實威國際股份有限公司
  </footer>
</div>

<!-- ===========================
     LOGIN OVERLAY
=========================== -->
<div class="overlay" id="login-overlay">
  <div class="login-box">
    <div class="lock-icon">
      <svg viewBox="0 0 20 20"><rect x="3" y="9" width="14" height="10" rx="2"/><path d="M7 9V6a3 3 0 016 0v3"/></svg>
    </div>
    <h3>管理員登入</h3>
    <p>請輸入管理員密碼</p>
    <input type="password" id="pwd-input" placeholder="••••" maxlength="20"
      onkeydown="if(event.key==='Enter')doLogin()">
    <span class="login-err" id="login-err"></span>
    <button class="btn primary" style="width:100%;justify-content:center" onclick="doLogin()">登入</button>
    <button class="btn" style="width:100%;justify-content:center;margin-top:8px" onclick="closeOverlay('login-overlay')">取消</button>
  </div>
</div>

<!-- ===========================
     CARD EDIT / ADD OVERLAY
=========================== -->
<div class="overlay" id="card-overlay">
  <div class="modal">
    <div class="modal-header">
      <h3 id="card-modal-title">新增連結</h3>
      <button class="modal-close" onclick="closeOverlay('card-overlay')">✕</button>
    </div>
    <div class="modal-body">
      <div class="field">
        <label>封面圖片</label>
        <img id="img-preview" class="img-preview" src="" alt="預覽">
        <div class="upload-zone" id="upload-zone" onclick="document.getElementById('img-file').click()">
          <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          <span>點擊上傳圖片</span>
          <small>JPG / PNG · 自動裁切為 16:9</small>
        </div>
        <input type="file" id="img-file" accept="image/*" style="display:none" onchange="handleImgUpload(event)">
        <div class="img-change-row" id="img-change-row">
          <button class="btn sm" style="width:100%" onclick="document.getElementById('img-file').click()">
            🖼 更換圖片
          </button>
        </div>
      </div>
      <div class="field">
        <label>名稱</label>
        <input type="text" id="card-name" placeholder="系統或連結名稱">
      </div>
      <div class="field">
        <label>連結網址</label>
        <input type="text" id="card-url" placeholder="https://">
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn" onclick="closeOverlay('card-overlay')">取消</button>
      <button class="btn primary" onclick="saveCard()">💾 儲存</button>
    </div>
  </div>
</div>

<!-- ===========================
     CATEGORY MANAGE OVERLAY
=========================== -->
<div class="overlay" id="cat-overlay">
  <div class="modal">
    <div class="modal-header">
      <h3>分類管理</h3>
      <button class="modal-close" onclick="closeOverlay('cat-overlay')">✕</button>
    </div>
    <div class="modal-body">
      <div id="cat-list-container"></div>
      <div class="new-cat-row">
        <input type="text" id="new-cat-input" placeholder="新分類名稱" onkeydown="if(event.key==='Enter')addCategory()">
        <button class="btn primary" onclick="addCategory()">新增</button>
      </div>
      <div style="margin-top:10px">
        <label style="display:block;font-size:11px;font-weight:700;color:var(--text2);text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px">選擇圖示</label>
        <div class="emoji-row" id="emoji-selector"></div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn" onclick="closeOverlay('cat-overlay')">關閉</button>
    </div>
  </div>
</div>

<script>
// =====================
//  CONFIG
// =====================
const ADMIN_PASS = '0000';
const STORAGE_KEY = 'swtc_portal_v3';

// =====================
//  DEFAULT DATA
// =====================
const DEFAULT_DATA = {
  categories: [
    {
      id: 'internal', name: 'A · 內部系統', emoji: '🏢',
      cards: [
        {title:'CRM', url:'http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx', img:'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=640&q=80'},
        {title:'EIP', url:'http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx', img:'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=640&q=80'},
        {title:'EASYFLOW', url:'http://192.168.100.85/efnet/', img:'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=640&q=80'},
        {title:'請假系統', url:'http://192.168.2.251/MotorWeb/CHIPage/Login.asp', img:'https://images.unsplash.com/photo-1508385082359-f38ae991e8f2?w=640&q=80'}
      ]
    },
    {
      id: 'official', name: 'B · 官方系統', emoji: '🌐',
      cards: [
        {title:'實威國際官網', url:'https://www.swtc.com/zh-tw/', img:'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=640&q=80'},
        {title:'實威國際 YouTube', url:'https://www.youtube.com/@solidwizard', img:'https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=640&q=80'},
        {title:'智慧製造 YouTube', url:'https://www.youtube.com/@SWTCIM', img:'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=640&q=80'},
        {title:'實威知識+', url:'https://www.youtube.com/@實威知識', img:'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=640&q=80'}
      ]
    },
    {
      id: 'solidworks', name: 'C · SOLIDWORKS', emoji: '⚙️',
      cards: [
        {title:'SOLIDWORKS 官網', url:'https://www.solidworks.com/', img:'https://images.unsplash.com/photo-1581092335397-9fa1f9a2d2a1?w=640&q=80'},
        {title:'MySolidWorks', url:'https://my.solidworks.com/', img:'https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?w=640&q=80'},
        {title:'SOLIDWORKS Forum', url:'https://forum.solidworks.com/', img:'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=640&q=80'}
      ]
    },
    {
      id: 'formlabs', name: 'C · Formlabs', emoji: '🖨️',
      cards: [
        {title:'Formlabs 原廠', url:'https://formlabs.com/', img:'https://images.unsplash.com/photo-1581090700227-1e37b190418e?w=640&q=80'},
        {title:'Formlabs Support', url:'https://support.formlabs.com/', img:'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=640&q=80'},
        {title:'Formlabs Dashboard', url:'https://dashboard.formlabs.com/', img:'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=640&q=80'}
      ]
    },
    {
      id: 'scanology', name: 'D · SCANOLOGY', emoji: '📡',
      cards: [
        {title:'SCANOLOGY 官網', url:'https://www.scanology.com/', img:'https://images.unsplash.com/photo-1518770660439-4636190af475?w=640&q=80'}
      ]
    }
  ]
};

// =====================
//  STATE
// =====================
let appData = null;
let isAdmin = false;
let editState = null; // {catIdx, cardIdx} — cardIdx=null means new
let selectedEmoji = '📁';

const EMOJIS = ['📁','🏢','🌐','⚙️','🖨️','📡','💡','🔧','🎯','📊','🔬','🖥️','📱','🌍','⭐','🔑','🗂️','📌'];

// =====================
//  STORAGE (localStorage fallback)
// =====================
async function loadData() {
  try {
    if (window.storage) {
      const r = await window.storage.get(STORAGE_KEY);
      if (r && r.value) return JSON.parse(r.value);
    }
  } catch(e) {}
  try {
    const ls = localStorage.getItem(STORAGE_KEY);
    if (ls) return JSON.parse(ls);
  } catch(e) {}
  return JSON.parse(JSON.stringify(DEFAULT_DATA));
}

async function saveData() {
  const str = JSON.stringify(appData);
  try { if(window.storage) await window.storage.set(STORAGE_KEY, str); } catch(e) {}
  try { localStorage.setItem(STORAGE_KEY, str); } catch(e) {}
}

// =====================
//  RENDER
// =====================
function render() {
  const container = document.getElementById('sections-container');
  container.innerHTML = '';
  appData.categories.forEach((cat, ci) => {
    const sec = document.createElement('section');
    sec.className = 'section';
    sec.id = 'section-' + ci;
    sec.innerHTML = `
      <div class="section-header">
        <div class="section-label">
          <span class="section-tag">${cat.emoji}</span>
          <h2>${escHtml(cat.name)}</h2>
        </div>
        <div class="section-actions" id="sec-actions-${ci}" style="display:${isAdmin ? 'flex' : 'none'}">
          <button class="btn sm primary" onclick="openNewCard(${ci})">+ 新增連結</button>
          <button class="btn sm danger" onclick="confirmDeleteCat(${ci})">刪除分類</button>
        </div>
      </div>
      <div class="cards-grid" id="grid-${ci}"></div>
    `;
    container.appendChild(sec);
    renderGrid(ci);
  });
}

function renderGrid(ci) {
  const grid = document.getElementById('grid-' + ci);
  if (!grid) return;
  grid.innerHTML = '';
  const cat = appData.categories[ci];

  if (cat.cards.length === 0) {
    grid.innerHTML = '<div class="empty-state">此分類尚無連結，點上方「+ 新增連結」加入</div>';
    return;
  }

  cat.cards.forEach((card, ki) => {
    const el = document.createElement(isAdmin ? 'div' : 'a');
    el.className = 'card' + (isAdmin ? '' : '');
    if (!isAdmin) {
      el.href = card.url;
      el.target = '_blank';
      el.rel = 'noopener noreferrer';
    }

    const imgHtml = card.img
      ? `<img class="card-thumb" src="${escAttr(card.img)}" alt="${escAttr(card.title)}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">`
      : '';
    const placeholderStyle = card.img ? 'style="display:none"' : '';
    const hostPart = (() => {
      try { return new URL(card.url).hostname.replace(/^www\./, ''); } catch(e) { return card.url; }
    })();

    el.innerHTML = `
      ${imgHtml}
      <div class="card-placeholder" ${placeholderStyle}>🔗</div>
      <div class="card-body">
        <div class="card-title">${escHtml(card.title)}</div>
        <div class="card-host">${escHtml(hostPart)}</div>
      </div>
      ${isAdmin ? `
      <div class="card-admin-bar">
        <button class="card-edit-btn" onclick="event.preventDefault();event.stopPropagation();openEditCard(${ci},${ki})">✎ 編輯</button>
        <button class="card-del-btn" onclick="event.preventDefault();event.stopPropagation();confirmDeleteCard(${ci},${ki})">✕</button>
      </div>` : ''}
    `;
    grid.appendChild(el);
  });
}

// =====================
//  AUTH
// =====================
function openLogin() {
  document.getElementById('pwd-input').value = '';
  document.getElementById('login-err').textContent = '';
  openOverlay('login-overlay');
  setTimeout(() => document.getElementById('pwd-input').focus(), 150);
}

function doLogin() {
  const val = document.getElementById('pwd-input').value;
  if (val === ADMIN_PASS) {
    isAdmin = true;
    closeOverlay('login-overlay');
    document.getElementById('admin-badge').style.display = '';
    document.getElementById('logout-btn').style.display = '';
    document.getElementById('cat-manage-btn').style.display = '';
    document.getElementById('login-btn').style.display = 'none';
    document.getElementById('admin-notice').style.display = '';
    render();
  } else {
    document.getElementById('login-err').textContent = '密碼錯誤，請再試一次';
    document.getElementById('pwd-input').select();
  }
}

function doLogout() {
  if (!confirm('確定要登出管理員模式？')) return;
  isAdmin = false;
  document.getElementById('admin-badge').style.display = 'none';
  document.getElementById('logout-btn').style.display = 'none';
  document.getElementById('cat-manage-btn').style.display = 'none';
  document.getElementById('login-btn').style.display = '';
  document.getElementById('admin-notice').style.display = 'none';
  render();
}

// =====================
//  OVERLAYS
// =====================
function openOverlay(id) { document.getElementById(id).classList.add('open'); }
function closeOverlay(id) { document.getElementById(id).classList.remove('open'); }

// Close on backdrop click
document.querySelectorAll('.overlay').forEach(el => {
  el.addEventListener('click', function(e) {
    if (e.target === this) closeOverlay(this.id);
  });
});

// =====================
//  IMAGE UPLOAD → canvas resize 16:9
// =====================
function handleImgUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      const W = 640, H = 360;
      const canvas = document.createElement('canvas');
      canvas.width = W; canvas.height = H;
      const ctx = canvas.getContext('2d');
      const ratio = Math.max(W / img.width, H / img.height);
      const nw = img.width * ratio, nh = img.height * ratio;
      ctx.drawImage(img, (W - nw) / 2, (H - nh) / 2, nw, nh);
      const b64 = canvas.toDataURL('image/jpeg', 0.85);
      const preview = document.getElementById('img-preview');
      preview.src = b64;
      preview.classList.add('show');
      preview.dataset.b64 = b64;
      document.getElementById('upload-zone').classList.add('hidden');
      document.getElementById('img-change-row').classList.add('show');
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

function resetImgModal() {
  const preview = document.getElementById('img-preview');
  preview.src = '';
  preview.classList.remove('show');
  preview.dataset.b64 = '';
  document.getElementById('upload-zone').classList.remove('hidden');
  document.getElementById('img-change-row').classList.remove('show');
  document.getElementById('img-file').value = '';
}

// =====================
//  CARD CRUD
// =====================
function openNewCard(ci) {
  editState = { catIdx: ci, cardIdx: null };
  document.getElementById('card-modal-title').textContent = '新增連結';
  document.getElementById('card-name').value = '';
  document.getElementById('card-url').value = 'https://';
  resetImgModal();
  openOverlay('card-overlay');
  setTimeout(() => document.getElementById('card-name').focus(), 150);
}

function openEditCard(ci, ki) {
  editState = { catIdx: ci, cardIdx: ki };
  const card = appData.categories[ci].cards[ki];
  document.getElementById('card-modal-title').textContent = '編輯連結';
  document.getElementById('card-name').value = card.title;
  document.getElementById('card-url').value = card.url;

  const preview = document.getElementById('img-preview');
  if (card.img) {
    preview.src = card.img;
    preview.classList.add('show');
    preview.dataset.b64 = card.img;
    document.getElementById('upload-zone').classList.add('hidden');
    document.getElementById('img-change-row').classList.add('show');
  } else {
    resetImgModal();
  }
  openOverlay('card-overlay');
}

async function saveCard() {
  const name = document.getElementById('card-name').value.trim();
  const url = document.getElementById('card-url').value.trim();
  const img = document.getElementById('img-preview').dataset.b64 || '';
  if (!name) { alert('請輸入連結名稱'); return; }
  if (!url || url === 'https://') { alert('請輸入有效網址'); return; }

  const { catIdx, cardIdx } = editState;
  const card = { title: name, url, img };

  if (cardIdx === null) {
    appData.categories[catIdx].cards.push(card);
  } else {
    appData.categories[catIdx].cards[cardIdx] = card;
  }
  await saveData();
  closeOverlay('card-overlay');
  renderGrid(catIdx);
}

function confirmDeleteCard(ci, ki) {
  const name = appData.categories[ci].cards[ki].title;
  if (!confirm(`確定要刪除「${name}」？`)) return;
  deleteCard(ci, ki);
}

async function deleteCard(ci, ki) {
  appData.categories[ci].cards.splice(ki, 1);
  await saveData();
  renderGrid(ci);
}

// =====================
//  CATEGORY CRUD
// =====================
function openCatModal() {
  renderCatList();
  renderEmojiSelector();
  openOverlay('cat-overlay');
}

function renderCatList() {
  const container = document.getElementById('cat-list-container');
  if (appData.categories.length === 0) {
    container.innerHTML = '<p style="font-size:13px;color:var(--text3);text-align:center;padding:12px">尚無分類</p>';
    return;
  }
  container.innerHTML = appData.categories.map((cat, ci) => `
    <div class="cat-row">
      <span style="font-size:18px">${cat.emoji}</span>
      <span class="cat-row-name">${escHtml(cat.name)}</span>
      <span class="cat-row-count">${cat.cards.length} 項</span>
      <button class="btn sm danger" onclick="confirmDeleteCatFromModal(${ci})">刪除</button>
    </div>
  `).join('');
}

function renderEmojiSelector() {
  const row = document.getElementById('emoji-selector');
  row.innerHTML = EMOJIS.map(e => `
    <button class="emoji-btn${selectedEmoji === e ? ' selected' : ''}"
      onclick="selectEmoji('${e}')" title="${e}">${e}</button>
  `).join('');
}

function selectEmoji(e) {
  selectedEmoji = e;
  renderEmojiSelector();
}

async function addCategory() {
  const val = document.getElementById('new-cat-input').value.trim();
  if (!val) { alert('請輸入分類名稱'); return; }
  appData.categories.push({
    id: 'cat_' + Date.now(),
    name: val,
    emoji: selectedEmoji,
    cards: []
  });
  document.getElementById('new-cat-input').value = '';
  await saveData();
  renderCatList();
  render();
}

function confirmDeleteCatFromModal(ci) {
  const cat = appData.categories[ci];
  if (!confirm(`確定刪除分類「${cat.name}」及其 ${cat.cards.length} 個連結？`)) return;
  deleteCategoryAt(ci);
}

function confirmDeleteCat(ci) {
  const cat = appData.categories[ci];
  if (!confirm(`確定刪除分類「${cat.name}」及其所有連結？`)) return;
  deleteCategoryAt(ci);
}

async function deleteCategoryAt(ci) {
  appData.categories.splice(ci, 1);
  await saveData();
  renderCatList();
  render();
}

// =====================
//  UTILS
// =====================
function escHtml(s) {
  return String(s)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;')
    .replace(/'/g,'&#39;');
}
function escAttr(s) { return escHtml(s); }

// =====================
//  INIT
// =====================
(async () => {
  appData = await loadData();
  render();
})();
</script>
</body>
</html>
