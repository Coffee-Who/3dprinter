# 3D 列印管理平台 — Firebase 版

## 🚀 快速開始

### 1. 建立 Firebase 專案

1. 前往 [Firebase Console](https://console.firebase.google.com/)
2. 點選「新增專案」→ 輸入名稱（例：`3dprinter-dashboard`）
3. 視需要啟用 Google Analytics
4. 建立完成後，點選「</> 網頁應用程式」圖示
5. 複製 `firebaseConfig` 物件

### 2. 填入設定

編輯 `src/firebase/firebase-config.js`：

```javascript
const FIREBASE_CONFIG = {
  apiKey: "AIzaSy...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123:web:abc123"
};
```

### 3. 啟用 Firebase Authentication

Firebase Console → Authentication → Sign-in method → **Email/密碼** → 啟用

### 4. 建立 Firestore 資料庫

Firebase Console → Firestore Database → 建立資料庫 → 選擇區域（建議 `asia-east1`）

### 5. 設定 Security Rules

Firebase Console → Firestore → 規則，貼上以下內容：

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function isAdmin() {
      return request.auth != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid))
          .data.permissions.hasAny(['admin']);
    }
    function hasPermission(perm) {
      return request.auth != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid))
          .data.permissions.hasAny([perm, 'admin']);
    }

    match /users/{userId} {
      allow read: if request.auth != null;
      allow create, update, delete: if isAdmin();
    }
    match /orders/{docId} {
      allow read:  if hasPermission('view_board');
      allow write: if hasPermission('edit_board');
      allow delete: if hasPermission('delete_board');
    }
    match /issues/{docId} {
      allow read:  if hasPermission('view_issues');
      allow write: if hasPermission('edit_issues');
      allow delete: if hasPermission('delete_issues');
    }
    match /ipa_purchases/{docId} {
      allow read:  if hasPermission('view_issues');
      allow write: if hasPermission('edit_issues');
    }
    match /equipment/{docId} {
      allow read:  if hasPermission('view_issues');
      allow write: if hasPermission('edit_issues');
    }
  }
}
```

### 6. 建立第一個管理員帳號

**方法 A：Firebase Console 直接建立（推薦）**

1. Firebase Console → Authentication → Users → 新增使用者
2. 填入 Email 和密碼
3. 複製 User UID
4. Firebase Console → Firestore → 新增 Collection → `users`
5. Document ID = 剛才複製的 UID
6. 填入以下欄位：
   ```
   displayName: "管理員"
   email: "admin@yourcompany.com"
   role: "admin"
   permissions: ["admin"]
   active: true
   ```

**方法 B：首次啟動後於平台建立**

先用任意帳號登入，系統會自動建立基本 user 文件，再到 Firestore 手動加入 `"admin"` 至 permissions 陣列。

---

## 📁 檔案結構

```
.
├── index.html              ← 主入口（登入頁 + Shell + Sidebar）
├── workboard.html          ← 工作看板（可獨立開啟）
├── issues.html             ← 異常與資源（可獨立開啟）
├── admin.html              ← 管理員後台（可獨立開啟）
├── README.md
│
└── src/
    ├── firebase/
    │   ├── firebase-config.js    ← ⚠️ 填入你的 Firebase 設定
    │   └── firebase-service.js   ← Auth + Firestore CRUD
    ├── helpers.js                ← 共用工具、常數
    └── styles/
        ├── styles-shell.css      ← 外殼、登入、Sidebar
        └── styles-admin.css      ← 管理員面板
```

---

## 🔐 權限系統

| 權限代碼 | 說明 |
|---------|------|
| `view_board` | 查看工作看板 |
| `edit_board` | 新增/編輯訂單 |
| `delete_board` | 刪除訂單 |
| `view_issues` | 查看異常資源 |
| `edit_issues` | 新增/編輯異常、IPA、設備 |
| `delete_issues` | 刪除異常資源資料 |
| `view_report` | 查看報表/分析 |
| `admin` | 管理員（包含所有權限） |

### 角色預設

| 角色 | 包含權限 |
|------|---------|
| 👑 管理員 | 全部 |
| 🔷 主管 | 查看/編輯 看板 + 異常資源 + 查看報表 |
| 🔩 工程師 | 查看/編輯 看板 + 異常資源 |
| 👁 檢視者 | 查看 看板 + 異常資源 + 報表 |

---

## 🌐 部署到 GitHub Pages

```bash
git init
git add .
git commit -m "init 3dprinter dashboard"
git remote add origin https://github.com/你的帳號/你的repo.git
git push -u origin main
```

GitHub → Settings → Pages → Branch: main / (root)

---

## 💻 本機測試

```bash
# Python
python3 -m http.server 8000

# Node
npx serve .
```

開啟 `http://localhost:8000/`

---

## ⚠️ 注意事項

- `firebase-config.js` 內的 API Key 為前端設定，請在 Firebase Console 設定適當的 **Application restrictions** 和 **API restrictions**
- 建議設定 Firebase Authentication 的 **Authorized domains**（加入你的 GitHub Pages domain）
- 正式環境請啟用嚴格的 Firestore Security Rules

---

MIT License — 自由使用、修改、商用。
