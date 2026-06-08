// ============================================================
// Firebase Service — 支援 Demo 模式（不需要 Firebase）
// 設定 window.USE_DEMO_MODE = true 即可使用假資料
// ============================================================

(function () {

// ── Demo 假資料 ──
const DEMO_DATA = {
  users: [
    { id: 'admin001', displayName: '管理員', email: 'admin@demo.com', permissions: ['admin'], active: true },
    { id: 'eng001',   displayName: 'Jimmy',  email: 'jimmy@demo.com',  permissions: ['view_board','edit_board','view_issues','edit_issues'], active: true },
    { id: 'eng002',   displayName: 'Jaylen', email: 'jaylen@demo.com', permissions: ['view_board','edit_board','view_issues'], active: true },
    { id: 'viewer01', displayName: '檢視者', email: 'viewer@demo.com', permissions: ['view_board','view_issues'], active: true },
  ],
  orders: [
    { id:'o1',  seq:1,  orderId:'202512100001', customer:'台積電',   engineer:'Jimmy',  dueDate:'2026-06-15', startDate:'2026-06-01', endDate:'2026-06-10', material:'足夠',  progress:75,  machine:'Form4',  complete:'否', remark:'' },
    { id:'o2',  seq:2,  orderId:'202512100002', customer:'聯發科',   engineer:'Jaylen', dueDate:'2026-06-20', startDate:'2026-06-05', endDate:'2026-06-18', material:'足夠',  progress:50,  machine:'Form4L', complete:'否', remark:'' },
    { id:'o3',  seq:3,  orderId:'202512100003', customer:'鴻海精密', engineer:'Bill',   dueDate:'2026-05-30', startDate:'2026-05-20', endDate:'2026-05-28', material:'需調撥',progress:100, machine:'Fuse1+', complete:'是', remark:'已交件' },
    { id:'o4',  seq:4,  orderId:'202512100004', customer:'廣達電腦', engineer:'Barry',  dueDate:'2026-06-08', startDate:'2026-06-01', endDate:'2026-06-07', material:'足夠',  progress:25,  machine:'Mark2',  complete:'否', remark:'' },
    { id:'o5',  seq:5,  orderId:'202512100005', customer:'緯創資通', engineer:'Jimmy',  dueDate:'2026-06-25', startDate:'2026-06-10', endDate:'2026-06-22', material:'足夠',  progress:0,   machine:'Form4',  complete:'否', remark:'' },
    { id:'o6',  seq:6,  orderId:'202512100006', customer:'仁寶電腦', engineer:'Jaylen', dueDate:'2026-06-12', startDate:'2026-06-03', endDate:'2026-06-11', material:'足夠',  progress:90,  machine:'Form4',  complete:'否', remark:'' },
    { id:'o7',  seq:7,  orderId:'202512100007', customer:'英業達',   engineer:'Bill',   dueDate:'2026-05-25', startDate:'2026-05-15', endDate:'2026-05-24', material:'足夠',  progress:100, machine:'Form4L', complete:'是', remark:'' },
    { id:'o8',  seq:8,  orderId:'202512100008', customer:'和碩聯合', engineer:'Barry',  dueDate:'2026-06-30', startDate:'2026-06-15', endDate:'2026-06-28', material:'需調撥',progress:10,  machine:'Fuse1+', complete:'否', remark:'' },
  ],
  issues: [
    { id:'i1', caseNo:'IS-2024-001', customer:'台積電',   engineer:'Jimmy',  issueType:'列印失敗', status:'處理中', description:'第3層出現翹曲', reportDate:'2026-05-20', progressList:[{date:'2026-05-21',note:'已調整支撐設定'},{date:'2026-05-25',note:'重新列印中'}] },
    { id:'i2', caseNo:'IS-2024-002', customer:'聯發科',   engineer:'Jaylen', issueType:'尺寸偏差', status:'待處理', description:'X軸偏差0.3mm',  reportDate:'2026-05-28', progressList:[] },
    { id:'i3', caseNo:'IS-2024-003', customer:'鴻海精密', engineer:'Bill',   issueType:'表面瑕疵', status:'已解決', description:'表面有氣泡',    reportDate:'2026-05-10', progressList:[{date:'2026-05-12',note:'重新列印已解決'}] },
  ],
  ipa_purchases: [
    { id:'p1', date:'2026-05-01', purchaser:'Jimmy',  liters:5, price:2500, supplier:'化工行A', payMethod:'轉帳', remark:'' },
    { id:'p2', date:'2026-05-15', purchaser:'Jaylen', liters:3, price:1500, supplier:'化工行A', payMethod:'現金', remark:'' },
    { id:'p3', date:'2026-06-01', purchaser:'Bill',   liters:8, price:4000, supplier:'化工行B', payMethod:'轉帳', remark:'促銷優惠' },
  ],
  equipment: [
    { id:'e1', name:'刮刀組',     type:'工具', quantity:3, unit:'組', price:350,  purchaseDate:'2026-01-10', condition:'良好', location:'工具櫃A' },
    { id:'e2', name:'樹脂槽',     type:'器材', quantity:2, unit:'個', price:2800, purchaseDate:'2026-02-20', condition:'良好', location:'機台旁' },
    { id:'e3', name:'酒精噴瓶',   type:'工具', quantity:5, unit:'個', price:120,  purchaseDate:'2026-03-05', condition:'良好', location:'清洗區' },
    { id:'e4', name:'Form4 樹脂', type:'耗材', quantity:10,unit:'瓶', price:1800, purchaseDate:'2026-05-01', condition:'良好', location:'倉庫' },
  ],
};

// ── 本地 Store（記憶體） ──
const store = JSON.parse(JSON.stringify(DEMO_DATA)); // deep copy
let listeners = {};

function notify(col) {
  if (listeners[col]) listeners[col](store[col].map(i=>({...i})));
}

function uid() { return 'demo_' + Math.random().toString(36).slice(2); }

// ── Demo Auth ──
const DEMO_USERS_LOGIN = {
  'admin@demo.com':  { password:'admin123',  uid:'admin001' },
  'jimmy@demo.com':  { password:'jimmy123',  uid:'eng001'   },
  'jaylen@demo.com': { password:'jaylen123', uid:'eng002'   },
  'viewer@demo.com': { password:'view123',   uid:'viewer01' },
};

let _currentUser = null;
let _authListeners = [];

const Auth = {
  async login(email, password) {
    const entry = DEMO_USERS_LOGIN[email.toLowerCase()];
    if (!entry || entry.password !== password) throw new Error('Email 或密碼錯誤');
    _currentUser = { uid: entry.uid, email };
    _authListeners.forEach(cb => cb(_currentUser));
    return _currentUser;
  },
  async logout() {
    _currentUser = null;
    _authListeners.forEach(cb => cb(null));
  },
  onAuthStateChanged(cb) {
    _authListeners.push(cb);
    // 不自動觸發，讓頁面顯示登入
    return () => { _authListeners = _authListeners.filter(f=>f!==cb); };
  },
  currentUser() { return _currentUser; },
  async sendPasswordReset(email) {
    console.log('[DEMO] 重設密碼信發送至', email);
  }
};

// ── Demo CRUD factory ──
function makeCollection(col, sortFn) {
  return {
    async getAll() { return store[col].map(i=>({...i})).sort(sortFn||((a,b)=>0)); },
    async create(data) {
      const id = uid();
      const item = { ...data, id, createdAt: new Date(), updatedAt: new Date() };
      store[col].push(item);
      notify(col);
      return id;
    },
    async update(id, data) {
      const idx = store[col].findIndex(i=>i.id===id);
      if (idx>=0) { store[col][idx] = { ...store[col][idx], ...data, updatedAt: new Date() }; notify(col); }
    },
    async delete(id) {
      store[col] = store[col].filter(i=>i.id!==id);
      notify(col);
    },
    onSnapshot(cb) {
      listeners[col] = cb;
      cb(store[col].map(i=>({...i})));
      return () => { delete listeners[col]; };
    }
  };
}

// ── Demo Users ──
const Users = {
  async getAll() { return store.users.map(u=>({...u})); },
  async get(uid) { return store.users.find(u=>u.id===uid) || null; },
  async create(uid, data) {
    store.users.push({ ...data, id: uid, createdAt: new Date() });
  },
  async update(uid, data) {
    const idx = store.users.findIndex(u=>u.id===uid);
    if (idx>=0) store.users[idx] = { ...store.users[idx], ...data };
  },
  async delete(uid) { store.users = store.users.filter(u=>u.id!==uid); }
};

// ── 初始化（空操作，Demo 不需要） ──
function initFirebase() { /* no-op in demo mode */ }

// ── 匯出 ──
window.FB = {
  initFirebase,
  Auth,
  Users,
  Orders:    makeCollection('orders',    (a,b)=>(a.seq||0)-(b.seq||0)),
  Issues:    makeCollection('issues'),
  IPA:       makeCollection('ipa_purchases'),
  Equipment: makeCollection('equipment'),
};

// ── Demo 提示 ──
console.log('%c🎮 Demo 模式已啟用', 'color:#3b82f6;font-size:14px;font-weight:bold;');
console.log('測試帳號：');
Object.entries(DEMO_USERS_LOGIN).forEach(([email, v]) =>
  console.log(`  ${email}  /  ${v.password}`)
);

})();
