# 3D 列印 · 工作管理平台

## 檔案結構

```
Dashboard/
├── index.html            ← 主入口（登入 + Shell + 管理員後台）
├── workboard.js          ← 工作看板元件（可獨立編輯）
├── issues.js             ← 異常與資源元件（可獨立編輯）
├── firebase-service.js   ← Firebase CRUD 服務層（共用）
├── firebase-config.js    ← ⚠️ 填入你的 Firebase 設定
└── README.md
```

## 各檔案職責

| 檔案 | 說明 | 何時需要修改 |
|------|------|-------------|
| `firebase-config.js` | Firebase 連線設定 | 換專案時 |
| `firebase-service.js` | Firestore CRUD / Auth / 權限 | 新增 Collection 時 |
| `workboard.js` | 工作看板 UI + 新增/編輯/刪除訂單 | 修改看板功能時 |
| `issues.js` | 異常/IPA/設備 UI + CRUD | 修改異常資源功能時 |
| `index.html` | 登入頁 / Sidebar / 管理員後台 | 修改框架 / 新增頁面時 |

## 快速開始

1. 填寫 `firebase-config.js`
2. Firebase Console → Authentication → 啟用 Email/密碼
3. Firestore → 建立管理員 users 文件（見下方說明）
4. 上傳全部檔案到 GitHub Pages

## 建立管理員

Authentication → 新增使用者 → 複製 UID

Firestore → `users` collection → 新增文件（Document ID = UID）：

```
displayName: "管理員"
email:       "your@email.com"
permissions: ["admin"]
active:      true
```

## Firestore Security Rules

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function hasPerm(p) {
      return request.auth != null &&
        get(/databases/$(database)/documents/users/$(request.auth.uid))
          .data.permissions.hasAny([p, 'admin']);
    }
    match /users/{uid} {
      allow read: if request.auth != null;
      allow write: if hasPerm('admin');
    }
    match /orders/{id} {
      allow read:   if hasPerm('view_board');
      allow write:  if hasPerm('edit_board');
      allow delete: if hasPerm('delete_board');
    }
    match /anomalies/{id} {
      allow read:   if hasPerm('view_issues');
      allow write:  if hasPerm('edit_issues');
      allow delete: if hasPerm('delete_issues');
    }
    match /ipa_purchases/{id} {
      allow read:  if hasPerm('view_issues');
      allow write: if hasPerm('edit_issues');
    }
    match /equipment/{id} {
      allow read:  if hasPerm('view_issues');
      allow write: if hasPerm('edit_issues');
    }
  }
}
```
