import streamlit as st
import pypdf
import io
from utils.embedder import get_embedding, chunk_text
from utils.supabase_db import (
    insert_document, insert_chunks, get_all_documents,
    delete_document, get_document_chunk_count,
    insert_crawl_job, update_crawl_job, get_crawl_jobs
)
from utils.firecrawl import crawl_website

st.set_page_config(
    page_title="知識庫後台管理",
    page_icon="⚙️",
    layout="wide"
)

st.markdown("""
<style>
.admin-title { font-size:1.6rem; font-weight:700; color:#2563eb; }
</style>
""", unsafe_allow_html=True)

# ── 登入驗證 ──
if "admin_auth" not in st.session_state:
    st.session_state.admin_auth = False

if not st.session_state.admin_auth:
    st.markdown('<div class="admin-title">🔐 後台管理登入</div>', unsafe_allow_html=True)
    pwd = st.text_input("管理員密碼", type="password")
    if st.button("登入", type="primary"):
        if pwd == st.secrets.get("ADMIN_PASSWORD", "admin123"):
            st.session_state.admin_auth = True
            st.rerun()
        else:
            st.error("密碼錯誤")
    st.stop()

# ── 後台主頁 ──
st.markdown('<div class="admin-title">⚙️ 知識庫後台管理</div>', unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📄 文件管理", "🌐 網站爬取", "📊 資料總覽"])

# ════════════════════════════════
# TAB 1：文件管理
# ════════════════════════════════
with tab1:
    st.markdown("### 上傳文件")
    st.markdown("支援 **TXT** 和 **PDF** 格式，上傳後自動切段並向量化存入知識庫。")

    uploaded_files = st.file_uploader(
        "拖曳或選擇文件",
        type=["txt", "pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        if st.button("🚀 開始上傳並建立向量索引", type="primary"):
            for file in uploaded_files:
                with st.status(f"處理中：{file.name}...", expanded=True) as status:
                    try:
                        st.write("📖 讀取文件內容...")

                        if file.name.endswith(".pdf"):
                            pdf_reader = pypdf.PdfReader(io.BytesIO(file.read()))
                            text = "\n".join(p.extract_text() or "" for p in pdf_reader.pages)
                        else:
                            # 自動偵測編碼
                            raw = file.read()
                            text = None
                            for enc in ["utf-8", "utf-8-sig", "big5", "cp950", "gbk"]:
                                try:
                                    text = raw.decode(enc)
                                    st.write(f"   編碼：{enc}")
                                    break
                                except:
                                    continue
                            if text is None:
                                text = raw.decode("utf-8", errors="ignore")

                        if not text.strip():
                            st.error("文件內容為空，跳過")
                            continue

                        st.write("✂️ 切割段落...")
                        chunks = chunk_text(text, chunk_size=300, overlap=30)
                        st.write(f"   共 {len(chunks)} 個段落")

                        st.write("🔢 向量化中（Jina AI）...")
                        embeddings = []
                        for i, c in enumerate(chunks):
                            emb = get_embedding(c)
                            embeddings.append(emb)
                            if (i+1) % 5 == 0:
                                st.write(f"   已完成 {i+1}/{len(chunks)}")

                        st.write("💾 存入 Supabase...")
                        doc_id = insert_document(
                            title=file.name,
                            source_type="file"
                        )
                        insert_chunks(doc_id, chunks, embeddings)

                        status.update(
                            label=f"✅ {file.name} 完成！{len(chunks)} 段落已建立索引",
                            state="complete"
                        )

                    except Exception as e:
                        status.update(label=f"❌ {file.name} 失敗：{e}", state="error")

    st.markdown("---")
    st.markdown("### 已上傳文件")

    docs = get_all_documents()
    file_docs = [d for d in docs if d['source_type'] == 'file']

    if not file_docs:
        st.info("尚未上傳任何文件")
    else:
        for doc in file_docs:
            col1, col2, col3 = st.columns([5, 2, 1])
            with col1:
                st.markdown(f"📄 **{doc['title']}**")
                st.caption(f"建立時間：{doc['created_at'][:19]}")
            with col2:
                try:
                    count = get_document_chunk_count(doc['id'])
                    st.markdown(f"`{count} 段落`")
                except:
                    pass
            with col3:
                if st.button("🗑", key=f"del_{doc['id']}", help="刪除此文件"):
                    delete_document(doc['id'])
                    st.success("已刪除")
                    st.rerun()

# ════════════════════════════════
# TAB 2：網站爬取
# ════════════════════════════════
with tab2:
    st.markdown("### 新增網站爬取任務")
    st.markdown("輸入網址後，Firecrawl 會自動爬取多頁內容並建立向量索引。")

    col1, col2 = st.columns([4, 1])
    with col1:
        url_input = st.text_input("網站網址", placeholder="https://support.formlabs.com")
    with col2:
        max_pages = st.number_input("最多爬取頁數", min_value=1, max_value=50, value=10)

    if st.button("🕷️ 開始爬取", type="primary"):
        if not url_input:
            st.warning("請輸入網址")
        else:
            job_id = insert_crawl_job(url_input, max_pages)
            with st.status(f"爬取中：{url_input}...", expanded=True) as status:
                try:
                    update_crawl_job(job_id, "running")
                    st.write(f"🌐 開始爬取，最多 {max_pages} 頁...")

                    pages = crawl_website(url_input, max_pages)
                    st.write(f"✅ 爬取完成，共 {len(pages)} 頁")

                    total_chunks = 0
                    for i, page in enumerate(pages):
                        st.write(f"🔢 向量化第 {i+1}/{len(pages)} 頁：{page['title'][:40]}...")
                        chunks = chunk_text(page['content'], chunk_size=300, overlap=30)
                        embeddings = [get_embedding(c) for c in chunks]
                        doc_id = insert_document(
                            title=page['title'],
                            source_type="website",
                            source_url=page['url']
                        )
                        insert_chunks(doc_id, chunks, embeddings)
                        total_chunks += len(chunks)
                        update_crawl_job(job_id, "running", i+1)

                    update_crawl_job(job_id, "done", len(pages))
                    status.update(
                        label=f"✅ 完成！爬取 {len(pages)} 頁，建立 {total_chunks} 個向量索引",
                        state="complete"
                    )

                except Exception as e:
                    update_crawl_job(job_id, "failed")
                    status.update(label=f"❌ 爬取失敗：{e}", state="error")

    st.markdown("---")
    st.markdown("### 爬取任務紀錄")

    jobs = get_crawl_jobs()
    if not jobs:
        st.info("尚未有爬取任務")
    else:
        for job in jobs:
            status_map = {
                "done":    ("✅ 完成", "color:green"),
                "running": ("⏳ 進行中", "color:orange"),
                "failed":  ("❌ 失敗", "color:red"),
                "pending": ("⏸ 等待中", "color:gray"),
            }
            s_text, s_style = status_map.get(job['status'], ("未知", ""))
            col1, col2 = st.columns([6, 2])
            with col1:
                st.markdown(f"🌐 **{job['url']}**")
                st.caption(f"建立時間：{job['created_at'][:19]}")
            with col2:
                st.markdown(f"`{job['pages_done']}/{job['max_pages']} 頁` · <span style='{s_style}'>{s_text}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 已爬取網站文件")

    docs = get_all_documents()
    web_docs = [d for d in docs if d['source_type'] == 'website']

    if not web_docs:
        st.info("尚未爬取任何網站")
    else:
        for doc in web_docs:
            col1, col2, col3 = st.columns([5, 2, 1])
            with col1:
                url = doc.get('source_url', '')
                st.markdown(f"🌐 **{doc['title']}**")
                if url:
                    st.caption(url)
            with col2:
                try:
                    count = get_document_chunk_count(doc['id'])
                    st.markdown(f"`{count} 段落`")
                except:
                    pass
            with col3:
                if st.button("🗑", key=f"wdel_{doc['id']}", help="刪除"):
                    delete_document(doc['id'])
                    st.success("已刪除")
                    st.rerun()

# ════════════════════════════════
# TAB 3：資料總覽
# ════════════════════════════════
with tab3:
    st.markdown("### 知識庫統計")

    docs = get_all_documents()
    file_docs = [d for d in docs if d['source_type'] == 'file']
    web_docs  = [d for d in docs if d['source_type'] == 'website']

    col1, col2, col3 = st.columns(3)
    col1.metric("📚 總文件數", len(docs))
    col2.metric("📄 上傳文件", len(file_docs))
    col3.metric("🌐 網站來源", len(web_docs))

    st.markdown("---")
    st.markdown("### 所有知識庫資料")

    if docs:
        for doc in docs:
            icon = "🌐" if doc['source_type'] == 'website' else "📄"
            try:
                count = get_document_chunk_count(doc['id'])
            except:
                count = 0
            st.markdown(f"{icon} **{doc['title']}** · `{count} 段落` · {doc['created_at'][:10]}")
    else:
        st.info("知識庫目前為空，請先上傳文件或爬取網站")

    st.markdown("---")
    if st.button("🚪 登出", type="secondary"):
        st.session_state.admin_auth = False
        st.rerun()
