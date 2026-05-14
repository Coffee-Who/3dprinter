/* Dashboard view — 3 預設 + 3 自由選擇 */
const { useState: useStateD, useMemo: useMemoD } = React;

// 維度定義
const DIMENSIONS = {
  status: {
    label: '狀態',
    extract: (it) => window.K.statusOf(it),
    order: ['todo', 'blocked', 'progress', 'done', 'cancelled'],
    label_for: (k) => window.K.STATUS_TONE[k].label,
    color_for: (k) => window.K.STATUS_TONE[k].fg,
  },
  engineer: {
    label: '工程師',
    extract: (it) => it.engineer,
    order: window.K.ENG_ORDER,
    label_for: (k) => window.K.ENG_LABEL[k] || k,
    color_for: (k) => (window.K.ENG_TONE[k] || { fg: '#0c7a99' }).fg,
  },
  progress: {
    label: '進度',
    extract: (it) => String(it.progress),
    order: ['0', '25', '50', '75', '100'],
    label_for: (k) => k + '%',
    color_for: (k) => {
      const n = parseInt(k, 10);
      if (n === 0) return '#9aa3b2';
      if (n === 100) return '#1d6f43';
      return '#0c7a99';
    },
  },
  machine: {
    label: '機台',
    extract: (it) => it.machine || '未指派',
    order: null,
    label_for: (k) => k,
    color_for: () => '#0c7a99',
  },
  material: {
    label: '材料',
    extract: (it) => it.material,
    order: ['足夠', '需調撥'],
    label_for: (k) => k,
    color_for: (k) => k === '足夠' ? '#1d6f43' : '#c79b2a',
  },
  customer: {
    label: '客戶 (Top 8)',
    extract: (it) => it.customer,
    order: null,
    label_for: (k) => k.length > 12 ? k.slice(0, 12) + '…' : k,
    color_for: () => '#0c7a99',
  },
};

function aggregate(data, dimKey) {
  const dim = DIMENSIONS[dimKey];
  const counts = {};
  data.forEach(it => {
    const k = dim.extract(it);
    counts[k] = (counts[k] || 0) + 1;
  });
  let keys;
  if (dim.order) {
    keys = dim.order.filter(k => counts[k] !== undefined);
    // 加入 order 沒有列到的(避免漏掉)
    Object.keys(counts).forEach(k => { if (!keys.includes(k)) keys.push(k); });
  } else {
    keys = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
    if (dimKey === 'customer') keys = keys.slice(0, 8);
  }
  return keys.map(k => ({
    key: k,
    label: dim.label_for(k),
    value: counts[k] || 0,
    color: dim.color_for(k),
  }));
}

// ─── 圖表元件 ───────────────────

function VerticalBar({ data, height = 200 }) {
  if (data.length === 0) return <div className="chart-empty">無資料</div>;
  const max = Math.max(...data.map(d => d.value), 1);
  const padding = { top: 16, right: 8, bottom: 28, left: 28 };
  const W = 320, H = height;
  const innerW = W - padding.left - padding.right;
  const innerH = H - padding.top - padding.bottom;
  const barW = innerW / data.length;
  const gridLines = [0, 0.25, 0.5, 0.75, 1].map(p => Math.round(max * p));

  return (
    <svg className="svg-chart" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet">
      {/* gridlines */}
      {gridLines.map((v, i) => {
        const y = padding.top + innerH - (v / max) * innerH;
        return (
          <g key={i}>
            <line x1={padding.left} x2={W - padding.right} y1={y} y2={y} className="vbar-grid"/>
            <text x={padding.left - 4} y={y + 3} fontSize="9" textAnchor="end" fill="#8a93a3">{v}</text>
          </g>
        );
      })}
      {/* bars */}
      {data.map((d, i) => {
        const h = (d.value / max) * innerH;
        const x = padding.left + i * barW + barW * 0.2;
        const w = barW * 0.6;
        const y = padding.top + innerH - h;
        return (
          <g key={d.key}>
            <rect x={x} y={padding.top} width={w} height={innerH}
              className="vbar-track" rx="2"/>
            <rect x={x} y={y} width={w} height={h}
              fill={d.color} className="vbar-bar" rx="2"/>
            <text x={x + w/2} y={y - 4} fontSize="10" textAnchor="middle" fill="#0a0e14" fontWeight="600">
              {d.value}
            </text>
            <text x={x + w/2} y={H - padding.bottom + 14} fontSize="9.5" textAnchor="middle" fill="#5a6270">
              {d.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

function HorizontalBar({ data }) {
  if (data.length === 0) return <div className="chart-empty">無資料</div>;
  const max = Math.max(...data.map(d => d.value), 1);
  return (
    <div className="hbar-list">
      {data.map(d => (
        <div key={d.key} className="hbar-row">
          <div className="hbar-label" title={d.label}>{d.label}</div>
          <div className="hbar-track">
            <div className="hbar-fill" style={{
              width: `${(d.value / max) * 100}%`,
              background: d.color,
            }}/>
          </div>
          <div className="hbar-num">{d.value}</div>
        </div>
      ))}
    </div>
  );
}

function DonutChart({ data, centerLabel = '總計' }) {
  if (data.length === 0) return <div className="chart-empty">無資料</div>;
  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  const W = 200, R = 78, r = 52, cx = W/2, cy = W/2;
  let cumulative = 0;
  const segments = data.map(d => {
    const start = cumulative / total;
    cumulative += d.value;
    const end = cumulative / total;
    return { ...d, start, end };
  });
  function arcPath(start, end) {
    if (end - start >= 0.9999) {
      // full circle — draw as two arcs
      return [
        `M ${cx + R} ${cy}`,
        `A ${R} ${R} 0 1 1 ${cx - R} ${cy}`,
        `A ${R} ${R} 0 1 1 ${cx + R} ${cy}`,
        `L ${cx + r} ${cy}`,
        `A ${r} ${r} 0 1 0 ${cx - r} ${cy}`,
        `A ${r} ${r} 0 1 0 ${cx + r} ${cy}`,
        'Z',
      ].join(' ');
    }
    const a0 = start * Math.PI * 2 - Math.PI / 2;
    const a1 = end * Math.PI * 2 - Math.PI / 2;
    const x0 = cx + R * Math.cos(a0), y0 = cy + R * Math.sin(a0);
    const x1 = cx + R * Math.cos(a1), y1 = cy + R * Math.sin(a1);
    const x2 = cx + r * Math.cos(a1), y2 = cy + r * Math.sin(a1);
    const x3 = cx + r * Math.cos(a0), y3 = cy + r * Math.sin(a0);
    const large = end - start > 0.5 ? 1 : 0;
    return [
      `M ${x0} ${y0}`,
      `A ${R} ${R} 0 ${large} 1 ${x1} ${y1}`,
      `L ${x2} ${y2}`,
      `A ${r} ${r} 0 ${large} 0 ${x3} ${y3}`,
      'Z',
    ].join(' ');
  }
  return (
    <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
      <div style={{ position: 'relative', width: W, height: W }}>
        <svg width={W} height={W} viewBox={`0 0 ${W} ${W}`}>
          {segments.map(seg => (
            <path key={seg.key} d={arcPath(seg.start, seg.end)} fill={seg.color}
              stroke="#fff" strokeWidth="1.5"/>
          ))}
        </svg>
        <div className="donut-center">
          <div className="donut-center-value">{total}</div>
          <div className="donut-center-label">{centerLabel}</div>
        </div>
      </div>
      <div className="chart-legend" style={{ marginTop: 14, borderTop: 0, paddingTop: 0 }}>
        {segments.map(seg => (
          <span key={seg.key} className="chart-legend-item">
            <span className="chart-legend-dot" style={{ background: seg.color }}/>
            {seg.label} · {seg.value}
          </span>
        ))}
      </div>
    </div>
  );
}

function PieChart({ data, centerLabel = '總計' }) {
  // 跟 Donut 一樣,但內半徑為 0
  if (data.length === 0) return <div className="chart-empty">無資料</div>;
  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  const W = 200, R = 84, cx = W/2, cy = W/2;
  let cumulative = 0;
  const segments = data.map(d => {
    const start = cumulative / total;
    cumulative += d.value;
    const end = cumulative / total;
    return { ...d, start, end };
  });
  function piePath(start, end) {
    if (end - start >= 0.9999) {
      return [
        `M ${cx + R} ${cy}`,
        `A ${R} ${R} 0 1 1 ${cx - R} ${cy}`,
        `A ${R} ${R} 0 1 1 ${cx + R} ${cy}`,
        'Z',
      ].join(' ');
    }
    const a0 = start * Math.PI * 2 - Math.PI / 2;
    const a1 = end * Math.PI * 2 - Math.PI / 2;
    const x0 = cx + R * Math.cos(a0), y0 = cy + R * Math.sin(a0);
    const x1 = cx + R * Math.cos(a1), y1 = cy + R * Math.sin(a1);
    const large = end - start > 0.5 ? 1 : 0;
    return [
      `M ${cx} ${cy}`,
      `L ${x0} ${y0}`,
      `A ${R} ${R} 0 ${large} 1 ${x1} ${y1}`,
      'Z',
    ].join(' ');
  }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
      <svg width={W} height={W} viewBox={`0 0 ${W} ${W}`}>
        {segments.map(seg => (
          <path key={seg.key} d={piePath(seg.start, seg.end)} fill={seg.color}
            stroke="#fff" strokeWidth="1.5"/>
        ))}
      </svg>
      <div className="chart-legend" style={{ marginTop: 14, borderTop: 0, paddingTop: 0 }}>
        {segments.map(seg => (
          <span key={seg.key} className="chart-legend-item">
            <span className="chart-legend-dot" style={{ background: seg.color }}/>
            {seg.label} · {seg.value}
          </span>
        ))}
      </div>
    </div>
  );
}

function LineChart({ data, height = 200 }) {
  // 折線適合時序資料 — 把資料當作有順序的時間軸
  if (data.length === 0) return <div className="chart-empty">無資料</div>;
  const max = Math.max(...data.map(d => d.value), 1);
  const padding = { top: 16, right: 12, bottom: 28, left: 28 };
  const W = 320, H = height;
  const innerW = W - padding.left - padding.right;
  const innerH = H - padding.top - padding.bottom;
  const stepX = data.length > 1 ? innerW / (data.length - 1) : 0;
  const points = data.map((d, i) => ({
    x: padding.left + i * stepX,
    y: padding.top + innerH - (d.value / max) * innerH,
    value: d.value,
    label: d.label,
  }));
  const pathD = points.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(' ');
  const areaD = points.length > 0
    ? `${pathD} L ${points[points.length-1].x} ${padding.top + innerH} L ${points[0].x} ${padding.top + innerH} Z`
    : '';
  const gridLines = [0, 0.5, 1].map(p => Math.round(max * p));

  return (
    <svg className="svg-chart" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="xMidYMid meet">
      {gridLines.map((v, i) => {
        const y = padding.top + innerH - (v / max) * innerH;
        return (
          <g key={i}>
            <line x1={padding.left} x2={W - padding.right} y1={y} y2={y} className="line-grid"/>
            <text x={padding.left - 4} y={y + 3} fontSize="9" textAnchor="end" fill="#8a93a3">{v}</text>
          </g>
        );
      })}
      <path d={areaD} className="line-area"/>
      <path d={pathD} className="line-path"/>
      {points.map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r="3.5" className="line-dot"/>
          <text x={p.x} y={H - padding.bottom + 14} fontSize="9" textAnchor="middle" fill="#5a6270">
            {p.label}
          </text>
        </g>
      ))}
    </svg>
  );
}

function ChartByType({ type, data, centerLabel }) {
  if (type === 'bar') return <VerticalBar data={data}/>;
  if (type === 'hbar') return <HorizontalBar data={data}/>;
  if (type === 'donut') return <DonutChart data={data} centerLabel={centerLabel}/>;
  if (type === 'pie') return <PieChart data={data} centerLabel={centerLabel}/>;
  if (type === 'line') return <LineChart data={data}/>;
  return null;
}

// ─── 主元件 ──────────────────────

function DashboardView({ data }) {
  const K = window.K;

  // 3 自由選擇 slot 的狀態
  const [c1, setC1] = useStateD({ dim: 'machine',  type: 'donut' });
  const [c2, setC2] = useStateD({ dim: 'material', type: 'donut' });
  const [c3, setC3] = useStateD({ dim: 'customer', type: 'hbar' });

  // KPI
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

  // 預設 3 個圖表
  const statusData = useMemoD(() => aggregate(data, 'status'), [data]);
  const engineerData = useMemoD(() => aggregate(data, 'engineer'), [data]);
  const progressData = useMemoD(() => aggregate(data, 'progress'), [data]);

  // 3 個自由 slot
  const customCharts = [
    { state: c1, setState: setC1, idx: 1 },
    { state: c2, setState: setC2, idx: 2 },
    { state: c3, setState: setC3, idx: 3 },
  ];

  const CHART_TYPES = [
    { value: 'bar',   label: '長條圖' },
    { value: 'hbar',  label: '橫條圖' },
    { value: 'donut', label: '環狀圖' },
    { value: 'pie',   label: '圓餅圖' },
    { value: 'line',  label: '折線圖' },
  ];

  return (
    <div className="dash">
      {/* KPI */}
      <div className="dash-kpis">
        <div className="dash-kpi">
          <div className="dash-kpi-label">總訂單</div>
          <div className="dash-kpi-value">{stats.total}</div>
          <div className="dash-kpi-sub">全部資料筆數</div>
        </div>
        <div className="dash-kpi">
          <div className="dash-kpi-label">進行中</div>
          <div className="dash-kpi-value">{stats.wip}</div>
          <div className="dash-kpi-sub">已開工未完成</div>
        </div>
        <div className="dash-kpi">
          <div className="dash-kpi-label">等待材料</div>
          <div className="dash-kpi-value" style={{ color: '#c79b2a' }}>{stats.blocked}</div>
          <div className="dash-kpi-sub">需調撥 / 待簽回</div>
        </div>
        <div className="dash-kpi">
          <div className="dash-kpi-label">7 天內到期</div>
          <div className="dash-kpi-value" style={{ color: '#c0392b' }}>{stats.due7}</div>
          <div className="dash-kpi-sub">未完成且交期 ≤ 7 天</div>
        </div>
        <div className="dash-kpi">
          <div className="dash-kpi-label">已完成</div>
          <div className="dash-kpi-value" style={{ color: '#1d6f43' }}>{stats.done}</div>
          <div className="dash-kpi-sub">100% / 完成</div>
        </div>
      </div>

      {/* 預設圖表 */}
      <div className="dash-section">
        <div className="dash-section-title">預設分析</div>
        <div className="dash-section-sub">DEFAULT VIEWS</div>
      </div>
      <div className="dash-grid">
        <div className="chart-card">
          <div className="chart-card-head">
            <div className="chart-card-title">狀態分布</div>
            <div className="chart-card-meta">DONUT</div>
          </div>
          <div className="chart-body">
            <DonutChart data={statusData} centerLabel="總訂單"/>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-card-head">
            <div className="chart-card-title">工程師負荷</div>
            <div className="chart-card-meta">HORIZONTAL BAR</div>
          </div>
          <div className="chart-body">
            <HorizontalBar data={engineerData}/>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-card-head">
            <div className="chart-card-title">進度分布</div>
            <div className="chart-card-meta">VERTICAL BAR</div>
          </div>
          <div className="chart-body">
            <VerticalBar data={progressData}/>
          </div>
        </div>
      </div>

      {/* 自由選擇 */}
      <div className="dash-section">
        <div className="dash-section-title">自由分析</div>
        <div className="dash-section-sub">CUSTOM — 選擇維度與圖表類型</div>
      </div>
      <div className="dash-grid">
        {customCharts.map(({ state, setState, idx }) => {
          const aggData = aggregate(data, state.dim);
          return (
            <div key={idx} className="chart-card custom">
              <div className="chart-card-head">
                <div className="chart-card-title">自由分析 #{idx}</div>
                <select className="chart-mini-sel" value={state.dim}
                  onChange={e => setState({ ...state, dim: e.target.value })}>
                  {Object.entries(DIMENSIONS).map(([k, d]) => (
                    <option key={k} value={k}>依 {d.label}</option>
                  ))}
                </select>
                <select className="chart-mini-sel" value={state.type}
                  onChange={e => setState({ ...state, type: e.target.value })}>
                  {CHART_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
              </div>
              <div className="chart-body">
                <ChartByType type={state.type} data={aggData}
                  centerLabel={DIMENSIONS[state.dim].label}/>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

window.DashboardView = DashboardView;
window.VerticalBar = VerticalBar;
window.HorizontalBar = HorizontalBar;
window.DonutChart = DonutChart;
window.PieChart = PieChart;
window.LineChart = LineChart;
