/* 主外殼 — 左側 sidebar(2 個 app) + 頂部 tabs(每 app 自己的 tabs) */
const { useState, useEffect } = React;
const TableView = window.TableView;
const KanbanView = window.KanbanView;
const GanttView = window.GanttView;
const DashboardView = window.DashboardView;
const IssuesView = window.IssuesView;

const APPS = [
  {
    key: 'board',
    label: '工作看板',
    sub: 'WORK BOARD',
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
        <rect x="2" y="3" width="3.5" height="12" rx="1" stroke="currentColor" strokeWidth="1.4"/>
        <rect x="7.25" y="3" width="3.5" height="7.5" rx="1" stroke="currentColor" strokeWidth="1.4"/>
        <rect x="12.5" y="3" width="3.5" height="10" rx="1" stroke="currentColor" strokeWidth="1.4"/>
      </svg>
    ),
    tabs: [
      { key: 'table',     label: '總表' },
      { key: 'kanban',    label: '看板' },
      { key: 'gantt',     label: '時間軸' },
      { key: 'dashboard', label: 'Dashboard' },
    ],
  },
  {
    key: 'issues',
    label: '異常與資源',
    sub: 'ISSUES · RESOURCES',
    icon: (
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
        <path d="M9 2L16 14.5H2L9 2Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round"/>
        <line x1="9" y1="7" x2="9" y2="10.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
        <circle cx="9" cy="12.5" r="0.8" fill="currentColor"/>
      </svg>
    ),
    tabs: [
      { key: 'issues', label: '異常與資源' },
    ],
  },
];

const TAB_ICONS = {
  table: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <rect x="1.5" y="2" width="11" height="10" rx="1.2" stroke="currentColor" strokeWidth="1.3"/>
      <line x1="1.5" y1="5.5" x2="12.5" y2="5.5" stroke="currentColor" strokeWidth="1.3"/>
      <line x1="5" y1="2" x2="5" y2="12" stroke="currentColor" strokeWidth="1.3"/>
    </svg>
  ),
  kanban: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <rect x="1.5" y="2" width="3" height="10" rx="0.8" stroke="currentColor" strokeWidth="1.3"/>
      <rect x="5.5" y="2" width="3" height="6.5" rx="0.8" stroke="currentColor" strokeWidth="1.3"/>
      <rect x="9.5" y="2" width="3" height="8.5" rx="0.8" stroke="currentColor" strokeWidth="1.3"/>
    </svg>
  ),
  gantt: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <line x1="1.5" y1="3" x2="9.5" y2="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
      <line x1="4" y1="7" x2="12.5" y2="7" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
      <line x1="2" y1="11" x2="8" y2="11" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
    </svg>
  ),
  dashboard: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M2 11.5V8.5M5 11.5V5M8 11.5V7M11 11.5V3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="1" y1="12.5" x2="13" y2="12.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
    </svg>
  ),
  issues: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.3"/>
      <line x1="7" y1="4.2" x2="7" y2="7.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      <circle cx="7" cy="9.6" r="0.7" fill="currentColor"/>
    </svg>
  ),
};

function Shell() {
  const K = window.K;
  const [data, setData] = useState(window.KANBAN_DATA);
  const [appKey, setAppKey] = useState('board');
  const [tab, setTab] = useState('table');

  // hash 還原 (#app/tab)
  useEffect(() => {
    const fromHash = (window.location.hash || '').replace('#', '');
    if (!fromHash) return;
    const [a, t] = fromHash.split('/');
    const app = APPS.find(x => x.key === a);
    if (!app) return;
    setAppKey(a);
    if (t && app.tabs.some(x => x.key === t)) setTab(t);
    else setTab(app.tabs[0].key);
  }, []);
  useEffect(() => {
    window.location.hash = `${appKey}/${tab}`;
  }, [appKey, tab]);

  function switchApp(key) {
    const app = APPS.find(x => x.key === key);
    if (!app) return;
    setAppKey(key);
    setTab(app.tabs[0].key);
  }

  const currentApp = APPS.find(a => a.key === appKey) || APPS[0];

  return (
    <div className="shell">
      {/* 左側 sidebar */}
      <aside className="shell-sidebar">
        <div className="sidebar-brand">
          <div className="shell-brand-mark"/>
          <div>
            <div className="shell-brand-title">3D Print</div>
            <div className="shell-brand-sub">WORKSPACE</div>
          </div>
        </div>

        <nav className="sidebar-nav" role="tablist">
          {APPS.map(a => (
            <button key={a.key}
              role="tab"
              aria-selected={appKey === a.key}
              className="sidebar-item"
              onClick={() => switchApp(a.key)}>
              <span className="sidebar-item-icon">{a.icon}</span>
              <span className="sidebar-item-text">
                <span className="sidebar-item-label">{a.label}</span>
                <span className="sidebar-item-sub">{a.sub}</span>
              </span>
            </button>
          ))}
        </nav>

        <div className="sidebar-foot">
          <div className="sidebar-foot-date">{K.fmtYmd(K.TODAY)}</div>
          <div className="sidebar-foot-tag">即時資料 · v1.0</div>
        </div>
      </aside>

      {/* 主體 */}
      <div className="shell-main">
        <div className="shell-top">
          <nav className="shell-tabs" role="tablist">
            {currentApp.tabs.map(t => (
              <button key={t.key}
                role="tab"
                aria-selected={tab === t.key}
                className="shell-tab"
                onClick={() => setTab(t.key)}>
                <span className="shell-tab-icon">{TAB_ICONS[t.key]}</span>
                {t.label}
              </button>
            ))}
          </nav>
          <div className="shell-spacer"/>
          <div className="shell-aux">{currentApp.sub}</div>
        </div>

        <div className="shell-body">
          {appKey === 'board' && tab === 'table'     && <TableView data={data} setData={setData}/>}
          {appKey === 'board' && tab === 'kanban'    && <KanbanView data={data} setData={setData}/>}
          {appKey === 'board' && tab === 'gantt'     && <GanttView data={data}/>}
          {appKey === 'board' && tab === 'dashboard' && <DashboardView data={data}/>}
          {appKey === 'issues' && <IssuesView/>}
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<Shell/>);
