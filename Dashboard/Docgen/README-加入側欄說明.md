# 文件產生器 — 安裝與側欄整合說明

## 一、檔案擺放（GitHub repo：coffee-who/3dprinter）

把以下 2 個檔案放進 `Dashboard/` 資料夾（跟 index.html 同層）：

```
Dashboard/
 ├ index.html            ← 你原本的儀表板
 ├ docgen-full.html      ← 新增：文件產生器頁面
 └ template.pptx         ← 新增：PPT 底稿範本（本次交付的檔案）
```

push 上 GitHub 後，任何電腦開
`https://coffee-who.github.io/3dprinter/Dashboard/docgen-full.html`
就能直接使用（也可以先不整合側欄、直接用這個網址）。

## 二、加入左側側欄（跟「3D列印估價」同樣做法）

打開 `Dashboard/index.html`：

### 1. 在 NAV 陣列加一個項目
搜尋 `NAV`（側欄項目清單，裡面有 工作看板／異常與資源／3D列印估價…），
**複製「3D列印估價」那一項**，貼在後面並改成：

```jsx
{ key:'docgen', label:'文件產生器', ... }   // icon / sub 照抄估價那項的寫法即可
```

### 2. 在主內容區加 iframe
搜尋 `quote-full.html`（3D列印估價的載入位置），會看到類似：

```jsx
{page==='quote' && <iframe src="quote-full.html" ... />}
```

**複製整行**，貼在下面並改成：

```jsx
{page==='docgen' && <iframe src="docgen-full.html" style={{width:'100%',height:'100%',border:0}} title="文件產生器"/>}
```

（style 直接照抄估價那行的寫法，保持一致即可。）

### 3. 如果 index.html 有用 ?tab= 網址參數
在對應的網址→頁面對照處加上 `docgen`，之後就能用
`index.html?tab=docgen` 直接開啟。

## 三、使用重點

- **PPT 簡報輸入**：畫面即範本頁面，黃底格子直接打字、虛線框點擊／拖曳／Ctrl+V 上傳圖片。
  - P1 說明頁預設不輸出（可勾選輸出）；P3、P4、P9 底稿原樣沿用。
  - 選「評估機型」自動帶入精度標準與各量測組的 RP 規範公差（可手改）。
  - 量測組每 3 組自動排一頁；只有 1 頁時會自動移除範本的第二頁量測頁。
  - 材料頁可「＋加一頁材料」，不換圖時沿用範本 White V5 圖片。
- **同步共用欄位 → Word**：客戶名稱、廠牌/型號、列印時間、完成日期、量測照片與 CAD/誤差一鍵帶入。
- **Word 確認單**輸出 .docx（含資料表、確認項目 V 勾、三視角照片、CAD/誤差、簽名欄）。
- **跨電腦**：設定檔存在各自瀏覽器；要帶到別台電腦用「匯出 JSON → 匯入 JSON」。
- 檔名自動：`日期_客戶公司全名_材料特性與列印尺寸確認.pptx`、`日期_客戶_3D列印服務確認單.docx`。

## 四、注意事項

- `template.pptx` 一定要跟 `docgen-full.html` 同資料夾，否則按「產生 PPT」會提示讀不到範本。
- 直接雙擊本機 html 檔（file://）無法讀取範本；請透過 GitHub Pages 或任何 http 伺服器開啟。
- 若之後範本改版，直接覆蓋 `template.pptx` 即可，但「可輸入的紅圈位置與文字」需維持原本的佔位文字
  （例如儲存格內的「*輸入品牌…」「量測照片」「請輸入是或否」等），程式是靠這些文字定位的。
