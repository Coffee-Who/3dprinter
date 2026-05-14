/* 時間軸 / 甘特圖 view */
const { useState: useStateG, useMemo: useMemoG } = React;

function GanttView({ data }) {
  const K = window.K;
  const TODAY = K.TODAY;
  const DAY = K.DAY;

  const [rangeKey, setRangeKey] = useStateG('quarter');
  const [engF, setEngF] = useStateG('');
  const [tip, setTip] = useStateG(null);

  const RANGES = [
    { key:'month',  label:'本月',   spanDays: 30,  startOffset: -14 },
    { key:'quarter',label:'3 個月', spanDays: 92,  startOffset: -30 },
    { key:'half',   label:'半年',   spanDays: 180, startOffset: -60 },
  ];

  const range = RANGES.find(r => r.key === rangeKey);
  const start = new Date(TODAY.getTime() + range.startOffset * DAY);
  start.setHours(0,0,0,0);
  const days = [];
  for (let d = new Date(start); d < new Date(start.getTime() + range.spanDays * DAY); d = new Date(d.getTime() + DAY)) {
    days.push(new Date(d));
  }

  const monthsAgg = [];
  days.forEach(d => {
    const ym = `${d.getFullYear()}-${d.getMonth()}`;
    const last = monthsAgg[monthsAgg.length-1];
    if (last && last.ym === ym) last.count++;
    else monthsAgg.push({ ym, count: 1, year: d.getFullYear(), month: d.getMonth() });
  });

  const items = data.filter(it => !engF || it.engineer === engF);
  const lanes = K.ENG_ORDER.filter(e => !engF || engF === e).map(eng => ({
    eng, items: items.filter(it => it.engineer === eng),
  }));

  function parseDate(s) {
    if (!s) return null;
    const d = new Date(s);
    return Number.isNaN(d.getTime()) ? null : d;
  }
  function barPos(it) {
    const sd = parseDate(it.startDate);
    const dd = parseDate(it.dueDate);
    if (!dd) return null;
    const barStart = sd || new Date(dd.getTime() - 7 * DAY);
    const startIdx = Math.round((barStart - start) / DAY);
    const dueIdx = Math.round((dd - start) / DAY);
    if (dueIdx < 0 || startIdx > days.length) return null;
    const clippedStart = Math.max(0, startIdx);
    const clippedEnd = Math.min(days.length, dueIdx + 1);
    return {
      left: clippedStart * 22,
      width: Math.max(28, (clippedEnd - clippedStart) * 22),
      noStart: !sd,
      overdue: dd < TODAY && K.statusOf(it) !== 'done' && K.statusOf(it) !== 'cancelled',
    };
  }
  function todayPos() {
    const idx = (TODAY - start) / DAY;
    if (idx < 0 || idx > days.length) return null;
    return idx * 22;
  }
  const isWeekend = (d) => { const w = d.getDay(); return w === 0 || w === 6; };
  const isMonday = (d) => d.getDay() === 1;
  const isToday = (d) =>
    d.getFullYear() === TODAY.getFullYear() &&
    d.getMonth() === TODAY.getMonth() &&
    d.getDate() === TODAY.getDate();

  const tpos = todayPos();

  return (
    <div className="gantt-view">
      <div className="toolbar">
        <div className="toolbar-title">時間軸 / 甘特圖</div>
        <span className="toolbar-sub">{items.length} 筆訂單 · 滑鼠移到 bar 顯示詳情</span>
        <span className="today-pill">
          <span className="dot"></span>
          今天 <b>{K.fmtYmd(TODAY)}</b>
        </span>
        <select className="t-sel" value={engF} onChange={e => setEngF(e.target.value)}>
          <option value="">所有工程師</option>
          {K.ENG_ORDER.map(k => <option key={k} value={k}>{K.ENG_FULLLABEL[k]}</option>)}
        </select>
        <div className="seg">
          {RANGES.map(r => (
            <button key={r.key}
              className={`seg-btn ${rangeKey === r.key ? 'seg-btn-active' : ''}`}
              onClick={() => setRangeKey(r.key)}>{r.label}</button>
          ))}
        </div>
      </div>

      <div className="legend">
        <span className="lg"><span className="lg-chip todo"/>待開始</span>
        <span className="lg"><span className="lg-chip blocked"/>等待材料</span>
        <span className="lg"><span className="lg-chip progress"/>進行中</span>
        <span className="lg"><span className="lg-chip done"/>已完成</span>
        <span className="lg"><span className="lg-chip cancelled"/>已取消</span>
        <span className="lg-spacer"/>
        <span className="lg-hint">bar 內填色 = 進度 %</span>
      </div>

      <div className="gantt">
        <div className="gantt-left">
          <div className="lane-head-sticky">工程師</div>
          {lanes.map(l => (
            <div key={l.eng} className="lane">
              <span className="lane-avatar" style={{
                color: K.ENG_TONE[l.eng].fg,
                background: K.ENG_TONE[l.eng].bg,
              }}>{K.ENG_INIT[l.eng]}</span>
              <div className="lane-meta">
                <span className="lane-name">{K.ENG_FULLLABEL[l.eng]}</span>
                <span className="lane-sub">{l.items.length} 訂單</span>
              </div>
            </div>
          ))}
        </div>

        <div className="gantt-right" style={{ minWidth: days.length * 22 + 'px' }}>
          <div className="scale" style={{ width: days.length * 22 + 'px' }}>
            <div className="scale-months">
              {monthsAgg.map((m, i) => (
                <div key={i} className="scale-month" style={{ width: m.count * 22 + 'px' }}>
                  {m.year} · {String(m.month + 1).padStart(2, '0')} 月
                </div>
              ))}
            </div>
            <div className="scale-days">
              {days.map((d, i) => (
                <div key={i} className={[
                  'scale-day',
                  isWeekend(d) ? 'weekend' : '',
                  isMonday(d) ? 'is-monday' : '',
                  isToday(d) ? 'is-today' : '',
                ].filter(Boolean).join(' ')}>
                  {d.getDate()}
                </div>
              ))}
            </div>
          </div>

          {tpos !== null && (
            <div className="today-line" style={{ left: tpos + 'px', top: 48 }}/>
          )}

          {lanes.map((l, li) => (
            <div key={l.eng} className={`row ${li % 2 === 1 ? 'alt' : ''}`} style={{ width: days.length * 22 + 'px' }}>
              <div className="grid-lines">
                {days.map((d, i) => (
                  <div key={i} className={[
                    'grid-cell',
                    isWeekend(d) ? 'weekend' : '',
                    isMonday(d) ? 'is-monday' : '',
                  ].filter(Boolean).join(' ')}/>
                ))}
              </div>

              {l.items.map(it => {
                const pos = barPos(it);
                if (!pos) return null;
                const st = K.statusOf(it);
                const cls = `bar ${st} ${pos.noStart ? 'todo-pending' : ''} ${pos.overdue ? 'overdue' : ''}`;
                return (
                  <div key={it.seq} className={cls}
                    style={{ left: pos.left + 'px', width: pos.width + 'px' }}
                    onMouseEnter={e => setTip({
                      item: it,
                      x: e.currentTarget.offsetLeft + pos.width + 10,
                      y: e.currentTarget.offsetTop - 6,
                    })}
                    onMouseLeave={() => setTip(null)}
                  >
                    {!pos.noStart && st !== 'todo' && (
                      <div className="bar-fill" style={{ width: `${it.progress}%` }}/>
                    )}
                    <span className="bar-text">
                      EF·{it.id.slice(-7)} · {it.customer.length > 10 ? it.customer.slice(0, 10) + '…' : it.customer}
                    </span>
                    {!pos.noStart && st !== 'done' && st !== 'cancelled' && pos.overdue && (
                      <div className="bar-due-marker"/>
                    )}
                  </div>
                );
              })}
            </div>
          ))}

          {tip && (
            <div className="tooltip" style={{ left: tip.x + 'px', top: tip.y + 48 + 'px' }}>
              <div className="tooltip-title">{tip.item.customer}</div>
              <div className="tooltip-row">EF · <b>{tip.item.id}</b></div>
              <div className="tooltip-row">機台 · <b>{tip.item.machine || '—'}</b></div>
              <div className="tooltip-row">進度 · <b>{tip.item.progress}%</b></div>
              <div className="tooltip-row">期望交期 · <b>{tip.item.dueDate || '—'}</b></div>
              <div className="tooltip-row">開始日 · <b>{tip.item.startDate || '未排程'}</b></div>
              <div className="tooltip-row">材料 · <b>{tip.item.material}</b></div>
              {tip.item.remark && <div className="tooltip-row" style={{ marginTop: 4 }}>備註 · <b>{tip.item.remark}</b></div>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

window.GanttView = GanttView;
