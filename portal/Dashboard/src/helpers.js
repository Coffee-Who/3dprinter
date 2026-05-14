/* 共用常數 / 工具 — 所有 view 都靠 window.K 取用 */
(function () {
  const K = {};

  K.TODAY = new Date('2026-05-14');
  K.DAY = 86400000;

  K.ENG_ORDER = ['Jimmy', 'Jaylen', 'Bill', 'Barry'];
  K.ENG_LABEL = {
    Jimmy:  '廖璟程',
    Jaylen: '何哲綸',
    Bill:   '陳柏元',
    Barry:  'Barry',
  };
  K.ENG_FULLLABEL = {
    Jimmy:  '廖璟程 (Jimmy)',
    Jaylen: '何哲綸 (Jaylen)',
    Bill:   '陳柏元 (Bill)',
    Barry:  'Barry',
  };
  K.ENG_INIT = { Jimmy: 'JC', Jaylen: 'JL', Bill: 'BL', Barry: 'BR' };
  K.ENG_TONE = {
    Jimmy:  { fg: '#0c7a99', bg: '#e6f1f6' },
    Jaylen: { fg: '#6b3fa0', bg: '#efe9f7' },
    Bill:   { fg: '#1d6f43', bg: '#e6f1ea' },
    Barry:  { fg: '#a05a00', bg: '#f7eed8' },
  };

  K.MACHINES = ['Form4', 'Form4L', 'Fuse1+', 'Mark2'];
  K.MATERIALS = ['足夠', '需調撥'];
  K.PROGRESS_VALUES = [0, 25, 50, 75, 100];

  K.STATUS_TONE = {
    todo:      { fg: '#5a6270', bg: '#eef0f3', label: '待開始' },
    blocked:   { fg: '#8b6b13', bg: '#fbf3dc', label: '等待材料' },
    progress:  { fg: '#0c7a99', bg: '#e6f1f6', label: '進行中' },
    done:      { fg: '#1d6f43', bg: '#e6f1ea', label: '已完成' },
    cancelled: { fg: '#8a93a3', bg: '#f0f1f4', label: '已取消' },
  };

  K.daysUntil = function (dateStr) {
    if (!dateStr) return null;
    const d = new Date(dateStr);
    if (Number.isNaN(d.getTime())) return null;
    return Math.round((d - K.TODAY) / K.DAY);
  };

  K.statusOf = function (item) {
    if (/取消/.test(item.remark)) return 'cancelled';
    if (item.complete === '是' || item.progress === 100) return 'done';
    if (item.material === '需調撥') return 'blocked';
    if (item.progress > 0) return 'progress';
    return 'todo';
  };

  K.fmtYmd = function (d) {
    if (!d) return '—';
    const x = (d instanceof Date) ? d : new Date(d);
    if (Number.isNaN(x.getTime())) return '—';
    return `${x.getFullYear()}-${String(x.getMonth()+1).padStart(2,'0')}-${String(x.getDate()).padStart(2,'0')}`;
  };

  // 預設過濾器套用到所有 view 的入口
  K.applyFilters = function (data, { search = '', engineer = '', machine = '', status = '' } = {}) {
    const s = (search || '').trim().toLowerCase();
    return data.filter((d) => {
      if (s && !d.id.toLowerCase().includes(s) && !d.customer.toLowerCase().includes(s)) return false;
      if (engineer && d.engineer !== engineer) return false;
      if (machine && d.machine !== machine) return false;
      if (status && K.statusOf(d) !== status) return false;
      return true;
    });
  };

  window.K = K;
})();
