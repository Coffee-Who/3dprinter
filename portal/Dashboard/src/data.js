// 工作資料 — 沿用原檔 12 筆 + 補幾筆讓看板各欄都有東西
window.KANBAN_DATA = [
  { seq: 1,  id: '202512100001', customer: '維格工業股份有限公司',         engineer: 'Jimmy',  dueDate: '2026-01-21', startDate: '2026-01-16', endDate: '2026-01-19', material: '足夠',   progress: 100, machine: 'Form4',    complete: '是', remark: '' },
  { seq: 2,  id: '202605080001', customer: '眾里科技股份有限公司',         engineer: 'Bill',   dueDate: '2026-05-18', startDate: '2026-05-08', endDate: '2026-05-08', material: '足夠',   progress: 75,  machine: 'Fuse1+',   complete: '否', remark: '已調撥台北' },
  { seq: 3,  id: '202604100002', customer: '彥豪智能科技股份有限公司',     engineer: 'Jimmy',  dueDate: '2026-04-17', startDate: '',           endDate: '',           material: '需調撥', progress: 0,   machine: 'Mark2',    complete: '否', remark: '待客戶簽回' },
  { seq: 4,  id: '202604000000', customer: '久允工業股份有限公司',         engineer: 'Jimmy',  dueDate: '2026-04-30', startDate: '',           endDate: '',           material: '足夠',   progress: 0,   machine: 'Form4L',   complete: '否', remark: '已取消' },
  { seq: 5,  id: '202601260002', customer: '太宇科技股份有限公司',         engineer: 'Bill',   dueDate: '2026-02-04', startDate: '2026-01-26', endDate: '2026-02-02', material: '足夠',   progress: 100, machine: 'Form4',    complete: '是', remark: '等待樣品調撥' },
  { seq: 6,  id: '202601220001', customer: '太宇科技股份有限公司',         engineer: 'Bill',   dueDate: '2026-02-04', startDate: '2026-01-26', endDate: '2026-02-02', material: '足夠',   progress: 100, machine: 'Form4',    complete: '是', remark: '' },
  { seq: 7,  id: '202601260001', customer: '太宇科技股份有限公司',         engineer: 'Bill',   dueDate: '2026-02-04', startDate: '2026-01-28', endDate: '2026-02-02', material: '足夠',   progress: 50,  machine: 'Form4L',   complete: '否', remark: '' },
  { seq: 8,  id: '202601270001', customer: '博大科技股份有限公司',         engineer: 'Bill',   dueDate: '2026-02-06', startDate: '2026-01-29', endDate: '2026-02-11', material: '足夠',   progress: 100, machine: 'Fuse1+',   complete: '是', remark: '烘烤完成' },
  { seq: 9,  id: '202601290002', customer: '恭勤化學工業股份有限公司',     engineer: 'Jimmy',  dueDate: '2026-02-04', startDate: '2026-01-30', endDate: '2026-02-02', material: '足夠',   progress: 100, machine: 'Form4',    complete: '是', remark: '' },
  { seq: 10, id: '202602040001', customer: '國立中興大學-機械工程系',      engineer: 'Jimmy',  dueDate: '2026-03-12', startDate: '2026-02-12', endDate: '2026-03-13', material: '足夠',   progress: 100, machine: 'Mark2',    complete: '是', remark: '' },
  { seq: 11, id: '202602050003', customer: '鑫元鴻實業股份有限公司',       engineer: 'Jimmy',  dueDate: '2026-03-06', startDate: '2026-02-10', endDate: '2026-03-06', material: '足夠',   progress: 100, machine: 'Form4L',   complete: '是', remark: '' },
  { seq: 12, id: '202602050001', customer: '太宇科技股份有限公司',         engineer: 'Bill',   dueDate: '2026-02-13', startDate: '',           endDate: '',           material: '需調撥', progress: 0,   machine: 'Form4',    complete: '否', remark: '' },
  // 補幾筆讓看板更立體
  { seq: 13, id: '202605120001', customer: '台灣電綜股份有限公司',         engineer: 'Jaylen', dueDate: '2026-05-22', startDate: '2026-05-12', endDate: '',           material: '足夠',   progress: 25,  machine: 'Fuse1+',   complete: '否', remark: '客戶要求加急' },
  { seq: 14, id: '202605130002', customer: '宏遠精密工業',                 engineer: 'Jaylen', dueDate: '2026-05-20', startDate: '2026-05-13', endDate: '',           material: '足夠',   progress: 50,  machine: 'Form4',    complete: '否', remark: '' },
  { seq: 15, id: '202605110003', customer: 'Barry 內部測試件',             engineer: 'Barry',  dueDate: '2026-05-19', startDate: '2026-05-11', endDate: '',           material: '需調撥', progress: 25,  machine: 'Mark2',    complete: '否', remark: '材料下週到貨' },
  { seq: 16, id: '202605140001', customer: '群創光電股份有限公司',         engineer: 'Barry',  dueDate: '2026-05-28', startDate: '',           endDate: '',           material: '足夠',   progress: 0,   machine: 'Form4L',   complete: '否', remark: '' },
  { seq: 17, id: '202605090002', customer: '聯華電子股份有限公司',         engineer: 'Jaylen', dueDate: '2026-05-16', startDate: '2026-05-09', endDate: '',           material: '足夠',   progress: 75,  machine: 'Form4',    complete: '否', remark: '即將完工' },
];
