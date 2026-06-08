// ============================================================
// helpers.js — 共用工具、常數、狀態判定
// ============================================================

const K = {};

K.TODAY = new Date(); // 改成 new Date('2026-05-14') 可固定日期

// 工程師
K.ENG_ORDER  = ['Jimmy', 'Jaylen', 'Bill', 'Barry'];
K.ENG_LABEL  = { Jimmy:'Jimmy', Jaylen:'Jaylen', Bill:'Bill', Barry:'Barry' };
K.ENG_TONE   = { Jimmy:'#3b82f6', Jaylen:'#10b981', Bill:'#f59e0b', Barry:'#8b5cf6' };

// 機台
K.MACHINES = ['Form4', 'Form4L', 'Fuse1+', 'Mark2'];

// 狀態色
K.STATUS_COLOR = {
  '未開始':'#94a3b8',
  '進行中':'#3b82f6',
  '已完成':'#10b981',
  '逾期':  '#ef4444',
  '暫停':  '#f59e0b',
};

// 素材
K.MATERIALS = ['足夠','需調撥'];

// 進度選項
K.PROGRESS_OPTS = [0,25,50,75,100];

// 異常狀態
K.ISSUE_STATUS = ['待處理','處理中','已解決','關閉'];

// 設備類型
K.EQUIPMENT_TYPES = ['工具','器材','耗材','其他'];

// 付款方式
K.PAYMENT_METHODS = ['現金','轉帳','信用卡','其他'];

// 權限清單
K.PERMISSIONS = {
  view_board:   '查看工作看板',
  edit_board:   '編輯工作看板',
  delete_board: '刪除工作看板資料',
  view_issues:  '查看異常資源',
  edit_issues:  '編輯異常資源',
  delete_issues:'刪除異常資源',
  view_report:  '查看報表',
  admin:        '管理員（所有權限）',
};

// 預設權限組合
K.ROLE_PRESETS = {
  admin:    Object.keys(K.PERMISSIONS),
  manager:  ['view_board','edit_board','view_issues','edit_issues','view_report'],
  operator: ['view_board','edit_board','view_issues','edit_issues'],
  viewer:   ['view_board','view_issues','view_report'],
};

// ---- 工具函式 ----

K.today = () => new Date(K.TODAY);

K.fmt = (d) => {
  if (!d) return '';
  const dt = d.toDate ? d.toDate() : new Date(d);
  return dt.toLocaleDateString('zh-TW', { year:'numeric', month:'2-digit', day:'2-digit' });
};

K.fmtDateTime = (d) => {
  if (!d) return '';
  const dt = d.toDate ? d.toDate() : new Date(d);
  return dt.toLocaleString('zh-TW', { year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' });
};

K.daysLeft = (dueDate) => {
  if (!dueDate) return null;
  const due = new Date(dueDate);
  const diff = Math.round((due - K.today()) / 86400000);
  return diff;
};

K.orderStatus = (order) => {
  if (order.complete === '是') return '已完成';
  const d = K.daysLeft(order.dueDate);
  if (d === null) return '未開始';
  if (order.progress === 0) return '未開始';
  if (d < 0) return '逾期';
  return '進行中';
};

K.progressColor = (pct) => {
  if (pct >= 100) return '#10b981';
  if (pct >= 75)  return '#3b82f6';
  if (pct >= 50)  return '#f59e0b';
  if (pct >= 25)  return '#fb923c';
  return '#ef4444';
};

K.hasPermission = (user, perm) => {
  if (!user) return false;
  if (!user.permissions) return false;
  if (user.permissions.includes('admin')) return true;
  return user.permissions.includes(perm);
};

K.uuid = () => Math.random().toString(36).slice(2);

K.nextSeq = (orders) => {
  if (!orders || orders.length === 0) return 1;
  return Math.max(...orders.map(o => o.seq || 0)) + 1;
};

K.exportCSV = (rows, filename = 'export.csv') => {
  if (!rows || rows.length === 0) return;
  const keys = Object.keys(rows[0]).filter(k => !['id','createdAt','updatedAt'].includes(k));
  const header = keys.join(',');
  const body = rows.map(r => keys.map(k => {
    const v = r[k] ?? '';
    return String(v).includes(',') ? `"${v}"` : v;
  }).join(',')).join('\n');
  const blob = new Blob(['\uFEFF' + header + '\n' + body], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
};

window.K = K;
