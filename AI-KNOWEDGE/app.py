import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.readers.web import SimpleWebPageReader
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. 初始化頁面設定 ---
st.set_page_config(page_title="3D Printer 知識庫", layout="wide")
st.title("🤖 3D Printer 專屬知識搜尋")

# --- 2. 核心模型配置 (解決 BadRequestError) ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ 找不到 GROQ_API_KEY！請在 Streamlit Secrets 中設定。")
    st.stop()

# 使用 Groq 最新穩定模型名稱，避免相容性錯誤
Settings.llm = Groq(model="llama-3.3-70b-versatile", api_key=api_key)

# 使用中文優化 Embedding 模型 (完全免費，解決搜尋不到中文的問題)
@st.cache_resource
def load_embedding():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

Settings.embed_model = load_embedding()

# --- 3. 資料路徑與檔案檢查 ---
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")
url_file = os.path.join(base_dir, "urls.txt")

# --- 4. 建立索引功能 ---
@st.cache_resource(show_spinner="正在讀取知識庫...")
def initialize_knowledge_base():
    all_docs = []
    
    # A. 讀取 data 資料夾
    if os.path.exists(data_dir) and os.listdir(data_dir):
        try:
            # 支援 PDF, Docx, TXT 等格式
            reader = SimpleDirectoryReader(input_dir=data_dir, recursive=True)
            all_docs.extend(reader.load_data())
        except Exception as e:
            st.error(f"讀取文件發生錯誤: {e}")
    
    # B. 讀取 urls.txt
    if os.path.exists(url_file):
        with open(url_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip().startswith("http")]
        if urls:
            try:
                web_docs = SimpleWebPageReader(html_to_text=True).load_data(urls)
                all_docs.extend(web_docs)
            except Exception as e:
                st.sidebar.warning(f"部分網址無法存取: {e}")

    if not all_docs:
        return None

    return VectorStoreIndex.from_documents(all_docs)

# --- 5. 介面與對話邏輯 ---
with st.sidebar:
    st.header("📋 知識庫狀態")
    if os.path.exists(data_dir):
        file_count = len(os.listdir(data_dir))
        st.success(f"已偵測到 {file_count} 份文件")
    else:
        st.warning("找不到 data 資料夾")
    
    st.info("💡 提示：在 GitHub 上傳新文件後，重新整理網頁即可更新內容。")

# 建立索引
index = initialize_knowledge_base()

if index:
    # 建立搜尋引擎 (設定 top_k=5 以增加搜尋深度)
    query_engine = index.as_query_engine(similarity_top_k=5)

    # 對話紀錄管理
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 顯示歷史對話
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 使用者提問
    if prompt := st.chat_input("請輸入您的問題..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("正在搜尋資料庫..."):
                try:
                    response = query_engine.query(prompt)
                    answer = str(response)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"發生錯誤：{e}")
                    st.info("這通常與 API 額度或格式有關，請稍後再試。")
else:
    st.warning("目前的知識庫是空的。請在 GitHub 的 'data' 資料夾放檔案或在 'urls.txt' 放網址。")
