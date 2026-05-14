/* 主外殼 — 4 個分頁:總表 / 看板 / 時間軸 / Dashboard */
const { useState, useEffect } = React;
const TableView = window.TableView;
const KanbanView = window.KanbanView;
const GanttView = window.GanttView;
const DashboardView = window.DashboardView;

const TABS = [
  {
    key: 'table',
    label: '總表',
    icon: (
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <rect x="1.5" y="2" width="11" height="10" rx="1.2" stroke="currentColor" strokeWidth="1.3"/>
        <line x1="1.5" y1="5.5" x2="12.5" y2="5.5" stroke="currentColor" strokeWidth="1.3"/>
        <line x1="5" y1="2" x2="5" y2="12" stroke="currentColor" strokeWidth="1.3"/>
      </svg>
    ),
  },
  {
    key: 'kanban',
    label: '看板',
    icon: (
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <rect x="1.5" y="2" width="3" height="10" rx="0.8" stroke="currentColor" strokeWidth="1.3"/>
        <rect x="5.5" y="2" width="3" height="6.5" rx="0.8" stroke="currentColor" strokeWidth="1.3"/>
        <rect x="9.5" y="2" width="3" height="8.5" rx="0.8" stroke="currentColor" strokeWidth="1.3"/>
      </svg>
    ),
  },
  {
    key: 'gantt',
    label: '時間軸',
    icon: (
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <line x1="1.5" y1="3" x2="9.5" y2="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        <line x1="4" y1="7" x2="12.5" y2="7" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        <line x1="2" y1="11" x2="8" y2="11" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
      </svg>
    ),
  },
  {
    key: 'dashboard',
    label: 'Dashboard',
    icon: (
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M2 11.5V8.5M5 11.5V5M8 11.5V7M11 11.5V3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        <line x1="1" y1="12.5" x2="13" y2="12.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
      </svg>
    ),
  },
];

function Shell() {
  const K = window.K;
  const [data, setData] = useState(window.KANBAN_DATA);
  const [tab, setTab] = useState('table');

  // 從 hash 還原(可分享連結)
  useEffect(() => {
    const fromHash = (window.location.hash || '').replace('#', '');
    if (fromHash && TABS.some(t => t.key === fromHash)) setTab(fromHash);
  }, []);
  useEffect(() => {
    window.location.hash = tab;
  }, [tab]);

  function counts(key) {
    if (key === 'table') return data.length;
    if (key === 'kanban') return data.length;
    if (key === 'gantt') return data.filter(d => d.dueDate).length;
    if (key === 'dashboard') return null;
    return null;
  }

  return (
    <div className="shell">
      <div className="shell-top">
        <div className="shell-brand">
          <div className="shell-brand-mark"/>
          <div>
            <div className="shell-brand-title">工作看板</div>
            <div className="shell-brand-sub">3D PRINT · WORK BOARD</div>
          </div>
        </div>

        <nav className="shell-tabs" role="tablist">
          {TABS.map(t => {
            const c = counts(t.key);
            return (
              <button key={t.key}
                role="tab"
                aria-selected={tab === t.key}
                className="shell-tab"
                onClick={() => setTab(t.key)}>
                <span className="shell-tab-icon">{t.icon}</span>
                {t.label}
                {c !== null && <span className="shell-tab-num">{c}</span>}
              </button>
            );
          })}
        </nav>

        <div className="shell-spacer"/>
        <div className="shell-aux">
          {K.fmtYmd(K.TODAY)} · 即時資料
        </div>
      </div>

      <div className="shell-body">
        {tab === 'table'     && <TableView data={data} setData={setData}/>}
        {tab === 'kanban'    && <KanbanView data={data} setData={setData}/>}
        {tab === 'gantt'     && <GanttView data={data}/>}
        {tab === 'dashboard' && <DashboardView data={data}/>}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<Shell/>);
