st.markdown("""
<style>

/* ==============================
🌙 全域背景（桌機 + 手機）
============================== */
html, body, .main, .block-container {
    background-color: #0a0f1c !important;
    color: #e5e7eb !important;
}

/* ==============================
📦 Sidebar（高對比）
============================== */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}

[data-testid="stSidebar"] * {
    color: #e5e7eb !important;
}

/* ==============================
🔤 標題（亮一點）
============================== */
h1, h2, h3, h4 {
    color: #f8fafc !important;
    font-weight: 700;
}

/* ==============================
🏷 Label（次要資訊）
============================== */
label {
    color: #9ca3af !important;
}

/* ==============================
⌨️ 輸入框（高對比）
============================== */
input, textarea, select {
    background-color: #111827 !important;
    color: #f9fafb !important;
    border: 1px solid #374151 !important;
    border-radius: 6px !important;
}

/* selectbox 修正 */
[data-baseweb="select"] > div {
    background-color: #111827 !important;
    color: #f9fafb !important;
}

/* ==============================
🎛 Slider / Radio / Checkbox
============================== */
.stSlider div, .stRadio label, .stCheckbox label {
    color: #e5e7eb !important;
}

/* ==============================
🔘 按鈕（工程風）
============================== */
.stButton>button {
    width: 100%;
    border-radius: 6px;
    font-weight: 600;
    background-color: #1f2937;
    color: #e5e7eb;
    border: 1px solid #374151;
    height: 38px;
    font-size: 13px;
    transition: all .15s;
}

.stButton>button:hover {
    background-color: #2563eb;
    color: #ffffff;
    border-color: #2563eb;
}

/* 主按鈕（亮色） */
div[data-testid="stButton"]:has(button[kind="primary"]) button {
    background:#0081FF !important;
    color:#fff !important;
    border-color:#0059b3 !important;
}

/* ==============================
💰 報價卡片（強對比）
============================== */
.price-container {
    background-color: #111827 !important;
    border: 1px solid #1f2937 !important;
    box-shadow: none !important;
}

.price-result {
    color: #22d3ee !important;
    border-bottom: 2px solid #0081FF !important;
}

/* 數據 */
.data-label {
    color: #6b7280 !important;
}

.data-value {
    color: #f9fafb !important;
}

/* ==============================
📊 成本區
============================== */
.cost-breakdown {
    background: #0f172a !important;
    border: 1px solid #1e293b !important;
}

.cost-row {
    color: #9ca3af !important;
}

.cost-row.total {
    color: #f9fafb !important;
}

/* ==============================
📌 提示區
============================== */
.priority-note {
    background: rgba(59,130,246,0.18) !important;
    color: #93c5fd !important;
    border-left: 3px solid #3b82f6 !important;
}

/* ==============================
📂 File uploader
============================== */
[data-testid="stFileUploader"] {
    background-color: #111827 !important;
    border: 1px dashed #374151 !important;
}

/* ==============================
⚠️ 提示框
============================== */
.stAlert {
    background-color: #1f2937 !important;
    color: #e5e7eb !important;
    border: 1px solid #374151 !important;
}

/* ==============================
📏 Divider
============================== */
hr {
    border-color: #1f2937 !important;
}

/* ==============================
🧾 Dataframe
============================== */
[data-testid="stDataFrame"] {
    background-color: #0f172a !important;
}

/* ==============================
🖱 Scrollbar（高質感）
============================== */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #0f172a;
}
::-webkit-scrollbar-thumb {
    background: #374151;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #4b5563;
}

</style>
""", unsafe_allow_html=True)
