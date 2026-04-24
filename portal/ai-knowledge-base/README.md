# 🧠 實威國際 AI 知識庫查詢系統

智能語意搜尋系統，整合文件與網站資料，支援中英文跨語言查詢。

## 技術架構
- **前台搜尋**：Streamlit + Groq Llama3
- **後台管理**：Streamlit 管理介面
- **向量資料庫**：Supabase pgvector
- **網站爬取**：Firecrawl
- **向量化模型**：sentence-transformers（多語言）

## 使用方式

### 前台搜尋
```
streamlit run app.py
```

### 後台管理
```
streamlit run admin.py
```

## 部署
本系統部署於 Streamlit Cloud，連接 GitHub 自動更新。
