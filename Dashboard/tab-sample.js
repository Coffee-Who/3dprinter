/**
 * tab-sample.js
 * 3D 列印樣品管理模組
 * ─────────────────────────────────────────────
 * 使用方式：在 index.html 的 </body> 前加上：
 *   <script src="tab-sample.js"></script>
 * ─────────────────────────────────────────────
 * 依賴：
 *   - window.showToast(msg, type)  ← 由 index.html 提供
 *   - window.hasPerm(user, perm)   ← 由 index.html 提供
 *   - window._currentUser          ← Firebase Auth 登入後設定
 *   - window._userPerms            ← Firestore permissions 載入後設定
 *   - window._ghToken              ← 可選，從 Firestore userSettings 載入
 */

/* ══════════════════════════════════════════
   1. 注入 CSS
   ══════════════════════════════════════════ */
(function injectCSS() {
  if (document.getElementById('sm-style')) return;
  const style = document.createElement('style');
  style.id = 'sm-style';
  style.textContent = `
/* ══ SAMPLE MODULE CSS (sm- prefix) ══ */
.sm-panel{flex:1;overflow-y:auto;background:#f5f6f8;display:flex;flex-direction:column}
.sm-pg-hdr{background:#fff;border-bottom:1px solid #e6e8ec;padding:12px 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;flex-shrink:0}
.sm-pg-title{font-size:15px;font-weight:700;color:#0a0e14}
.sm-pg-sub{font-size:11px;color:#5a6270;margin-top:2px}
.sm-sync{display:flex;align-items:center;gap:5px;background:#e6f1ea;border:1px solid #9acfb4;border-radius:20px;padding:3px 10px;font-size:11px;color:#1d6f43;font-weight:600;flex-shrink:0}
.sm-sync.err{background:#fcebeb;border-color:#f5b0b0;color:#a32d2d}
.sm-sync.spin{background:#fbf3dc;border-color:#f5d5a0;color:#8b6b13}
.sm-sync-dot{width:6px;height:6px;border-radius:50%;background:#3fb950;animation:smBlink 1.6s infinite;flex-shrink:0}
.sm-sync.err .sm-sync-dot{background:#a32d2d}
.sm-sync.spin .sm-sync-dot{background:#8b6b13;animation:smBlink .6s infinite}
@keyframes smBlink{0%,100%{opacity:1}50%{opacity:.3}}
.sm-ctabs{display:flex;padding:0 20px;background:#fff;border-bottom:1px solid #e6e8ec;overflow-x:auto;flex-shrink:0}
.sm-ctab{padding:9px 16px;font-size:12px;color:#5a6270;cursor:pointer;border-bottom:2px solid transparent;font-weight:600;white-space:nowrap;display:flex;align-items:center;gap:5px;user-select:none;flex-shrink:0}
.sm-ctab.on{color:#185fa5;border-bottom-color:#185fa5}
.sm-ctab:hover:not(.on){color:#0a0e14}
.sm-toolbar{display:flex;align-items:center;gap:8px;padding:9px 20px;background:#fff;border-bottom:1px solid #eef0f3;flex-wrap:wrap;flex-shrink:0}
.sm-tsearch{display:flex;align-items:center;gap:6px;background:#f5f6f8;border:1.5px solid #e6e8ec;border-radius:6px;padding:5px 10px}
.sm-tsearch input{border:none;background:none;outline:none;font-size:12px;color:#0a0e14;width:110px;font-family:inherit}
.sm-tsel{padding:5px 8px;border:1.5px solid #e6e8ec;border-radius:6px;font-size:12px;background:#fff;color:#3b4250;font-family:inherit;height:30px}
.sm-tbtn{height:30px;padding:0 12px;border:1.5px solid #e6e8ec;border-radius:6px;font-size:12px;font-weight:600;background:#fff;color:#3b4250;cursor:pointer;font-family:inherit;display:inline-flex;align-items:center;gap:5px;white-space:nowrap;transition:.12s}
.sm-tbtn:hover{background:#f5f6f8}
.sm-tbtn.green{border-color:#1d6f43;background:#e6f1ea;color:#1d6f43}
.sm-tbtn.blue{border-color:#185fa5;background:#e6f1fb;color:#185fa5}
.sm-sizebtns{display:flex;border:1.5px solid #e6e8ec;border-radius:6px;overflow:hidden}
.sm-sizebtn{padding:4px 10px;font-size:11px;font-weight:700;border:none;border-right:1px solid #e6e8ec;background:#fff;color:#5a6270;cursor:pointer;transition:.12s;font-family:inherit}
.sm-sizebtn:last-child{border-right:none}
.sm-sizebtn.on{background:#185fa5;color:#fff}
.sm-period-btns{display:flex;border:1.5px solid #e6e8ec;border-radius:6px;overflow:hidden}
.sm-period-btn{padding:5px 16px;font-size:12px;font-weight:600;border:none;border-right:1px solid #e6e8ec;background:#fff;color:#5a6270;cursor:pointer;transition:.12s;font-family:inherit}
.sm-period-btn:last-child{border-right:none}
.sm-period-btn.on{background:#185fa5;color:#fff}
.sm-stat-row{display:flex;gap:8px;padding:14px 20px;flex-wrap:wrap;flex-shrink:0}
.sm-sc{background:#fff;border:1.5px solid #e6e8ec;border-radius:8px;padding:9px 14px;display:flex;align-items:center;gap:10px}
.sm-sc-num{font-size:22px;font-weight:700;line-height:1}
.sm-sc-lbl{font-size:9px;color:#8a93a3;text-transform:uppercase;letter-spacing:.07em;margin-top:2px;font-weight:700}
.sm-sc.bw .sm-sc-num{color:#a32d2d}
.sm-sc.av .sm-sc-num{color:#1d6f43}
.sm-sc.tot .sm-sc-num{color:#185fa5}
.sm-card{background:#fff;border:1.5px solid #e6e8ec;border-radius:8px;overflow:hidden;display:flex;flex-direction:column;transition:.15s}
.sm-card:hover{border-color:#b5d4f4;box-shadow:0 2px 12px rgba(0,0,0,.08)}
.sm-card-img{position:relative;width:100%;aspect-ratio:1/1;background:#eef0f3;display:flex;align-items:center;justify-content:center;overflow:hidden;color:#c8cdd6}
.sm-card-img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;cursor:pointer}
.sm-card-img.lg{aspect-ratio:4/3}
.sm-sp-pill{position:absolute;top:5px;left:5px;font-size:8px;font-weight:700;padding:2px 6px;border-radius:10px;pointer-events:none}
.sm-sp-av{background:#e6f1ea;color:#1d6f43}
.sm-sp-bw{background:#fcebeb;color:#a32d2d}
.sm-upload-hover{position:absolute;bottom:5px;right:5px;background:rgba(10,14,20,.75);color:#fff;border:none;border-radius:5px;padding:3px 7px;font-size:9px;cursor:pointer;display:none;align-items:center;gap:3px}
.sm-card:hover .sm-upload-hover{display:flex}
.sm-edit-hover{position:absolute;top:5px;right:5px;background:rgba(10,14,20,.75);color:#fff;border:none;border-radius:5px;padding:3px 7px;font-size:9px;cursor:pointer;display:none}
.sm-card:hover .sm-edit-hover{display:block}
.sm-card-body{padding:8px 10px 6px;flex:1}
.sm-card-name{font-size:11px;font-weight:700;color:#0a0e14;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:2px;cursor:pointer}
.sm-card-desc{font-size:9px;color:#5a6270;line-height:1.5;margin-bottom:4px}
.sm-mrow{display:flex;gap:3px;font-size:9px;margin-bottom:1px}
.sm-ml{color:#8a93a3;font-weight:700;min-width:30px;font-size:9px;flex-shrink:0}
.sm-mv{color:#0a0e14}
.sm-mv.rd{color:#a32d2d;font-weight:700}
.sm-note-box{background:#e6f1fb;border-left:3px solid #b5d4f4;border-radius:0 4px 4px 0;padding:4px 7px;font-size:9px;color:#5a6270;font-style:italic;margin-top:3px}
.sm-card-foot{padding:6px 8px 8px;border-top:1px solid #eef0f3}
.sm-frow{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.sm-fsel{flex:1;min-width:0;padding:4px 5px;border-radius:4px;border:1.5px solid #e6e8ec;font-size:10px;background:#f5f6f8;color:#0a0e14;font-family:inherit}
.sm-fdate{width:88px;padding:4px 5px;border-radius:4px;border:1.5px solid #e6e8ec;font-size:10px;background:#f5f6f8;color:#5a6270;font-family:inherit}
.sm-cfbtn{padding:4px 9px;border-radius:4px;border:1.5px solid #185fa5;background:#185fa5;color:#fff;font-size:10px;cursor:pointer;font-family:inherit;font-weight:700;white-space:nowrap;transition:.12s}
.sm-cfbtn:hover{background:#0c7a99;border-color:#0c7a99}
.sm-cfbtn.ret{border-color:#a32d2d;background:#fcebeb;color:#a32d2d}
.sm-cfbtn.ret:hover{background:#a32d2d;color:#fff}
.sm-tbl-wrap{padding:0 20px 20px}
.sm-sec-hd{display:flex;align-items:center;justify-content:space-between;padding:14px 0 8px;border-top:1px solid #eef0f3;flex-wrap:wrap;gap:6px}
.sm-sec-title{font-size:13px;font-weight:700;color:#0a0e14}
.sm-sec-title span{color:#185fa5}
.sm-at{background:#fff;border:1.5px solid #e6e8ec;border-radius:8px;overflow:hidden;overflow-x:auto}
.sm-at-head{display:grid;background:#f8f9fb;padding:8px 14px;font-size:9px;text-transform:uppercase;letter-spacing:.08em;font-weight:700;color:#8a93a3;border-bottom:1.5px solid #e6e8ec;min-width:600px;position:relative}
.sm-at-head>div{display:flex;align-items:center;gap:3px;position:relative}
.sm-resize{position:absolute;right:-4px;top:0;height:100%;width:8px;cursor:col-resize;z-index:2}
.sm-resize:hover::after,.sm-resize.active::after{content:'';position:absolute;left:3px;top:20%;height:60%;width:2px;background:#185fa5;border-radius:2px}
.sm-at-row{display:grid;padding:8px 14px;border-bottom:1px solid #eef0f3;font-size:11px;align-items:center;min-width:600px}
.sm-at-row:last-child{border-bottom:none}
.sm-at-row:hover{background:#f8f9fb}
.sm-at-name{font-weight:700;color:#0a0e14;display:flex;align-items:center;gap:5px;overflow:hidden}
.sm-chip{display:inline-flex;font-size:9px;padding:1px 7px;border-radius:10px;font-weight:700;flex-shrink:0}
.sm-chip-bw{background:#fcebeb;color:#a32d2d}
.sm-chip-av{background:#e6f1ea;color:#1d6f43}
.sm-days-red{font-weight:700;color:#a32d2d}
.sm-tbl-edit-btn{padding:2px 9px;border-radius:4px;border:1.5px solid #e6e8ec;background:#fff;color:#5a6270;font-size:10px;cursor:pointer;font-family:inherit;transition:.12s;white-space:nowrap}
.sm-tbl-edit-btn:hover{border-color:#0c7a99;color:#0c7a99;background:#e6f1f6}
.sm-dash{padding:0 20px 28px}
.sm-kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}
.sm-kpi{background:#fff;border:1.5px solid #e6e8ec;border-radius:8px;padding:13px 15px}
.sm-kpi-num{font-size:26px;font-weight:700;line-height:1;margin-bottom:4px}
.sm-kpi-lbl{font-size:10px;color:#5a6270;font-weight:700;text-transform:uppercase;letter-spacing:.06em}
.sm-kpi-trend{font-size:10px;margin-top:4px;font-weight:600;color:#8a93a3}
.sm-kpi.blue .sm-kpi-num{color:#185fa5}
.sm-kpi.green .sm-kpi-num{color:#1d6f43}
.sm-kpi.red .sm-kpi-num{color:#a32d2d}
.sm-kpi.teal .sm-kpi-num{color:#0c7a99}
.sm-trend-up{color:#1d6f43}.sm-trend-dn{color:#a32d2d}
.sm-chart-card{background:#fff;border:1.5px solid #e6e8ec;border-radius:8px;padding:14px 16px;margin-bottom:14px}
.sm-chart-title{font-size:12px;font-weight:700;color:#0a0e14;margin-bottom:12px;padding-bottom:7px;border-bottom:1px solid #eef0f3}
.sm-bar-chart{display:flex;align-items:flex-end;gap:6px;height:100px;padding:4px 0 0}
.sm-bar-col{display:flex;flex-direction:column;align-items:center;gap:3px;flex:1;min-width:0}
.sm-bar-fill{width:80%;border-radius:3px 3px 0 0;min-height:2px;transition:height .4s}
.sm-bar-lbl{font-size:9px;color:#8a93a3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
.sm-bar-val{font-size:9px;font-weight:700;color:#3b4250}
.sm-chart-2col{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px}
.sm-hbar-row{display:flex;align-items:center;gap:8px;margin-bottom:7px}
.sm-hbar-lbl{font-size:11px;color:#3b4250;font-weight:600;min-width:64px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sm-hbar-bg{flex:1;height:7px;background:#eef0f3;border-radius:4px;overflow:hidden}
.sm-hbar-fill{height:100%;border-radius:4px;transition:width .4s}
.sm-hbar-val{font-size:11px;color:#5a6270;min-width:28px;text-align:right;font-weight:600}
.sm-warn-hd{padding:9px 14px;background:#fff8f0;border-bottom:1.5px solid #f5d5b0;font-size:12px;font-weight:700;color:#8b4513;display:flex;align-items:center;gap:6px}
.sm-mo{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:5100;align-items:center;justify-content:center;padding:16px}
.sm-mo.on{display:flex}
.sm-mb{background:#fff;border-radius:12px;padding:22px;width:100%;max-width:460px;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,.25)}
.sm-mb h3{font-size:15px;font-weight:700;margin-bottom:16px}
.sm-mb label{display:block;font-size:10px;font-weight:700;color:#5a6270;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px;margin-top:10px}
.sm-mb label:first-of-type{margin-top:0}
.sm-mb input,.sm-mb textarea,.sm-mb select{width:100%;padding:8px 10px;border-radius:6px;border:1.5px solid #e6e8ec;font-size:13px;background:#f5f6f8;color:#0a0e14;outline:none;transition:.12s;font-family:inherit;box-sizing:border-box}
.sm-mb input:focus,.sm-mb textarea:focus,.sm-mb select:focus{border-color:#185fa5}
.sm-mb textarea{min-height:60px;resize:vertical}
.sm-mb-foot{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}
.sm-btn-cancel{height:34px;padding:0 16px;border:1.5px solid #e6e8ec;border-radius:6px;font-size:13px;background:#fff;color:#3b4250;cursor:pointer;font-weight:600;font-family:inherit}
.sm-btn-save{height:34px;padding:0 16px;border:none;border-radius:6px;font-size:13px;background:#185fa5;color:#fff;cursor:pointer;font-weight:600;font-family:inherit}
.sm-btn-save:hover{background:#0c7a99}
.sm-btn-del{height:34px;padding:0 14px;border:none;border-radius:6px;font-size:13px;background:#fcebeb;color:#a32d2d;cursor:pointer;font-weight:600;margin-right:auto;font-family:inherit}
.sm-upload-area{border:2px dashed #e6e8ec;border-radius:6px;padding:14px;text-align:center;cursor:pointer;margin-top:6px;font-size:12px;color:#5a6270}
.sm-upload-area:hover{border-color:#185fa5;color:#185fa5}
.sm-prev-img{width:100%;max-height:150px;object-fit:cover;border-radius:6px;margin-top:8px;display:none}
.sm-borrow-edit-sec{border-radius:8px;background:#e6f1f6;border:1.5px solid #9acfcf;padding:12px 14px}
.sm-borrow-edit-sec label{color:#0c7a99 !important}
.sm-lb{display:none;position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:6000;align-items:center;justify-content:center}
.sm-lb.on{display:flex}
.sm-lb img{max-width:92vw;max-height:88vh;object-fit:contain;border-radius:8px}
.sm-lb-close{position:absolute;top:14px;right:18px;color:#fff;font-size:26px;cursor:pointer;line-height:1}

/* Responsive */
@media(max-width:960px){:root{--sidebar-w:60px}.sidebar-brand>div:not(.shell-brand-mark){display:none}.sidebar-item-text{display:none}.sidebar-item{justify-content:center;padding:10px 8px}.sidebar-foot{display:none}}
@media(max-width:1100px){.dash-kpis{grid-template-columns:repeat(3,1fr)}.dash-grid{grid-template-columns:repeat(2,1fr)}.kpi-strip{grid-template-columns:repeat(3,1fr)}.sm-kpi-row{grid-template-columns:repeat(2,1fr)}.sm-chart-2col{grid-template-columns:1fr}}
@media(max-width:720px){.dash-kpis{grid-template-columns:repeat(2,1fr)}.dash-grid{grid-template-columns:1fr}.sm-kpi-row{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.shell-top{padding:0 14px;gap:6px}.shell-tab{padding:11px 10px;font-size:12px}.shell-aux{display:none}.sm-chart-2col{grid-template-columns:1fr}}

  `;
  document.head.appendChild(style);
})();

/* ══════════════════════════════════════════
   2. 注入 HTML Modals（Add/Edit、Borrow、Return、Lightbox）
   ══════════════════════════════════════════ */
(function injectHTML() {
  if (document.getElementById('sm-mo-add')) return;
  const div = document.createElement('div');
  div.innerHTML = `
<!-- Lightbox -->
<div class="sm-lb" id="sm-lb" onclick="if(event.target===this)this.classList.remove('on')">
  <span class="sm-lb-close" onclick="document.getElementById('sm-lb').classList.remove('on')">×</span>
  <img id="sm-lb-img" src="" alt="">
</div>

<!-- ══ SAMPLE MODALS HTML ══ -->
<!-- Add / Edit -->
<div class="sm-mo" id="sm-mo-add" onclick="if(event.target===this)this.classList.remove('on')">
  <div class="sm-mb">
    <h3>➕ 新增樣品</h3>
    <input type="hidden" id="sm-edit-id">
    <label>樣品名稱 *</label>
    <input type="text" id="sm-f-name" placeholder="例：FDM 齒輪組">
    <label>摘要描述</label>
    <textarea id="sm-f-desc" placeholder="簡短說明此樣品特性…" rows="2"></textarea>
    <label>備註</label>
    <input type="text" id="sm-f-note" placeholder="選填備註…">
    <label>照片網址</label>
    <input type="url" id="sm-f-imgurl" placeholder="https://…" oninput="smPreviewImg(this.value)">
    <div class="sm-upload-area" onclick="document.getElementById('sm-f-imgfile').click()">
      📷 點擊上傳照片（jpg / png / webp）
      <input type="file" id="sm-f-imgfile" accept="image/*" style="display:none" onchange="smHandleImgUpload(this)">
    </div>
    <img id="sm-f-imgprev" class="sm-prev-img" alt="">
    <div id="sm-borrow-edit-sec" class="sm-borrow-edit-sec" style="display:none;margin-top:14px;padding:12px 14px;border-radius:8px">
      <div style="font-size:11px;font-weight:700;color:#0c7a99;text-transform:uppercase;letter-spacing:.07em;margin-bottom:10px">📋 借用狀態編輯</div>
      <label>借用狀態</label>
      <select id="sm-f-status" onchange="smOnStatusChange()">
        <option value="available">✅ 在庫</option>
        <option value="borrowed">📤 借出中</option>
      </select>
      <div id="sm-f-borrow-fields" style="display:none">
        <label>借用人（選單）</label>
        <select id="sm-f-bw"><option value="">選擇借用人</option></select>
        <label>或直接輸入借用人</label>
        <input type="text" id="sm-f-bw-manual" placeholder="直接輸入姓名">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:4px">
          <div><label>借出日期</label><input type="date" id="sm-f-bd"></div>
          <div><label>歸還日期</label><input type="date" id="sm-f-rd"></div>
        </div>
      </div>
    </div>
    <div class="sm-mb-foot">
      <button class="sm-btn-del" id="sm-btn-del" style="display:none" onclick="smDeleteCard()">🗑 刪除</button>
      <button class="sm-btn-cancel" onclick="document.getElementById('sm-mo-add').classList.remove('on')">取消</button>
      <button class="sm-btn-save" onclick="smSaveCard()">💾 儲存</button>
    </div>
  </div>
</div>
<!-- Borrow -->
<div class="sm-mo" id="sm-mo-borrow" onclick="if(event.target===this)this.classList.remove('on')">
  <div class="sm-mb">
    <h3>📤 確認借出</h3>
    <input type="hidden" id="sm-borrow-sid">
    <label>借用人</label><select id="sm-borrow-person"></select>
    <label>借出日期 *</label><input type="date" id="sm-borrow-date">
    <div class="sm-mb-foot">
      <button class="sm-btn-cancel" onclick="document.getElementById('sm-mo-borrow').classList.remove('on')">取消</button>
      <button class="sm-btn-save" onclick="smConfirmBorrow()">確認借出</button>
    </div>
  </div>
</div>
<!-- Return -->
<div class="sm-mo" id="sm-mo-return" onclick="if(event.target===this)this.classList.remove('on')">
  <div class="sm-mb">
    <h3>📥 確認歸還</h3>
    <input type="hidden" id="sm-return-sid">
    <label>歸還日期 *</label><input type="date" id="sm-return-date">
    <div class="sm-mb-foot">
      <button class="sm-btn-cancel" onclick="document.getElementById('sm-mo-return').classList.remove('on')">取消</button>
      <button class="sm-btn-save" onclick="smConfirmReturn()">確認歸還</button>
    </div>
  </div>
</div>
  `;
  document.body.appendChild(div);
})();

/* ══════════════════════════════════════════
   3. 樣品模組主邏輯
   ══════════════════════════════════════════ */

(function(){
'use strict';
const GH_USER='Coffee-Who',GH_REPO='3dprinter';
const GH_PATH_DATA='image/samples.json',GH_PATH_IMG='image/';
const GH_RAW=`https://raw.githubusercontent.com/${GH_USER}/${GH_REPO}/main/${GH_PATH_DATA}`;
const LS_DATA='sw_samples_v3',LS_TOKEN='sw_gh_token_v3',LS_BORROW='sw_borrowers_v3';

let samples=[],returnHistory=[],nid=1;
let borrowers=['王小明','李美華','張大偉','陳怡君','林志豪'];
let cardSize='md',currentPeriod='month';
let colWidths=[2,1.4,1.2,0.8],resizeState=null;

const getToken=()=>window._ghToken||localStorage.getItem(LS_TOKEN)||'';
const todayStr=()=>new Date().toISOString().slice(0,10);
const daysBetween=(d1,d2)=>{if(!d1)return 0;return Math.max(0,Math.round((new Date(d2||new Date())-new Date(d1))/86400000));};

function smCanEdit(){
  const u=window._currentUser;if(!u)return false;
  const p=(window._userPerms||{})[u.uid||u]||{};
  return p.admin===true||p.samples_edit===true;
}

/* ── Sync UI ── */
function smSetSync(state,txt){
  const el=document.getElementById('sm-sync');if(!el)return;
  el.className='sm-sync '+state;
  const t=document.getElementById('sm-sync-txt');if(t)t.textContent=txt;
}

/* ── Load / Save ── */
window.smLoad=async function(){
  smSetSync('spin','連線中…');
  try{
    const r=await fetch(GH_RAW+'?t='+Date.now(),{cache:'no-store'});
    if(r.ok){const d=await r.json();smApply(d);localStorage.setItem(LS_DATA,JSON.stringify(d));smSetSync('ok','已同步 GitHub');return;}
  }catch(e){}
  const cache=localStorage.getItem(LS_DATA);
  if(cache){try{smApply(JSON.parse(cache));smSetSync('err','本機快取');return;}catch(e){}}
  smSetSync('err','載入失敗');
};

function smApply(d){
  samples=d.samples||[];returnHistory=d.returnHistory||[];
  if(d.borrowers)borrowers=d.borrowers;
  nid=samples.length?Math.max(...samples.map(s=>s.id||0))+1:1;
  localStorage.setItem(LS_BORROW,JSON.stringify(borrowers));
  smRenderAll();
}

async function smSave(){
  const payload={samples,returnHistory,borrowers,updatedAt:new Date().toISOString()};
  localStorage.setItem(LS_DATA,JSON.stringify(payload));
  const token=getToken();
  if(!token){smSetSync('err','未設定 Token');return;}
  smSetSync('spin','儲存中…');
  const json=JSON.stringify(payload,null,2);let sha='';
  try{const r=await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/contents/${GH_PATH_DATA}`,{headers:{Authorization:`token ${token}`,Accept:'application/vnd.github.v3+json'}});if(r.ok)sha=(await r.json()).sha;}catch(e){}
  try{
    const r=await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/contents/${GH_PATH_DATA}`,{
      method:'PUT',headers:{Authorization:`token ${token}`,'Content-Type':'application/json',Accept:'application/vnd.github.v3+json'},
      body:JSON.stringify({message:`Samples update ${new Date().toISOString().slice(0,19)}`,content:btoa(unescape(encodeURIComponent(json))),...(sha?{sha}:{})})
    });
    if(r.ok){smSetSync('ok','已同步 GitHub ✓');return;}
  }catch(e){}
  smSetSync('err','GitHub 失敗，已存本機');
}

async function smUploadImg(filename,base64data){
  const token=getToken();if(!token){showToast('請先設定 Token','err');return null;}
  const b64=base64data.split(',')[1];const path=GH_PATH_IMG+filename;let sha='';
  try{const r=await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/contents/${path}`,{headers:{Authorization:`token ${token}`,Accept:'application/vnd.github.v3+json'}});if(r.ok)sha=(await r.json()).sha;}catch(e){}
  try{const r=await fetch(`https://api.github.com/repos/${GH_USER}/${GH_REPO}/contents/${path}`,{method:'PUT',headers:{Authorization:`token ${token}`,'Content-Type':'application/json',Accept:'application/vnd.github.v3+json'},body:JSON.stringify({message:`Upload ${filename}`,content:b64,...(sha?{sha}:{})})});if(r.ok)return`https://raw.githubusercontent.com/${GH_USER}/${GH_REPO}/main/${path}`;}catch(e){}
  return null;
}

/* ── Render All ── */
window.smRenderAll=function(){smRenderCards();smRenderBorrowTable();smRenderReturnTable();smRenderDashboard();smUpdateStats();};

function smUpdateStats(){
  const set=(id,v)=>{const el=document.getElementById(id);if(el)el.textContent=v;};
  set('sm-stat-bw',samples.filter(s=>s.st==='borrowed').length);
  set('sm-stat-av',samples.filter(s=>s.st==='available').length);
  set('sm-stat-tot',samples.length);
}

/* ── Cards ── */
function smRenderCards(){
  const q=(document.getElementById('sm-search')?.value||'').toLowerCase();
  const sf=document.getElementById('sm-status-f')?.value||'';
  const cg=document.getElementById('sm-cg');if(!cg)return;
  const list=samples.filter(s=>{
    if(q&&!s.name.toLowerCase().includes(q))return false;
    if(sf&&s.st!==sf)return false;
    return true;
  });
  if(!list.length){cg.innerHTML='<div style="padding:32px;text-align:center;color:#8a93a3;font-size:13px">沒有符合條件的樣品</div>';return;}
  const cols=cardSize==='lg'?'repeat(auto-fill,minmax(240px,1fr))':cardSize==='md'?'repeat(auto-fill,minmax(160px,1fr))':'repeat(auto-fill,minmax(110px,1fr))';
  cg.style.gridTemplateColumns=cols;
  cg.innerHTML=list.map(s=>smCardHTML(s)).join('');
}

function smCardHTML(s){
  const isBw=s.st==='borrowed';
  const isLg=cardSize==='lg',isSm=cardSize==='sm';
  const canEdit=smCanEdit();
  const imgEl=s.img?`<img src="${s.img}" alt="${s.name}" onclick="smOpenLB('${s.img.replace(/'/g,"\\'")}') " loading="lazy">`:`<span style="font-size:${isSm?'14px':'24px'};opacity:.3">🖨️</span>`;
  const editBtn=canEdit?`<button onclick="smOpenEdit(${s.id})" class="sm-edit-hover">✏️</button>`:'';
  const uploadBtn=canEdit?`<label class="sm-upload-hover" title="上傳照片">📷<input type="file" accept="image/*" style="display:none" onchange="smUploadCardImg(event,${s.id})"></label>`:'';
  let foot='';
  if(!isSm){
    if(canEdit){
      foot=isBw
        ?`<div class="sm-frow"><span style="font-size:10px;font-weight:700;color:#0a0e14;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">👤 ${s.bw}</span><button class="sm-cfbtn" style="background:#e6f1f6;border-color:#0c7a99;color:#0c7a99" onclick="smOpenEdit(${s.id})">✏️</button><button class="sm-cfbtn ret" onclick="smOpenReturn(${s.id})">📥 歸還</button></div>`
        :`<div class="sm-frow"><select class="sm-fsel" id="sm-sel-${s.id}"><option value="">選擇借用人</option>${borrowers.map(b=>`<option>${b}</option>`).join('')}</select><input type="date" class="sm-fdate" id="sm-bd-${s.id}" value="${todayStr()}"><button class="sm-cfbtn" onclick="smOpenBorrow(${s.id})">借出</button><button class="sm-cfbtn" style="background:#f5f6f8;border-color:#e6e8ec;color:#5a6270;padding:4px 7px" onclick="smOpenEdit(${s.id})">✏️</button></div>`;
    }else{
      foot=`<div style="font-size:10px;color:#8a93a3;padding:2px 0">${isBw?`👤 ${s.bw} · ${s.bd}`:'在庫中'}</div>`;
    }
  }
  return`<div class="sm-card">
    <div class="sm-card-img${isLg?' lg':''}">
      ${imgEl}
      <div class="sm-sp-pill ${isBw?'sm-sp-bw':'sm-sp-av'}">${isBw?'借出中':'在庫'}</div>
      ${editBtn}${uploadBtn}
    </div>
    <div class="sm-card-body">
      <div class="sm-card-name" onclick="smOpenEdit(${s.id})">${s.name}</div>
      ${!isSm?`<div class="sm-card-desc">${s.desc||''}</div>`:''}
      ${!isSm&&isBw?`<div class="sm-mrow"><span class="sm-ml">借出人</span><span class="sm-mv rd">${s.bw}</span></div><div class="sm-mrow"><span class="sm-ml">借出日</span><span class="sm-mv">${s.bd||''}</span></div>`:''}
      ${!isSm&&s.note?`<div class="sm-note-box">📝 ${s.note}</div>`:''}
    </div>
    ${!isSm?`<div class="sm-card-foot">${foot}</div>`:''}
  </div>`;
}

/* ── Borrow Table ── */
function smRenderBorrowTable(){
  const borrowed=samples.filter(s=>s.st==='borrowed');
  const fw=colWidths.map(w=>w+'fr').join(' ')+' 80px';
  const head=document.getElementById('sm-borrow-head');
  const body=document.getElementById('sm-borrow-body');
  if(!head||!body)return;
  head.style.gridTemplateColumns=fw;
  head.innerHTML=['樣品名稱','借用人','借出日期','天數'].map((h,i)=>
    `<div>${h}<span style="color:#d0d4db;font-size:11px">⠿</span><div class="sm-resize" onmousedown="smStartResize(event,${i})"></div></div>`
  ).join('')+'<div>操作</div>';
  if(!borrowed.length){body.innerHTML='<div style="padding:18px;text-align:center;color:#8a93a3;font-size:12px">目前無借出中樣品</div>';return;}
  const canEdit=smCanEdit();
  body.innerHTML=borrowed.map(s=>{
    const d=daysBetween(s.bd,'');
    return`<div class="sm-at-row" style="grid-template-columns:${fw}">
      <div class="sm-at-name">${s.name}<span class="sm-chip sm-chip-bw">借出中</span></div>
      <div style="font-weight:700">${s.bw||'—'}</div>
      <div style="color:#5a6270">${s.bd||'—'}</div>
      <div class="${d>30?'sm-days-red':''}">${d} 天</div>
      <div>${canEdit?`<button class="sm-tbl-edit-btn" onclick="smOpenEdit(${s.id})">✏️ 編輯</button>`:''}</div>
    </div>`;
  }).join('');
}

/* ── Return Table ── */
function smRenderReturnTable(){
  const body=document.getElementById('sm-return-body');if(!body)return;
  if(!returnHistory.length){body.innerHTML='<div style="padding:18px;text-align:center;color:#8a93a3;font-size:12px">尚無歸還紀錄</div>';return;}
  body.innerHTML=[...returnHistory].reverse().map(r=>`
    <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;padding:8px 14px;border-bottom:1px solid #eef0f3;font-size:11px;align-items:center;min-width:500px">
      <div style="font-weight:700">${r.name}</div><div>${r.bw}</div>
      <div style="color:#5a6270">${r.bd}</div><div style="color:#1d6f43;font-weight:600">${r.rd}</div>
      <div style="color:#5a6270">${daysBetween(r.bd,r.rd)} 天</div>
    </div>`).join('');
}

/* ── Column Resize ── */
window.smStartResize=function(e,i){
  e.preventDefault();
  resizeState={colIdx:i,startX:e.clientX,startWidths:[...colWidths]};
  document.addEventListener('mousemove',smDoResize);document.addEventListener('mouseup',smEndResize);
};
function smDoResize(e){
  if(!resizeState)return;
  const dx=e.clientX-resizeState.startX;
  const head=document.getElementById('sm-borrow-head');if(!head)return;
  const totalW=head.offsetWidth;
  const frUnit=totalW/resizeState.startWidths.reduce((a,b)=>a+b,0);
  const delta=dx/frUnit;
  const nw=[...resizeState.startWidths];
  nw[resizeState.colIdx]=Math.max(0.4,nw[resizeState.colIdx]+delta);
  if(resizeState.colIdx+1<nw.length)nw[resizeState.colIdx+1]=Math.max(0.4,resizeState.startWidths[resizeState.colIdx+1]-delta);
  colWidths=nw;
  const fw=colWidths.map(w=>w+'fr').join(' ')+' 80px';
  head.style.gridTemplateColumns=fw;
  document.querySelectorAll('#sm-borrow-body .sm-at-row').forEach(r=>r.style.gridTemplateColumns=fw);
}
function smEndResize(){resizeState=null;document.removeEventListener('mousemove',smDoResize);document.removeEventListener('mouseup',smEndResize);}

/* ── Tab / Size / Period ── */
window.smSwitchTab=function(name){
  document.getElementById('sm-tab-samples')?.classList.toggle('on',name==='samples');
  document.getElementById('sm-tab-dash')?.classList.toggle('on',name==='dashboard');
  const ps=document.getElementById('sm-panel-samples');const pd=document.getElementById('sm-panel-dashboard');
  if(ps)ps.style.display=name==='samples'?'':'none';
  if(pd)pd.style.display=name==='dashboard'?'':'none';
  if(name==='dashboard')smRenderDashboard();
};
window.smSetSize=function(sz,btn){
  cardSize=sz;
  document.querySelectorAll('.sm-sizebtn').forEach(b=>b.classList.remove('on'));
  if(btn)btn.classList.add('on');
  smRenderCards();
};
window.smSetPeriod=function(p){
  currentPeriod=p;
  ['month','quarter','year'].forEach(k=>document.getElementById('sm-pb-'+k)?.classList.toggle('on',k===p));
  smRenderDashboard();
};

/* ── Modals ── */
window.smOpenAdd=function(){
  if(!smCanEdit()){showToast('無新增權限','err');return;}
  const m=document.getElementById('sm-mo-add');if(!m)return;
  m.querySelector('#sm-edit-id').value='';
  m.querySelector('#sm-f-name').value='';
  m.querySelector('#sm-f-desc').value='';
  m.querySelector('#sm-f-note').value='';
  m.querySelector('#sm-f-imgurl').value='';
  m.querySelector('#sm-f-imgprev').style.display='none';
  m.querySelector('#sm-btn-del').style.display='none';
  m.querySelector('#sm-borrow-edit-sec').style.display='none';
  m.querySelector('h3').textContent='➕ 新增樣品';
  const fi=m.querySelector('#sm-f-imgfile');if(fi)fi._b64=null;
  m.classList.add('on');
};
window.smOpenEdit=function(id){
  const s=samples.find(x=>x.id===id);if(!s)return;
  const m=document.getElementById('sm-mo-add');if(!m)return;
  m.querySelector('#sm-edit-id').value=id;
  m.querySelector('#sm-f-name').value=s.name;
  m.querySelector('#sm-f-desc').value=s.desc||'';
  m.querySelector('#sm-f-note').value=s.note||'';
  m.querySelector('#sm-f-imgurl').value=s.img||'';
  const prev=m.querySelector('#sm-f-imgprev');
  if(s.img){prev.src=s.img;prev.style.display='block';}else prev.style.display='none';
  m.querySelector('#sm-btn-del').style.display=smCanEdit()?'block':'none';
  m.querySelector('h3').textContent='✏️ 編輯樣品';
  const fi=m.querySelector('#sm-f-imgfile');if(fi)fi._b64=null;
  const sec=m.querySelector('#sm-borrow-edit-sec');sec.style.display='block';
  m.querySelector('#sm-f-status').value=s.st||'available';
  const bwSel=m.querySelector('#sm-f-bw');
  bwSel.innerHTML='<option value="">選擇借用人</option>'+borrowers.map(b=>`<option${s.bw===b?' selected':''}>${b}</option>`).join('');
  m.querySelector('#sm-f-bw-manual').value='';
  m.querySelector('#sm-f-bd').value=s.bd||'';
  m.querySelector('#sm-f-rd').value=s.rd||'';
  m.querySelector('#sm-f-borrow-fields').style.display=s.st==='borrowed'?'block':'none';
  m.classList.add('on');
};
window.smOnStatusChange=function(){
  const m=document.getElementById('sm-mo-add');if(!m)return;
  m.querySelector('#sm-f-borrow-fields').style.display=m.querySelector('#sm-f-status').value==='borrowed'?'block':'none';
};
window.smPreviewImg=function(url){
  const p=document.getElementById('sm-mo-add')?.querySelector('#sm-f-imgprev');
  if(!p)return;
  if(url){p.src=url;p.style.display='block';}else p.style.display='none';
};
window.smHandleImgUpload=function(inp){
  if(!inp.files[0])return;
  const r=new FileReader();
  r.onload=e=>{inp._b64=e.target.result;smPreviewImg(e.target.result);document.getElementById('sm-mo-add').querySelector('#sm-f-imgurl').value='';};
  r.readAsDataURL(inp.files[0]);
};
window.smSaveCard=async function(){
  if(!smCanEdit())return;
  const m=document.getElementById('sm-mo-add');
  const name=m.querySelector('#sm-f-name').value.trim();
  if(!name){showToast('請填寫樣品名稱','err');return;}
  const desc=m.querySelector('#sm-f-desc').value.trim();
  const note=m.querySelector('#sm-f-note').value.trim();
  let img=m.querySelector('#sm-f-imgurl').value.trim();
  const fi=m.querySelector('#sm-f-imgfile');
  if(fi?._b64&&!img){
    showToast('上傳照片中…','inf');
    const ext=fi._b64.split(';')[0].split('/')[1];
    const url=await smUploadImg(`sample_${Date.now()}.${ext}`,fi._b64);
    img=url||fi._b64;fi._b64=null;if(url)showToast('照片已上傳','ok');
  }
  const editId=m.querySelector('#sm-edit-id').value;
  if(editId){
    const s=samples.find(x=>x.id===+editId);if(!s)return;
    const newSt=m.querySelector('#sm-f-status').value;
    const newBw=m.querySelector('#sm-f-bw-manual').value.trim()||m.querySelector('#sm-f-bw').value;
    const newBd=m.querySelector('#sm-f-bd').value;
    const newRd=m.querySelector('#sm-f-rd').value;
    if(s.st==='borrowed'&&newSt==='available'&&s.bw){
      const rd=newRd||todayStr();
      if(!returnHistory.some(r=>r.name===s.name&&r.bd===s.bd&&r.bw===s.bw))
        returnHistory.push({name:s.name,bw:s.bw,bd:s.bd,rd});
    }
    s.name=name;s.desc=desc;s.note=note;s.img=img;s.st=newSt;
    if(newSt==='borrowed'){
      if(!newBw){showToast('請選擇借用人','err');return;}
      s.bw=newBw;s.bd=newBd||todayStr();s.rd=newRd||'';
    }else{s.bw='';s.bd='';s.rd=newRd||'';}
  }else{
    samples.push({id:nid++,name,desc,note,img,st:'available',bw:'',bd:'',rd:''});
  }
  m.classList.remove('on');
  smRenderAll();await smSave();
  showToast(editId?'已更新 ✓':'已新增 ✓','ok');
};
window.smDeleteCard=async function(){
  if(!smCanEdit())return;
  const id=+document.getElementById('sm-mo-add').querySelector('#sm-edit-id').value;
  if(!confirm('確定刪除此樣品？'))return;
  samples=samples.filter(s=>s.id!==id);
  document.getElementById('sm-mo-add').classList.remove('on');
  smRenderAll();await smSave();showToast('已刪除','ok');
};
window.smOpenBorrow=function(id){
  if(!smCanEdit())return;
  const m=document.getElementById('sm-mo-borrow');if(!m)return;
  m.querySelector('#sm-borrow-sid').value=id;
  m.querySelector('#sm-borrow-person').innerHTML='<option value="">選擇借用人</option>'+borrowers.map(b=>`<option>${b}</option>`).join('');
  const card=document.getElementById(`sm-bd-${id}`);
  m.querySelector('#sm-borrow-date').value=card?card.value:todayStr();
  m.classList.add('on');
};
window.smConfirmBorrow=async function(){
  const m=document.getElementById('sm-mo-borrow');
  const id=+m.querySelector('#sm-borrow-sid').value;
  const bw=m.querySelector('#sm-borrow-person').value;
  const bd=m.querySelector('#sm-borrow-date').value;
  if(!bw){showToast('請選擇借用人','err');return;}
  if(!bd){showToast('請選擇借出日期','err');return;}
  const s=samples.find(x=>x.id===id);
  if(s){s.st='borrowed';s.bw=bw;s.bd=bd;s.rd='';}
  m.classList.remove('on');smRenderAll();await smSave();
  showToast(`✅ ${s?.name} 已借出給 ${bw}`,'ok');
};
window.smOpenReturn=function(id){
  if(!smCanEdit())return;
  const m=document.getElementById('sm-mo-return');if(!m)return;
  m.querySelector('#sm-return-sid').value=id;
  m.querySelector('#sm-return-date').value=todayStr();
  m.classList.add('on');
};
window.smConfirmReturn=async function(){
  const m=document.getElementById('sm-mo-return');
  const id=+m.querySelector('#sm-return-sid').value;
  const rd=m.querySelector('#sm-return-date').value;
  if(!rd){showToast('請選擇歸還日期','err');return;}
  const s=samples.find(x=>x.id===id);
  if(s){returnHistory.push({name:s.name,bw:s.bw,bd:s.bd,rd});s.st='available';s.rd=rd;s.bw='';s.bd='';}
  m.classList.remove('on');smRenderAll();await smSave();
  showToast(`✅ ${s?.name} 已歸還`,'ok');
};
window.smOpenLB=function(src){
  const lb=document.getElementById('sm-lb');if(!lb)return;
  document.getElementById('sm-lb-img').src=src;lb.classList.add('on');
};
window.smExportExcel=function(){
  const rows=[['樣品名稱','借用人','借出日期','歸還日期','借用天數']];
  returnHistory.forEach(r=>rows.push([r.name,r.bw,r.bd,r.rd,daysBetween(r.bd,r.rd)]));
  samples.filter(s=>s.st==='borrowed').forEach(s=>rows.push([s.name,s.bw,s.bd,'（借出中）',daysBetween(s.bd,'')]));
  const ws=rows.map(r=>r.join('\t')).join('\n');
  const blob=new Blob(['\ufeff'+ws],{type:'text/tab-separated-values;charset=utf-8'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`借用紀錄_${todayStr()}.xls`;a.click();
  showToast('Excel 已下載','ok');
};
window.smUploadCardImg=async function(e,id){
  const file=e.target.files[0];if(!file)return;
  const r=new FileReader();
  r.onload=async ev=>{
    const b64=ev.target.result;showToast('上傳照片中…','inf');
    const ext=b64.split(';')[0].split('/')[1];
    let url=await smUploadImg(`sample_${id}_${Date.now()}.${ext}`,b64);
    if(!url)url=b64;
    const s=samples.find(x=>x.id===id);if(s)s.img=url;
    smRenderCards();await smSave();showToast('照片已更新 ✓','ok');
  };
  r.readAsDataURL(file);
};

/* ── Dashboard ── */
window.smRenderDashboard=function(){
  const now=new Date();
  const allEvents=[...returnHistory.map(r=>({date:r.bd,bw:r.bw,name:r.name})),...samples.filter(s=>s.st==='borrowed').map(s=>({date:s.bd,bw:s.bw,name:s.name}))];
  const outstanding=samples.filter(s=>s.st==='borrowed').length;
  const avgDays=returnHistory.length?Math.round(returnHistory.reduce((a,r)=>a+daysBetween(r.bd,r.rd),0)/returnHistory.length):0;
  let labels=[],vals=[],trendColor='#185fa5';

  if(currentPeriod==='month'){
    const months=[];for(let i=5;i>=0;i--){const d=new Date(now.getFullYear(),now.getMonth()-i,1);months.push({label:`${d.getMonth()+1}月`,year:d.getFullYear(),month:d.getMonth()});}
    labels=months.map(m=>m.label);vals=months.map(m=>allEvents.filter(e=>{if(!e.date)return false;const d=new Date(e.date);return d.getFullYear()===m.year&&d.getMonth()===m.month;}).length);
    smSet('sm-kpi-total',vals[vals.length-1],'本月借出次數');
    smSet('sm-kpi-ret',returnHistory.filter(r=>{const d=new Date(r.rd);return d.getFullYear()===now.getFullYear()&&d.getMonth()===now.getMonth();}).length,'本月已歸還');
    smSetTrend('sm-kpi-total-trend',vals[vals.length-1]-(vals[vals.length-2]||0),'較上月');
    setEl('sm-trend-title','📅 每月借出次數趨勢');
  }else if(currentPeriod==='quarter'){
    trendColor='#0c7a99';
    const qs=[];for(let i=3;i>=0;i--){const qn=Math.floor(now.getMonth()/3)-i;const y=now.getFullYear()+Math.floor(qn/4);const q=((qn%4)+4)%4;qs.push({label:`Q${q+1}`,year:y,q});}
    labels=qs.map(q=>q.label);vals=qs.map(q=>allEvents.filter(e=>{if(!e.date)return false;const d=new Date(e.date);return d.getFullYear()===q.year&&Math.floor(d.getMonth()/3)===q.q;}).length);
    smSet('sm-kpi-total',vals[vals.length-1],'本季借出次數');
    const curQ=Math.floor(now.getMonth()/3);
    smSet('sm-kpi-ret',returnHistory.filter(r=>{const d=new Date(r.rd);return d.getFullYear()===now.getFullYear()&&Math.floor(d.getMonth()/3)===curQ;}).length,'本季已歸還');
    smSetTrend('sm-kpi-total-trend',vals[vals.length-1]-(vals[vals.length-2]||0),'較上季');
    setEl('sm-trend-title','📅 季度借出次數趨勢');
  }else{
    trendColor='#8b6b13';
    const years=[now.getFullYear()-3,now.getFullYear()-2,now.getFullYear()-1,now.getFullYear()];
    labels=years.map(y=>String(y));vals=years.map(y=>allEvents.filter(e=>e.date&&new Date(e.date).getFullYear()===y).length);
    smSet('sm-kpi-total',vals[vals.length-1],'今年借出次數');
    smSet('sm-kpi-ret',returnHistory.filter(r=>new Date(r.rd).getFullYear()===now.getFullYear()).length,'今年已歸還');
    smSetTrend('sm-kpi-total-trend',vals[vals.length-1]-(vals[vals.length-2]||0),'較去年');
    setEl('sm-trend-title','📅 年度借出次數趨勢');
  }

  smSet('sm-kpi-out',outstanding,'累計未歸還');
  const oe=document.getElementById('sm-kpi-out-trend');
  if(oe){oe.textContent=outstanding>3?'⚠️ 偏多':'正常';oe.className='sm-kpi-trend '+(outstanding>3?'sm-trend-dn':'sm-trend-up');}
  smSet('sm-kpi-avg',avgDays,'平均借用天數');
  const ae=document.getElementById('sm-kpi-avg-trend');if(ae)ae.textContent=avgDays>30?'⚠️ 偏長':avgDays?'正常':'—';

  const maxV=Math.max(...vals,1);
  const tc=document.getElementById('sm-trend-chart');
  if(tc)tc.innerHTML=labels.map((lbl,i)=>{const h=Math.round((vals[i]/maxV)*84);return`<div class="sm-bar-col"><div class="sm-bar-val">${vals[i]}</div><div class="sm-bar-fill" style="height:${h}px;background:${trendColor}"></div><div class="sm-bar-lbl">${lbl}</div></div>`;}).join('');

  const pCount={};returnHistory.forEach(r=>{pCount[r.bw]=(pCount[r.bw]||0)+1;});samples.filter(s=>s.st==='borrowed').forEach(s=>{if(s.bw)pCount[s.bw]=(pCount[s.bw]||0)+1;});
  const pMax=Math.max(...Object.values(pCount),1);const COLORS=['#c0392b','#e67e22','#185fa5','#0c7a99','#1d6f43'];
  const pc=document.getElementById('sm-person-chart');
  if(pc)pc.innerHTML=Object.entries(pCount).sort((a,b)=>b[1]-a[1]).slice(0,6).map(([name,cnt],i)=>`<div class="sm-hbar-row"><span class="sm-hbar-lbl">${name}</span><div class="sm-hbar-bg"><div class="sm-hbar-fill" style="width:${Math.round(cnt/pMax*100)}%;background:${COLORS[i%5]}"></div></div><span class="sm-hbar-val">${cnt} 次</span></div>`).join('')||'<div style="padding:12px;color:#8a93a3;font-size:12px">尚無資料</div>';

  const iCount={};returnHistory.forEach(r=>{iCount[r.name]=(iCount[r.name]||0)+1;});samples.filter(s=>s.st==='borrowed').forEach(s=>{iCount[s.name]=(iCount[s.name]||0)+1;});
  const iMax=Math.max(...Object.values(iCount),1);
  const ic=document.getElementById('sm-item-chart');
  if(ic)ic.innerHTML=Object.entries(iCount).sort((a,b)=>b[1]-a[1]).slice(0,6).map(([name,cnt])=>`<div class="sm-hbar-row"><span class="sm-hbar-lbl">${name}</span><div class="sm-hbar-bg"><div class="sm-hbar-fill" style="width:${Math.round(cnt/iMax*100)}%;background:#0c7a99"></div></div><span class="sm-hbar-val">${cnt} 次</span></div>`).join('')||'<div style="padding:12px;color:#8a93a3;font-size:12px">尚無資料</div>';

  const warnItems=samples.filter(s=>s.st==='borrowed'&&daysBetween(s.bd,'')>30);
  const wb=document.getElementById('sm-warn-body');
  if(wb)wb.innerHTML=warnItems.length?warnItems.map(s=>`<div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr 1fr;padding:8px 14px;border-bottom:1px solid #eef0f3;font-size:11px;align-items:center;min-width:400px"><div style="font-weight:700">${s.name}</div><div>${s.bw}</div><div style="color:#5a6270">${s.bd}</div><div class="sm-days-red">${daysBetween(s.bd,'')} 天</div><div><span class="sm-chip sm-chip-bw">借出中</span></div></div>`).join(''):'<div style="padding:16px;text-align:center;color:#8a93a3;font-size:12px">目前無長期借用樣品 ✓</div>';
};

function smSet(id,val,lbl){
  const el=document.getElementById(id);if(el)el.textContent=val;
  const ll=document.getElementById(id+'-lbl');if(ll)ll.textContent=lbl;
}
function setEl(id,txt){const el=document.getElementById(id);if(el)el.textContent=txt;}
function smSetTrend(elId,diff,label){
  const el=document.getElementById(elId);if(!el)return;
  if(diff>0){el.textContent=`↑ ${label} +${diff}`;el.className='sm-kpi-trend sm-trend-up';}
  else if(diff<0){el.textContent=`↓ ${label} ${diff}`;el.className='sm-kpi-trend sm-trend-dn';}
  else{el.textContent=`→ 與${label.replace('較','')}持平`;el.className='sm-kpi-trend';}
}

window.smSetToken=function(token){window._ghToken=token;localStorage.setItem(LS_TOKEN,token);showToast('Token 已儲存','ok');window.smLoad();};
setInterval(window.smLoad,60000);
})();

