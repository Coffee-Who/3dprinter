import streamlit as st
from utils.embedder import get_embedding
from utils.supabase_db import search_chunks, get_all_documents, get_client
from utils.groq_llm import generate_answer

st.set_page_config(
    page_title="實威國際 AI 知識庫",
    page_icon="🧠",
    layout="centered"
)

st.markdown("""
<style>
/* ── 全域重置 ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
    color: #1a1a1a !important;
}
[data-testid="stAppViewContainer"] {
    max-width: 100% !important;
    padding: 0 !important;
}
[data-testid="stMain"] {
    background-color: #ffffff !important;
}
section.main > div {
    padding: 0 !important;
}

/* ── 響應式外層容器 ── */
.page-wrapper {
    width: 100%;
    max-width: 860px;
    margin: 0 auto;
    padding: 24px 16px 60px;
    box-sizing: border-box;
}

/* ── Header ── */
.kb-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
}
.kb-icon {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #2563eb, #06b6d4);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
}
.kb-title {
    font-size: clamp(20px, 4vw, 28px);
    font-weight: 700; color: #111827;
    letter-spacing: -0.5px; margin: 0;
}
.kb-subtitle {
    font-size: 13px; color: #6b7280;
    margin-bottom: 24px; margin-left: 56px;
}

/* ── 統計卡片 ── */
.stats-row {
    display: flex; gap: 12px;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.stat-card {
    flex: 1; min-width: 100px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 14px 16px;
    text-align: center;
}
.stat-num {
    font-size: 24px; font-weight: 700;
    color: #2563eb; line-height: 1;
}
.stat-label {
    font-size: 11px; color: #9ca3af;
    margin-top: 4px; font-weight: 500;
    text-transform: uppercase; letter-spacing: .5px;
}

/* ── 搜尋框 ── */
.search-wrap {
    background: #ffffff;
    border: 1.5px solid #d1d5db;
    border-radius: 12px;
    padding: 4px 4px 4px 16px;
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,.06);
    transition: border-color .2s;
}
.search-wrap:focus-within {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37,99,235,.1);
}

/* Streamlit input 覆寫 */
[data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #111827 !important;
    font-size: 15px !important;
    padding: 10px 0 !important;
}
[data-testid="stTextInput"] input::placeholder { color: #9ca3af !important; }
[data-testid="stTextInput"] > div { border: none !important; box-shadow: none !important; background: transparent !important; }

/* ── 控制列 ── */
.controls-row {
    display: flex; gap: 16px; align-items: flex-end;
    margin-bottom: 20px; flex-wrap: wrap;
}
.controls-row > div { flex: 1; min-width: 140px; }

/* Slider 標籤顏色 */
[data-testid="stSlider"] label { color: #374151 !important; font-size: 13px !important; }
[data-testid="stSlider"] [data-testid="stMarkdownContainer"] p { color: #374151 !important; }

/* ── 範例問題 ── */
.hints-label {
    font-size: 12px; font-weight: 600;
    color: #6b7280; margin-bottom: 8px;
    text-transform: uppercase; letter-spacing: .5px;
}
/* hint 按鈕樣式 */
[data-testid="stButton"] button {
    background: #f3f4f6 !important;
    color: #374151 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 20px !important;
    font-size: 12px !important;
    padding: 4px 12px !important;
    transition: all .15s !important;
}
[data-testid="stButton"] button:hover {
    background: #eff6ff !important;
    color: #2563eb !important;
    border-color: #bfdbfe !important;
}
/* 主要搜尋按鈕 */
[data-testid="stButton"].primary button,
button[kind="primary"] {
    background: #2563eb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    padding: 8px 20px !important;
}
button[kind="primary"]:hover {
    background: #1d4ed8 !important;
}

/* ── 分隔線 ── */
hr { border: none; border-top: 1px solid #f3f4f6; margin: 20px 0; }

/* ── 回答卡片 ── */
.answer-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,.06);
    margin-top: 16px;
}
.answer-header {
    background: #f9fafb;
    border-bottom: 1px solid #e5e7eb;
    padding: 12px 18px;
    display: flex; align-items: center; gap: 8px;
}
.answer-tag {
    background: #eff6ff; color: #2563eb;
    border: 1px solid #bfdbfe;
    border-radius: 5px; font-size: 11px;
    font-weight: 700; padding: 2px 8px;
    text-transform: uppercase; letter-spacing: .5px;
}
.answer-query { font-size: 13px; color: #6b7280; }
.answer-query strong { color: #374151; }
.answer-body {
    padding: 20px 20px;
    font-size: 14px; line-height: 1.85;
    color: #1f2937;
    max-height: 520px; overflow-y: auto;
}
.answer-body::-webkit-scrollbar { width: 4px; }
.answer-body::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 2px; }
.answer-footer {
    background: #f9fafb;
    border-top: 1px solid #e5e7eb;
    padding: 10px 18px;
    display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 8px;
}
.src-label {
    font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: .5px; color: #9ca3af;
    margin-right: 6px;
}
.src-chip {
    display: inline-flex; align-items: center; gap: 4px;
    background: #ecfdf5; color: #059669;
    border: 1px solid #a7f3d0;
    border-radius: 20px; padding: 2px 10px;
    font-size: 11px; margin: 2px;
}
.src-chip a { color: #059669 !important; text-decoration: none; }
.meta-stat { font-size: 11px; color: #9ca3af; }

/* ── 錯誤卡片 ── */
.err-card {
    background: #fef2f2; border: 1px solid #fecaca;
    border-radius: 10px; padding: 14px 18px;
    color: #dc2626; font-size: 13px;
    display: flex; align-items: flex-start; gap: 10px;
    margin-top: 12px;
}

/* ── 段落展開 ── */
[data-testid="stExpander"] {
    border: 1px solid #e5e7eb !important;
    border-radius: 10px !important;
    background: #fafafa !important;
}
[data-testid="stExpander"] summary { color: #374151 !important; }

/* ── 頁尾 ── */
.kb-footer {
    text-align: center; color: #9ca3af;
    font-size: 11px; margin-top: 40px;
    padding-top: 20px; border-top: 1px solid #f3f4f6;
}

/* ── 響應式 ── */
@media (max-width: 600px) {
    .page-wrapper { padding: 16px 12px 40px; }
    .kb-subtitle { margin-left: 0; }
    .stats-row { gap: 8px; }
    .stat-card { padding: 10px 8px; }
    .stat-num { font-size: 20px; }
    .controls-row { gap: 10px; }
    .answer-body { font-size: 13px; padding: 14px; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════
# HEADER
# ══════════════════════════════════
st.markdown("""
<div class="page-wrapper">
<div class="kb-header">
  <div class="kb-icon">🧠</div>
  <h1 class="kb-title">實威國際 AI 知識庫</h1>
</div>
<div class="kb-subtitle">智能語意搜尋 · 支援中英文 · 整合文件與網站資料</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════
# 統計
# ══════════════════════════════════
try:
    docs = get_all_documents()
    file_count = len([d for d in docs if d['source_type'] == 'file'])
    web_count  = len([d for d in docs if d['source_type'] == 'website'])
    st.markdown(f"""
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-num">{len(docs)}</div>
        <div class="stat-label">知識庫總數</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:#7c3aed">{file_count}</div>
        <div class="stat-label">文件數量</div>
      </div>
      <div class="stat-card">
        <div class="stat-num" style="color:#059669">{web_count}</div>
        <div class="stat-label">網站來源</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
except:
    pass

# ══════════════════════════════════
# 搜尋框
# ══════════════════════════════════
query = st.text_input(
    "search",
    placeholder="輸入問題…例如：光固化擺放角度、resin support settings、材料儲存方式",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    result_count = st.slider("搜尋段落數", 3, 10, 5)
with col2:
    threshold = st.slider("相似度門檻", 0.1, 0.9, 0.3, 0.05)
with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("🔍 搜尋", type="primary", use_container_width=True)

# ══════════════════════════════════
# 範例問題
# ══════════════════════════════════
st.markdown('<div class="hints-label">常見問題</div>', unsafe_allow_html=True)
hints = ["光固化擺放角度建議", "Formlabs 機台維護步驟", "resin support settings", "樹脂材料儲存方式", "列印失敗原因排查"]
cols = st.columns(len(hints))
for i, hint in enumerate(hints):
    with cols[i]:
        if st.button(hint, key=f"hint_{i}", use_container_width=True):
            query = hint
            search_btn = True

# ══════════════════════════════════
# 搜尋執行
# ══════════════════════════════════
if search_btn and query:
    with st.spinner("🤔 AI 正在分析語意並搜尋知識庫..."):
        try:
            query_embedding = get_embedding(query)
            chunks = search_chunks(query_embedding, match_count=result_count, threshold=threshold)

            if chunks:
                db = get_client()
                doc_ids = list(set(c['document_id'] for c in chunks))
                docs_result = db.table("documents").select("id,title,source_type,source_url").in_("id", doc_ids).execute()
                doc_map = {d['id']: d for d in (docs_result.data or [])}
                for c in chunks:
                    doc = doc_map.get(c['document_id'], {})
                    c['source_title'] = doc.get('title', '未知來源')
                    c['source_type']  = doc.get('source_type', 'file')
                    c['source_url']   = doc.get('source_url', '')

            answer = generate_answer(query, chunks)

            # 來源整理
            seen = {}
            for c in chunks:
                t = c.get('source_title', '')
                if t and t not in seen:
                    seen[t] = c

            src_chips = ""
            for title, c in seen.items():
                icon = "🌐" if c.get('source_type') == 'website' else "📄"
                url  = c.get('source_url', '')
                label = title[:35] + ('…' if len(title) > 35 else '')
                if url:
                    src_chips += f'<span class="src-chip">{icon} <a href="{url}" target="_blank">{label}</a></span>'
                else:
                    src_chips += f'<span class="src-chip">{icon} {label}</span>'

            if not src_chips:
                src_chips = '<span class="src-chip" style="background:#f9fafb;color:#9ca3af;border-color:#e5e7eb">AI 知識推理</span>'

            # 回答顯示
            import html as htmllib
            answer_html = htmllib.escape(answer)\
                .replace('**', '<strong>', 1)
            # 簡單 markdown 轉換
            import re
            answer_safe = answer\
                .replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
            answer_safe = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', answer_safe)
            answer_safe = re.sub(r'^### (.+)$', r'<h4 style="color:#2563eb;margin:12px 0 6px">\1</h4>', answer_safe, flags=re.MULTILINE)
            answer_safe = re.sub(r'^## (.+)$',  r'<h4 style="color:#2563eb;margin:12px 0 6px">\1</h4>', answer_safe, flags=re.MULTILINE)
            answer_safe = re.sub(r'^# (.+)$',   r'<h4 style="color:#2563eb;margin:12px 0 6px">\1</h4>', answer_safe, flags=re.MULTILINE)
            answer_safe = re.sub(r'^[\-\*] (.+)$', r'<li>\1</li>', answer_safe, flags=re.MULTILINE)
            answer_safe = re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul style="padding-left:18px;margin:8px 0">{m.group()}</ul>', answer_safe, flags=re.DOTALL)
            answer_safe = answer_safe.replace('\n\n', '</p><p>').replace('\n', '<br>')
            answer_safe = f'<p>{answer_safe}</p>'

            st.markdown(f"""
            <div class="answer-card">
              <div class="answer-header">
                <span class="answer-tag">AI 回答</span>
                <span class="answer-query">搜尋：<strong>{query[:60]}</strong></span>
              </div>
              <div class="answer-body">{answer_safe}</div>
              <div class="answer-footer">
                <div>
                  <span class="src-label">來源</span>
                  {src_chips}
                </div>
                <span class="meta-stat">知識庫搜尋 · {len(chunks)} 段落</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            if chunks:
                with st.expander(f"📋 查看 {len(chunks)} 個相關段落"):
                    for i, c in enumerate(chunks):
                        st.markdown(f"**段落 {i+1}** · 來源：{c.get('source_title','')} · 相似度：`{c.get('similarity',0):.2f}`")
                        st.markdown(f"> {c['content'][:300]}...")
                        st.divider()

        except Exception as e:
            st.markdown(f"""
            <div class="err-card">
              <span>✕</span>
              <div><strong>搜尋失敗</strong><br><span style="font-size:12px">{e}</span></div>
            </div>
            """, unsafe_allow_html=True)

elif search_btn and not query:
    st.warning("請輸入問題！")

# ══════════════════════════════════
# 頁尾
# ══════════════════════════════════
st.markdown("""
<div class="kb-footer">
  © 2025 實威國際股份有限公司 · Powered by Groq Llama3 + Supabase pgvector
</div>
</div>
""", unsafe_allow_html=True)
