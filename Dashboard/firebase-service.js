
// firebase-service.js
// Firebase CRUD 服務層 + 權限工具
// 由 index.html 載入，workboard.js 和 issues.js 共用

(function () {
  // ── 初始化 ──
  function init(cfg) {
    if (window._fbReady) return;
    try {
      firebase.initializeApp(cfg);
      window._fbReady = true;
      window._auth = firebase.auth();
      window._db   = firebase.firestore();
      console.log('[FB] 初始化完成');
    } catch (e) { console.error('[FB] 初始化失敗', e); }
  }
  if (typeof FIREBASE_CONFIG !== 'undefined' &&
      FIREBASE_CONFIG.apiKey &&
      FIREBASE_CONFIG.apiKey !== 'YOUR_API_KEY') {
    init(FIREBASE_CONFIG);
  }

  // ── CRUD factory ──
  function ts()  { return firebase.firestore.FieldValue.serverTimestamp(); }
  function toObj(d) { return Object.assign({ _id: d.id }, d.data()); }

  function makeService(colName) {
    return {
      onSnapshot: function (cb) {
        return window._db.collection(colName).orderBy('seq')
          .onSnapshot(function (snap) { cb(snap.docs.map(toObj)); });
      },
      add: async function (data) {
        var ref = await window._db.collection(colName)
          .add(Object.assign({}, data, { _ts: ts() }));
        return ref.id;
      },
      update: async function (id, data) {
        await window._db.collection(colName).doc(id)
          .update(Object.assign({}, data, { _ts: ts() }));
      },
      del: async function (id) {
        await window._db.collection(colName).doc(id).delete();
      }
    };
  }

  // ── Auth / Users ──
  window.FBAuth = {
    onStateChanged: function (cb) { window._auth.onAuthStateChanged(cb); },
    signIn: async function (email, pw) {
      return await window._auth.signInWithEmailAndPassword(email, pw);
    },
    signOut: async function () { await window._auth.signOut(); },
    getUser: async function (uid) {
      var doc = await window._db.collection('users').doc(uid).get();
      return doc.exists ? toObj(doc) : null;
    },
    getUsers: async function () {
      var snap = await window._db.collection('users').get();
      return snap.docs.map(toObj);
    },
    createUser: async function (email, pw, data) {
      var app2 = firebase.initializeApp(FIREBASE_CONFIG, 'create_' + Date.now());
      try {
        var cred = await app2.auth().createUserWithEmailAndPassword(email, pw);
        await app2.auth().signOut();
        await window._db.collection('users').doc(cred.user.uid)
          .set(Object.assign({}, data, { createdAt: ts() }));
        return cred.user.uid;
      } finally { await app2.delete(); }
    },
    updateUser: async function (uid, data) {
      await window._db.collection('users').doc(uid)
        .update(Object.assign({}, data, { updatedAt: ts() }));
    },
    deleteUser: async function (uid) {
      await window._db.collection('users').doc(uid).delete();
    }
  };

  window.FBOrders    = makeService('orders');
  window.FBAnomalies = makeService('anomalies');
  window.FBIPA       = makeService('ipa_purchases');
  window.FBEquipment = makeService('equipment');

  // ── 權限 ──
  window.hasPerm = function (user, p) {
    if (!user || !user.permissions) return false;
    if (user.permissions.indexOf('admin') >= 0) return true;
    return user.permissions.indexOf(p) >= 0;
  };

  window.PERMS_MAP = {
    view_board:'查看工作看板', edit_board:'編輯工作看板', delete_board:'刪除工作看板',
    view_issues:'查看異常資源', edit_issues:'編輯異常資源', delete_issues:'刪除異常資源',
    view_report:'查看報表', admin:'管理員（所有權限）'
  };
  window.ROLE_PRESETS = {
    admin:    ['admin'],
    manager:  ['view_board','edit_board','view_issues','edit_issues','view_report'],
    operator: ['view_board','edit_board','view_issues','edit_issues'],
    viewer:   ['view_board','view_issues','view_report'],
  };

  // ── Settings (工程師/機台設定，存 Firestore) ──
  window.FBSettings = {
    // 讀取設定（一次性）
    get: async function () {
      var doc = await window._db.collection('settings').doc('workspace').get();
      return doc.exists ? doc.data() : null;
    },
    // 儲存設定
    save: async function (data) {
      await window._db.collection('settings').doc('workspace').set(
        Object.assign({}, data, { _ts: ts() })
      );
    },
    // 即時監聽設定變動（跨裝置同步）
    onSnapshot: function (cb) {
      return window._db.collection('settings').doc('workspace')
        .onSnapshot(function (doc) {
          cb(doc.exists ? doc.data() : null);
        });
    }
  };

  // ── Toast ──
  window.showToast = function (msg, type) {
    type = type || 'ok';
    var c = document.getElementById('toasts');
    if (!c) return;
    var el = document.createElement('div');
    el.className = 'toast-item ' + type;
    el.textContent = (type==='ok'?'✓ ':type==='err'?'✕ ':'ℹ ') + msg;
    c.appendChild(el);
    setTimeout(function () { el.remove(); }, 3200);
  };
})();
