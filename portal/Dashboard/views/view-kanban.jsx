/* 看板 view — 經典卡片欄 */
const { useState: useStateK, useMemo: useMemoK } = React;

function KanbanView({ data, setData }) {
  const K = window.K;
  const [search, setSearch] = useStateK('');
  const [engF, setEngF] = useStateK('');
  const [machF, setMachF] = useStateK('');
  const [groupBy, setGroupBy] = useStateK('status');
  const [density, setDensity] = useStateK('comfortable');
  const [showCancelled, setShowCancelled] = useStateK(true);
  const [open, setOpen] = useStateK(null);
  const [dragItem, setDragItem] = useStateK(null);

  // -- 欄位定義 --
  const STATUS_COLUMNS = [
    { key: 'todo',     title: '待開始',  hint: '0%, 尚未排程',         tone: '#5a6270' },
    { key: 'blocked',  title: '等待材料', hint: '需調撥 / 待客戶',      tone: '#c79b2a' },
    { key: 'progress', title: '進行中',  hint: '已排程, 列印中',       tone: '#0c7a99' },
    { key: 'done',     title: '已完成',  hint: '100% / 出貨',          tone: '#1d6f43' },
    { key: 'cancelled',title: '已取消',  hint: '備註含「取消」',       tone: '#9aa3b2' },
  ];
  const PROGRESS_COLUMNS = [
    { key: '0',   title: '0%',   hint: '尚未開始', tone: '#9aa3b2' },
    { key: '25',  title: '25%',  hint: '備料/起印', tone: '#c79b2a' },
    { key: '50',  title: '50%',  hint: '列印中',    tone: '#c79b2a' },
    { key: '75',  title: '75%',  hint: '後處理',    tone: '#0c7a99' },
    { key: '100', title: '100%', hint: '完成',     tone: '#1d6f43' },
  ];
  const ENGINEER_COLUMNS = K.ENG_ORDER.map(k => ({
    key: k, title: K.ENG_LABEL[k], hint: k, tone: K.ENG_TONE[k].fg,
  }));
  const MACHINE_COLUMNS = K.MACHINES.map(k => ({
    key: k, title: k, hint: '機台', tone: '#0c7a99',
  }));

  function columnKeyFor(item) {
    if (groupBy === 'status')   return K.statusOf(item);
    if (groupBy === 'progress') return String(item.progress);
    if (groupBy === 'engineer') return item.engineer;
    if (groupBy === 'machine')  return item.machine || '—';
    return K.statusOf(item);
  }
  let cols =
    groupBy === 'status'   ? STATUS_COLUMNS :
    groupBy === 'progress' ? PROGRESS_COLUMNS :
    groupBy === 'engineer' ? ENGINEER_COLUMNS :
    MACHINE_COLUMNS;
  if (groupBy === 'status' && !showCancelled) {
    cols = cols.filter(c => c.key !== 'cancelled');
  }

  // -- 過濾 / 分組 --
  const filtered = useMemoK(() => K.applyFilters(data, { search, engineer: engF, machine: machF }),
    [data, search, engF, machF]);

  const grouped = useMemoK(() => {
    const m = {}; cols.forEach(c => { m[c.key] = []; });
    filtered.forEach(it => {
      const k = columnKeyFor(it);
      if (m[k]) m[k].push(it);
    });
    return m;
  }, [filtered, cols, groupBy]);

  // -- KPI --
  const stats = {
    total: data.length,
    wip: data.filter(d => K.statusOf(d) === 'progress').length,
    blocked: data.filter(d => K.statusOf(d) === 'blocked').length,
    due7: data.filter(d => {
      const s = K.statusOf(d);
      if (s === 'done' || s === 'cancelled') return false;
      const du = K.daysUntil(d.dueDate);
      return du !== null && du <= 7;
    }).length,
    done: data.filter(d => K.statusOf(d) === 'done').length,
  };

  function handleDrop(colKey) {
    if (!dragItem) return;
    setData(prev => prev.map(d => {
      if (d.seq !== dragItem.seq) return d;
      const u = { ...d };
      if (groupBy === 'status') {
        if (colKey === 'done')         { u.progress = 100; u.complete = '是'; u.remark = u.remark.replace('已取消', '').trim(); }
        else if (colKey === 'todo')    { u.progress = 0;   u.complete = '否'; u.remark = u.remark.replace('已取消', '').trim(); }
        else if (colKey === 'progress'){ if (u.progress === 0 || u.progress === 100) u.progress = 50; u.complete = '否'; u.remark = u.remark.replace('已取消', '').trim(); }
        else if (colKey === 'blocked') { u.material = '需調撥'; u.complete = '否'; }
        else if (colKey === 'cancelled'){ u.remark = u.remark ? `${u.remark} · 已取消` : '已取消'; }
      } else if (groupBy === 'progress') {
        u.progress = parseInt(colKey, 10);
        u.complete = u.progress === 100 ? '是' : '否';
      } else if (groupBy === 'engineer') {
        u.engineer = colKey;
      } else if (groupBy === 'machine') {
        u.machine = colKey;
      }
      return u;
    }));
    setDragItem(null);
  }

  function updateItem(updated) {
    setData(prev => prev.map(d => d.seq === updated.seq ? updated : d));
    setOpen(updated);
  }

  function Avatar({ engineer }) {
    const tone = K.ENG_TONE[engineer] || { fg: '#5a6270', bg: '#eef0f3' };
    return (
      <span className="avatar"
        style={{ color: tone.fg, background: tone.bg }}
        title={K.ENG_LABEL[engineer] || engineer}>
        {K.ENG_INIT[engineer] || engineer.slice(0, 2)}
      </span>
    );
  }

  function DueChip({ dateStr, isDone }) {
    if (!dateStr) return <span className="chip chip-muted">未訂期</span>;
    const d = K.daysUntil(dateStr);
    if (isDone) return <span className="chip chip-muted">{dateStr.slice(5)}</span>;
    let cls = 'chip', label = dateStr.slice(5);
    if (d < 0)        { cls += ' chip-red';    label = `逾期 ${-d}d`; }
    else if (d <= 3)  { cls += ' chip-red';    label = `${dateStr.slice(5)} · ${d}d`; }
    else if (d <= 7)  { cls += ' chip-amber';  label = `${dateStr.slice(5)} · ${d}d`; }
    else              { cls += ' chip-muted';  label = `${dateStr.slice(5)} · ${d}d`; }
    return <span className={cls}>{label}</span>;
  }

  function Card({ item }) {
    const st = K.statusOf(item);
    const done = st === 'done';
    const cancelled = st === 'cancelled';
    return (
      <div
        className={`card ${density === 'compact' ? 'card-compact' : ''} ${dragItem && dragItem.seq === item.seq ? 'card-dragging' : ''} ${cancelled ? 'card-cancelled' : ''}`}
        draggable
        onDragStart={() => setDragItem(item)}
        onDragEnd={() => setDragItem(null)}
        onClick={() => setOpen(item)}
      >
        <div className="card-top">
          <span className="card-id">EF · {item.id.slice(-7)}</span>
          <div className="card-top-right">
            {item.material === '需調撥' && <span className="dot dot-amber" title="需調撥材料"></span>}
            <Avatar engineer={item.engineer}/>
          </div>
        </div>
        <div className="card-title">{item.customer}</div>
        {density !== 'compact' && (
          <div className="card-meta">
            <span className="meta-machine">{item.machine || '未指派機台'}</span>
            {item.remark && <span className="meta-remark" title={item.remark}>· {item.remark}</span>}
          </div>
        )}
        <div className="card-progress">
          <div className="progress-track">
            <div className="progress-fill" style={{
              width: `${item.progress}%`,
              background: done ? '#1d6f43' : cancelled ? '#cbd0d8' : '#0c7a99',
            }}/>
          </div>
          <span className="progress-num">{item.progress}%</span>
        </div>
        <div className="card-foot">
          <DueChip dateStr={item.dueDate} isDone={done}/>
          <span className="seq-num">#{String(item.seq).padStart(3, '0')}</span>
        </div>
      </div>
    );
  }

  function Column({ col, items }) {
    const [over, setOver] = useStateK(false);
    return (
      <div
        className={`col ${over ? 'col-over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={() => { setOver(false); handleDrop(col.key); }}
      >
        <div className="col-head">
          <div className="col-head-left">
            <span className="col-dot" style={{ background: col.tone }}/>
            <span className="col-title">{col.title}</span>
            <span className="col-count">{items.length}</span>
          </div>
          <span className="col-hint">{col.hint}</span>
        </div>
        <div className="col-body">
          {items.map(it => <Card key={it.seq} item={it}/>)}
          {items.length === 0 && <div className="col-empty">—</div>}
        </div>
      </div>
    );
  }

  function Drawer() {
    if (!open) return null;
    const st = K.statusOf(open);
    return (
      <div className="drawer-wrap" onClick={() => setOpen(null)}>
        <aside className="drawer" onClick={e => e.stopPropagation()}>
          <header className="drawer-head">
            <div>
              <div className="drawer-eyebrow">EF 訂單詳情</div>
              <div className="drawer-id">{open.id}</div>
            </div>
            <button className="icon-btn" onClick={() => setOpen(null)}>×</button>
          </header>
          <div className="drawer-customer">{open.customer}</div>
          <div className="drawer-row">
            <div className="drawer-field">
              <div className="field-label">執行工程師</div>
              <div className="field-value">
                <Avatar engineer={open.engineer}/>
                <span style={{ marginLeft: 8 }}>{K.ENG_LABEL[open.engineer]}</span>
              </div>
            </div>
            <div className="drawer-field">
              <div className="field-label">機台</div>
              <div className="field-value">{open.machine || '—'}</div>
            </div>
          </div>
          <div className="drawer-row">
            <div className="drawer-field">
              <div className="field-label">期望交期</div>
              <div className="field-value"><DueChip dateStr={open.dueDate} isDone={st === 'done'}/></div>
            </div>
            <div className="drawer-field">
              <div className="field-label">材料</div>
              <div className="field-value">
                <span className={`pill ${open.material === '需調撥' ? 'pill-amber' : 'pill-ok'}`}>
                  {open.material}
                </span>
              </div>
            </div>
          </div>
          <div className="drawer-row">
            <div className="drawer-field">
              <div className="field-label">開始日期</div>
              <div className="field-value mono">{open.startDate || '—'}</div>
            </div>
            <div className="drawer-field">
              <div className="field-label">預計完成</div>
              <div className="field-value mono">{open.endDate || '—'}</div>
            </div>
          </div>
          <div className="drawer-field" style={{ marginTop: 18 }}>
            <div className="field-label">進度</div>
            <div className="progress-controls">
              {[0, 25, 50, 75, 100].map(p => (
                <button key={p}
                  className={`prog-btn ${open.progress === p ? 'prog-btn-active' : ''}`}
                  onClick={() => updateItem({ ...open, progress: p, complete: p === 100 ? '是' : '否' })}>
                  {p}%
                </button>
              ))}
            </div>
          </div>
          <div className="drawer-field" style={{ marginTop: 18 }}>
            <div className="field-label">備註</div>
            <div className="field-value remark-box">{open.remark || '—'}</div>
          </div>
          <footer className="drawer-foot">
            <span>序列 #{String(open.seq).padStart(3, '0')}</span>
            <span>狀態:{K.STATUS_TONE[st].label}</span>
          </footer>
        </aside>
      </div>
    );
  }

  return (
    <div className="kanban-view">
      {/* 工具列 */}
      <div className="toolbar">
        <div className="toolbar-title">看板檢視</div>
        <div className="t-search">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="搜尋 EF / 客戶"/>
        </div>
        <select className="t-sel" value={engF} onChange={e => setEngF(e.target.value)}>
          <option value="">所有工程師</option>
          {K.ENG_ORDER.map(k => <option key={k} value={k}>{K.ENG_LABEL[k]}</option>)}
        </select>
        <select className="t-sel" value={machF} onChange={e => setMachF(e.target.value)}>
          <option value="">所有機台</option>
          {K.MACHINES.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
        <div className="seg">
          {[
            { k: 'status',   label: '狀態' },
            { k: 'progress', label: '進度' },
            { k: 'engineer', label: '工程師' },
            { k: 'machine',  label: '機台' },
          ].map(o => (
            <button key={o.k}
              className={`seg-btn ${groupBy === o.k ? 'seg-btn-active' : ''}`}
              onClick={() => setGroupBy(o.k)}>{o.label}</button>
          ))}
        </div>
      </div>

      {/* KPI */}
      <div className="kpi-strip">
        {[
          { label: '總訂單',     value: stats.total },
          { label: '進行中',     value: stats.wip },
          { label: '等待材料',   value: stats.blocked, sub: '需調撥/待簽回', accent: '#c79b2a' },
          { label: '7 天內到期', value: stats.due7,    sub: '未完成且交期 ≤ 7 天', accent: '#c0392b' },
          { label: '已完成',     value: stats.done,    sub: '100% / 完成', accent: '#1d6f43' },
        ].map((c, i) => (
          <div key={i} className="kpi-cell">
            <div className="kpi-label">{c.label}</div>
            <div className="kpi-value" style={c.accent ? { color: c.accent } : null}>{c.value}</div>
            <div className="kpi-sub">{c.sub || '即時更新'}</div>
          </div>
        ))}
      </div>

      {/* 看板 */}
      <main className="board">
        {cols.map(col => <Column key={col.key} col={col} items={grouped[col.key] || []}/>)}
      </main>

      <footer className="footnote">
        <span>共 {filtered.length} / {data.length} 筆</span>
        <span className="dot-sep"/>
        <span>依「{ {status:'狀態',progress:'進度',engineer:'工程師',machine:'機台'}[groupBy] }」分欄</span>
        <span className="dot-sep"/>
        <span>拖曳卡片可在欄間移動</span>
      </footer>

      <Drawer/>
    </div>
  );
}

window.KanbanView = KanbanView;
