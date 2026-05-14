/* 總表 view —— 沿用原始 12 欄位 + 排序篩選 */
const { useState, useMemo } = React;

function TableView({ data, setData }) {
  const K = window.K;
  const [search, setSearch] = useState('');
  const [engF, setEngF] = useState('');
  const [machF, setMachF] = useState('');
  const [statusF, setStatusF] = useState('');
  const [matF, setMatF] = useState('');
  const [sortKey, setSortKey] = useState('seq');
  const [sortDir, setSortDir] = useState('asc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  const filtered = useMemo(() => {
    let arr = K.applyFilters(data, { search, engineer: engF, machine: machF, status: statusF });
    if (matF) arr = arr.filter(d => d.material === matF);
    arr = [...arr].sort((a, b) => {
      const dir = sortDir === 'asc' ? 1 : -1;
      const va = a[sortKey], vb = b[sortKey];
      if (typeof va === 'number') return (va - vb) * dir;
      return String(va || '').localeCompare(String(vb || '')) * dir;
    });
    return arr;
  }, [data, search, engF, machF, statusF, matF, sortKey, sortDir]);

  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const safePage = Math.min(page, totalPages);
  const start = (safePage - 1) * pageSize;
  const pageData = filtered.slice(start, start + pageSize);

  function toggleSort(key) {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  }

  function clearFilters() {
    setSearch(''); setEngF(''); setMachF(''); setStatusF(''); setMatF('');
    setSortKey('seq'); setSortDir('asc');
  }

  function exportCSV() {
    const headers = ['序列','EF單號','客戶名稱','執行工程師','EF期望交期','開始執行日期','預計完成日期','材料庫存','進度%','機器','完成','備註'];
    const lines = [headers.join(',')];
    filtered.forEach(it => {
      lines.push([
        it.seq, it.id, `"${it.customer}"`, K.ENG_LABEL[it.engineer]||it.engineer,
        it.dueDate, it.startDate, it.endDate, it.material, it.progress,
        it.machine, it.complete, `"${(it.remark||'').replace(/"/g,'""')}"`
      ].join(','));
    });
    const blob = new Blob(['\uFEFF' + lines.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = '工作進度_總表.csv'; a.click();
    URL.revokeObjectURL(url);
  }

  function SortHeader({ k, children, align }) {
    const isSorted = sortKey === k;
    return (
      <th
        className={`sortable ${isSorted ? 'sorted' : ''}`}
        style={align === 'right' ? { textAlign: 'right' } : null}
        onClick={() => toggleSort(k)}
      >
        {children}
        <span className="sort-indicator">{isSorted ? (sortDir === 'asc' ? '↑' : '↓') : '↕'}</span>
      </th>
    );
  }

  function DueCell({ item }) {
    const st = K.statusOf(item);
    const done = st === 'done' || st === 'cancelled';
    if (!item.dueDate) return <span className="kt-due" style={{ color: '#8a93a3' }}>未訂期</span>;
    const d = K.daysUntil(item.dueDate);
    let cls = 'kt-due';
    let suffix = '';
    if (!done && d !== null) {
      if (d < 0)      { cls += ' kt-due-red'; suffix = ` · 逾${-d}d`; }
      else if (d <= 3){ cls += ' kt-due-red'; suffix = ` · ${d}d`; }
      else if (d <= 7){ cls += ' kt-due-amber'; suffix = ` · ${d}d`; }
      else            { suffix = ` · ${d}d`; }
    }
    return <span className={cls}>{item.dueDate}{suffix}</span>;
  }

  return (
    <div className="table-view">
      <div className="toolbar">
        <div className="toolbar-title">訂單總表</div>
        <span className="toolbar-sub">{total} / {data.length} 筆 · 點欄位標題可排序</span>

        <div className="t-search">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <input value={search} onChange={e=>{ setSearch(e.target.value); setPage(1); }} placeholder="搜尋 EF / 客戶"/>
        </div>

        <select className="t-sel" value={statusF} onChange={e=>{setStatusF(e.target.value); setPage(1);}}>
          <option value="">所有狀態</option>
          <option value="todo">待開始</option>
          <option value="blocked">等待材料</option>
          <option value="progress">進行中</option>
          <option value="done">已完成</option>
          <option value="cancelled">已取消</option>
        </select>

        <select className="t-sel" value={engF} onChange={e=>{setEngF(e.target.value); setPage(1);}}>
          <option value="">所有工程師</option>
          {K.ENG_ORDER.map(k=><option key={k} value={k}>{K.ENG_LABEL[k]}</option>)}
        </select>

        <select className="t-sel" value={machF} onChange={e=>{setMachF(e.target.value); setPage(1);}}>
          <option value="">所有機台</option>
          {K.MACHINES.map(m=><option key={m} value={m}>{m}</option>)}
        </select>

        <select className="t-sel" value={matF} onChange={e=>{setMatF(e.target.value); setPage(1);}}>
          <option value="">所有材料狀況</option>
          {K.MATERIALS.map(m=><option key={m} value={m}>{m}</option>)}
        </select>

        <button className="t-btn" onClick={clearFilters} title="清除所有篩選與排序">清除</button>
        <button className="t-btn" onClick={exportCSV}>匯出 CSV</button>
      </div>

      <div className="table-wrap">
        <table className="kt">
          <thead>
            <tr>
              <SortHeader k="seq" align="right">序列</SortHeader>
              <SortHeader k="id">EF 單號</SortHeader>
              <SortHeader k="customer">客戶名稱</SortHeader>
              <SortHeader k="engineer">執行工程師</SortHeader>
              <SortHeader k="dueDate">期望交期</SortHeader>
              <SortHeader k="startDate">開始日</SortHeader>
              <SortHeader k="endDate">完成日</SortHeader>
              <th>材料</th>
              <SortHeader k="progress">進度</SortHeader>
              <SortHeader k="machine">機台</SortHeader>
              <th>狀態</th>
              <th>備註</th>
              <th className="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            {pageData.map(it => {
              const st = K.statusOf(it);
              const tone = K.ENG_TONE[it.engineer] || { fg: '#5a6270', bg: '#eef0f3' };
              return (
                <tr key={it.seq}>
                  <td className="col-seq">{it.seq}</td>
                  <td className="col-id">{it.id}</td>
                  <td className="col-customer">{it.customer}</td>
                  <td className="col-eng">
                    <span className="kt-eng">
                      <span className="kt-eng-dot" style={{ color: tone.fg, background: tone.bg }}>
                        {K.ENG_INIT[it.engineer]||it.engineer.slice(0,2)}
                      </span>
                      {K.ENG_LABEL[it.engineer]||it.engineer}
                    </span>
                  </td>
                  <td className="col-date"><DueCell item={it}/></td>
                  <td className="col-date">{it.startDate || '—'}</td>
                  <td className="col-date">{it.endDate || '—'}</td>
                  <td>
                    <span className={it.material==='足夠'?'kt-mat-ok':'kt-mat-need'}>
                      {it.material}
                    </span>
                  </td>
                  <td className="col-prog">
                    <div className="kt-prog">
                      <div className="kt-prog-bar">
                        <div className="kt-prog-fill" style={{
                          width: `${it.progress}%`,
                          background: st==='done' ? '#1d6f43' : st==='cancelled' ? '#cbd0d8' : '#0c7a99',
                        }}/>
                      </div>
                      <span className="kt-prog-num">{it.progress}%</span>
                    </div>
                  </td>
                  <td className="col-machine">{it.machine || '—'}</td>
                  <td>
                    <span className={`kt-pill kt-pill-${st}`}>{K.STATUS_TONE[st].label}</span>
                  </td>
                  <td style={{ color: '#5a6270', maxWidth: 180, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {it.remark || '—'}
                  </td>
                  <td className="col-actions">
                    <span className="kt-act">
                      <button className="kt-actbtn" title="切換完成">✓</button>
                      <button className="kt-actbtn" title="編輯">✎</button>
                      <button className="kt-actbtn danger" title="刪除"
                        onClick={()=>{ if(confirm('確定刪除此筆?')) setData(d=>d.filter(x=>x.seq!==it.seq)); }}>
                        ✕
                      </button>
                    </span>
                  </td>
                </tr>
              );
            })}
            {pageData.length === 0 && (
              <tr><td colSpan="13"><div className="kt-empty">沒有符合條件的訂單</div></td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="kt-pagination">
        <div className="kt-pagination-info">
          <span>每頁</span>
          <select className="t-sel" style={{ height: 26, fontSize: 11.5 }} value={pageSize} onChange={e=>{ setPageSize(parseInt(e.target.value,10)); setPage(1); }}>
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
          <span>筆 · 共 {total} 筆</span>
        </div>

        <div className="kt-pagination-pages">
          <button className="kt-page" disabled={safePage<=1} onClick={()=>setPage(safePage-1)}>‹</button>
          {Array.from({ length: totalPages }).map((_,i)=>(
            <button key={i} className="kt-page" aria-current={i+1===safePage}
              onClick={()=>setPage(i+1)}>{i+1}</button>
          ))}
          <button className="kt-page" disabled={safePage>=totalPages} onClick={()=>setPage(safePage+1)}>›</button>
        </div>
      </div>
    </div>
  );
}

window.TableView = TableView;
