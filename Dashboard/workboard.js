
// workboard.js
// 工作看板：TableView / KanbanView / GanttView / DashboardView
// + Firebase CRUD + OrderModal
// 依賴：React, firebase-service.js, helpers.js, 原始 view-*.jsx

(function () {
  const { useState, useEffect } = React;

  // ── 訂單 Modal ──
  function OrderModal({ order, onClose, onSave }) {
    const K = window.K;
    const empty = {
      seq:'', id:'', customer:'', engineer: K.ENG_ORDER[0],
      dueDate:'', startDate:'', endDate:'', material:'足夠',
      progress: 0, machine: K.MACHINES[0], complete:'否', remark:''
    };
    const [form, setForm] = useState(order ? { ...order } : empty);
    const [busy, setBusy] = useState(false);
    const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

    const save = async () => {
      if (!form.customer || !form.dueDate) {
        showToast('請填客戶名稱與期望交期', 'err'); return;
      }
      setBusy(true);
      try { await onSave(form); onClose(); }
      catch (e) { showToast(e.message || '儲存失敗', 'err'); }
      finally { setBusy(false); }
    };

    const S = { input: { width:'100%', padding:'8px 11px', border:'1.5px solid #e6e8ec', borderRadius:6, fontSize:13, fontFamily:'inherit', outline:'none' } };
    const LBL = { display:'block', fontSize:11.5, fontWeight:600, color:'#5a6270', marginBottom:5 };

    return (
      <div className="m-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
        <div className="m-box">
          <div className="m-hd">
            <h3>{order ? '✏️ 編輯訂單' : '➕ 新增訂單'}</h3>
            <button className="m-close" onClick={onClose}>×</button>
          </div>
          <div className="m-body">
            <div className="m-row">
              <div className="m-field"><label style={LBL}>EF 單號</label><input style={S.input} value={form.id||''} onChange={e=>set('id',e.target.value)} placeholder="202512100001"/></div>
              <div className="m-field"><label style={LBL}>客戶名稱 *</label><input style={S.input} value={form.customer} onChange={e=>set('customer',e.target.value)}/></div>
            </div>
            <div className="m-row">
              <div className="m-field"><label style={LBL}>執行工程師</label>
                <select style={S.input} value={form.engineer} onChange={e=>set('engineer',e.target.value)}>
                  {K.ENG_ORDER.map(e=><option key={e} value={e}>{K.ENG_LABEL[e]||e}</option>)}</select></div>
              <div className="m-field"><label style={LBL}>機台</label>
                <select style={S.input} value={form.machine} onChange={e=>set('machine',e.target.value)}>
                  {K.MACHINES.map(m=><option key={m}>{m}</option>)}</select></div>
            </div>
            <div className="m-row">
              <div className="m-field"><label style={LBL}>開始日</label><input style={S.input} type="date" value={form.startDate||''} onChange={e=>set('startDate',e.target.value)}/></div>
              <div className="m-field"><label style={LBL}>預計完成日</label><input style={S.input} type="date" value={form.endDate||''} onChange={e=>set('endDate',e.target.value)}/></div>
            </div>
            <div className="m-row">
              <div className="m-field"><label style={LBL}>期望交期 *</label><input style={S.input} type="date" value={form.dueDate||''} onChange={e=>set('dueDate',e.target.value)}/></div>
              <div className="m-field"><label style={LBL}>材料庫存</label>
                <select style={S.input} value={form.material} onChange={e=>set('material',e.target.value)}>
                  {K.MATERIALS.map(m=><option key={m}>{m}</option>)}</select></div>
            </div>
            <div className="m-row">
              <div className="m-field"><label style={LBL}>進度 %</label>
                <select style={S.input} value={form.progress} onChange={e=>set('progress',+e.target.value)}>
                  {K.PROGRESS_VALUES.map(p=><option key={p} value={p}>{p}%</option>)}</select></div>
              <div className="m-field"><label style={LBL}>完成</label>
                <select style={S.input} value={form.complete} onChange={e=>set('complete',e.target.value)}>
                  <option>否</option><option>是</option></select></div>
            </div>
            <div className="m-field"><label style={LBL}>備註</label>
              <textarea style={{...S.input, resize:'vertical'}} value={form.remark||''} onChange={e=>set('remark',e.target.value)} rows={3}/></div>
          </div>
          <div className="m-foot">
            <button className="btn-cancel" onClick={onClose}>取消</button>
            <button className="btn-save" onClick={save} disabled={busy}>{busy?'儲存中...':'💾 儲存'}</button>
          </div>
        </div>
      </div>
    );
  }

  // ── WorkBoard 主元件 ──
  function WorkBoardApp({ user }) {
    const K = window.K;
    const [data,    setData]    = useState([]);
    const [loading, setLoading] = useState(true);
    const [tab,     setTab]     = useState('table');
    const [modal,   setModal]   = useState(false);
    const [editO,   setEditO]   = useState(null);

    const canEdit = window.hasPerm(user, 'edit_board');
    const canDel  = window.hasPerm(user, 'delete_board');

    useEffect(() => {
      const unsub = FBOrders.onSnapshot(rows => { setData(rows); setLoading(false); });
      return () => unsub();
    }, []);

    const nextSeq = () => data.length ? Math.max(...data.map(d => d.seq || 0)) + 1 : 1;

    const handleSave = async form => {
      if (editO) { await FBOrders.update(editO._id, form); showToast('訂單已更新 ✓'); }
      else       { await FBOrders.add({ ...form, seq: nextSeq() }); showToast('訂單已新增 ✓'); }
    };

    const proxySetData = updater => {
      const next = typeof updater === 'function' ? updater(data) : updater;
      data.filter(d => !next.find(n => n.seq === d.seq)).forEach(r => {
        if (canDel) FBOrders.del(r._id).then(() => showToast('已刪除', 'inf'));
      });
      next.forEach(n => {
        const orig = data.find(d => d.seq === n.seq);
        if (orig && JSON.stringify(orig) !== JSON.stringify(n)) FBOrders.update(n._id, n);
      });
    };

    const TABS = [
      { key:'table',     label:'總表' },
      { key:'kanban',    label:'看板' },
      { key:'gantt',     label:'時間軸' },
      { key:'dashboard', label:'Dashboard' },
    ];
    const TAB_ICONS = {
      table:     <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><rect x="1.5" y="2" width="11" height="10" rx="1.2" stroke="currentColor" strokeWidth="1.3"/><line x1="1.5" y1="5.5" x2="12.5" y2="5.5" stroke="currentColor" strokeWidth="1.3"/><line x1="5" y1="2" x2="5" y2="12" stroke="currentColor" strokeWidth="1.3"/></svg>,
      kanban:    <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><rect x="1.5" y="2" width="3" height="10" rx="0.8" stroke="currentColor" strokeWidth="1.3"/><rect x="5.5" y="2" width="3" height="6.5" rx="0.8" stroke="currentColor" strokeWidth="1.3"/><rect x="9.5" y="2" width="3" height="8.5" rx="0.8" stroke="currentColor" strokeWidth="1.3"/></svg>,
      gantt:     <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><line x1="1.5" y1="3" x2="9.5" y2="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/><line x1="4" y1="7" x2="12.5" y2="7" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/><line x1="2" y1="11" x2="8" y2="11" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>,
      dashboard: <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 11.5V8.5M5 11.5V5M8 11.5V7M11 11.5V3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><line x1="1" y1="12.5" x2="13" y2="12.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>,
    };

    if (loading) return (
      <div style={{display:'flex',alignItems:'center',justifyContent:'center',height:300,color:'#8a93a3',fontSize:14}}>
        ⏳ 從 Firebase 載入中...
      </div>
    );

    return (
      <div style={{display:'flex', flexDirection:'column', flex:1, minHeight:0}}>
        <div className="shell-top">
          <nav className="shell-tabs" role="tablist">
            {TABS.map(t => (
              <button key={t.key} role="tab" aria-selected={tab===t.key} className="shell-tab" onClick={() => setTab(t.key)}>
                <span className="shell-tab-icon">{TAB_ICONS[t.key]}</span>{t.label}
              </button>
            ))}
          </nav>
          <div className="shell-spacer"/>
          <div className="shell-aux">WORK BOARD</div>
          {canEdit && (
            <button className="btn-add" style={{marginRight:8}}
              onClick={() => { setEditO(null); setModal(true); }}>
              + 新增訂單
            </button>
          )}
        </div>
        <div className="shell-body" style={{flex:1, minHeight:0}}>
          {tab==='table'     && <window.TableView     data={data} setData={proxySetData}/>}
          {tab==='kanban'    && <window.KanbanView    data={data} setData={proxySetData}/>}
          {tab==='gantt'     && <window.GanttView     data={data}/>}
          {tab==='dashboard' && <window.DashboardView data={data}/>}
        </div>
        {modal && (
          <OrderModal
            order={editO}
            onClose={() => setModal(false)}
            onSave={async form => { await handleSave(form); setModal(false); }}
          />
        )}
      </div>
    );
  }

  // 掛到全域供 index.html 呼叫
  window.WorkBoardApp = WorkBoardApp;
})();
