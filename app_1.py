# 4. 主介面高級 CSS 調校 (修復字體遮擋問題)
st.markdown("""
    <style>
    /* 1. 當前體積 (Metric) */
    [data-testid="stMetricValue"] {
        font-size: 42px !important;
        font-weight: 800 !important;
        color: #1E40AF !important;
    }

    /* 2. 修復材料選擇框 (Selectbox) 文字遮擋 */
    /* 強制增加容器高度並調整行高讓文字置中 */
    div[data-baseweb="select"] > div {
        font-size: 42px !important;
        font-weight: 800 !important;
        color: #1E40AF !important;
        height: 85px !important;     /* 強制增加高度 */
        display: flex !important;
        align-items: center !important; /* 垂直置中 */
        line-height: 85px !important;  /* 確保行高足夠 */
    }
    
    /* 調整選擇框內部的文字顯示區域 */
    div[data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        font-size: 36px !important; /* 稍微縮小一點點確保安全 */
        font-weight: 800 !important;
        color: #1E40AF !important;
    }

    /* 3. 基本費輸入框 (NumberInput) */
    div[data-testid="stNumberInput"] input {
        font-size: 42px !important;
        font-weight: 800 !important;
        color: #1E40AF !important;
        height: 85px !important; /* 與選擇框同步高度 */
    }

    /* 輔助樣式 */
    .big-font { font-size: 24px !important; font-weight: bold !important; color: #1E40AF !important; }
    .material-price-info { font-size: 16px; color: #64748B; font-weight: bold; margin-top: 5px; }

    .result-container {
        background-color: #FFFFFF; padding: 30px; border-radius: 15px;
        border: 1px solid #E2E8F0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)
