import streamlit as st
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.readers.web import SimpleWebPageReader
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. 基礎設定與 UI ---
st.set_page_config(page_title="3D Printer 智能知識庫", layout="wide")
st.title("🤖 3D Printer 專屬 AI 助手 (含自動爬蟲)")

# 讀取 Secrets 中的 API Key
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ 找不到 GROQ_API_KEY！請在 Streamlit Cloud 的 Secrets 中設定。")
    st.stop()

# --- 2. 配置 AI 大腦 (LLM 與 中文 Embedding) ---
# 使用 Llama 3.3 穩定版模型，避免 BadRequestError
Settings.llm = Groq(model="llama-3.3-70b-versatile", api_key=api_key)

# 強制使用中文優化模型 (解決「查不到」的核心關鍵)
@st.cache_resource
def load_zh_embedding():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

Settings.embed_model = load_zh_embedding()

# --- 3. 自動爬蟲功能邏輯 ---
def get_internal_links(base_url):
    """抓取同網站下的所有子連結 (限一層)"""
    links = {base_url}
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        domain = urlparse(base_url).netloc
        for a in soup.find_all('a', href=True):
            full_url = urljoin(base_url, a['href'])
            # 過濾掉外連、圖片、檔案、以及跳轉錨點
            if urlparse(full_url).netloc == domain and "#" not in full_url:
                if not full_url.lower().endswith(('.pdf', '.jpg', '.png', '.zip', '.docx')):
                    links.add(full_url)
        return list(links)
    except Exception as e:
        st.sidebar.warning(f"掃描網址失敗 {base_url}: {e}")
        return [base_url]

# --- 4. 讀取資料並建立索引 ---
@st.cache_resource(show_spinner="正在載入知識庫與掃描網頁...")
def initialize_index():
    all_docs = []
    # 使用絕對路徑確保在雲端環境能讀到資料夾
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "data")
    url_path = os.path.join(base_path, "urls.txt")

    # A. 讀取本地文件 (PDF, Word, TXT)
    if os.path.exists(data_path) and os.listdir(data_path):
        try:
            reader = SimpleDirectoryReader(input_dir=data_path, recursive=True)
            all_docs.extend(reader.load_data())
        except Exception as e:
            st.error(f"文件載入失敗: {e}")

    # B. 讀取並自動爬取網頁
    if os.path.exists(url_path):
        with open(url_path, "r", encoding="utf-8") as f:
            seeds = [line.strip() for line in f if line.strip().startswith("http")]
        
        if seeds:
            total_urls = []
            st.sidebar.write("🌐 正在掃描網址...")
            for seed in seeds:
                found = get_internal_links(seed)
                total_urls.extend(found)
            
            final_urls = list(set(total_urls)) # 去除重複
            st.sidebar.info(f"總共發現 {len(final_urls)} 個網頁頁面")
            
            try:
                web_docs = SimpleWebPageReader(html_to_text=True).load_data(final_urls)
                all_docs.extend(web_docs)
            except Exception as e:
                st.sidebar.error(f"網頁內容讀取失敗: {e}")

    if not all_docs:
        return None

    return VectorStoreIndex.from_documents(all_docs)

# --- 5. 側邊欄狀態診斷 ---
with st.sidebar:
    st.header("📋 系統診斷")
    index = initialize_index()
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "data")
    
    if os.path.exists(data_path):
        files = os.listdir(data_path)
        if files:
            st.success(f"已讀取 {len(files)} 個檔案")
            with st.expander("查看檔案清單"):
                for f in files: st.text(f)
        else:
            st.warning("⚠️ data 資料夾是空的")
    else:
        st.error("❌ 找不到 data 資料夾")
    
    st.divider()
    st.caption("提示：若查詢不到，請確認 PDF 是否為圖片掃描檔 (AI 無法讀取圖片文字)。")

# --- 6. 對話介面 ---
if index:
    # 建立查詢引擎 (一次參考 5 段最相關資料)
    query_engine = index.as_query_engine(similarity_top_k=5)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("請問關於 3D Printer 的問題..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("正在搜尋文件與網頁內容..."):
                try:
                    response = query_engine.query(prompt)
                    st.markdown(str(response))
                    st.session_state.messages.append({"role": "assistant", "content": str(response)})
                except Exception as e:
                    st.error(f"查詢時發生錯誤: {e}")
else:
    st.warning("目前知識庫沒有資料。請上傳檔案到 GitHub 的 data/ 資料夾。")
