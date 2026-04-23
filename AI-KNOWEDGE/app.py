import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.readers.web import SimpleWebPageReader
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. 頁面與核心配置 ---
st.set_page_config(page_title="3D Printer 智能爬蟲知識庫", layout="wide")
st.title("🤖 3D Printer 知識庫 (含網頁自動爬取)")

# 讀取 Secrets
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ 未設定 GROQ_API_KEY，請在 Streamlit Secrets 中配置。")
    st.stop()

# 模型設定：使用 Groq 最新模型 & 中文優化 Embedding
Settings.llm = Groq(model="llama-3.3-70b-versatile", api_key=api_key)

@st.cache_resource
def load_embed_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

Settings.embed_model = load_embed_model()

# --- 2. 自動爬蟲邏輯 (抓取同站連結) ---
def get_internal_links(base_url):
    """獲取同域名下的所有子連結 (限一層)"""
    internal_links = {base_url}
    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        domain = urlparse(base_url).netloc
        
        for a in soup.find_all('a', href=True):
            link = urljoin(base_url, a['href'])
            parsed_link = urlparse(link)
            # 規則：同域名、必須是 http(s)、排除非 HTML 檔案格式
            if parsed_link.netloc == domain and parsed_link.scheme in ["http", "https"]:
                clean_link = link.split('#')[0].rstrip('/') # 移除錨點與結尾斜線避免重複
                if not clean_link.lower().endswith(('.pdf', '.jpg', '.png', '.zip', '.docx')):
                    internal_links.add(clean_link)
        return list(internal_links)
    except Exception as e:
        st.sidebar.warning(f"掃描網址失敗 {base_url}: {e}")
        return [base_url]

# --- 3. 初始化知識庫 (文件 + 網頁) ---
@st.cache_resource(show_spinner="正在同步雲端資料並爬取網頁...")
def initialize_index():
    all_docs = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    url_file = os.path.join(base_dir, "urls.txt")

    # A. 讀取本地文件 (data/ 資料夾)
    if os.path.exists(data_dir) and os.listdir(data_dir):
        try:
            reader = SimpleDirectoryReader(input_dir=data_dir, recursive=True)
            all_docs.extend(reader.load_data())
        except Exception as e:
            st.error(f"文件讀取失敗: {e}")

    # B. 讀取並爬取網頁內容
    if os.path.exists(url_file):
        with open(url_file, "r", encoding="utf-8") as f:
            seeds = [line.strip() for line in f if line.strip().startswith("http")]
        
        if seeds:
            total_urls = []
            with st.sidebar.status("🌐 網頁爬蟲進行中...", expanded=True) as status:
                for seed in seeds:
                    st.write(f"正在搜尋: {seed}")
                    links = get_internal_links(seed)
                    total_urls.extend(links)
                
                final_urls = list(set(total_urls)) # 去重
                st.write(f"總計發現 {len(final_urls)} 個相關頁面")
                
                try:
                    # 讀取所有爬到的網頁內容
                    web_docs = SimpleWebPageReader(html_to_text=True).load_data(final_urls)
                    all_docs.extend(web_docs)
                    status.update(label="✅ 網頁爬取完成！", state="complete")
                except Exception as e:
                    st.error(f"讀取網頁內容出錯: {e}")

    if not all_docs:
        return None

    return VectorStoreIndex.from_documents(all_docs)

# --- 4. 側邊欄狀態顯示 ---
with st.sidebar:
    st.header("📊 知識庫狀態")
    index = initialize_index()
    if index:
        st.success("🧠 AI 大腦已就緒")
    else:
        st.warning("⚠️ 知識庫目前無資料")
    
    st.divider()
    st.caption("自動爬蟲模式：開啟")
    st.info("系統會自動抓取 urls.txt 中網址的「所有同站子連結」。")

# --- 5. 對話介面 ---
if index:
    # 建立查詢引擎
    query_engine = index.as_query_engine(similarity_top_k=5)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("請問關於 3D Printer 的任何事？"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("正在檢索文件與網頁..."):
                response = query_engine.query(prompt)
                st.markdown(str(response))
                st.session_state.messages.append({"role": "assistant", "content": str(response)})
else:
    st.info("請上傳檔案到 GitHub 的 data/ 資料夾，或在 urls.txt 寫入網址以啟用功能。")
