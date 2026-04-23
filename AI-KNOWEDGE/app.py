import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.readers.web import SimpleWebPageReader
from llama_index.llms.groq import Groq
from llama_index.core import Settings

# --- 配置區 ---
GROQ_API_KEY = "你的_GROQ_API_KEY" # 建議從 Streamlit Secrets 讀取以保安全
st.set_page_config(page_title="GitHub 知識庫", layout="wide")

# 初始化 LLM (使用免費又極快的 Groq)
Settings.llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
# 使用本地輕量化 Embedding (這部分完全免費且在雲端跑得動)
Settings.embed_model = "local:BAAI/bge-small-en-v1.5"

@st.cache_resource(show_spinner="正在載入知識庫...")
def initialize_index():
    # A. 讀取 data/ 資料夾內的文件
    documents = []
    if os.path.exists("./data") and os.listdir("./data"):
        documents.extend(SimpleDirectoryReader("./data").load_data())
    
    # B. 讀取 urls.txt 內的網址
    if os.path.exists("urls.txt"):
        with open("urls.txt", "r") as f:
            urls = [line.strip() for line in f if line.strip().startswith("http")]
        if urls:
            web_docs = SimpleWebPageReader(html_to_text=True).load_data(urls)
            documents.extend(web_docs)
    
    # 建立搜尋索引
    return VectorStoreIndex.from_documents(documents)

# --- 網頁介面 ---
st.title("🤖 GitHub 知識庫助手")

try:
    index = initialize_index()
    query_engine = index.as_query_engine()

    # 聊天介面
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("請輸入問題..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = query_engine.query(prompt)
            st.markdown(str(response))
            st.session_state.messages.append({"role": "assistant", "content": str(response)})

except Exception as e:
    st.error(f"載入失敗，請確認是否已上傳文件或 API Key 正確。錯誤: {e}")
