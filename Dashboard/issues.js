
// issues.js
// 異常與資源：客戶異常 / IPA採購 / 設備清單 / 分析
// + Firebase CRUD + 各種 Modal
// 依賴：React, firebase-service.js, helpers.js, 原始 view-dashboard.jsx（IssuesStats）

(function () {
  const { useState, useEffect } = React;
  const K = window.K;

  const S_INP = { width:'100%', padding:'8px 11px', border:'1.5px solid #e6e8ec', borderRadius:6, fontSize:13, fontFamily:'inherit', outline:'none' };
  const LBL   = { display:'block', fontSize:11.5, fontWeight:600, color:'#5a6270', marginBottom:5 };

  // ── 異常 Modal ──
  function AnomalyModal({ item, onClose, onSave }) {
    const empty = { customer:'', date:'', product:'', engineer: K.ENG_ORDER[0], status:'處理中', progresses:[] };
    const [form, setForm] = useState(item ? { ...item, progresses: [...(item.progresses||[])].map(p=>({...p})) } : empty);
    const [busy, setBusy] = useState(false);
    const [note, setNote] = useState('');
    const set = (k,v) => setForm(f => ({ ...f, [k]:v }));
    const addNote = () => {
      if (!note.trim()) return;
      set('progresses', [...form.progresses, { date: new Date().toISOString().split('T')[0], status: note.trim() }]);
      setNote('');
    };
    const save = async () => {
      if (!form.customer || !form.product) { showToast('請填客戶與品名','err'); return; }
      setBusy(true);
      try { await onSave(form); onClose(); }
      catch(e) { showToast(e.message||'失敗','err'); }
      finally { setBusy(false); }
    };
    return (
      <div className="m-overlay" onClick={e=>e.target===e.currentTarget&&onClose()}>
        <div className="m-box">
          <div className="m-hd"><h3>{item?'✏️ 編輯異常':'➕ 新增異常'}</h3><button className="m-close" onClick={onClose}>×</button></div>
          <div className="m-body">
            <div className="m-row">
              <div className="m-field"><label style={LBL}>客戶 *</label><input style={S_INP} value={form.customer} onChange={e=>set('customer',e.target.value)}/></div>
              <div className="m-field"><label style={LBL}>異常日期</label><input style={S_INP} type="date" value={form.date||''} onChange={e=>set('date',e.target.value)}/></div>
            </div>
            <div className="m-row">
              <div className="m-field"><label style={LBL}>品名 *</label><input style={S_INP} value={form.product} onChange={e=>set('product',e.target.value)}/></div>
              <div className="m-field"><label style={LBL}>工程師</label>
                <select style={S_INP} value={form.engineer} onChange={e=>set('engineer',e.target.value)}>
                  {K.ENG_ORDER.map(e=><option key={e} value={e}>{K.ENG_LABEL[e]||e}</option>)}</select></div>
            </div>
            <div className="m-field"><label style={LBL}>狀態</label>
              <select style={S_INP} value={form.status} onChange={e=>set('status',e.target.value)}>
                <option>處理中</option><option>已完成</option><option>暫停</option></select></div>
            <div className="m-field">
              <label style={LBL}>後續進度</label>
              <div style={{background:'#fafbfc',border:'1px solid #e6e8ec',borderRadius:6,padding:10,marginBottom:8,minHeight:44}}>
                {form.progresses.map((p,i)=>(
                  <div key={i} style={{display:'flex',gap:8,marginBottom:4,fontSize:12,alignItems:'flex-start'}}>
                    <span style={{color:'#8a93a3',whiteSpace:'nowrap',minWidth:80}}>{p.date}</span>
                    <span style={{flex:1}}>{p.status}</span>
                    <button onClick={()=>set('progresses',form.progresses.filter((_,j)=>j!==i))} style={{background:'none',border:'none',color:'#c0392b',cursor:'pointer',fontSize:14,lineHeight:1}}>×</button>
                  </div>
                ))}
                {!form.progresses.length && <div style={{fontSize:12,color:'#8a93a3'}}>尚無進度</div>}
              </div>
              <div style={{display:'flex',gap:6}}>
                <input style={{...S_INP,flex:1}} placeholder="輸入進度說明後按 Enter" value={note} onChange={e=>setNote(e.target.value)} onKeyDown={e=>e.key==='Enter'&&addNote()}/>
                <button className="btn-cancel" style={{padding:'0 12px'}} onClick={addNote}>+</button>
              </div>
            </div>
          </div>
          <div className="m-foot"><button className="btn-cancel" onClick={onClose}>取消</button><button className="btn-save" onClick={save} disabled={busy}>{busy?'儲存中...':'💾 儲存'}</button></div>
        </div>
      </div>
    );
  }

  // ── IPA Modal ──
  function IPAModal({ item, onClose, onSave }) {
    const empty = { purchaseDate:'', useDate:'', product:'20L-IPA 異丙醇', quantity:1, person: K.ENG_ORDER[0], remark:'' };
    const [form, setForm] = useState(item?{...item}:empty);
    const [busy, setBusy] = useState(false);
    const set = (k,v) => setForm(f=>({...f,[k]:v}));
    const save = async () => {
      if (!form.purchaseDate) { showToast('請填採購日期','err'); return; }
      setBusy(true);
      try { await onSave(form); onClose(); }
      catch(e) { showToast(e.message||'失敗','err'); }
      finally { setBusy(false); }
    };
    return (
      <div className="m-overlay" onClick={e=>e.target===e.currentTarget&&onClose()}>
        <div className="m-box" style={{width:560}}>
          <div className="m-hd"><h3>{item?'✏️ 編輯採購':'➕ 新增採購'}</h3><button className="m-close" onClick={onClose}>×</button></div>
          <div className="m-body">
            <div className="m-row">
              <div className="m-field"><label style={LBL}>採購日期 *</label><input style={S_INP} type="date" value={form.purchaseDate||''} onChange={e=>set('purchaseDate',e.target.value)}/></div>
              <div className="m-field"><label style={LBL}>採購人員</label>
                <select style={S_INP} value={form.person} onChange={e=>set('person',e.target.value)}>
                  {K.ENG_ORDER.map(e=><option key={e} value={e}>{K.ENG_LABEL[e]||e}</option>)}</select></div>
            </div>
            <div className="m-row">
              <div className="m-field"><label style={LBL}>品名</label><input style={S_INP} value={form.product} onChange={e=>set('product',e.target.value)}/></div>
              <div className="m-field"><label style={LBL}>數量 (桶)</label><input style={S_INP} type="number" min={1} value={form.quantity} onChange={e=>set('quantity',+e.target.value)}/></div>
            </div>
            <div className="m-field"><label style={LBL}>使用區間</label><input style={S_INP} value={form.useDate||''} onChange={e=>set('useDate',e.target.value)} placeholder="2026-01-08 ~ 02-04"/></div>
            <div className="m-field"><label style={LBL}>備註</label><textarea style={{...S_INP,resize:'vertical'}} value={form.remark||''} onChange={e=>set('remark',e.target.value)} rows={2}/></div>
          </div>
          <div className="m-foot"><button className="btn-cancel" onClick={onClose}>取消</button><button className="btn-save" onClick={save} disabled={busy}>{busy?'儲存中...':'💾 儲存'}</button></div>
        </div>
      </div>
    );
  }

  // ── 設備 Modal ──
  function EquipModal({ item, onClose, onSave }) {
    const empty = { purchaseDate:'', product:'', quantity:1, method:'Easy Flow', number:'', remark:'', price:0 };
    const [form, setForm] = useState(item?{...item}:empty);
    const [busy, setBusy] = useState(false);
    const set = (k,v) => setForm(f=>({...f,[k]:v}));
    const save = async () => {
      if (!form.product) { showToast('請填品名','err'); return; }
      setBusy(true);
      try { await onSave(form); onClose(); }
      catch(e) { showToast(e.message||'失敗','err'); }
      finally { setBusy(false); }
    };
    return (
      <div className="m-overlay" onClick={e=>e.target===e.currentTarget&&onClose()}>
        <div className="m-box" style={{width:560}}>
          <div className="m-hd"><h3>{item?'✏️ 編輯設備':'➕ 新增設備'}</h3><button className="m-close" onClick={onClose}>×</button></div>
          <div className="m-body">
            <div className="m-row">
              <div className="m-field"><label style={LBL}>品名 *</label><input style={S_INP} value={form.product} onChange={e=>set('product',e.target.value)}/></div>
              <div className="m-field"><label style={LBL}>採購日期</label><input style={S_INP} type="date" value={form.purchaseDate||''} onChange={e=>set('purchaseDate',e.target.value)}/></div>
            </div>
            <div className="m-row">
              <div className="m-field"><label style={LBL}>數量</label><input style={S_INP} type="number" min={1} value={form.quantity} onChange={e=>set('quantity',+e.target.value)}/></div>
              <div className="m-field"><label style={LBL}>採購方式</label>
                <select style={S_INP} value={form.method} onChange={e=>set('method',e.target.value)}>
                  <option>Easy Flow</option><option>零用金</option><option>其他</option></select></div>
            </div>
            <div className="m-row">
              <div className="m-field"><label style={LBL}>單號</label><input style={S_INP} value={form.number||''} onChange={e=>set('number',e.target.value)}/></div>
              <div className="m-field"><label style={LBL}>金額 (NT$)</label><input style={S_INP} type="number" min={0} value={form.price||0} onChange={e=>set('price',+e.target.value)}/></div>
            </div>
            <div className="m-field"><label style={LBL}>備註 (用途)</label><textarea style={{...S_INP,resize:'vertical'}} value={form.remark||''} onChange={e=>set('remark',e.target.value)} rows={2}/></div>
          </div>
          <div className="m-foot"><button className="btn-cancel" onClick={onClose}>取消</button><button className="btn-save" onClick={save} disabled={busy}>{busy?'儲存中...':'💾 儲存'}</button></div>
        </div>
      </div>
    );
  }

  // ── IssuesApp 主元件 ──
  function IssuesApp({ user }) {
    const [anomalies,  setAnomalies]  = useState([]);
    const [ipa,        setIpa]        = useState([]);
    const [equipment,  setEquipment]  = useState([]);
    const [loading,    setLoading]    = useState(true);
    const [sub,        setSub]        = useState('anomaly');
    const [modal,      setModal]      = useState(null);
    const [editItem,   setEditItem]   = useState(null);
    const [search1,    setSearch1]    = useState('');
    const [statusF,    setStatusF]    = useState('');
    const [engF,       setEngF]       = useState('');
    const [search2,    setSearch2]    = useState('');
    const [personF,    setPersonF]    = useState('');
    const [search3,    setSearch3]    = useState('');
    const [methodF,    setMethodF]    = useState('');

    const canE = window.hasPerm(user, 'edit_issues');
    const canD = window.hasPerm(user, 'delete_issues');

    useEffect(() => {
      let n = 0;
      const chk = () => { if (++n >= 3) setLoading(false); };
      const u1 = FBAnomalies.onSnapshot(r => { setAnomalies(r); chk(); });
      const u2 = FBIPA.onSnapshot(      r => { setIpa(r);       chk(); });
      const u3 = FBEquipment.onSnapshot(r => { setEquipment(r); chk(); });
      return () => { u1(); u2(); u3(); };
    }, []);

    const nextSeq = arr => arr.length ? Math.max(...arr.map(d => d.seq||0)) + 1 : 1;

    const saveA = async f => { if(editItem){await FBAnomalies.update(editItem._id,f);showToast('已更新 ✓');}else{await FBAnomalies.add({...f,seq:nextSeq(anomalies)});showToast('已新增 ✓');}setModal(null); };
    const delA  = async it => { if(!confirm('刪除？'))return; await FBAnomalies.del(it._id); showToast('已刪除','inf'); };
    const saveI = async f => { if(editItem){await FBIPA.update(editItem._id,f);showToast('已更新 ✓');}else{await FBIPA.add({...f,seq:nextSeq(ipa)});showToast('已新增 ✓');}setModal(null); };
    const delI  = async it => { if(!confirm('刪除？'))return; await FBIPA.del(it._id); showToast('已刪除','inf'); };
    const saveE = async f => { if(editItem){await FBEquipment.update(editItem._id,f);showToast('已更新 ✓');}else{await FBEquipment.add({...f,seq:nextSeq(equipment)});showToast('已新增 ✓');}setModal(null); };
    const delE  = async it => { if(!confirm('刪除？'))return; await FBEquipment.del(it._id); showToast('已刪除','inf'); };

    const filtA = anomalies.filter(it => {
      const s = search1.toLowerCase();
      if (s && !it.customer.toLowerCase().includes(s) && !it.product.toLowerCase().includes(s)) return false;
      if (statusF && it.status !== statusF) return false;
      if (engF && it.engineer !== engF) return false;
      return true;
    });
    const filtI = ipa.filter(it => {
      if (search2 && !it.product.toLowerCase().includes(search2.toLowerCase())) return false;
      if (personF && it.person !== personF) return false;
      return true;
    });
    const filtT = equipment.filter(it => {
      if (search3 && !it.product.toLowerCase().includes(search3.toLowerCase())) return false;
      if (methodF && it.method !== methodF) return false;
      return true;
    });

    const pillCls = st => st==='已完成'?'kt-pill kt-pill-完成':st==='處理中'?'kt-pill kt-pill-處理':'kt-pill kt-pill-暫停';
    const SUBTABS = [
      {key:'anomaly',label:'客戶異常', count:anomalies.length},
      {key:'ipa',    label:'IPA 採購',count:ipa.length},
      {key:'tools',  label:'設備清單',count:equipment.length},
      {key:'stats',  label:'分析',    count:null},
    ];

    if (loading) return (
      <div style={{display:'flex',alignItems:'center',justifyContent:'center',height:300,color:'#8a93a3',fontSize:14}}>
        ⏳ 從 Firebase 載入中...
      </div>
    );

    return (
      <div style={{display:'flex',flexDirection:'column',flex:1,minHeight:0}}>
        <div className="shell-top">
          <nav className="shell-tabs" role="tablist">
            <button role="tab" aria-selected={true} className="shell-tab" style={{fontWeight:600,color:'#0a0e14'}}>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style={{marginRight:6}}><circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.3"/><line x1="7" y1="4.2" x2="7" y2="7.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/><circle cx="7" cy="9.6" r="0.7" fill="currentColor"/></svg>
              異常與資源
            </button>
          </nav>
          <div className="shell-spacer"/>
          <div className="shell-aux">ISSUES · RESOURCES</div>
        </div>
        <div className="shell-body" style={{flex:1,minHeight:0,overflowY:'auto'}}>
          <div className="table-view">
            <div className="toolbar">
              <div className="toolbar-title">工作異常與資源</div>
              <span className="toolbar-sub">客戶異常 · IPA 採購 · 設備清單 · 統計分析</span>
              <div className="issues-subtabs" role="tablist">
                {SUBTABS.map(t=>(
                  <button key={t.key} role="tab" aria-selected={sub===t.key} className="issues-subtab" onClick={()=>setSub(t.key)}>
                    {t.label}{t.count!==null&&<span className="issues-subtab-count">{t.count}</span>}
                  </button>
                ))}
              </div>
            </div>

            {sub==='anomaly'&&<>
              <div className="toolbar" style={{borderTop:'1px solid var(--line-soft)',paddingTop:10,paddingBottom:10}}>
                <div className="t-search" style={{marginRight:'auto'}}><svg width="14" height="14" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/><path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg><input value={search1} onChange={e=>setSearch1(e.target.value)} placeholder="搜尋客戶 / 品名"/></div>
                <select className="t-sel" value={statusF} onChange={e=>setStatusF(e.target.value)}><option value="">所有狀態</option><option>處理中</option><option>已完成</option><option>暫停</option></select>
                <select className="t-sel" value={engF} onChange={e=>setEngF(e.target.value)}><option value="">所有工程師</option>{K.ENG_ORDER.map(k=><option key={k} value={k}>{K.ENG_LABEL[k]}</option>)}</select>
                {canE&&<button className="t-btn t-btn-primary" onClick={()=>{setEditItem(null);setModal('a');}}>+ 新增異常</button>}
              </div>
              <div className="table-wrap"><table className="kt"><thead><tr>
                <th className="col-seq">序</th><th>客戶</th><th>異常日期</th><th>品名</th><th>工程師</th><th>狀態</th><th>進度日期</th><th>進度狀況</th><th className="col-actions">操作</th>
              </tr></thead><tbody>
                {filtA.map(it=>{
                  const tone=K.ENG_TONE[it.engineer]||{fg:'#5a6270',bg:'#eef0f3'};
                  const first=(it.progresses||[])[0]||{date:'—',status:'—'};
                  const rest=(it.progresses||[]).slice(1);
                  return (<React.Fragment key={it._id}>
                    <tr>
                      <td className="col-seq">{it.seq}</td><td className="col-customer">{it.customer}</td><td className="col-date">{it.date}</td><td>{it.product}</td>
                      <td><span className="kt-eng"><span className="kt-eng-dot" style={{color:tone.fg,background:tone.bg}}>{K.ENG_INIT[it.engineer]||it.engineer.slice(0,2)}</span>{K.ENG_LABEL[it.engineer]||it.engineer}</span></td>
                      <td><span className={pillCls(it.status)}>{it.status}</span></td>
                      <td className="col-date">{first.date}</td><td>{first.status}</td>
                      <td className="col-actions"><span className="kt-act">
                        {canE&&<button className="kt-actbtn" title="編輯" onClick={()=>{setEditItem(it);setModal('a');}}>✎</button>}
                        {canD&&<button className="kt-actbtn danger" title="刪除" onClick={()=>delA(it)}>✕</button>}
                      </span></td>
                    </tr>
                    {rest.map((p,i)=><tr key={i} className="kt-anomaly-sub"><td colSpan="6"><span className="kt-anomaly-sub-marker">↳ 後續 #{i+2}</span></td><td className="col-date">{p.date}</td><td>{p.status}</td><td></td></tr>)}
                  </React.Fragment>);
                })}
                {!filtA.length&&<tr><td colSpan="9"><div className="kt-empty">無異常紀錄</div></td></tr>}
              </tbody></table></div>
            </>}

            {sub==='ipa'&&<>
              <div className="toolbar" style={{borderTop:'1px solid var(--line-soft)',paddingTop:10,paddingBottom:10}}>
                <div className="t-search" style={{marginRight:'auto'}}><svg width="14" height="14" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/><path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg><input value={search2} onChange={e=>setSearch2(e.target.value)} placeholder="搜尋品名"/></div>
                <span className="toolbar-sub">合計 <b style={{color:'#0a0e14'}}>{filtI.reduce((s,r)=>s+Number(r.quantity||0),0)}</b> 桶</span>
                <select className="t-sel" value={personF} onChange={e=>setPersonF(e.target.value)}><option value="">所有人員</option>{K.ENG_ORDER.map(k=><option key={k} value={k}>{K.ENG_LABEL[k]}</option>)}</select>
                {canE&&<button className="t-btn t-btn-primary" onClick={()=>{setEditItem(null);setModal('i');}}>+ 新增採購</button>}
              </div>
              <div className="table-wrap"><table className="kt"><thead><tr>
                <th className="col-seq">序</th><th>採購日期</th><th>使用區間</th><th>品名</th><th>數量</th><th>採購人員</th><th>備註</th><th className="col-actions">操作</th>
              </tr></thead><tbody>
                {filtI.map(it=>{
                  const tone=K.ENG_TONE[it.person]||{fg:'#5a6270',bg:'#eef0f3'};
                  return (<tr key={it._id}>
                    <td className="col-seq">{it.seq}</td><td className="col-date">{it.purchaseDate}</td><td className="col-date">{it.useDate}</td><td>{it.product}</td>
                    <td><span className="kt-num-badge">{it.quantity} 桶</span></td>
                    <td><span className="kt-eng"><span className="kt-eng-dot" style={{color:tone.fg,background:tone.bg}}>{K.ENG_INIT[it.person]||it.person.slice(0,2)}</span>{K.ENG_LABEL[it.person]||it.person}</span></td>
                    <td style={{color:'#5a6270'}}>{it.remark||'—'}</td>
                    <td className="col-actions"><span className="kt-act">
                      {canE&&<button className="kt-actbtn" onClick={()=>{setEditItem(it);setModal('i');}}>✎</button>}
                      {canD&&<button className="kt-actbtn danger" onClick={()=>delI(it)}>✕</button>}
                    </span></td>
                  </tr>);
                })}
                {!filtI.length&&<tr><td colSpan="8"><div className="kt-empty">無採購紀錄</div></td></tr>}
              </tbody></table></div>
            </>}

            {sub==='tools'&&<>
              <div className="toolbar" style={{borderTop:'1px solid var(--line-soft)',paddingTop:10,paddingBottom:10}}>
                <div className="t-search" style={{marginRight:'auto'}}><svg width="14" height="14" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/><path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg><input value={search3} onChange={e=>setSearch3(e.target.value)} placeholder="搜尋品名 / 用途"/></div>
                <span className="toolbar-sub">合計 <b style={{color:'#0a0e14'}}>NT$ {filtT.reduce((s,r)=>s+(Number(r.price||0)*Number(r.quantity||1)),0).toLocaleString()}</b></span>
                <select className="t-sel" value={methodF} onChange={e=>setMethodF(e.target.value)}><option value="">所有方式</option><option>Easy Flow</option><option>零用金</option></select>
                {canE&&<button className="t-btn t-btn-primary" onClick={()=>{setEditItem(null);setModal('e');}}>+ 新增設備</button>}
              </div>
              <div className="table-wrap"><table className="kt"><thead><tr>
                <th className="col-seq">序</th><th>採購日期</th><th>品名</th><th>數量</th><th>採購方式</th><th>單號</th><th>備註</th><th style={{textAlign:'right'}}>金額</th><th className="col-actions">操作</th>
              </tr></thead><tbody>
                {filtT.map(it=>(<tr key={it._id}>
                  <td className="col-seq">{it.seq}</td><td className="col-date">{it.purchaseDate||'—'}</td><td>{it.product}</td>
                  <td><span className="kt-num-badge">{it.quantity}</span></td><td>{it.method}</td><td className="col-id">{it.number||'—'}</td>
                  <td style={{color:'#5a6270'}}>{it.remark||'—'}</td>
                  <td className="kt-money">NT$ {(Number(it.price||0)*Number(it.quantity||1)).toLocaleString()}</td>
                  <td className="col-actions"><span className="kt-act">
                    {canE&&<button className="kt-actbtn" onClick={()=>{setEditItem(it);setModal('e');}}>✎</button>}
                    {canD&&<button className="kt-actbtn danger" onClick={()=>delE(it)}>✕</button>}
                  </span></td>
                </tr>))}
                {!filtT.length&&<tr><td colSpan="9"><div className="kt-empty">無設備</div></td></tr>}
              </tbody></table></div>
            </>}

            {sub==='stats'&&<window.IssuesStats anomalies={anomalies} ipa={ipa} tools={equipment}/>}

            {modal==='a'&&<AnomalyModal item={editItem} onClose={()=>setModal(null)} onSave={saveA}/>}
            {modal==='i'&&<IPAModal     item={editItem} onClose={()=>setModal(null)} onSave={saveI}/>}
            {modal==='e'&&<EquipModal   item={editItem} onClose={()=>setModal(null)} onSave={saveE}/>}
          </div>
        </div>
      </div>
    );
  }

  window.IssuesApp = IssuesApp;
})();
