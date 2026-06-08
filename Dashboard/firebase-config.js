// ============================================================
//  firebase-config.js
//  請將下方設定換成你自己 Firebase 專案的內容
//  取得方式：Firebase Console → 專案設定 → 你的應用程式 → firebaseConfig
// ============================================================
const FIREBASE_CONFIG = {
  apiKey:            "YOUR_API_KEY",
  authDomain:        "YOUR_PROJECT_ID.firebaseapp.com",
  projectId:         "YOUR_PROJECT_ID",
  storageBucket:     "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId:             "YOUR_APP_ID"
};

// ============================================================
//  Firestore Collections 說明
// ============================================================
// users/          → 使用者帳號與權限
// orders/         → 工作看板訂單
// anomalies/      → 客戶異常
// ipa_purchases/  → IPA 採購
// equipment/      → 設備清單
// ============================================================
