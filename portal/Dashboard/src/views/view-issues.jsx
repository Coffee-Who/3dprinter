/* 工作異常與資源 view — 4 子分頁:客戶異常 / IPA採購 / 設備清單 / 分析 */
const { useState: useStateI, useMemo: useMemoI } = React;
const VerticalBar = window.VerticalBar;
const HorizontalBar = window.HorizontalBar;
const DonutChart = window.DonutChart;
const LineChart = window.LineChart;

function IssuesView() {
  const K = window.K;
  const [tab, setTab] = useStateI('anomaly');

  const [anomalies] = useStateI(window.ISSUES_ANOMALIES);
  const [ipa] = useStateI(window.ISSUES_IPA);
  const [tools] = useStateI(window.ISSUES_TOOLS);

  const SUBTABS = [
    { key: 'anomaly', label: '客戶異常', count: anomalies.length },
    { key: 'ipa',     label: 'IPA 採購', count: ipa.length },
    { key: 'tools',   label: '設備清單', count: tools.length },
    { key: 'stats',   label: '分析',     count: null },
  ];

  return (
    <div className="table-view">
      <div className="toolbar">
        <div className="toolbar-title">工作異常與資源</div>
        <span className="toolbar-sub">
          客戶異常 · IPA 採購 · 設備清單 · 統計分析
        </span>
        <div className="issues-subtabs" role="tablist">
          {SUBTABS.map(t => (
            <button key={t.key}
              role="tab"
              aria-selected={tab === t.key}
              className="issues-subtab"
              onClick={() => setTab(t.key)}>
              {t.label}
              {t.count !== null && <span className="issues-subtab-count">{t.count}</span>}
            </button>
          ))}
        </div>
      </div>

      {tab === 'anomaly' && <AnomalyTable items={anomalies}/>}
      {tab === 'ipa'     && <IpaTable     items={ipa}/>}
      {tab === 'tools'   && <ToolsTable   items={tools}/>}
      {tab === 'stats'   && <IssuesStats  anomalies={anomalies} ipa={ipa} tools={tools}/>}
    </div>
  );
}

// ─── 客戶異常 ─────────────────────
function AnomalyTable({ items }) {
  const K = window.K;
  const [search, setSearch] = useStateI('');
  const [statusF, setStatusF] = useStateI('');
  const [engF, setEngF] = useStateI('');

  const filtered = useMemoI(() => {
    const s = search.trim().toLowerCase();
    return items.filter(it => {
      if (s && !it.customer.toLowerCase().includes(s) && !it.product.toLowerCase().includes(s)) return false;
      if (statusF && it.status !== statusF) return false;
      if (engF && it.engineer !== engF) return false;
      return true;
    });
  }, [items, search, statusF, engF]);

  function pillCls(st) {
    if (st === '已完成') return 'kt-pill kt-pill-完成';
    if (st === '處理中') return 'kt-pill kt-pill-處理';
    return 'kt-pill kt-pill-暫停';
  }

  return (
    <>
      <div className="toolbar" style={{ borderTop: '1px solid var(--line-soft)', paddingTop: 10, paddingBottom: 10 }}>
        <div className="t-search" style={{ marginRight: 'auto' }}>
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="搜尋客戶 / 品名"/>
        </div>
        <select className="t-sel" value={statusF} onChange={e=>setStatusF(e.target.value)}>
          <option value="">所有狀態</option>
          <option value="處理中">處理中</option>
          <option value="已完成">已完成</option>
          <option value="暫停">暫停</option>
        </select>
        <select className="t-sel" value={engF} onChange={e=>setEngF(e.target.value)}>
          <option value="">所有工程師</option>
          {K.ENG_ORDER.map(k => <option key={k} value={k}>{K.ENG_LABEL[k]}</option>)}
        </select>
        <button className="t-btn">+ 新增異常</button>
      </div>

      <div className="table-wrap">
        <table className="kt">
          <thead>
            <tr>
              <th className="col-seq">序</th>
              <th>客戶</th>
              <th>異常日期</th>
              <th>品名</th>
              <th>窗口工程師</th>
              <th>狀態</th>
              <th>進度日期</th>
              <th>進度狀況</th>
              <th className="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(it => {
              const tone = K.ENG_TONE[it.engineer] || { fg: '#5a6270', bg: '#eef0f3' };
              const first = it.progresses[0] || { date: '—', status: '—' };
              const rest = it.progresses.slice(1);
              return (
                <React.Fragment key={it.seq}>
                  <tr>
                    <td className="col-seq">{it.seq}</td>
                    <td className="col-customer">{it.customer}</td>
                    <td className="col-date">{it.date}</td>
                    <td>{it.product}</td>
                    <td>
                      <span className="kt-eng">
                        <span className="kt-eng-dot" style={{ color: tone.fg, background: tone.bg }}>
                          {K.ENG_INIT[it.engineer] || it.engineer.slice(0,2)}
                        </span>
                        {K.ENG_LABEL[it.engineer] || it.engineer}
                      </span>
                    </td>
                    <td><span className={pillCls(it.status)}>{it.status}</span></td>
                    <td className="col-date">{first.date}</td>
                    <td>{first.status}</td>
                    <td className="col-actions">
                      <span className="kt-act">
                        <button className="kt-actbtn" title="編輯">✎</button>
                      </span>
                    </td>
                  </tr>
                  {rest.map((p, i) => (
                    <tr key={i} className="kt-anomaly-sub">
                      <td colSpan="6">
                        <span className="kt-anomaly-sub-marker">↳ 後續進度 #{i+2}</span>
                      </td>
                      <td className="col-date">{p.date}</td>
                      <td>{p.status}</td>
                      <td></td>
                    </tr>
                  ))}
                </React.Fragment>
              );
            })}
            {filtered.length === 0 && (
              <tr><td colSpan="9"><div className="kt-empty">沒有符合條件的異常紀錄</div></td></tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

// ─── IPA 採購 ─────────────────────
function IpaTable({ items }) {
  const K = window.K;
  const [search, setSearch] = useStateI('');
  const [personF, setPersonF] = useStateI('');

  const filtered = useMemoI(() => {
    const s = search.trim().toLowerCase();
    return items.filter(it => {
      if (s && !it.product.toLowerCase().includes(s) && !(it.remark||'').toLowerCase().includes(s)) return false;
      if (personF && it.person !== personF) return false;
      return true;
    });
  }, [items, search, personF]);

  const totalBarrels = filtered.reduce((s, r) => s + r.quantity, 0);

  return (
    <>
      <div className="toolbar" style={{ borderTop: '1px solid var(--line-soft)', paddingTop: 10, paddingBottom: 10 }}>
        <div className="t-search" style={{ marginRight: 'auto' }}>
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="搜尋品名 / 備註"/>
        </div>
        <span className="toolbar-sub">合計 <b style={{color:'#0a0e14',fontWeight:600}}>{totalBarrels}</b> 桶</span>
        <select className="t-sel" value={personF} onChange={e=>setPersonF(e.target.value)}>
          <option value="">所有採購人員</option>
          {K.ENG_ORDER.map(k => <option key={k} value={k}>{K.ENG_LABEL[k]}</option>)}
        </select>
        <button className="t-btn">+ 新增採購</button>
      </div>

      <div className="table-wrap">
        <table className="kt">
          <thead>
            <tr>
              <th className="col-seq">序</th>
              <th>採購日期</th>
              <th>使用區間</th>
              <th>品名</th>
              <th>數量</th>
              <th>採購人員</th>
              <th>備註</th>
              <th className="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(it => {
              const tone = K.ENG_TONE[it.person] || { fg: '#5a6270', bg: '#eef0f3' };
              return (
                <tr key={it.seq}>
                  <td className="col-seq">{it.seq}</td>
                  <td className="col-date">{it.purchaseDate}</td>
                  <td className="col-date">{it.useDate}</td>
                  <td>{it.product}</td>
                  <td><span className="kt-num-badge">{it.quantity} 桶</span></td>
                  <td>
                    <span className="kt-eng">
                      <span className="kt-eng-dot" style={{ color: tone.fg, background: tone.bg }}>
                        {K.ENG_INIT[it.person] || it.person.slice(0,2)}
                      </span>
                      {K.ENG_LABEL[it.person] || it.person}
                    </span>
                  </td>
                  <td style={{ color: '#5a6270' }}>{it.remark || '—'}</td>
                  <td className="col-actions">
                    <span className="kt-act">
                      <button className="kt-actbtn" title="編輯">✎</button>
                    </span>
                  </td>
                </tr>
              );
            })}
            {filtered.length === 0 && (
              <tr><td colSpan="8"><div className="kt-empty">沒有符合條件的採購紀錄</div></td></tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

// ─── 設備清單 ─────────────────────
function ToolsTable({ items }) {
  const [search, setSearch] = useStateI('');
  const [methodF, setMethodF] = useStateI('');

  const filtered = useMemoI(() => {
    const s = search.trim().toLowerCase();
    return items.filter(it => {
      if (s && !it.product.toLowerCase().includes(s) && !(it.remark||'').toLowerCase().includes(s)) return false;
      if (methodF && it.method !== methodF) return false;
      return true;
    });
  }, [items, search, methodF]);

  const totalAmount = filtered.reduce((s, r) => s + (r.price || 0) * (r.quantity || 1), 0);

  return (
    <>
      <div className="toolbar" style={{ borderTop: '1px solid var(--line-soft)', paddingTop: 10, paddingBottom: 10 }}>
        <div className="t-search" style={{ marginRight: 'auto' }}>
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="搜尋品名 / 用途"/>
        </div>
        <span className="toolbar-sub">合計金額 <b style={{color:'#0a0e14',fontWeight:600}}>NT$ {totalAmount.toLocaleString()}</b></span>
        <select className="t-sel" value={methodF} onChange={e=>setMethodF(e.target.value)}>
          <option value="">所有採購方式</option>
          <option value="Easy Flow">Easy Flow</option>
          <option value="零用金">零用金</option>
        </select>
        <button className="t-btn">+ 新增設備</button>
      </div>

      <div className="table-wrap">
        <table className="kt">
          <thead>
            <tr>
              <th className="col-seq">序</th>
              <th>採購日期</th>
              <th>品名</th>
              <th>數量</th>
              <th>採購方式</th>
              <th>單號</th>
              <th>備註(用途)</th>
              <th style={{textAlign:'right'}}>金額</th>
              <th className="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(it => (
              <tr key={it.seq}>
                <td className="col-seq">{it.seq}</td>
                <td className="col-date">{it.purchaseDate || '—'}</td>
                <td>{it.product}</td>
                <td><span className="kt-num-badge">{it.quantity}</span></td>
                <td>{it.method}</td>
                <td className="col-id">{it.number || '—'}</td>
                <td style={{ color: '#5a6270' }}>{it.remark || '—'}</td>
                <td className="kt-money">NT$ {((it.price||0) * (it.quantity||1)).toLocaleString()}</td>
                <td className="col-actions">
                  <span className="kt-act">
                    <button className="kt-actbtn" title="編輯">✎</button>
                  </span>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan="9"><div className="kt-empty">沒有符合條件的設備</div></td></tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

// ─── 分析 ──────────────────────────
function IssuesStats({ anomalies, ipa, tools }) {
  const K = window.K;

  // 工程師分布
  const engineerCounts = {};
  anomalies.forEach(a => { engineerCounts[a.engineer] = (engineerCounts[a.engineer] || 0) + 1; });
  const engineerData = K.ENG_ORDER
    .filter(k => engineerCounts[k])
    .map(k => ({
      key: k, label: K.ENG_LABEL[k], value: engineerCounts[k],
      color: K.ENG_TONE[k].fg,
    }));

  // 狀態分布
  const statusCounts = { '已完成': 0, '處理中': 0, '暫停': 0 };
  anomalies.forEach(a => { if (statusCounts[a.status] !== undefined) statusCounts[a.status]++; });
  const statusData = [
    { key: '已完成', label: '已完成', value: statusCounts['已完成'], color: '#1d6f43' },
    { key: '處理中', label: '處理中', value: statusCounts['處理中'], color: '#c79b2a' },
    { key: '暫停',   label: '暫停',   value: statusCounts['暫停'],   color: '#c0392b' },
  ].filter(d => d.value > 0);

  // 採購人員 (IPA)
  const personCounts = {};
  ipa.forEach(r => { personCounts[r.person] = (personCounts[r.person] || 0) + r.quantity; });
  const personData = K.ENG_ORDER
    .filter(k => personCounts[k])
    .map(k => ({
      key: k, label: K.ENG_LABEL[k], value: personCounts[k],
      color: K.ENG_TONE[k].fg,
    }));

  // 設備採購方式
  const methodCounts = {};
  tools.forEach(r => { methodCounts[r.method] = (methodCounts[r.method] || 0) + (r.price * r.quantity); });
  const methodData = Object.entries(methodCounts).map(([k, v]) => ({
    key: k, label: k, value: v,
    color: k === 'Easy Flow' ? '#0c7a99' : '#c79b2a',
  }));

  const totalBarrels = ipa.reduce((s, r) => s + r.quantity, 0);
  const totalSpend = tools.reduce((s, r) => s + r.price * r.quantity, 0);

  return (
    <div className="iss-analytic">
      {/* KPI */}
      <div className="dash-kpis" style={{ paddingTop: 0 }}>
        <div className="dash-kpi">
          <div className="dash-kpi-label">總異常</div>
          <div className="dash-kpi-value">{anomalies.length}</div>
          <div className="dash-kpi-sub">累計紀錄</div>
        </div>
        <div className="dash-kpi">
          <div className="dash-kpi-label">處理中</div>
          <div className="dash-kpi-value" style={{ color: '#c79b2a' }}>{statusCounts['處理中']}</div>
          <div className="dash-kpi-sub">待解決</div>
        </div>
        <div className="dash-kpi">
          <div className="dash-kpi-label">已完成</div>
          <div className="dash-kpi-value" style={{ color: '#1d6f43' }}>{statusCounts['已完成']}</div>
          <div className="dash-kpi-sub">結案</div>
        </div>
        <div className="dash-kpi">
          <div className="dash-kpi-label">IPA 採購 (桶)</div>
          <div className="dash-kpi-value">{totalBarrels}</div>
          <div className="dash-kpi-sub">{ipa.length} 筆紀錄</div>
        </div>
        <div className="dash-kpi">
          <div className="dash-kpi-label">設備支出</div>
          <div className="dash-kpi-value" style={{ color: '#0c7a99' }}>NT$ {totalSpend.toLocaleString()}</div>
          <div className="dash-kpi-sub">{tools.length} 項設備</div>
        </div>
      </div>

      <div className="dash-section">
        <div className="dash-section-title">分析圖表</div>
        <div className="dash-section-sub">PIVOT ANALYSIS</div>
      </div>

      <div className="iss-grid">
        <div className="chart-card">
          <div className="chart-card-head">
            <div className="chart-card-title">異常 · 工程師分布</div>
            <div className="chart-card-meta">HORIZONTAL BAR</div>
          </div>
          <div className="chart-body">
            <HorizontalBar data={engineerData}/>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-card-head">
            <div className="chart-card-title">異常 · 狀態分布</div>
            <div className="chart-card-meta">DONUT</div>
          </div>
          <div className="chart-body">
            <DonutChart data={statusData} centerLabel="異常案件"/>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-card-head">
            <div className="chart-card-title">IPA 採購 · 人員(桶數)</div>
            <div className="chart-card-meta">VERTICAL BAR</div>
          </div>
          <div className="chart-body">
            <VerticalBar data={personData}/>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-card-head">
            <div className="chart-card-title">設備支出 · 採購方式</div>
            <div className="chart-card-meta">DONUT</div>
          </div>
          <div className="chart-body">
            <DonutChart data={methodData} centerLabel="NT$"/>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-card-head">
            <div className="chart-card-title">設備清單 · 金額排行</div>
            <div className="chart-card-meta">HORIZONTAL BAR</div>
          </div>
          <div className="chart-body">
            <HorizontalBar data={
              [...tools]
                .sort((a,b) => b.price*b.quantity - a.price*a.quantity)
                .slice(0, 6)
                .map(t => ({
                  key: t.seq,
                  label: t.product.length > 8 ? t.product.slice(0,8)+'…' : t.product,
                  value: t.price * t.quantity,
                  color: '#0c7a99',
                }))
            }/>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-card-head">
            <div className="chart-card-title">IPA 採購 · 月份趨勢</div>
            <div className="chart-card-meta">LINE</div>
          </div>
          <div className="chart-body">
            <LineChart data={(() => {
              const monthly = {};
              ipa.forEach(r => {
                const m = (r.purchaseDate || '').slice(0, 7);
                if (!m) return;
                monthly[m] = (monthly[m] || 0) + r.quantity;
              });
              return Object.keys(monthly).sort().map(m => ({
                key: m,
                label: m.slice(2).replace('-', '/'),
                value: monthly[m],
                color: '#0c7a99',
              }));
            })()}/>
          </div>
        </div>
      </div>
    </div>
  );
}

window.IssuesView = IssuesView;
