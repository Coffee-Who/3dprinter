/**
 * tab-sample.js
 * 3D 列印樣品管理模組 (Firestore 版)
 * ─────────────────────────────────────────────
 * 使用方式：在 index.html 的 </body> 前加上：
 *   <script src="tab-sample.js"></script>
 * ─────────────────────────────────────────────
 * 依賴（由 index.html 提供）：
 *   - firebase-config.js  ← Firebase 設定
 *   - firebase-service.js ← window._db, window.FBSettings
 *   - echarts CDN         ← https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js
 * ─────────────────────────────────────────────
 * 資料儲存：
 *   - 樣品資料  → Firestore collection: samples
 *   - 歸還紀錄  → Firestore collection: returnHistory
 *   - 借用人清單 → Firestore settings/workspace.borrowers
 *   - 照片       → GitHub image/ 資料夾 (需 GitHub Token)
 */

/* ══════════════════════════════════════════
   1. 注入 CSS
   ══════════════════════════════════════════ */
(function injectCSS() {
  if (document.getElementById('sm-style')) return;
  const style = document.createElement('style');
  style.id = 'sm-style';
  style.textContent = `
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f5f6f8;--surf:#fff;--line:#e6e8ec;--line-soft:#eef0f3;
  --t1:#1a1d23;--t2:#3b4250;--t3:#5a6270;--t4:#8a93a3;
  --blue:#185fa5;--blue-bg:#e6f1fb;--blue-bd:#b5d4f4;
  --teal:#0c7a99;--teal-bg:#e6f1f6;
  --green:#1d6f43;--green-bg:#e6f1ea;
  --red:#a32d2d;--red-bg:#fcebeb;
  --amber:#8b6b13;--amber-bg:#fbf3dc;
  --sh:0 2px 12px rgba(0,0,0,.08)
}
body{font-family:'DM Sans','Noto Sans TC',sans-serif;background:var(--bg);color:var(--t1);min-height:100vh}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-thumb{background:var(--line);border-radius:3px}
input,select,button,textarea{font-family:inherit}

/* header */
.pg-hdr{background:var(--surf);border-bottom:1px solid var(--line);padding:12px 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;position:sticky;top:0;z-index:50}
.pg-title{font-size:15px;font-weight:700}
.pg-sub{font-size:11px;color:var(--t3);margin-top:2px}
.sync-pill{display:flex;align-items:center;gap:5px;background:var(--green-bg);border:1px solid #9acfb4;border-radius:20px;padding:3px 10px;font-size:11px;color:var(--green);font-weight:600}
.dot{width:6px;height:6px;border-radius:50%;background:#3fb950;animation:blink 1.6s infinite;flex-shrink:0}
.sync-pill.err{background:var(--red-bg);border-color:#f5b0b0;color:var(--red)}
.sync-pill.err .dot{background:var(--red)}
.sync-pill.spin{background:var(--amber-bg);border-color:#f5d5a0;color:var(--amber)}
.sync-pill.spin .dot{background:var(--amber);animation:blink .6s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}

/* tabs */
.ctabs{display:flex;padding:0 20px;background:var(--surf);border-bottom:1px solid var(--line);overflow-x:auto;-webkit-overflow-scrolling:touch;position:sticky;top:57px;z-index:49}
.ctab{padding:9px 16px;font-size:12px;color:var(--t3);cursor:pointer;border-bottom:2px solid transparent;font-weight:600;white-space:nowrap;display:flex;align-items:center;gap:5px;user-select:none;flex-shrink:0}
.ctab.on{color:var(--blue);border-bottom-color:var(--blue)}
.ctab:hover:not(.on){color:var(--t1)}

/* toolbar */
.toolbar{display:flex;align-items:center;gap:8px;padding:9px 20px;background:var(--surf);border-bottom:1px solid var(--line-soft);flex-wrap:wrap}
.t-search{display:flex;align-items:center;gap:6px;background:var(--bg);border:1.5px solid var(--line);border-radius:6px;padding:5px 10px}
.t-search input{border:none;background:none;outline:none;font-size:12px;color:var(--t1);width:120px}
.t-sel{padding:5px 8px;border:1.5px solid var(--line);border-radius:6px;font-size:12px;background:var(--surf);color:var(--t2);cursor:pointer}
.tbtn{height:30px;padding:0 12px;border:1.5px solid var(--line);border-radius:6px;font-size:12px;font-weight:600;background:var(--surf);color:var(--t2);cursor:pointer;display:flex;align-items:center;gap:5px;white-space:nowrap;transition:.12s}
.tbtn:hover{background:var(--bg)}
.tbtn.green{border-color:var(--green);background:var(--green-bg);color:var(--green)}
.tbtn.blue{border-color:var(--blue);background:var(--blue-bg);color:var(--blue)}
.size-group{display:flex;border:1.5px solid var(--line);border-radius:6px;overflow:hidden}
.sbtn{padding:4px 10px;font-size:11px;font-weight:700;border:none;border-right:1px solid var(--line);background:var(--surf);color:var(--t3);cursor:pointer;transition:.12s}
.sbtn:last-child{border-right:none}
.sbtn.on{background:var(--blue);color:#fff}
.sp{flex:1}

/* stats */
.stat-row{display:flex;gap:8px;padding:14px 20px;flex-wrap:wrap}
.sc{background:var(--surf);border:1.5px solid var(--line);border-radius:8px;padding:9px 14px;display:flex;align-items:center;gap:10px}
.sc-num{font-size:22px;font-weight:700;line-height:1}
.sc-lbl{font-size:9px;color:var(--t4);text-transform:uppercase;letter-spacing:.07em;margin-top:2px;font-weight:700}
.sc.bw .sc-num{color:var(--red)}
.sc.av .sc-num{color:var(--green)}
.sc.tot .sc-num{color:var(--blue)}

/* cards */
.cg{display:grid;gap:10px;padding:0 20px 20px}
.cg.sz-lg{grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
.cg.sz-md{grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}
.cg.sz-sm{grid-template-columns:repeat(auto-fill,minmax(110px,1fr))}
@media(max-width:640px){
  .cg.sz-lg{grid-template-columns:repeat(2,1fr)}
  .cg.sz-md{grid-template-columns:repeat(3,1fr)}
  .cg.sz-sm{grid-template-columns:repeat(4,1fr)}
}
.card{background:var(--surf);border:1.5px solid var(--line);border-radius:8px;overflow:hidden;display:flex;flex-direction:column;transition:.15s}
.card:hover{border-color:var(--blue-bd);box-shadow:var(--sh)}
.card-img{position:relative;width:100%;aspect-ratio:1/1;background:var(--line-soft);display:flex;align-items:center;justify-content:center;color:#c8cdd6;overflow:hidden;cursor:pointer}
.card-img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.card-img .ph{font-size:32px;opacity:.4}
.sz-md .card-img .ph,.sz-sm .card-img .ph{font-size:20px}
.sp-pill{position:absolute;top:5px;left:5px;font-size:8px;font-weight:700;padding:2px 6px;border-radius:10px;pointer-events:none}
.sp-av{background:var(--green-bg);color:var(--green)}
.sp-bw{background:var(--red-bg);color:var(--red)}
.upload-btn{position:absolute;bottom:5px;right:5px;background:rgba(26,29,35,.75);color:#fff;border:none;border-radius:5px;padding:3px 7px;font-size:9px;cursor:pointer;display:none;align-items:center;gap:3px}
.upload-btn input{display:none}
.card:hover .upload-btn{display:flex}
.card-body{padding:8px 10px 6px;flex:1}
.card-name{font-size:11px;font-weight:700;color:var(--t1);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:2px;cursor:pointer}
.card-desc{font-size:9px;color:var(--t3);line-height:1.5;margin-bottom:5px}
.sz-md .card-desc,.sz-sm .card-desc{display:none}
.mrow{display:flex;gap:3px;font-size:9px;margin-bottom:1px}
.ml{color:var(--t4);font-weight:700;min-width:30px;font-size:9px;flex-shrink:0}
.mv{color:var(--t1)}
.mv.rd{color:var(--red);font-weight:700}
.sz-md .mrow,.sz-sm .mrow{display:none}
.note-box{background:var(--blue-bg);border-left:3px solid var(--blue-bd);border-radius:0 4px 4px 0;padding:4px 7px;font-size:9px;color:var(--t3);font-style:italic;margin-top:3px}
.sz-md .note-box,.sz-sm .note-box{display:none}
.card-foot{padding:6px 8px 8px;border-top:1px solid var(--line-soft)}
.footrow{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.fsel{flex:1;min-width:0;padding:4px 5px;border-radius:4px;border:1.5px solid var(--line);font-size:10px;background:var(--bg);color:var(--t1)}
.fdate{width:90px;padding:4px 5px;border-radius:4px;border:1.5px solid var(--line);font-size:10px;background:var(--bg);color:var(--t3)}
.cfbtn{padding:4px 9px;border-radius:4px;border:1.5px solid var(--blue);background:var(--blue);color:#fff;font-size:10px;cursor:pointer;font-weight:700;white-space:nowrap;transition:.12s}
.cfbtn:hover{background:var(--teal);border-color:var(--teal)}
.cfbtn.ret{border-color:var(--red);background:var(--red-bg);color:var(--red)}
.cfbtn.ret:hover{background:var(--red);color:#fff}
.sz-md .card-foot,.sz-sm .card-foot{display:none}

/* table */
.tbl-wrap{padding:0 20px 20px}
.sec-hd{display:flex;align-items:center;justify-content:space-between;padding:14px 0 8px;border-top:1px solid var(--line-soft);flex-wrap:wrap;gap:6px}
.sec-title{font-size:13px;font-weight:700;color:var(--t1)}
.sec-title span{color:var(--blue)}
.drag-hint{font-size:10px;color:var(--t4);display:flex;align-items:center;gap:3px}
.at{background:var(--surf);border:1.5px solid var(--line);border-radius:8px;overflow:hidden;overflow-x:auto}
.at-head{display:grid;background:#f8f9fb;padding:8px 14px;font-size:9px;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:var(--t4);border-bottom:1.5px solid var(--line);min-width:500px}
.at-head>div{display:flex;align-items:center;gap:3px;user-select:none;overflow:hidden;position:relative}
.resize-handle{position:absolute;right:-4px;top:0;height:100%;width:8px;cursor:col-resize;z-index:2}
.resize-handle:hover::after,.resize-handle.active::after{content:'';position:absolute;left:3px;top:20%;height:60%;width:2px;background:var(--blue);border-radius:2px}
.at-row{display:grid;padding:8px 14px;border-bottom:1px solid var(--line-soft);font-size:11px;align-items:center;min-width:500px}
.at-row:last-child{border-bottom:none}
.at-row:hover{background:#f8f9fb}
.at-name{font-weight:700;color:var(--t1);display:flex;align-items:center;gap:5px;overflow:hidden}
.chip{display:inline-flex;font-size:9px;padding:1px 7px;border-radius:10px;font-weight:700;flex-shrink:0}
.chip-bw{background:var(--red-bg);color:var(--red)}
.chip-av{background:var(--green-bg);color:var(--green)}
.days-red{font-weight:700;color:var(--red)}
.ri{color:#d0d4db;font-size:11px;flex-shrink:0;cursor:col-resize}
.tbl-edit-btn{padding:2px 9px;border-radius:4px;border:1.5px solid var(--line);background:var(--surf);color:var(--t3);font-size:10px;cursor:pointer;transition:.12s;white-space:nowrap}
.tbl-edit-btn:hover{border-color:var(--teal);color:var(--teal);background:var(--teal-bg)}

/* modal */
.mo{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:500;align-items:center;justify-content:center;padding:16px}
.mo.on{display:flex}
.mb{background:var(--surf);border-radius:12px;padding:22px;width:100%;max-width:420px;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.25)}
.mb h3{font-size:15px;font-weight:700;margin-bottom:16px;display:flex;align-items:center;gap:8px}
.mb label{display:block;font-size:10px;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;margin-top:12px}
.mb label:first-of-type{margin-top:0}
.mb input,.mb textarea,.mb select{width:100%;padding:8px 10px;border-radius:6px;border:1.5px solid var(--line);font-size:13px;background:var(--bg);color:var(--t1);outline:none;transition:.12s}
.mb input:focus,.mb textarea:focus,.mb select:focus{border-color:var(--blue)}
.mb textarea{min-height:60px;resize:vertical}
.mb-foot{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}
.btn-cancel{height:34px;padding:0 16px;border:1.5px solid var(--line);border-radius:6px;font-size:13px;background:var(--surf);color:var(--t2);cursor:pointer;font-weight:600}
.btn-save{height:34px;padding:0 16px;border:none;border-radius:6px;font-size:13px;background:var(--blue);color:#fff;cursor:pointer;font-weight:600}
.btn-save:hover{background:var(--teal)}
.btn-del{height:34px;padding:0 14px;border:none;border-radius:6px;font-size:13px;background:var(--red-bg);color:var(--red);cursor:pointer;font-weight:600;margin-right:auto}
.prev-img{width:100%;max-height:150px;object-fit:cover;border-radius:6px;margin-top:8px;display:none}
.upload-area{border:2px dashed var(--line);border-radius:6px;padding:14px;text-align:center;cursor:pointer;margin-top:6px;font-size:12px;color:var(--t3)}
.upload-area:hover{border-color:var(--blue);color:var(--blue)}
#borrow-edit-section{border-radius:8px;background:var(--teal-bg);border:1.5px solid #9acfcf;padding:12px 14px;margin-top:14px}
#borrow-edit-section label{color:var(--teal)!important}
#borrow-edit-section select,#borrow-edit-section input{background:var(--surf)!important;border-color:rgba(12,122,153,.25)!important}

/* lightbox */
.lb{display:none;position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:600;align-items:center;justify-content:center}
.lb.on{display:flex}
.lb img{max-width:92vw;max-height:88vh;object-fit:contain;border-radius:8px}
.lb-close{position:absolute;top:14px;right:18px;color:#fff;font-size:26px;cursor:pointer}

/* toast */
#toasts{position:fixed;bottom:20px;right:20px;display:flex;flex-direction:column;gap:7px;z-index:900}
.toast{padding:9px 16px;border-radius:8px;font-size:12px;font-weight:600;animation:tin .2s ease;max-width:300px}
.toast.ok{background:#e6f1ea;border:1.5px solid #9acfb4;color:var(--green)}
.toast.err{background:var(--red-bg);border:1.5px solid #f5b0b0;color:var(--red)}
.toast.inf{background:var(--blue-bg);border:1.5px solid var(--blue-bd);color:var(--blue)}
@keyframes tin{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* dashboard */
.dash-panel{padding:0 20px 28px}
.period-bar{display:flex;align-items:center;justify-content:space-between;padding:14px 0 12px;flex-wrap:wrap;gap:8px}
.period-title{font-size:13px;font-weight:700}
.period-group{display:flex;border:1.5px solid var(--line);border-radius:6px;overflow:hidden}
.pbtn{padding:5px 16px;font-size:12px;font-weight:600;border:none;border-right:1px solid var(--line);background:var(--surf);color:var(--t3);cursor:pointer;transition:.12s}
.pbtn:last-child{border-right:none}
.pbtn.on{background:var(--blue);color:#fff}
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}
@media(max-width:640px){.kpi-row{grid-template-columns:repeat(2,1fr)}}
.kpi{background:var(--surf);border:1.5px solid var(--line);border-radius:8px;padding:13px 15px}
.kpi-num{font-size:26px;font-weight:700;line-height:1;margin-bottom:4px}
.kpi-lbl{font-size:10px;color:var(--t3);font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.kpi-trend{font-size:10px;margin-top:4px;font-weight:600;color:var(--t4)}
.kpi.blue .kpi-num{color:var(--blue)}
.kpi.green .kpi-num{color:var(--green)}
.kpi.red .kpi-num{color:var(--red)}
.kpi.teal .kpi-num{color:var(--teal)}
.trend-up{color:var(--green)}.trend-dn{color:var(--red)}
.chart-2col{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px}
@media(max-width:640px){.chart-2col{grid-template-columns:1fr}}
.chart-card{background:var(--surf);border:1.5px solid var(--line);border-radius:8px;padding:14px 16px;margin-bottom:14px}
.chart-title{font-size:12px;font-weight:700;color:var(--t1);margin-bottom:12px;padding-bottom:7px;border-bottom:1px solid var(--line-soft)}
.bar-row{display:flex;align-items:center;gap:8px;margin-bottom:7px}
.bar-lbl{font-size:11px;color:var(--t2);font-weight:600;min-width:72px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar-bg{flex:1;height:7px;background:var(--line-soft);border-radius:4px;overflow:hidden}
.bar-fill{height:100%;border-radius:4px;transition:width .4s}
.bar-val{font-size:11px;color:var(--t3);min-width:28px;text-align:right;font-weight:600}
.bar-chart-wrap{display:flex;align-items:flex-end;gap:6px;height:100px;padding:4px 0 0}
.bar-col{display:flex;flex-direction:column;align-items:center;gap:3px;flex:1;min-width:0}
.bar-col-fill{width:80%;border-radius:3px 3px 0 0;transition:height .4s;min-height:2px}
.bar-col-lbl{font-size:9px;color:var(--t4);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
.bar-col-val{font-size:9px;font-weight:700;color:var(--t2)}
.warn-hd{padding:9px 14px;background:#fff8f0;border-bottom:1.5px solid #f5d5b0;font-size:12px;font-weight:700;color:#8b4513;display:flex;align-items:center;gap:6px}
.th5{grid-template-columns:2fr 1fr 1fr 1fr 1fr}

/* ECharts dynamic panel */
.ec-panel{background:var(--surf);border:1.5px solid var(--line);border-radius:8px;padding:16px;margin-bottom:14px}
.ec-toolbar{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid var(--line-soft)}
.ec-toolbar-title{font-size:13px;font-weight:700;color:var(--t1);margin-right:4px}
.ec-axis-group{display:flex;align-items:center;gap:6px;background:var(--bg);border:1.5px solid var(--line);border-radius:7px;padding:5px 10px}
.ec-axis-group label{font-size:10px;font-weight:700;color:var(--t4);white-space:nowrap;text-transform:uppercase;letter-spacing:.05em}
.ec-axis-group select{padding:3px 6px;border:1.5px solid var(--line);border-radius:5px;font-size:12px;background:var(--surf);color:var(--t2);cursor:pointer;min-width:90px}
.ec-chart{width:100%;height:320px}
.ec-live-dot{width:7px;height:7px;border-radius:50%;background:var(--green);animation:blink .8s infinite;flex-shrink:0}
@media(max-width:480px){.ec-chart{height:240px}}

@media(max-width:480px){
  .pg-hdr{padding:10px 14px}
  .ctabs{padding:0 14px}
  .toolbar{padding:8px 14px}
  .stat-row,.tbl-wrap,.cg{padding-left:14px;padding-right:14px}
  .dash-panel{padding-left:14px;padding-right:14px}
}
  `;
  document.head.appendChild(style);
})();

/* ══════════════════════════════════════════
   2. 注入 ECharts CDN（如未載入）
   ══════════════════════════════════════════ */
(function injectECharts() {
  if (window.echarts) return;
  const s = document.createElement('script');
  s.src = 'https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js';
  document.head.appendChild(s);
})();

/* ══════════════════════════════════════════
   3. 注入 HTML（Lightbox、Modals、頁面主體）
   ══════════════════════════════════════════ */
(function injectHTML() {
  if (document.getElementById('pg-hdr') || document.getElementById('sm-root-wrap')) return;
  const div = document.createElement('div');
  div.id = 'sm-root-wrap';
  div.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;overflow-y:auto;';
  div.innerHTML = `
<div id="toasts"></div>
<div class="lb" id="lb" onclick="closeLB()">
  <span class="lb-close" onclick="closeLB()">×</span>
  <img id="lb-img" src="" alt="">
</div>

<!-- header -->
<div class="pg-hdr">
  <div>
    <div class="pg-title">🖨 3D 列印樣品管理</div>
    <div class="pg-sub" id="pg-sub">實威國際 · 統一管理借用紀錄</div>
  </div>
  <div class="sync-pill spin" id="sync-pill">
    <span class="dot"></span>
    <span id="sync-txt">連線中…</span>
  </div>
</div>

<!-- tabs -->
<div class="ctabs">
  <div class="ctab on" id="tab-samples" onclick="switchTab('samples')">📦 3D列印樣品</div>
  <div class="ctab" id="tab-dashboard" onclick="switchTab('dashboard')">📊 Dashboard 分析</div>
</div>

<!-- ══ SAMPLES PANEL ══ -->
<div id="panel-samples">
  <div class="toolbar">
    <div class="t-search">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="5" stroke="currentColor" stroke-width="1.5"/><path d="M11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      <input id="search-input" placeholder="搜尋樣品…" oninput="renderCards()">
    </div>
    <select class="t-sel" id="status-filter" onchange="renderCards()">
      <option value="">所有狀態</option>
      <option value="available">在庫</option>
      <option value="borrowed">借出中</option>
    </select>
    <div class="sp"></div>
    <button class="tbtn green" onclick="exportExcel()">📊 匯出 Excel</button>
    <button class="tbtn blue" onclick="openAdd()">＋ 新增樣品</button>
    <div class="size-group">
      <button class="sbtn" onclick="setSize('lg',this)">大</button>
      <button class="sbtn on" onclick="setSize('md',this)">中</button>
      <button class="sbtn" onclick="setSize('sm',this)">小</button>
    </div>
  </div>
  <div class="stat-row">
    <div class="sc bw"><span style="font-size:18px">📤</span><div><div class="sc-num" id="stat-bw">0</div><div class="sc-lbl">借出中</div></div></div>
    <div class="sc av"><span style="font-size:18px">📥</span><div><div class="sc-num" id="stat-av">0</div><div class="sc-lbl">在庫</div></div></div>
    <div class="sc tot"><span style="font-size:18px">📦</span><div><div class="sc-num" id="stat-tot">0</div><div class="sc-lbl">總計</div></div></div>
  </div>
  <div class="cg sz-md" id="cg"></div>
  <div class="tbl-wrap">
    <div class="sec-hd">
      <span class="sec-title">目前 <span>借出狀態</span></span>
      <span class="drag-hint">⠿ 欄位可拖曳調整寬度</span>
    </div>
    <div class="at">
      <div class="at-head" id="borrow-head"></div>
      <div id="borrow-body"></div>
    </div>
    <div class="sec-hd" style="margin-top:4px">
      <span class="sec-title">歸還 <span>歷史紀錄</span></span>
      <button class="tbtn green" style="height:26px;font-size:11px" onclick="exportExcel()">📊 匯出</button>
    </div>
    <div class="at">
      <div class="at-row th5" style="background:#f8f9fb;font-size:9px;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:var(--t4);border-bottom:1.5px solid var(--line);min-width:500px">
        <div>樣品名稱</div><div>借用人</div><div>借出日期</div><div>歸還日期</div><div>天數</div>
      </div>
      <div id="return-body"></div>
    </div>
  </div>
</div>

<!-- ══ DASHBOARD PANEL ══ -->
<div id="panel-dashboard" style="display:none">
  <div class="dash-panel">
    <div class="period-bar">
      <span class="period-title">借用統計分析</span>
      <div class="period-group">
        <button class="pbtn on" id="pb-month" onclick="setPeriod('month')">月份</button>
        <button class="pbtn" id="pb-quarter" onclick="setPeriod('quarter')">季度</button>
        <button class="pbtn" id="pb-year" onclick="setPeriod('year')">年份</button>
      </div>
    </div>
    <div class="kpi-row">
      <div class="kpi blue"><div class="kpi-num" id="kpi-total">0</div><div class="kpi-lbl" id="kpi-total-lbl">本月借出次數</div><div class="kpi-trend" id="kpi-total-trend"></div></div>
      <div class="kpi green"><div class="kpi-num" id="kpi-ret">0</div><div class="kpi-lbl" id="kpi-ret-lbl">本月已歸還</div><div class="kpi-trend" id="kpi-ret-trend"></div></div>
      <div class="kpi red"><div class="kpi-num" id="kpi-out">0</div><div class="kpi-lbl" id="kpi-out-lbl">累計未歸還</div><div class="kpi-trend" id="kpi-out-trend"></div></div>
      <div class="kpi teal"><div class="kpi-num" id="kpi-avg">0</div><div class="kpi-lbl" id="kpi-avg-lbl">平均借用天數</div><div class="kpi-trend" id="kpi-avg-trend"></div></div>
    </div>

    <!-- 趨勢圖 -->
    <div class="chart-card">
      <div class="chart-title" id="trend-title">📅 每月借出次數趨勢</div>
      <div class="bar-chart-wrap" id="trend-chart"></div>
    </div>

    <!-- 排行圖 -->
    <div class="chart-2col">
      <div class="chart-card" style="margin-bottom:0">
        <div class="chart-title">借用人排行</div>
        <div id="person-chart"></div>
      </div>
      <div class="chart-card" style="margin-bottom:0">
        <div class="chart-title">樣品借用次數排行</div>
        <div id="item-chart"></div>
      </div>
    </div>

    <!-- ECharts Dynamic Data 圖表 (仿 dynamic-data 範例) -->
    <div class="ec-panel">
      <div class="ec-toolbar">
        <span class="ec-toolbar-title">📊 動態分析圖表</span>
        <span class="ec-live-dot" title="即時更新中"></span>
        <div class="ec-axis-group">
          <label>X 軸（類別）</label>
          <select id="ec-cat" onchange="rebuildEChart()">
            <option value="month">月份</option>
            <option value="borrower">借用人</option>
            <option value="item">樣品名稱</option>
            <option value="days_range">天數區間</option>
          </select>
        </div>
        <div class="ec-axis-group">
          <label>Y1（長條圖）</label>
          <select id="ec-y1" onchange="rebuildEChart()">
            <option value="count">借用次數</option>
            <option value="days">平均天數</option>
            <option value="outstanding">未歸還數</option>
          </select>
        </div>
        <div class="ec-axis-group">
          <label>Y2（折線圖）</label>
          <select id="ec-y2" onchange="rebuildEChart()">
            <option value="days">平均天數</option>
            <option value="count">借用次數</option>
            <option value="outstanding">未歸還數</option>
          </select>
        </div>
      </div>
      <div class="ec-chart" id="ec-main"></div>
    </div>

    <!-- 長期借用警示 -->
    <div class="at">
      <div class="warn-hd">⚠️ 長期借用警示（超過 30 天）</div>
      <div class="at-row th5" style="background:#f8f9fb;font-size:9px;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:var(--t4);border-bottom:1.5px solid var(--line);min-width:400px">
        <div>樣品名稱</div><div>借用人</div><div>借出日期</div><div>已借天數</div><div>狀態</div>
      </div>
      <div id="warn-body"></div>
    </div>
  </div>
</div>

<!-- ══ MODALS ══ -->
<!-- Add/Edit -->
<div class="mo" id="mo-add">
  <div class="mb">
    <h3 id="modal-title">➕ 新增樣品</h3>
    <input type="hidden" id="edit-id">
    <input type="hidden" id="edit-fbid">
    <label>樣品名稱 *</label>
    <input type="text" id="f-name" placeholder="例：FDM 齒輪組">
    <label>摘要描述</label>
    <textarea id="f-desc" placeholder="簡短說明此樣品特性…" rows="2"></textarea>
    <label>備註</label>
    <input type="text" id="f-note" placeholder="選填備註…">
    <label>照片（貼網址）</label>
    <input type="url" id="f-imgurl" placeholder="https://…" oninput="previewImg(this.value)">
    <div class="upload-area" onclick="document.getElementById('f-imgfile').click()">
      📷 點擊上傳照片（jpg / png / webp）
      <input type="file" id="f-imgfile" accept="image/*" style="display:none" onchange="handleImgUpload(this)">
    </div>
    <img id="f-imgprev" class="prev-img" alt="">
    <div id="borrow-edit-section" style="display:none">
      <span class="adm-lbl-edit" style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;margin-bottom:10px;display:block">📋 借用狀態編輯</span>
      <label>借用狀態</label>
      <select id="f-status" onchange="onStatusChange()">
        <option value="available">✅ 在庫</option>
        <option value="borrowed">📤 借出中</option>
      </select>
      <div id="f-borrow-fields" style="display:none">
        <label>借用人</label>
        <select id="f-bw"><option value="">選擇借用人</option></select>
        <label>或直接輸入</label>
        <input type="text" id="f-bw-manual" placeholder="直接輸入借用人姓名">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px">
          <div><label>借出日期</label><input type="date" id="f-bd"></div>
          <div><label>歸還日期</label><input type="date" id="f-rd"></div>
        </div>
      </div>
    </div>
    <div class="mb-foot">
      <button class="btn-del" id="btn-del" style="display:none" onclick="deleteCard()">🗑 刪除</button>
      <button class="btn-cancel" onclick="closeAdd()">取消</button>
      <button class="btn-save" onclick="saveCard()">💾 儲存</button>
    </div>
  </div>
</div>
<!-- Borrow -->
<div class="mo" id="mo-borrow">
  <div class="mb">
    <h3>📤 確認借出</h3>
    <input type="hidden" id="borrow-sample-id">
    <label>借用人</label>
    <select id="borrow-person"></select>
    <label>借出日期 *</label>
    <input type="date" id="borrow-date">
    <div class="mb-foot">
      <button class="btn-cancel" onclick="closeBorrow()">取消</button>
      <button class="btn-save" onclick="confirmBorrow()">確認借出</button>
    </div>
  </div>
</div>
<!-- Return -->
<div class="mo" id="mo-return">
  <div class="mb">
    <h3>📥 確認歸還</h3>
    <input type="hidden" id="return-sample-id">
    <label>歸還日期 *</label>
    <input type="date" id="return-date">
    <div class="mb-foot">
      <button class="btn-cancel" onclick="closeReturn()">取消</button>
      <button class="btn-save" onclick="confirmReturn()">確認歸還</button>
    </div>
  </div>
</div>
  `;
  document.body.appendChild(div);
})();

/* ══════════════════════════════════════════
   4. 樣品模組主邏輯
   ══════════════════════════════════════════ */
'use strict';
// ── GitHub config（照片仍用 GitHub）──
const GH_USER = 'Coffee-Who';
const GH_REPO = '3dprinter';
const GH_PATH_IMG = 'image/';
const LS_TOKEN = 'sw_gh_token_v3';
let GH_TOKEN = localStorage.getItem(LS_TOKEN) || '';

// ── 狀態 ──
let samples = [];
let returnHistory = [];
let borrowers = [];
let currentPeriod = 'month';
let colWidths = [2, 1.4, 1.2, 0.8, 1];
let resizeState = null;
let ecCharts = {};
let unsubSamples = null;
let unsubReturn = null;

const today = () => new Date().toISOString().slice(0, 10);
const daysBetween = (d1, d2) => {
  if (!d1) return 0;
  return Math.max(0, Math.round((new Date(d2 || new Date()) - new Date(d1)) / 86400000));
};

// ── Sync indicator ──
function setSyncState(state, txt) {
  const pill = document.getElementById('sync-pill');
  pill.className = 'sync-pill ' + state;
  document.getElementById('sync-txt').textContent = txt;
}

// ── 等待 Firebase 就緒 ──
function waitDB() {
  return new Promise(res => {
    const t = setInterval(() => {
      if (window._db) { clearInterval(t); res(); }
    }, 100);
    setTimeout(() => { clearInterval(t); res(); }, 8000);
  });
}

// ── 初始化 ──
async function init() {
  setSyncState('spin', '連線中…');
  await waitDB();
  if (!window._db) { setSyncState('err', '資料庫未就緒'); return; }

  // 讀取後台設定的借用人清單
  loadBorrowers();

  // 監聽 samples collection（即時更新）
  unsubSamples = window._db.collection('samples')
    .orderBy('seq')
    .onSnapshot(snap => {
      samples = snap.docs.map(d => Object.assign({ _id: d.id }, d.data()));
      renderAll();
      setSyncState('ok', '已同步');
    }, err => {
      setSyncState('err', '同步失敗');
    });

  // 監聽 returnHistory collection
  unsubReturn = window._db.collection('returnHistory')
    .orderBy('rd')
    .onSnapshot(snap => {
      returnHistory = snap.docs.map(d => Object.assign({ _id: d.id }, d.data()));
      renderAll();
    });
}

// ── 從 Firestore 設定讀借用人清單 ──
async function loadBorrowers() {
  try {
    const doc = await window._db.collection('settings').doc('workspace').get();
    if (doc.exists && doc.data().borrowers) {
      const raw = doc.data().borrowers;
      // 支援 {key,label} 格式或純字串
      borrowers = raw.map(b => typeof b === 'string' ? b : (b.label || b.key || b));
    } else {
      borrowers = ['王小明', '李美華', '張大偉', '陳怡君', '林志豪'];
    }
  } catch (e) {
    borrowers = ['王小明', '李美華', '張大偉', '陳怡君', '林志豪'];
  }
}

// 供後台更新借用人時呼叫
window.smSetBorrowers = function(list) {
  borrowers = list.map(b => typeof b === 'string' ? b : (b.label || b.key || b));
};

// ── nextSeq ──
function nextSeq() {
  return samples.length ? Math.max(...samples.map(s => s.seq || 0)) + 1 : 1;
}

// ── Render all ──
function renderAll() {
  renderCards();
  renderBorrowTable();
  renderReturnTable();
  if (document.getElementById('panel-dashboard').style.display !== 'none') renderDashboard();
  updateStats();
  document.getElementById('pg-sub').textContent =
    `實威國際 · Firestore 即時同步 · ${samples.length} 樣品`;
}

function updateStats() {
  document.getElementById('stat-bw').textContent = samples.filter(s => s.st === 'borrowed').length;
  document.getElementById('stat-av').textContent = samples.filter(s => s.st === 'available').length;
  document.getElementById('stat-tot').textContent = samples.length;
}

// ── Cards ──
function renderCards() {
  const q = document.getElementById('search-input').value.trim().toLowerCase();
  const sf = document.getElementById('status-filter').value;
  const cg = document.getElementById('cg');
  const filtered = samples.filter(s => {
    if (q && !s.name.toLowerCase().includes(q)) return false;
    if (sf && s.st !== sf) return false;
    return true;
  });
  if (!filtered.length) {
    cg.innerHTML = '<div style="padding:32px 0;text-align:center;color:var(--t4);font-size:13px">沒有符合條件的樣品</div>';
    return;
  }
  cg.innerHTML = filtered.map(s => cardHTML(s)).join('');
}

function cardHTML(s) {
  const isBw = s.st === 'borrowed';
  const img = s.img
    ? `<img src="${s.img}" alt="${s.name}" onclick="openLB('${s.img}')" loading="lazy">`
    : `<span class="ph">🖨️</span>`;
  const foot = isBw
    ? `<div class="footrow">
        <span style="font-size:10px;font-weight:700;color:var(--t1)">👤 ${s.bw || ''}</span>
        <button class="cfbtn" style="background:var(--teal-bg);border-color:var(--teal);color:var(--teal)" onclick="openEdit('${s._id}')">✏️</button>
        <button class="cfbtn ret" onclick="openReturn('${s._id}')">📥 歸還</button>
       </div>`
    : `<div class="footrow">
        <select class="fsel" id="sel-${s._id}"><option value="">選擇借用人</option>${borrowers.map(b => `<option>${b}</option>`).join('')}</select>
        <input type="date" class="fdate" id="bd-${s._id}" value="${today()}">
        <button class="cfbtn" onclick="openBorrow('${s._id}')">借出</button>
        <button class="cfbtn" style="background:var(--line-soft);border-color:var(--line);color:var(--t3);padding:4px 7px" onclick="openEdit('${s._id}')">✏️</button>
       </div>`;
  return `<div class="card">
    <div class="card-img">
      ${img}
      <div class="sp-pill ${isBw ? 'sp-bw' : 'sp-av'}">${isBw ? '借出中' : '在庫'}</div>
      <label class="upload-btn" title="上傳照片">📷<input type="file" accept="image/*" onchange="uploadCardImg(event,'${s._id}')"></label>
    </div>
    <div class="card-body">
      <div class="card-name" onclick="openEdit('${s._id}')" title="點擊編輯">${s.name}</div>
      <div class="card-desc">${s.desc || ''}</div>
      ${isBw ? `<div class="mrow"><span class="ml">借出人</span><span class="mv rd">${s.bw}</span></div>
                <div class="mrow"><span class="ml">借出日</span><span class="mv">${s.bd || ''}</span></div>` : ''}
      ${s.note ? `<div class="note-box">📝 ${s.note}</div>` : ''}
    </div>
    <div class="card-foot">${foot}</div>
  </div>`;
}

// ── Borrow table ──
function renderBorrowTable() {
  const borrowed = samples.filter(s => s.st === 'borrowed');
  const fw = colWidths.map(w => w + 'fr').join(' ') + ' 80px';
  const head = document.getElementById('borrow-head');
  head.style.gridTemplateColumns = fw;
  head.innerHTML = ['樣品名稱', '借用人', '借出日期', '天數', '操作'].map((h, i) =>
    i < 4
      ? `<div>${h}<span class="ri">⠿</span><div class="resize-handle" onmousedown="startResize(event,${i})"></div></div>`
      : `<div>${h}</div>`
  ).join('');
  const body = document.getElementById('borrow-body');
  if (!borrowed.length) {
    body.innerHTML = '<div style="padding:18px;text-align:center;color:var(--t4);font-size:12px">目前無借出中樣品</div>';
    return;
  }
  body.innerHTML = borrowed.map(s => {
    const d = daysBetween(s.bd, '');
    return `<div class="at-row" style="grid-template-columns:${fw}">
      <div class="at-name">${s.name}<span class="chip chip-bw">借出中</span></div>
      <div style="font-weight:700">${s.bw || '—'}</div>
      <div style="color:var(--t3)">${s.bd || '—'}</div>
      <div class="${d > 30 ? 'days-red' : ''}">${d} 天</div>
      <div><button class="tbl-edit-btn" onclick="openEdit('${s._id}')">✏️ 編輯</button></div>
    </div>`;
  }).join('');
}

// ── Return table ──
function renderReturnTable() {
  const body = document.getElementById('return-body');
  if (!returnHistory.length) {
    body.innerHTML = '<div style="padding:18px;text-align:center;color:var(--t4);font-size:12px">尚無歸還紀錄</div>';
    return;
  }
  body.innerHTML = [...returnHistory].reverse().map(r => `
    <div class="at-row th5" style="min-width:500px">
      <div style="font-weight:700">${r.name}</div>
      <div>${r.bw}</div>
      <div style="color:var(--t3)">${r.bd}</div>
      <div style="color:var(--green);font-weight:600">${r.rd}</div>
      <div style="color:var(--t3)">${daysBetween(r.bd, r.rd)} 天</div>
    </div>`).join('');
}

// ── Column resize ──
function startResize(e, colIdx) {
  e.preventDefault();
  resizeState = { colIdx, startX: e.clientX, startWidths: [...colWidths] };
  document.addEventListener('mousemove', doResize);
  document.addEventListener('mouseup', endResize);
  e.currentTarget.classList.add('active');
}
function doResize(e) {
  if (!resizeState) return;
  const dx = e.clientX - resizeState.startX;
  const head = document.getElementById('borrow-head');
  const totalW = head.offsetWidth;
  const sumFr = resizeState.startWidths.reduce((a, b) => a + b, 0);
  const frUnit = totalW / sumFr;
  const delta = dx / frUnit;
  const nw = [...resizeState.startWidths];
  nw[resizeState.colIdx] = Math.max(0.4, nw[resizeState.colIdx] + delta);
  if (resizeState.colIdx + 1 < nw.length)
    nw[resizeState.colIdx + 1] = Math.max(0.4, resizeState.startWidths[resizeState.colIdx + 1] - delta);
  colWidths = nw;
  const fw = colWidths.map(w => w + 'fr').join(' ') + ' 80px';
  head.style.gridTemplateColumns = fw;
  document.querySelectorAll('#borrow-body .at-row').forEach(r => r.style.gridTemplateColumns = fw);
}
function endResize() {
  resizeState = null;
  document.removeEventListener('mousemove', doResize);
  document.removeEventListener('mouseup', endResize);
  document.querySelectorAll('.resize-handle').forEach(h => h.classList.remove('active'));
}

// ── Tab switch ──
function switchTab(name) {
  document.getElementById('tab-samples').classList.toggle('on', name === 'samples');
  document.getElementById('tab-dashboard').classList.toggle('on', name === 'dashboard');
  document.getElementById('panel-samples').style.display = name === 'samples' ? '' : 'none';
  document.getElementById('panel-dashboard').style.display = name === 'dashboard' ? '' : 'none';
  if (name === 'dashboard') { renderDashboard(); rebuildEChart(); }
}

// ── Card size ──
function setSize(sz, btn) {
  document.querySelectorAll('.sbtn').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  document.getElementById('cg').className = 'cg sz-' + sz;
}

// ── Add modal ──
function openAdd() {
  document.getElementById('edit-id').value = '';
  document.getElementById('edit-fbid').value = '';
  document.getElementById('modal-title').textContent = '➕ 新增樣品';
  ['f-name', 'f-desc', 'f-note', 'f-imgurl'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('f-imgprev').style.display = 'none';
  document.getElementById('btn-del').style.display = 'none';
  document.getElementById('borrow-edit-section').style.display = 'none';
  const fi = document.getElementById('f-imgfile'); if (fi) fi._b64 = null;
  document.getElementById('mo-add').classList.add('on');
}

function openEdit(fbid) {
  const s = samples.find(x => x._id === fbid);
  if (!s) return;
  document.getElementById('edit-id').value = s.seq || '';
  document.getElementById('edit-fbid').value = fbid;
  document.getElementById('modal-title').textContent = '✏️ 編輯樣品';
  document.getElementById('f-name').value = s.name;
  document.getElementById('f-desc').value = s.desc || '';
  document.getElementById('f-note').value = s.note || '';
  document.getElementById('f-imgurl').value = s.img || '';
  const prev = document.getElementById('f-imgprev');
  if (s.img) { prev.src = s.img; prev.style.display = 'block'; } else prev.style.display = 'none';
  document.getElementById('btn-del').style.display = 'block';
  const fi = document.getElementById('f-imgfile'); if (fi) fi._b64 = null;
  document.getElementById('borrow-edit-section').style.display = 'block';
  document.getElementById('f-status').value = s.st || 'available';
  const bwSel = document.getElementById('f-bw');
  bwSel.innerHTML = '<option value="">選擇借用人</option>' +
    borrowers.map(b => `<option${s.bw === b ? ' selected' : ''}>${b}</option>`).join('');
  document.getElementById('f-bw-manual').value = '';
  document.getElementById('f-bd').value = s.bd || '';
  document.getElementById('f-rd').value = s.rd || '';
  document.getElementById('f-borrow-fields').style.display = s.st === 'borrowed' ? 'block' : 'none';
  document.getElementById('mo-add').classList.add('on');
}

function onStatusChange() {
  document.getElementById('f-borrow-fields').style.display =
    document.getElementById('f-status').value === 'borrowed' ? 'block' : 'none';
}
function closeAdd() { document.getElementById('mo-add').classList.remove('on'); }
function previewImg(url) {
  const p = document.getElementById('f-imgprev');
  if (url) { p.src = url; p.style.display = 'block'; } else p.style.display = 'none';
}
function handleImgUpload(inp) {
  if (!inp.files[0]) return;
  const r = new FileReader();
  r.onload = e => { inp._b64 = e.target.result; previewImg(e.target.result); document.getElementById('f-imgurl').value = ''; };
  r.readAsDataURL(inp.files[0]);
}

// ── Save card ──
async function saveCard() {
  const name = document.getElementById('f-name').value.trim();
  if (!name) { toast('請填寫樣品名稱', 'err'); return; }
  const desc = document.getElementById('f-desc').value.trim();
  const note = document.getElementById('f-note').value.trim();
  let img = document.getElementById('f-imgurl').value.trim();
  const fileInp = document.getElementById('f-imgfile');

  if (fileInp._b64 && !img) {
    toast('上傳照片中…', 'inf');
    const ext = fileInp._b64.split(';')[0].split('/')[1];
    const url = await uploadImageToGH(`sample_${Date.now()}.${ext}`, fileInp._b64);
    img = url || fileInp._b64;
    fileInp._b64 = null;
    if (url) toast('照片已上傳', 'ok');
  }

  const fbid = document.getElementById('edit-fbid').value;
  if (fbid) {
    const s = samples.find(x => x._id === fbid);
    if (!s) return;
    const newSt = document.getElementById('f-status').value;
    const newBw = document.getElementById('f-bw-manual').value.trim() || document.getElementById('f-bw').value;
    const newBd = document.getElementById('f-bd').value;
    const newRd = document.getElementById('f-rd').value;

    // 借出 → 在庫：寫入歸還紀錄
    if (s.st === 'borrowed' && newSt === 'available' && s.bw) {
      const rd = newRd || today();
      await window._db.collection('returnHistory').add({
        name: s.name, bw: s.bw, bd: s.bd, rd,
        _ts: firebase.firestore.FieldValue.serverTimestamp()
      });
    }

    const updateData = { name, desc, note, img, st: newSt, _ts: firebase.firestore.FieldValue.serverTimestamp() };
    if (newSt === 'borrowed') {
      if (!newBw) { toast('請選擇或輸入借用人', 'err'); return; }
      Object.assign(updateData, { bw: newBw, bd: newBd || today(), rd: newRd || '' });
    } else {
      Object.assign(updateData, { bw: '', bd: '', rd: newRd || '' });
    }
    await window._db.collection('samples').doc(fbid).update(updateData);
  } else {
    await window._db.collection('samples').add({
      seq: nextSeq(), name, desc, note, img,
      st: 'available', bw: '', bd: '', rd: '',
      _ts: firebase.firestore.FieldValue.serverTimestamp()
    });
  }
  closeAdd();
  toast(fbid ? '已更新 ✓' : '已新增 ✓', 'ok');
}

async function deleteCard() {
  const fbid = document.getElementById('edit-fbid').value;
  if (!confirm('確定刪除此樣品？')) return;
  await window._db.collection('samples').doc(fbid).delete();
  closeAdd();
  toast('已刪除', 'ok');
}

// ── Upload image to GitHub ──
async function uploadImageToGH(filename, base64data) {
  const token = GH_TOKEN || localStorage.getItem(LS_TOKEN) || '';
  if (!token) { toast('請先設定 GitHub Token', 'err'); return null; }
  const b64 = base64data.split(',')[1];
  const path = GH_PATH_IMG + filename;
  let sha = '';
  try {
    const r = await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/contents/${path}`,
      { headers: { Authorization: `token ${token}`, Accept: 'application/vnd.github.v3+json' } });
    if (r.ok) sha = (await r.json()).sha;
  } catch (e) {}
  try {
    const r = await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/contents/${path}`, {
      method: 'PUT',
      headers: { Authorization: `token ${token}`, 'Content-Type': 'application/json', Accept: 'application/vnd.github.v3+json' },
      body: JSON.stringify({ message: `Upload ${filename}`, content: b64, ...(sha ? { sha } : {}) })
    });
    if (r.ok) return `https://raw.githubusercontent.com/${GH_USER}/${GH_REPO}/main/${path}`;
  } catch (e) {}
  return null;
}

async function uploadCardImg(e, fbid) {
  const file = e.target.files[0]; if (!file) return;
  const r = new FileReader();
  r.onload = async ev => {
    const b64 = ev.target.result;
    toast('上傳照片中…', 'inf');
    const ext = b64.split(';')[0].split('/')[1];
    let url = await uploadImageToGH(`sample_${fbid}_${Date.now()}.${ext}`, b64);
    if (!url) url = b64;
    await window._db.collection('samples').doc(fbid).update({ img: url });
    toast('照片已更新 ✓', 'ok');
  };
  r.readAsDataURL(file);
}

// ── Borrow modal ──
function openBorrow(fbid) {
  document.getElementById('borrow-sample-id').value = fbid;
  const sel = document.getElementById('borrow-person');
  sel.innerHTML = '<option value="">選擇借用人</option>' + borrowers.map(b => `<option>${b}</option>`).join('');
  const card = document.getElementById(`bd-${fbid}`);
  document.getElementById('borrow-date').value = card ? card.value : today();
  document.getElementById('mo-borrow').classList.add('on');
}
function closeBorrow() { document.getElementById('mo-borrow').classList.remove('on'); }
async function confirmBorrow() {
  const fbid = document.getElementById('borrow-sample-id').value;
  const bw = document.getElementById('borrow-person').value;
  const bd = document.getElementById('borrow-date').value;
  if (!bw) { toast('請選擇借用人', 'err'); return; }
  if (!bd) { toast('請選擇借出日期', 'err'); return; }
  const s = samples.find(x => x._id === fbid);
  await window._db.collection('samples').doc(fbid).update({
    st: 'borrowed', bw, bd, rd: '',
    _ts: firebase.firestore.FieldValue.serverTimestamp()
  });
  closeBorrow();
  toast(`✅ ${s?.name} 已借出給 ${bw}`, 'ok');
}

// ── Return modal ──
function openReturn(fbid) {
  document.getElementById('return-sample-id').value = fbid;
  document.getElementById('return-date').value = today();
  document.getElementById('mo-return').classList.add('on');
}
function closeReturn() { document.getElementById('mo-return').classList.remove('on'); }
async function confirmReturn() {
  const fbid = document.getElementById('return-sample-id').value;
  const rd = document.getElementById('return-date').value;
  if (!rd) { toast('請選擇歸還日期', 'err'); return; }
  const s = samples.find(x => x._id === fbid);
  if (s) {
    await window._db.collection('returnHistory').add({
      name: s.name, bw: s.bw, bd: s.bd, rd,
      _ts: firebase.firestore.FieldValue.serverTimestamp()
    });
    await window._db.collection('samples').doc(fbid).update({
      st: 'available', rd, bw: '', bd: '',
      _ts: firebase.firestore.FieldValue.serverTimestamp()
    });
  }
  closeReturn();
  toast(`✅ ${s?.name} 已歸還`, 'ok');
}

// ── Lightbox ──
function openLB(src) { document.getElementById('lb-img').src = src; document.getElementById('lb').classList.add('on'); }
function closeLB() { document.getElementById('lb').classList.remove('on'); }

// ── Toast ──
function toast(msg, type = 'ok') {
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = msg;
  document.getElementById('toasts').appendChild(el);
  setTimeout(() => el.remove(), 3200);
}

// ── Export Excel ──
function exportExcel() {
  const rows = [['樣品名稱', '借用人', '借出日期', '歸還日期', '借用天數']];
  returnHistory.forEach(r => rows.push([r.name, r.bw, r.bd, r.rd, daysBetween(r.bd, r.rd)]));
  samples.filter(s => s.st === 'borrowed').forEach(s => rows.push([s.name, s.bw, s.bd, '（借出中）', daysBetween(s.bd, '')]));
  const blob = new Blob(['\ufeff' + rows.map(r => r.join('\t')).join('\n')], { type: 'text/tab-separated-values;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `借用紀錄_${today()}.xls`;
  a.click();
  toast('Excel 已下載', 'ok');
}

// ── Dashboard ──
function setPeriod(p) {
  currentPeriod = p;
  ['month', 'quarter', 'year'].forEach(k => document.getElementById('pb-' + k).classList.toggle('on', k === p));
  renderDashboard();
}

function renderDashboard() {
  const now = new Date();
  const allEvents = [
    ...returnHistory.map(r => ({ date: r.bd, bw: r.bw, name: r.name, days: daysBetween(r.bd, r.rd) })),
    ...samples.filter(s => s.st === 'borrowed').map(s => ({ date: s.bd, bw: s.bw, name: s.name, days: daysBetween(s.bd, '') }))
  ];
  const outstanding = samples.filter(s => s.st === 'borrowed').length;
  const avgDays = returnHistory.length
    ? Math.round(returnHistory.reduce((a, r) => a + daysBetween(r.bd, r.rd), 0) / returnHistory.length) : 0;

  let trendLabels = [], trendValues = [], trendColor = 'var(--blue)';

  if (currentPeriod === 'month') {
    const months = [];
    for (let i = 5; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      months.push({ label: `${d.getMonth() + 1}月`, year: d.getFullYear(), month: d.getMonth() });
    }
    trendLabels = months.map(m => m.label);
    trendValues = months.map(m => allEvents.filter(e => {
      if (!e.date) return false;
      const d = new Date(e.date);
      return d.getFullYear() === m.year && d.getMonth() === m.month;
    }).length);
    document.getElementById('kpi-total-lbl').textContent = '本月借出次數';
    document.getElementById('kpi-ret-lbl').textContent = '本月已歸還';
    document.getElementById('trend-title').textContent = '📅 每月借出次數趨勢';
    const thisMon = trendValues[trendValues.length - 1];
    const prevMon = trendValues[trendValues.length - 2] || 0;
    document.getElementById('kpi-total').textContent = thisMon;
    setTrend('kpi-total-trend', thisMon - prevMon, '較上月');
    document.getElementById('kpi-ret').textContent = returnHistory.filter(r => {
      const d = new Date(r.rd); return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
    }).length;
  } else if (currentPeriod === 'quarter') {
    trendColor = 'var(--teal)';
    const quarters = [];
    for (let i = 3; i >= 0; i--) {
      const qn = Math.floor(now.getMonth() / 3) - i;
      const y = now.getFullYear() + Math.floor(qn / 4);
      const q = ((qn % 4) + 4) % 4;
      quarters.push({ label: `Q${q + 1}`, year: y, q });
    }
    trendLabels = quarters.map(q => q.label);
    trendValues = quarters.map(q => allEvents.filter(e => {
      if (!e.date) return false;
      const d = new Date(e.date);
      return d.getFullYear() === q.year && Math.floor(d.getMonth() / 3) === q.q;
    }).length);
    document.getElementById('kpi-total-lbl').textContent = '本季借出次數';
    document.getElementById('kpi-ret-lbl').textContent = '本季已歸還';
    document.getElementById('trend-title').textContent = '📅 季度借出次數趨勢';
    const thisQ = trendValues[trendValues.length - 1];
    document.getElementById('kpi-total').textContent = thisQ;
    setTrend('kpi-total-trend', thisQ - (trendValues[trendValues.length - 2] || 0), '較上季');
    const curQ = Math.floor(now.getMonth() / 3);
    document.getElementById('kpi-ret').textContent = returnHistory.filter(r => {
      const d = new Date(r.rd); return d.getFullYear() === now.getFullYear() && Math.floor(d.getMonth() / 3) === curQ;
    }).length;
  } else {
    trendColor = 'var(--amber)';
    const years = [now.getFullYear() - 3, now.getFullYear() - 2, now.getFullYear() - 1, now.getFullYear()];
    trendLabels = years.map(y => String(y));
    trendValues = years.map(y => allEvents.filter(e => e.date && new Date(e.date).getFullYear() === y).length);
    document.getElementById('kpi-total-lbl').textContent = '今年借出次數';
    document.getElementById('kpi-ret-lbl').textContent = '今年已歸還';
    document.getElementById('trend-title').textContent = '📅 年度借出次數趨勢';
    const thisY = trendValues[trendValues.length - 1];
    document.getElementById('kpi-total').textContent = thisY;
    setTrend('kpi-total-trend', thisY - (trendValues[trendValues.length - 2] || 0), '較去年');
    document.getElementById('kpi-ret').textContent = returnHistory.filter(r => new Date(r.rd).getFullYear() === now.getFullYear()).length;
  }

  document.getElementById('kpi-out').textContent = outstanding;
  document.getElementById('kpi-out-trend').textContent = outstanding > 3 ? '⚠️ 偏多' : '正常';
  document.getElementById('kpi-out-trend').className = 'kpi-trend ' + (outstanding > 3 ? 'trend-dn' : 'trend-up');
  document.getElementById('kpi-avg').textContent = avgDays;
  document.getElementById('kpi-avg-trend').textContent = avgDays > 30 ? '⚠️ 偏長' : avgDays ? '正常' : '—';
  document.getElementById('kpi-ret-trend').textContent = '';
  document.getElementById('kpi-avg-lbl').textContent = '平均借用天數';
  document.getElementById('kpi-out-lbl').textContent = '累計未歸還';
  document.getElementById('kpi-avg-lbl').textContent = '平均借用天數';

  // trend chart
  const maxV = Math.max(...trendValues, 1);
  document.getElementById('trend-chart').innerHTML = trendLabels.map((lbl, i) => {
    const h = Math.round((trendValues[i] / maxV) * 84);
    return `<div class="bar-col"><div class="bar-col-val">${trendValues[i]}</div><div class="bar-col-fill" style="height:${h}px;background:${trendColor}"></div><div class="bar-col-lbl">${lbl}</div></div>`;
  }).join('');

  // person chart
  const pCount = {};
  returnHistory.forEach(r => { pCount[r.bw] = (pCount[r.bw] || 0) + 1; });
  samples.filter(s => s.st === 'borrowed').forEach(s => { if (s.bw) pCount[s.bw] = (pCount[s.bw] || 0) + 1; });
  const pMax = Math.max(...Object.values(pCount), 1);
  const COLORS = ['#c0392b', '#e67e22', 'var(--blue)', 'var(--teal)', 'var(--green)'];
  document.getElementById('person-chart').innerHTML = Object.entries(pCount).sort((a, b) => b[1] - a[1]).slice(0, 6)
    .map(([name, cnt], i) => `<div class="bar-row"><span class="bar-lbl">${name}</span><div class="bar-bg"><div class="bar-fill" style="width:${Math.round(cnt / pMax * 100)}%;background:${COLORS[i % 5]}"></div></div><span class="bar-val">${cnt} 次</span></div>`)
    .join('') || '<div style="padding:12px;color:var(--t4);font-size:12px">尚無資料</div>';

  // item chart
  const iCount = {};
  returnHistory.forEach(r => { iCount[r.name] = (iCount[r.name] || 0) + 1; });
  samples.filter(s => s.st === 'borrowed').forEach(s => { iCount[s.name] = (iCount[s.name] || 0) + 1; });
  const iMax = Math.max(...Object.values(iCount), 1);
  document.getElementById('item-chart').innerHTML = Object.entries(iCount).sort((a, b) => b[1] - a[1]).slice(0, 6)
    .map(([name, cnt]) => `<div class="bar-row"><span class="bar-lbl">${name}</span><div class="bar-bg"><div class="bar-fill" style="width:${Math.round(cnt / iMax * 100)}%;background:var(--teal)"></div></div><span class="bar-val">${cnt} 次</span></div>`)
    .join('') || '<div style="padding:12px;color:var(--t4);font-size:12px">尚無資料</div>';

  // warn
  const warnItems = samples.filter(s => s.st === 'borrowed' && daysBetween(s.bd, '') > 30);
  document.getElementById('warn-body').innerHTML = warnItems.length
    ? warnItems.map(s => `<div class="at-row th5" style="min-width:400px">
        <div style="font-weight:700">${s.name}</div><div>${s.bw}</div>
        <div style="color:var(--t3)">${s.bd}</div>
        <div class="days-red">${daysBetween(s.bd, '')} 天</div>
        <div><span class="chip chip-bw">借出中</span></div></div>`).join('')
    : '<div style="padding:16px;text-align:center;color:var(--t4);font-size:12px">目前無長期借用樣品 ✓</div>';

  rebuildEChart();
}

function setTrend(elId, diff, label) {
  const el = document.getElementById(elId);
  if (diff > 0) { el.textContent = `↑ ${label} +${diff}`; el.className = 'kpi-trend trend-up'; }
  else if (diff < 0) { el.textContent = `↓ ${label} ${diff}`; el.className = 'kpi-trend trend-dn'; }
  else { el.textContent = `→ 與${label.replace('較', '')}持平`; el.className = 'kpi-trend'; }
}

// ── ECharts Dynamic Data 圖表（仿 dynamic-data 範例原始碼）──
let ecMainChart = null;
let ecTimer = null;

// 從 Firestore 資料計算各維度數值
function calcGroupValues(catKey, valKey) {
  const allEvents = [
    ...returnHistory.map(r => ({
      cat: catKey === 'month' ? r.bd?.slice(0,7) :
           catKey === 'borrower' ? r.bw :
           catKey === 'item' ? r.name : getDaysRange(daysBetween(r.bd, r.rd)),
      days: daysBetween(r.bd, r.rd),
      returned: true
    })),
    ...samples.filter(s => s.st === 'borrowed').map(s => ({
      cat: catKey === 'month' ? s.bd?.slice(0,7) :
           catKey === 'borrower' ? s.bw :
           catKey === 'item' ? s.name : getDaysRange(daysBetween(s.bd, '')),
      days: daysBetween(s.bd, ''),
      returned: false
    }))
  ];

  // 建立分組
  let groups = {};
  if (catKey === 'month') {
    const now = new Date();
    for (let i = 11; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      groups[`${d.getFullYear()}/${String(d.getMonth()+1).padStart(2,'0')}`] = [];
    }
  } else if (catKey === 'days_range') {
    groups = {'1-7天':[], '8-14天':[], '15-30天':[], '31-60天':[], '60天以上':[]};
  }
  allEvents.forEach(e => {
    if (!e.cat) return;
    if (!groups[e.cat]) groups[e.cat] = [];
    groups[e.cat].push(e);
  });

  const labels = Object.keys(groups);
  const values = labels.map(k => {
    const evs = groups[k];
    if (valKey === 'count') return evs.length;
    if (valKey === 'days') return evs.length ? Math.round(evs.reduce((a,e)=>a+e.days,0)/evs.length) : 0;
    if (valKey === 'outstanding') {
      if (catKey === 'borrower') return samples.filter(s=>s.st==='borrowed'&&s.bw===k).length;
      if (catKey === 'item') return samples.filter(s=>s.st==='borrowed'&&s.name===k).length;
      return samples.filter(s=>s.st==='borrowed').length;
    }
    return 0;
  });
  return { labels, values };
}

function getDaysRange(d) {
  if (d <= 7) return '1-7天';
  if (d <= 14) return '8-14天';
  if (d <= 30) return '15-30天';
  if (d <= 60) return '31-60天';
  return '60天以上';
}

const Y_LABELS = { count:'借用次數', days:'平均天數（天）', outstanding:'未歸還數' };
const Y_MAXES  = { count:null, days:60, outstanding:null };

function rebuildEChart() {
  if (ecTimer) { clearInterval(ecTimer); ecTimer = null; }

  const catKey = document.getElementById('ec-cat').value;
  const y1Key  = document.getElementById('ec-y1').value;
  const y2Key  = document.getElementById('ec-y2').value;

  const { labels, values: v1 } = calcGroupValues(catKey, y1Key);
  const { values: v2 }         = calcGroupValues(catKey, y2Key);

  // 第二 X 軸 data（序號，仿 dynamic-data 的 categories2）
  const cats2 = labels.map((_, i) => i + 1);

  if (!ecMainChart) {
    ecMainChart = echarts.init(document.getElementById('ec-main'));
    window.addEventListener('resize', () => ecMainChart && ecMainChart.resize());
  }

  // ── 完全照搬 dynamic-data 的 option 結構 ──
  const option = {
    title: { text: 'Dynamic Data', left: 'center', textStyle: { fontSize: 13, fontWeight: 700, color: '#1a1d23' } },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross', label: { backgroundColor: '#283b56' } }
    },
    legend: { top: 30, textStyle: { fontSize: 11 } },
    toolbox: {
      show: true,
      right: 14,
      feature: {
        dataView: { readOnly: false, title: '資料檢視' },
        restore: { title: '還原' },
        saveAsImage: { title: '儲存圖片' }
      }
    },
    dataZoom: { show: false, start: 0, end: 100 },
    xAxis: [
      {
        type: 'category',
        boundaryGap: true,
        data: labels,
        axisLabel: { fontSize: 10, rotate: labels.length > 8 ? 30 : 0, overflow:'truncate', width:60 }
      },
      {
        type: 'category',
        boundaryGap: true,
        data: cats2,
        axisLabel: { fontSize: 10 }
      }
    ],
    yAxis: [
      {
        type: 'value',
        scale: true,
        name: Y_LABELS[y2Key],
        nameTextStyle: { fontSize: 10 },
        boundaryGap: [0.2, 0.2],
        axisLabel: { fontSize: 10 }
      },
      {
        type: 'value',
        scale: true,
        name: Y_LABELS[y1Key],
        nameTextStyle: { fontSize: 10 },
        boundaryGap: [0.2, 0.2],
        axisLabel: { fontSize: 10 }
      }
    ],
    series: [
      {
        name: Y_LABELS[y1Key],
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: v1,
        itemStyle: { color: '#185fa5' },
        label: { show: true, position: 'top', fontSize: 9 }
      },
      {
        name: Y_LABELS[y2Key],
        type: 'line',
        data: v2,
        smooth: true,
        itemStyle: { color: '#0c7a99' },
        areaStyle: { opacity: 0.12 },
        label: { show: true, position: 'top', fontSize: 9 }
      }
    ]
  };

  ecMainChart.setOption(option, true);

  // ── 動態更新（仿 dynamic-data 的 setInterval）──
  // 每 2.1 秒重新計算並 setOption，模擬即時動態效果
  ecTimer = setInterval(() => {
    const { values: nv1 } = calcGroupValues(catKey, y1Key);
    const { values: nv2 } = calcGroupValues(catKey, y2Key);
    ecMainChart.setOption({ series: [{ data: nv1 }, { data: nv2 }] });
  }, 2100);
}

// ── Modal overlay close ──
document.querySelectorAll('.mo').forEach(mo => {
  mo.addEventListener('click', e => { if (e.target === mo) mo.classList.remove('on'); });
});

// ── Init ──
init();
