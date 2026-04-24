import streamlit as st
from utils.embedder import get_embedding
from utils.supabase_db import search_chunks, get_all_documents, get_client
from utils.groq_llm import generate_answer

st.set_page_config(
    page_title="實威國際 AI 知識庫",
    page_icon="🧠",
    layout="centered"
)

# ── 樣式 ──
st.markdown("""
<style>
.main-title {
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(135deg, #4f7cff, #00c8e0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}
.sub-title { color: #8890b8; font-size: 0.9rem; margin-bottom: 2rem; }
.answer-box {
    background: #0d1020; border: 1px solid #1e2440;
    border-radius: 12px; padding: 1.2rem 1.4rem;
    margin-top: 1rem; line-height: 1.8;
}
.source-chip {
    display: inline-block;
    background: rgba(0,200,224,0.1); color: #00c8e0;
    border: 1px solid rgba(0,200,224,0.25);
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.75rem; margin: 2px;
}
.stat-box {
    background: #0d1020; border: 1px solid #1e2440;
    border-radius: 8px; padding: 0.8rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ── 標題 ──
st.markdown('<div class="main-title">🧠 實威國際 AI 知識庫</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">智能語意搜尋 · 支援中英文 · 整合文件與網站資料</div>', unsafe_allow_html=True)

# ── 統計 ──
try:
    docs = get_all_documents()
    file_count = len([d for d in docs if d['source_type'] == 'file'])
    web_count  = len([d for d in docs if d['source_type'] == 'website'])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="stat-box"><div style="font-size:1.5rem;font-weight:700;color:#4f7cff">{len(docs)}</div><div style="font-size:0.75rem;color:#8890b8">知識庫總數</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div style="font-size:1.5rem;font-weight:700;color:#00c8e0">{file_count}</div><div style="font-size:0.75rem;color:#8890b8">文件數量</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div style="font-size:1.5rem;font-weight:700;color:#00d68f">{web_count}</div><div style="font-size:0.75rem;color:#8890b8">網站來源</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
except:
    pass

# ── 搜尋框 ──
query = st.text_input(
    "輸入問題",
    placeholder="例如：光固化擺放角度、resin printing support density、材料儲存方式...",
    label_visibility="collapsed"
)

col_a, col_b, col_c = st.columns([2, 2, 1])
with col_a:
    result_count = st.slider("搜尋段落數", 3, 10, 5, label_visibility="visible")
with col_b:
    threshold = st.slider("相似度門檻", 0.1, 0.9, 0.3, 0.05)
with col_c:
    st.markdown("<br>", unsafe_allow_html=True)
    search_btn = st.button("🔍 搜尋", use_container_width=True, type="primary")

# ── 範例問題 ──
st.markdown("**常見問題：**")
hints = ["光固化擺放角度建議", "Formlabs 機台維護步驟", "resin printing support settings", "樹脂材料儲存方式", "列印失敗原因排查"]
cols = st.columns(len(hints))
for i, hint in enumerate(hints):
    with cols[i]:
        if st.button(hint, key=f"hint_{i}", use_container_width=True):
            query = hint
            search_btn = True

# ── 執行搜尋 ──
if search_btn and query:
    with st.spinner("🤔 AI 正在分析語意並搜尋知識庫..."):
        try:
            # 1. 問題向量化
            query_embedding = get_embedding(query)

            # 2. 向量搜尋
            chunks = search_chunks(query_embedding, match_count=result_count, threshold=threshold)

            # 3. 取得來源標題
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

            # 4. AI 生成回答
            answer = generate_answer(query, chunks)

            # ── 顯示結果 ──
            st.markdown("---")
            st.markdown("### 💡 AI 回答")
            st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

            # 來源
            if chunks:
                st.markdown("<br>**參考來源：**", unsafe_allow_html=True)
                seen = set()
                for c in chunks:
                    title = c.get('source_title', '')
                    if title not in seen:
                        seen.add(title)
                        icon = "🌐" if c.get('source_type') == 'website' else "📄"
                        url = c.get('source_url', '')
                        if url:
                            st.markdown(f'<span class="source-chip">{icon} <a href="{url}" target="_blank" style="color:#00c8e0;text-decoration:none">{title}</a></span>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<span class="source-chip">{icon} {title}</span>', unsafe_allow_html=True)

            # 相關段落展開
            if chunks:
                with st.expander(f"📋 查看 {len(chunks)} 個相關段落"):
                    for i, c in enumerate(chunks):
                        st.markdown(f"**段落 {i+1}** · 來源：{c.get('source_title','')} · 相似度：{c.get('similarity',0):.2f}")
                        st.markdown(f"> {c['content'][:300]}...")
                        st.markdown("---")

        except Exception as e:
            st.error(f"搜尋失敗：{e}")

elif search_btn and not query:
    st.warning("請輸入問題！")

# ── 頁尾 ──
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#454e78;font-size:0.75rem">'
    '© 2025 實威國際股份有限公司 · Powered by Groq Llama3 + Supabase pgvector'
    '</div>',
    unsafe_allow_html=True
)
