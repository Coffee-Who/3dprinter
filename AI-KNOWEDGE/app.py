import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, PromptTemplate
from llama_index.readers.web import SimpleWebPageReader
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. 基本設定 ---
st.set_page_config(page_title="3D Printer 專業知識庫", layout="wide")
st.title("🤖 3D Printer 智能助手 (終極強化版)")

if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ 找不到 API Key")
    st.stop()

# --- 2. 配置 AI 大腦 ---
Settings.llm = Groq(model="llama-3.3-70b-versatile", api_key=api_key)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

# 定義系統指令：讓 AI 更聰明地處理資料
qa_prompt_tmpl_str = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "你是 3D Printer 專家。請根據上述資料回答問題：{query_str}\n"
    "如果資料中沒有直接答案，請根據現有資訊提供最相關的建議。請使用繁體中文回答。"
)
qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

# --- 3. 爬蟲與資料處理 ---
def get_internal_links(base_url):
    links = {base_url}
    try:
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        domain = urlparse(base_url).netloc
        for a in soup.find_all('a', href=True):
            full_url = urljoin(base_url, a['href'])
            if urlparse(full_url).netloc == domain and "#" not in full_url:
                if not full_url.lower().endswith(('.pdf', '.jpg', '.png', '.zip')):
                    links.add(full_url)
        return list(links)
    except:
        return [base_url]

@st.cache_resource(show_spinner="同步知識庫中...")
def initialize_index():
    all_docs = []
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "data")
    url_path = os.path.join(base_path, "urls.txt")

    if os.path.exists(data_path) and os.listdir(data_path):
        all_docs.extend(SimpleDirectoryReader(data_path).load_data())

    if os.path.exists(url_path):
        with open(url_path, "r", encoding="utf-8") as f:
            seeds = [l.strip() for l in f if l.strip().startswith("http")]
        if seeds:
            urls = []
            for s in seeds: urls.extend(get_internal_links(s))
            all_docs.extend(SimpleWebPageReader(html_to_text=True).load_data(list(set(urls))))

    return VectorStoreIndex.from_documents(all_docs) if all_docs else None

# --- 4. 介面實作 ---
index = initialize_index()

with st.sidebar:
    st.header("⚙️ 診斷與設定")
    show_context = st.checkbox("顯示 AI 參考的原始資料 (Debug)", value=False)
    if st.button("清除快取並重新掃描"):
        st.cache_resource.clear()
        st.rerun()

if index:
    # 強化檢索：Top_K 調高到 10，讓 AI 參考更多內容
    query_engine = index.as_query_engine(
        similarity_top_k=10,
        text_qa_template=qa_prompt_tmpl
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("請輸入問題..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = query_engine.query(prompt)
            st.markdown(str(response))
            
            # 如果開啟 Debug 模式，顯示參考來源
            if show_context:
                with st.expander("AI 剛才讀到了這些片段："):
                    for node in response.source_nodes:
                        st.write(f"來自: {node.metadata.get('file_name', '網頁')}")
                        st.caption(node.get_content()[:300] + "...")
            
            st.session_state.messages.append({"role": "assistant", "content": str(response)})
else:
    st.warning("請在 GitHub 的 data 資料夾中放入檔案。")
