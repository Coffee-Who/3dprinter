import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="實威國際入口網")

html_code = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#F4F5F8;--surface:#fff;--surface2:#F0F1F6;
  --text:#111;--text2:#555566;--text3:#9999AA;
  --accent:#2563EB;--accent-h:#1d4ed8;
  --accent-light:#EFF4FF;--accent-border:#BFDBFE;
  --border:#E2E4EC;--border2:#C8CBD8;
  --danger-bg:#FFF1F1;--danger-border:#FCA5A5;--danger-text:#B91C1C;
  --r:16px;--rs:10px;--rxs:7px;
  --sh:0 2px 14px rgba(0,0,0,.07);--sh-lg:0 10px 40px rgba(0,0,0,.14);
}
@media(prefers-color-scheme:dark){:root{
  --bg:#0F1117;--surface:#1A1D27;--surface2:#242736;
  --text:#EEEEF3;--text2:#9090A8;--text3:#55556A;
  --accent:#3B82F6;--accent-h:#2563EB;
  --accent-light:#1E2A45;--accent-border:#1E3A6B;
  --border:#2A2D3E;--border2:#3A3D52;
  --danger-bg:#2A1515;--danger-border:#7F2A2A;--danger-text:#FCA5A5;
  --sh:0 2px 14px rgba(0,0,0,.3);--sh-lg:0 10px 40px rgba(0,0,0,.5);
}}
html{scroll-behavior:smooth}
body{font-family:'DM Sans','Noto Sans TC',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;line-height:1.5}
.wrap{max-width:1240px;margin:0 auto;padding:0 20px 80px}

/* HEADER */
.header{display:flex;align-items:center;justify-content:space-between;padding:18px 0 14px;border-bottom:1px solid var(--border);margin-bottom:8px;flex-wrap:wrap;gap:10px}
.logo{display:flex;align-items:center;gap:10px}
.logo-mark{width:34px;height:34px;border-radius:9px;background:var(--accent);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.logo-mark svg{width:18px;height:18px;fill:none;stroke:#fff;stroke-width:2}
.logo-text{font-size:16px;font-weight:700;letter-spacing:-0.4px;color:var(--text)}
.logo-text small{font-weight:400;color:var(--text3);font-size:13px;margin-left:5px}
.hdr{display:flex;align-items:center;gap:8px;flex-wrap:wrap}

/* BADGES */
.badge{display:inline-flex;align-items:center;gap:5px;font-size:12px;font-weight:600;padding:4px 10px;border-radius:20px;background:var(--accent-light);color:var(--accent);border:1px solid var(--accent-border)}

/* BUTTONS */
.btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:var(--rxs);font-size:13px;font-weight:500;cursor:pointer;border:1.5px solid var(--border);background:var(--surface);color:var(--text);transition:.15s;font-family:inherit;white-space:nowrap}
.btn:hover{background:var(--surface2);border-color:var(--border2)}
.btn:active{transform:scale(0.97)}
.btn.primary{background:var(--accent);color:#fff;border-color:var(--accent)}
.btn.primary:hover{background:var(--accent-h)}
.btn.danger{background:var(--danger-bg);color:var(--danger-text);border-color:var(--danger-border)}
.btn.sm{padding:5px 11px;font-size:12px}
.btn:disabled{opacity:.5;cursor:not-allowed}

/* HERO */
.hero{text-align:center;padding:40px 0 30px}
.eyebrow{display:inline-flex;align-items:center;gap:6px;font-size:12px;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;color:var(--accent);margin-bottom:14px}
.eyebrow::before,.eyebrow::after{content:'';width:24px;height:1px;background:var(--accent);opacity:.5}
.hero h1{font-size:clamp(28px,5vw,48px);font-weight:700;letter-spacing:-1.5px;line-height:1.1}
.hero h1 em{font-style:normal;color:var(--accent)}
.hero p{color:var(--text2);font-size:15px;margin-top:10px}

/* NOTICES */
.notice{background:var(--accent-light);border:1px solid var(--accent-border);border-radius:var(--rs);padding:10px 16px;font-size:13px;color:var(--accent);font-weight:500;margin-bottom:24px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.notice.warn{background:#fffbeb;border-color:#fcd34d;color:#92400e}
@media(prefers-color-scheme:dark){.notice.warn{background:#1c1700;border-color:#854d0e;color:#fbbf24}}

/* SECTIONS */
.section{margin-bottom:40px;animation:fadeUp .3s ease both}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.sec-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:10px}
.sec-label{display:flex;align-items:center;gap:10px}
.sec-tag{font-size:10px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;background:var(--accent-light);color:var(--accent);padding:4px 10px;border-radius:20px;border:1px solid var(--accent-border)}
.sec-label h2{font-size:17px;font-weight:700;letter-spacing:-0.3px}
.sec-actions{display:flex;gap:6px}

/* CARDS GRID */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:16px}
@media(max-width:600px){.grid{grid-template-columns:repeat(2,1fr);gap:12px}}
@media(max-width:360px){.grid{grid-template-columns:1fr}}

/* CARD */
.card{background:var(--surface);border-radius:var(--r);overflow:hidden;box-shadow:var(--sh);border:1px solid var(--border);transition:transform .2s,box-shadow .2s;display:flex;flex-direction:column}
a.card{text-decoration:none;cursor:pointer}
a.card:hover{transform:translateY(-5px);box-shadow:var(--sh-lg);border-color:var(--border2)}
.card-thumb{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;background:var(--surface2);flex-shrink:0}
.card-placeholder{width:100%;aspect-ratio:16/9;background:var(--surface2);display:flex;align-items:center;justify-content:center;font-size:32px;flex-shrink:0}
.card-body{padding:11px 13px 14px;flex:1}
.card-title{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.card-host{font-size:11px;color:var(--text3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:3px}
.card-bar{display:flex;gap:5px;padding:0 10px 10px}
.card-edit{flex:1;font-size:11px;font-weight:500;padding:5px 0;border-radius:6px;border:1px solid var(--border);background:var(--surface2);cursor:pointer;color:var(--text2);transition:.15s;font-family:inherit}
.card-edit:hover{background:var(--accent-light);color:var(--accent);border-color:var(--accent-border)}
.card-del{font-size:11px;font-weight:500;padding:5px 9px;border-radius:6px;border:1px solid var(--danger-border);background:var(--danger-bg);cursor:pointer;color:var(--danger-text);transition:.15s;font-family:inherit}
.card-del:hover{filter:brightness(.93)}
.empty{grid-column:1/-1;text-align:center;padding:32px;color:var(--text3);font-size:14px;border:2px dashed var(--border);border-radius:var(--r)}

/* OVERLAYS */
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:9000;align-items:center;justify-content:center;padding:16px;backdrop-filter:blur(3px)}
.overlay.open{display:flex}

/* MODAL */
.modal{background:var(--surface);border-radius:20px;width:100%;max-width:480px;box-shadow:var(--sh-lg);border:1px solid var(--border);overflow:hidden;animation:mIn .2s ease both;max-height:90vh;display:flex;flex-direction:column}
@keyframes mIn{from{opacity:0;transform:scale(.96) translateY(8px)}to{opacity:1;transform:scale(1) translateY(0)}}
.modal-hdr{padding:18px 20px 15px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-shrink:0}
.modal-hdr h3{font-size:16px;font-weight:700}
.modal-x{background:none;border:none;font-size:16px;cursor:pointer;color:var(--text3);width:28px;height:28px;border-radius:7px;display:flex;align-items:center;justify-content:center;transition:.15s}
.modal-x:hover{background:var(--surface2);color:var(--text)}
.modal-body{padding:20px;overflow-y:auto;flex:1}
.field{margin-bottom:16px}
.field label{display:block;font-size:11px;font-weight:700;color:var(--text2);margin-bottom:6px;text-transform:uppercase;letter-spacing:.6px}
.field input[type=text],.field input[type=url],.field input[type=password]{width:100%;padding:10px 13px;border:1.5px solid var(--border);border-radius:var(--rxs);font-size:14px;font-family:inherit;color:var(--text);background:var(--surface);transition:.2s;-webkit-appearance:none}
.field input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(37,99,235,.12)}
.modal-foot{padding:14px 20px;border-top:1px solid var(--border);display:flex;justify-content:flex-end;gap:8px;flex-shrink:0}

/* IMAGE UPLOAD */
.img-prev{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:10px;border:1.5px solid var(--border);display:none;margin-bottom:8px}
.img-prev.show{display:block}
.upload-zone{width:100%;aspect-ratio:16/9;border:2px dashed var(--border);border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;cursor:pointer;transition:.2s;background:var(--surface2)}
.upload-zone:hover{border-color:var(--accent);background:var(--accent-light)}
.upload-zone.hidden{display:none}
.upload-zone svg{width:30px;height:30px;stroke:var(--text3);fill:none;stroke-width:1.5}
.upload-zone span{font-size:13px;color:var(--text2);font-weight:500}
.upload-zone small{font-size:11px;color:var(--text3)}
.img-change{display:none;margin-top:6px}
.img-change.show{display:block}
.upload-prog{display:none;align-items:center;gap:10px;margin-top:8px;font-size:12px;color:var(--text2)}
.upload-prog.show{display:flex}
.prog-bar{flex:1;height:4px;background:var(--border);border-radius:2px;overflow:hidden}
.prog-fill{height:100%;background:var(--accent);width:0;transition:width .3s}

/* LOGIN */
.login-box{background:var(--surface);border-radius:20px;width:100%;max-width:340px;box-shadow:var(--sh-lg);border:1px solid var(--border);padding:32px 28px;text-align:center;animation:mIn .2s ease both}
.lock-icon{width:52px;height:52px;background:var(--accent-light);border-radius:14px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px}
.lock-icon svg{width:24px;height:24px;stroke:var(--accent);fill:none;stroke-width:2}
.login-box h3{font-size:19px;font-weight:700;margin-bottom:4px}
.login-box p{font-size:13px;color:var(--text2);margin-bottom:20px}
.login-box input{width:100%;padding:11px 14px;border:1.5px solid var(--border);border-radius:var(--rxs);font-size:15px;text-align:center;letter-spacing:6px;font-family:monospace;color:var(--text);background:var(--surface);margin-bottom:10px;-webkit-appearance:none}
.login-box input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(37,99,235,.12)}
.login-err{font-size:12px;color:var(--danger-text);min-height:16px;margin-bottom:8px;display:block}

/* CATEGORY LIST */
.cat-row{display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid var(--border)}
.cat-row:last-child{border-bottom:none}
.cat-row-name{flex:1;font-size:14px;font-weight:500}
.cat-row-count{font-size:12px;color:var(--text3);margin-right:4px}
.new-cat-row{display:flex;gap:8px;margin-top:14px;padding-top:14px;border-top:1px solid var(--border)}
.new-cat-row input{flex:1;padding:9px 12px;border:1.5px solid var(--border);border-radius:var(--rxs);font-size:14px;font-family:inherit;color:var(--text);background:var(--surface)}
.new-cat-row input:focus{outline:none;border-color:var(--accent)}
.emoji-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.emoji-btn{width:32px;height:32px;font-size:16px;border-radius:7px;border:1.5px solid var(--border);background:var(--surface2);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:.15s}
.emoji-btn:hover,.emoji-btn.sel{border-color:var(--accent);background:var(--accent-light)}

/* SYNC STATUS */
.sync-status{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--text3)}
.sync-dot{width:7px;height:7px;border-radius:50%;background:var(--text3)}
.sync-dot.ok{background:#22c55e}
.sync-dot.err{background:#ef4444}
.sync-dot.busy{background:#f59e0b;animation:pulse 1s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

/* FOOTER */
.footer{text-align:center;padding:24px;font-size:12px;color:var(--text3);border-top:1px solid var(--border);margin-top:16px}

/* SCROLLBAR */
::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px}

/* RESPONSIVE */
@media(max-width:640px){.wrap{padding:0 12px 60px}}
</style>
</head>
<body>
<div class="wrap">

  <!-- HEADER -->
  <header class="header">
    <div class="logo">
      <div class="logo-mark">
        <svg viewBox="0 0 20 20"><rect x="2" y="2" width="7" height="7" rx="1.5"/><rect x="11" y="2" width="7" height="7" rx="1.5"/><rect x="2" y="11" width="7" height="7" rx="1.5"/><rect x="11" y="11" width="7" height="7" rx="1.5"/></svg>
      </div>
      <span class="logo-text">實威國際<small>Portal</small></span>
    </div>
    <div class="hdr">
      <div class="sync-status" id="sync-status">
        <div class="sync-dot busy" id="sync-dot"></div>
        <span id="sync-text">連線中...</span>
      </div>
      <span class="badge" id="admin-badge" style="display:none">管理員模式</span>
      <button class="btn sm" id="cat-btn" style="display:none" onclick="openCatModal()">分類管理</button>
      <button class="btn sm danger" id="logout-btn" style="display:none" onclick="doLogout()">登出</button>
      <button class="btn sm" id="login-btn" onclick="openLogin()">管理登入</button>
    </div>
  </header>

  <!-- HERO -->
  <section class="hero">
    <div class="eyebrow">SWTC Digital Portal</div>
    <h1>實威國際<em>入口網站</em></h1>
    <p>統一管理所有系統入口 · Digital Gateway Dashboard</p>
  </section>

  <!-- NOTICES -->
  <div class="notice" id="admin-notice" style="display:none">
    ✦ 管理員模式已啟用：可新增、編輯、刪除連結與分類。圖片上傳後自動同步所有裝置。
  </div>
  <div class="notice warn" id="imgur-warn" style="display:none">
    ⚠ 圖片上傳服務暫時無法使用，圖片將改以本機資料儲存（僅限此裝置顯示），建議改貼圖片網址。
  </div>

  <!-- SECTIONS -->
  <div id="sections-container"></div>

  <footer class="footer">SWTC Portal &copy; 2026 &nbsp;·&nbsp; 實威國際股份有限公司</footer>
</div>

<!-- ===== LOGIN OVERLAY ===== -->
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
    <button class="btn" style="width:100%;justify-content:center;margin-top:8px"
            onclick="closeOvl('login-overlay')">取消</button>
  </div>
</div>

<!-- ===== CARD ADD / EDIT OVERLAY ===== -->
<div class="overlay" id="card-overlay">
  <div class="modal">
    <div class="modal-hdr">
      <h3 id="card-modal-title">新增連結</h3>
      <button class="modal-x" onclick="closeOvl('card-overlay')">✕</button>
    </div>
    <div class="modal-body">

      <div class="field">
        <label>封面圖片（上傳後自動同步所有裝置）</label>
        <img id="img-prev" class="img-prev" src="" alt="預覽">
        <div class="upload-zone" id="upload-zone"
             onclick="document.getElementById('img-file').click()">
          <svg viewBox="0 0 24 24">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          <span>點擊上傳圖片</span>
          <small>JPG / PNG · 自動裁切 16:9 並上傳雲端</small>
        </div>
        <input type="file" id="img-file" accept="image/*" style="display:none"
               onchange="handleImgUpload(event)">
        <div class="upload-prog" id="upload-prog">
          <div class="prog-bar"><div class="prog-fill" id="prog-fill"></div></div>
          <span id="prog-text">上傳中...</span>
        </div>
        <div class="img-change" id="img-change">
          <button class="btn sm" style="width:100%"
                  onclick="document.getElementById('img-file').click()">🖼 更換圖片</button>
        </div>
      </div>

      <div class="field">
        <label>或貼上圖片網址（推薦，確保跨裝置顯示）</label>
        <input type="url" id="card-img-url" placeholder="https://example.com/image.jpg"
               oninput="previewUrl(this.value)">
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
    <div class="modal-foot">
      <button class="btn" onclick="closeOvl('card-overlay')">取消</button>
      <button class="btn primary" onclick="saveCard()">💾 儲存</button>
    </div>
  </div>
</div>

<!-- ===== CATEGORY MANAGE OVERLAY ===== -->
<div class="overlay" id="cat-overlay">
  <div class="modal">
    <div class="modal-hdr">
      <h3>分類管理</h3>
      <button class="modal-x" onclick="closeOvl('cat-overlay')">✕</button>
    </div>
    <div class="modal-body">
      <div id="cat-list"></div>
      <div class="new-cat-row">
        <input type="text" id="new-cat-input" placeholder="新分類名稱"
               onkeydown="if(event.key==='Enter')addCat()">
        <button class="btn primary" onclick="addCat()">新增</button>
      </div>
      <div style="margin-top:10px">
        <label style="display:block;font-size:11px;font-weight:700;color:var(--text2);
                      text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px">選擇圖示</label>
        <div class="emoji-row" id="emoji-sel"></div>
      </div>
    </div>
    <div class="modal-foot">
      <button class="btn" onclick="closeOvl('cat-overlay')">關閉</button>
    </div>
  </div>
</div>

<script>
/* =====================
   CONFIG
===================== */
const ADMIN_PASS    = '0000';          // ← 修改此處變更管理員密碼
const SK            = 'swtc_portal_v4';
const IMGUR_CLIENT_ID = 'f4e34cfbcb66d73'; // 免費 Imgur Client ID

/* =====================
   DEFAULT DATA
===================== */
const DEFAULT = {
  categories: [
    {
      id: 'internal', name: 'A · 內部系統', emoji: '🏢',
      cards: [
        { title: 'CRM',
          url:   'http://192.168.100.85/WebCRM/src/_Common/AppUtil/FrameSet/NewLogin.aspx',
          img:   'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=640&q=80' },
        { title: 'EIP',
          url:   'http://192.168.100.89/SWTCweb4.0/production/ADLoginPage.aspx',
          img:   'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=640&q=80' },
        { title: 'EASYFLOW',
          url:   'http://192.168.100.85/efnet/',
          img:   'https://images.unsplash.com/photo-1551836022-d5d88e9218df?w=640&q=80' },
        { title: '請假系統',
          url:   'http://192.168.2.251/MotorWeb/CHIPage/Login.asp',
          img:   'https://images.unsplash.com/photo-1508385082359-f38ae991e8f2?w=640&q=80' }
      ]
    },
    {
      id: 'official', name: 'B · 官方系統', emoji: '🌐',
      cards: [
        { title: '實威國際官網',
          url:   'https://www.swtc.com/zh-tw/',
          img:   'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=640&q=80' },
        { title: '實威國際 YouTube',
          url:   'https://www.youtube.com/@solidwizard',
          img:   'https://images.unsplash.com/photo-1611162616475-46b635cb6868?w=640&q=80' },
        { title: '智慧製造 YouTube',
          url:   'https://www.youtube.com/@SWTCIM',
          img:   'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=640&q=80' },
        { title: '實威知識+',
          url:   'https://www.youtube.com/@實威知識',
          img:   'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=640&q=80' }
      ]
    },
    {
      id: 'solidworks', name: 'C · SOLIDWORKS', emoji: '⚙️',
      cards: [
        { title: 'SOLIDWORKS 官網',
          url:   'https://www.solidworks.com/',
          img:   'https://images.unsplash.com/photo-1581092335397-9fa1f9a2d2a1?w=640&q=80' },
        { title: 'MySolidWorks',
          url:   'https://my.solidworks.com/',
          img:   'https://images.unsplash.com/photo-1537462715879-360eeb61a0ad?w=640&q=80' },
        { title: 'SOLIDWORKS Forum',
          url:   'https://forum.solidworks.com/',
          img:   'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=640&q=80' }
      ]
    },
    {
      id: 'formlabs', name: 'C · Formlabs', emoji: '🖨️',
      cards: [
        { title: 'Formlabs 原廠',
          url:   'https://formlabs.com/',
          img:   'https://images.unsplash.com/photo-1581090700227-1e37b190418e?w=640&q=80' },
        { title: 'Formlabs Support',
          url:   'https://support.formlabs.com/',
          img:   'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=640&q=80' },
        { title: 'Formlabs Dashboard',
          url:   'https://dashboard.formlabs.com/',
          img:   'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=640&q=80' }
      ]
    },
    {
      id: 'scanology', name: 'D · SCANOLOGY', emoji: '📡',
      cards: [
        { title: 'SCANOLOGY 官網',
          url:   'https://www.scanology.com/',
          img:   'https://images.unsplash.com/photo-1518770660439-4636190af475?w=640&q=80' }
      ]
    }
  ]
};

/* =====================
   STATE
===================== */
let appData  = null;
let isAdmin  = false;
let editState = null;   // { catIdx, cardIdx }
let selEmoji = '📁';

const EMOJIS = ['📁','🏢','🌐','⚙️','🖨️','📡','💡','🔧','🎯','📊',
                '🔬','🖥️','📱','🌍','⭐','🔑','🗂️','📌'];

/* =====================
   SYNC STATUS UI
===================== */
function setSyncStatus(state, text) {
  document.getElementById('sync-dot').className = 'sync-dot ' + state;
  document.getElementById('sync-text').textContent = text;
}

/* =====================
   STORAGE  (shared = true → 跨裝置同步)
   Falls back to localStorage when window.storage unavailable
===================== */
async function loadData() {
  setSyncStatus('busy', '同步中...');
  try {
    if (window.storage) {
      const r = await window.storage.get(SK, true);   // shared=true
      if (r && r.value) {
        setSyncStatus('ok', '已同步');
        return JSON.parse(r.value);
      }
    }
  } catch(e) { console.warn('storage.get failed', e); }
  // fallback
  try {
    const ls = localStorage.getItem(SK);
    if (ls) { setSyncStatus('ok', '本機資料'); return JSON.parse(ls); }
  } catch(e) {}
  setSyncStatus('ok', '預設資料');
  return JSON.parse(JSON.stringify(DEFAULT));
}

async function saveData() {
  setSyncStatus('busy', '儲存中...');
  const str = JSON.stringify(appData);
  let ok = false;
  try {
    if (window.storage) {
      await window.storage.set(SK, str, true);   // shared=true
      ok = true;
    }
  } catch(e) { console.warn('storage.set failed', e); }
  // fallback
  try { localStorage.setItem(SK, str); } catch(e) {}
  setSyncStatus(ok ? 'ok' : 'err', ok ? '已同步 ✓' : '僅本機儲存');
}

/* =====================
   IMGUR UPLOAD
   圖片先裁切為 640×360 (16:9)，再上傳至 Imgur 取得公開 URL
   → 所有裝置都能顯示，不佔 storage 空間
===================== */
async function uploadToImgur(base64Data) {
  const base64 = base64Data.split(',')[1];
  const resp = await fetch('https://api.imgur.com/3/image', {
    method: 'POST',
    headers: {
      'Authorization': 'Client-ID ' + IMGUR_CLIENT_ID,
      'Content-Type':  'application/json'
    },
    body: JSON.stringify({ image: base64, type: 'base64' })
  });
  if (!resp.ok) throw new Error('HTTP ' + resp.status);
  const data = await resp.json();
  if (!data.success) throw new Error(data.data?.error || 'Upload failed');
  return data.data.link;   // 回傳 https://i.imgur.com/xxxxx.jpg
}

/* =====================
   IMAGE UPLOAD FLOW
===================== */
function setProgUI(pct, text) {
  document.getElementById('upload-prog').classList.add('show');
  document.getElementById('prog-fill').style.width = pct + '%';
  document.getElementById('prog-text').textContent = text;
}
function hideProgUI() {
  setTimeout(() => document.getElementById('upload-prog').classList.remove('show'), 1800);
}

function setPreviewImg(url) {
  const p = document.getElementById('img-prev');
  p.src = url;
  p.classList.add('show');
  p.dataset.url = url;
  document.getElementById('upload-zone').classList.add('hidden');
  document.getElementById('img-change').classList.add('show');
}

function resetImgModal() {
  const p = document.getElementById('img-prev');
  p.src = ''; p.classList.remove('show'); p.dataset.url = '';
  document.getElementById('upload-zone').classList.remove('hidden');
  document.getElementById('img-change').classList.remove('show');
  document.getElementById('upload-prog').classList.remove('show');
  document.getElementById('img-file').value = '';
  document.getElementById('card-img-url').value = '';
}

function previewUrl(url) {
  if (!url) return;
  setPreviewImg(url);
}

async function handleImgUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  setProgUI(10, '讀取圖片...');
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = async () => {
      // 裁切為 16:9
      const W = 640, H = 360;
      const canvas = document.createElement('canvas');
      canvas.width = W; canvas.height = H;
      const ctx = canvas.getContext('2d');
      const ratio = Math.max(W / img.width, H / img.height);
      const nw = img.width * ratio, nh = img.height * ratio;
      ctx.drawImage(img, (W - nw) / 2, (H - nh) / 2, nw, nh);
      const b64 = canvas.toDataURL('image/jpeg', 0.85);

      setProgUI(40, '上傳至雲端...');
      try {
        const url = await uploadToImgur(b64);
        setProgUI(100, '上傳完成 ✓');
        hideProgUI();
        setPreviewImg(url);
        document.getElementById('imgur-warn').style.display = 'none';
      } catch(err) {
        console.error('Imgur upload failed', err);
        setProgUI(100, '雲端上傳失敗，使用本機預覽');
        hideProgUI();
        // 用 base64 先顯示，但存檔時警示
        setPreviewImg(b64);
        document.getElementById('imgur-warn').style.display = '';
      }
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
  event.target.value = '';
}

/* =====================
   RENDER
===================== */
function render() {
  const c = document.getElementById('sections-container');
  c.innerHTML = '';
  appData.categories.forEach((cat, ci) => {
    const sec = document.createElement('section');
    sec.className = 'section';
    sec.innerHTML = `
      <div class="sec-hdr">
        <div class="sec-label">
          <span class="sec-tag">${cat.emoji}</span>
          <h2>${esc(cat.name)}</h2>
        </div>
        <div class="sec-actions" style="display:${isAdmin ? 'flex' : 'none'}">
          <button class="btn sm primary" onclick="openNewCard(${ci})">+ 新增連結</button>
          <button class="btn sm danger"  onclick="confirmDelCat(${ci})">刪除分類</button>
        </div>
      </div>
      <div class="grid" id="grid-${ci}"></div>`;
    c.appendChild(sec);
    renderGrid(ci);
  });
}

function renderGrid(ci) {
  const grid = document.getElementById('grid-' + ci);
  if (!grid) return;
  grid.innerHTML = '';
  const cat = appData.categories[ci];
  if (!cat.cards.length) {
    grid.innerHTML = '<div class="empty">此分類尚無連結，點上方「+ 新增連結」加入</div>';
    return;
  }
  cat.cards.forEach((card, ki) => {
    const el = document.createElement(isAdmin ? 'div' : 'a');
    el.className = 'card';
    if (!isAdmin) {
      el.href = card.url; el.target = '_blank'; el.rel = 'noopener noreferrer';
    }
    const host = (() => {
      try { return new URL(card.url).hostname.replace(/^www\./, ''); }
      catch(e) { return card.url; }
    })();
    const isB64 = card.img && card.img.startsWith('data:');
    el.innerHTML = `
      ${card.img
        ? `<img class="card-thumb" src="${esc(card.img)}" alt="${esc(card.title)}"
               loading="lazy"
               onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
           ${isB64 ? '<div title="此圖片僅限本裝置顯示" style="position:absolute;top:6px;right:6px;font-size:10px;background:rgba(0,0,0,.55);color:#fff;padding:2px 6px;border-radius:4px">本機</div>' : ''}`
        : ''}
      <div class="card-placeholder" ${card.img ? 'style="display:none"' : ''}>🔗</div>
      <div class="card-body">
        <div class="card-title">${esc(card.title)}</div>
        <div class="card-host">${esc(host)}</div>
      </div>
      ${isAdmin ? `
      <div class="card-bar">
        <button class="card-edit"
          onclick="event.preventDefault();event.stopPropagation();openEditCard(${ci},${ki})">✎ 編輯</button>
        <button class="card-del"
          onclick="event.preventDefault();event.stopPropagation();confirmDelCard(${ci},${ki})">✕</button>
      </div>` : ''}`;
    if (isAdmin && card.img) el.style.position = 'relative';
    grid.appendChild(el);
  });
}

/* =====================
   AUTH
===================== */
function openLogin() {
  document.getElementById('pwd-input').value = '';
  document.getElementById('login-err').textContent = '';
  openOvl('login-overlay');
  setTimeout(() => document.getElementById('pwd-input').focus(), 150);
}

function doLogin() {
  if (document.getElementById('pwd-input').value === ADMIN_PASS) {
    isAdmin = true;
    closeOvl('login-overlay');
    document.getElementById('admin-badge').style.display = '';
    document.getElementById('logout-btn').style.display = '';
    document.getElementById('cat-btn').style.display = '';
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
  document.getElementById('cat-btn').style.display = 'none';
  document.getElementById('login-btn').style.display = '';
  document.getElementById('admin-notice').style.display = 'none';
  render();
}

/* =====================
   OVERLAYS
===================== */
function openOvl(id) { document.getElementById(id).classList.add('open'); }
function closeOvl(id) { document.getElementById(id).classList.remove('open'); }
document.querySelectorAll('.overlay').forEach(el => {
  el.addEventListener('click', function(e) {
    if (e.target === this) closeOvl(this.id);
  });
});

/* =====================
   CARD CRUD
===================== */
function openNewCard(ci) {
  editState = { catIdx: ci, cardIdx: null };
  document.getElementById('card-modal-title').textContent = '新增連結';
  document.getElementById('card-name').value = '';
  document.getElementById('card-url').value = 'https://';
  resetImgModal();
  openOvl('card-overlay');
  setTimeout(() => document.getElementById('card-name').focus(), 150);
}

function openEditCard(ci, ki) {
  editState = { catIdx: ci, cardIdx: ki };
  const card = appData.categories[ci].cards[ki];
  document.getElementById('card-modal-title').textContent = '編輯連結';
  document.getElementById('card-name').value = card.title;
  document.getElementById('card-url').value  = card.url;
  resetImgModal();
  if (card.img) {
    setPreviewImg(card.img);
    if (!card.img.startsWith('data:'))
      document.getElementById('card-img-url').value = card.img;
  }
  openOvl('card-overlay');
}

async function saveCard() {
  const name = document.getElementById('card-name').value.trim();
  const url  = document.getElementById('card-url').value.trim();
  const img  = document.getElementById('img-prev').dataset.url || '';
  if (!name)            { alert('請輸入連結名稱'); return; }
  if (!url || url === 'https://') { alert('請輸入有效網址'); return; }

  const { catIdx, cardIdx } = editState;
  const card = { title: name, url, img };
  if (cardIdx === null) appData.categories[catIdx].cards.push(card);
  else                  appData.categories[catIdx].cards[cardIdx] = card;

  await saveData();
  closeOvl('card-overlay');
  renderGrid(catIdx);
}

function confirmDelCard(ci, ki) {
  const name = appData.categories[ci].cards[ki].title;
  if (!confirm(`確定要刪除「${name}」？`)) return;
  appData.categories[ci].cards.splice(ki, 1);
  saveData();
  renderGrid(ci);
}

/* =====================
   CATEGORY CRUD
===================== */
function openCatModal() {
  renderCatList();
  renderEmojiSel();
  openOvl('cat-overlay');
}

function renderCatList() {
  const c = document.getElementById('cat-list');
  if (!appData.categories.length) {
    c.innerHTML = '<p style="font-size:13px;color:var(--text3);text-align:center;padding:12px">尚無分類</p>';
    return;
  }
  c.innerHTML = appData.categories.map((cat, ci) => `
    <div class="cat-row">
      <span style="font-size:18px">${cat.emoji}</span>
      <span class="cat-row-name">${esc(cat.name)}</span>
      <span class="cat-row-count">${cat.cards.length} 項</span>
      <button class="btn sm danger" onclick="confirmDelCatFromModal(${ci})">刪除</button>
    </div>`).join('');
}

function renderEmojiSel() {
  document.getElementById('emoji-sel').innerHTML = EMOJIS.map(e =>
    `<button class="emoji-btn${selEmoji === e ? ' sel' : ''}"
             onclick="pickEmoji('${e}')">${e}</button>`
  ).join('');
}

function pickEmoji(e) { selEmoji = e; renderEmojiSel(); }

async function addCat() {
  const val = document.getElementById('new-cat-input').value.trim();
  if (!val) { alert('請輸入分類名稱'); return; }
  appData.categories.push({ id: 'cat_' + Date.now(), name: val, emoji: selEmoji, cards: [] });
  document.getElementById('new-cat-input').value = '';
  await saveData();
  renderCatList();
  render();
}

function confirmDelCatFromModal(ci) {
  const cat = appData.categories[ci];
  if (!confirm(`確定刪除分類「${cat.name}」及其 ${cat.cards.length} 個連結？`)) return;
  appData.categories.splice(ci, 1);
  saveData(); renderCatList(); render();
}

function confirmDelCat(ci) {
  const cat = appData.categories[ci];
  if (!confirm(`確定刪除分類「${cat.name}」及其所有連結？`)) return;
  appData.categories.splice(ci, 1);
  saveData(); render();
}

/* =====================
   UTILS
===================== */
function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}

/* =====================
   INIT
===================== */
(async () => {
  appData = await loadData();
  render();
})();
</script>
</body>
</html>"""

components.html(html_code, height=950, scrolling=True)
