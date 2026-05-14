/* 工作異常與資源 — 三類資料 */
(function () {
  // 客戶異常紀錄(含多筆進度)
  window.ISSUES_ANOMALIES = [
    {
      seq: 1, customer: '耿舜企業', date: '2026-01-05',
      product: 'Form 4 Printer', engineer: 'Jimmy', status: '已完成',
      progresses: [
        { date: '2026-01-05', status: '與客戶聯繫中' },
        { date: '2026-01-07', status: '前往客戶端處理完畢' },
      ],
    },
    {
      seq: 2, customer: '台灣迪卡儂', date: '2026-01-13',
      product: 'Tough1500V2', engineer: 'Jimmy', status: '已完成',
      progresses: [
        { date: '2026-01-13', status: '確認為產品設計瑕疵' },
        { date: '2026-01-14', status: '原廠答應替換樹脂罐' },
      ],
    },
    {
      seq: 3, customer: '彥豪智能科技', date: '2026-04-15',
      product: 'Tough2000V2', engineer: 'Jimmy', status: '處理中',
      progresses: [{ date: '2026-04-16', status: '提供客戶樹脂罐支架' }],
    },
    {
      seq: 4, customer: '太宇科技', date: '2026-03-22',
      product: 'Form 4L 樹脂罐', engineer: 'Bill', status: '已完成',
      progresses: [
        { date: '2026-03-22', status: '客戶反應列印失敗率高' },
        { date: '2026-03-25', status: '更換樹脂罐並重新校正' },
      ],
    },
    {
      seq: 5, customer: '群創光電', date: '2026-05-02',
      product: 'Fuse1+ 燒結艙', engineer: 'Jaylen', status: '處理中',
      progresses: [{ date: '2026-05-03', status: '已收件,等待零件到貨' }],
    },
    {
      seq: 6, customer: '宏遠精密', date: '2026-02-18',
      product: 'Mark 2 列印頭', engineer: 'Barry', status: '已完成',
      progresses: [
        { date: '2026-02-19', status: '到場排除' },
        { date: '2026-02-20', status: '回廠校驗完成' },
      ],
    },
    {
      seq: 7, customer: '聯華電子', date: '2026-04-28',
      product: 'IPA 清洗槽異音', engineer: 'Jaylen', status: '暫停',
      progresses: [{ date: '2026-04-29', status: '客戶內部協調中' }],
    },
  ];

  // IPA 採購紀錄
  window.ISSUES_IPA = [
    { seq: 1, purchaseDate: '2025-02-13', useDate: '2025-02-13 ~ 03-18', product: '20L-IPA 異丙醇', quantity: 4, person: 'Jaylen', remark: '' },
    { seq: 2, purchaseDate: '2025-03-18', useDate: '2025-03-18 ~ 04-10', product: '20L-IPA 異丙醇', quantity: 1, person: 'Jaylen', remark: '' },
    { seq: 3, purchaseDate: '2025-04-10', useDate: '2025-04-10 ~ 04-24', product: '20L-IPA 異丙醇', quantity: 1, person: 'Jaylen', remark: '' },
    { seq: 4, purchaseDate: '2025-04-24', useDate: '2025-04-24 ~ 05-08', product: '20L-IPA 異丙醇', quantity: 2, person: 'Barry',  remark: '台中廠加倍備庫' },
    { seq: 5, purchaseDate: '2025-05-12', useDate: '2025-05-12 ~ 進行中', product: '20L-IPA 異丙醇', quantity: 2, person: 'Jaylen', remark: '' },
    { seq: 6, purchaseDate: '2026-01-08', useDate: '2026-01-08 ~ 02-04', product: '20L-IPA 異丙醇', quantity: 3, person: 'Jimmy',  remark: '春節前備料' },
    { seq: 7, purchaseDate: '2026-03-02', useDate: '2026-03-02 ~ 進行中', product: '20L-IPA 異丙醇', quantity: 2, person: 'Bill',   remark: '' },
  ];

  // 台中設備工具清單
  window.ISSUES_TOOLS = [
    { seq: 1, purchaseDate: '2023-08-31', product: '電動筆型散打機',    quantity: 1, method: 'Easy Flow', number: 'E001', remark: '3D 列印研磨用',     price: 2750 },
    { seq: 2, purchaseDate: '2024-08-01', product: '電子游標卡尺',      quantity: 1, method: 'Easy Flow', number: 'E002', remark: '3D 列印量測用',     price: 10920 },
    { seq: 3, purchaseDate: '',           product: '充電式起子機',      quantity: 1, method: '零用金',    number: 'Z001', remark: '設備產品維修用',    price: 1900 },
    { seq: 4, purchaseDate: '2024-11-15', product: '氣動研磨機',        quantity: 1, method: 'Easy Flow', number: 'E003', remark: '後處理用',          price: 5800 },
    { seq: 5, purchaseDate: '2025-02-20', product: '超音波清洗機 6L',   quantity: 1, method: 'Easy Flow', number: 'E004', remark: '小零件清洗',        price: 8400 },
    { seq: 6, purchaseDate: '2025-06-12', product: '熱風槍',            quantity: 2, method: '零用金',    number: 'Z002', remark: '後處理 / 收縮膜',   price: 1280 },
    { seq: 7, purchaseDate: '2025-09-03', product: '電子秤 (10kg)',     quantity: 1, method: 'Easy Flow', number: 'E005', remark: '樹脂計量',          price: 2350 },
  ];
})();
