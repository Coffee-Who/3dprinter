import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.readers.web import SimpleWebPageReader
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. 初始化設定 ---
st.set_page_config(page_title="3D Printer 知識庫", layout="wide")
st.title("🤖 3D Printer 專屬知識搜尋")

# 讀取 Secrets
if "GROQ_API_KEY" in st.secrets:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
else:
    st.error("❌ 錯誤：未在 Streamlit Secrets 中設定 GROQ_API_KEY")
    st.stop()

# 設定 LLM (使用 Groq)
Settings.llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

# 設定中文優化 Embedding 模型
@st.cache_resource
def get_embed_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

Settings.embed_model = get_embed_model()

# --- 2. 資料路徑與檔案檢查 ---
# 取得目前程式執行所在的絕對路徑
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")
url_file = os.path.join(base_dir, "urls.txt")

# --- 3. 核心功能：建立索引 ---
@st.cache_resource(show_spinner="正在建立知識庫索引...")
def build_index():
    all_docs = []
    
    # A. 檢查並讀取資料夾
    if os.path.exists(data_dir) and os.listdir(data_dir):
        try:
            reader = SimpleDirectoryReader(input_dir=data_dir, recursive=True)
            all_docs.extend(reader.load_data())
        except Exception as e:
            st.error(f"讀取文件時發生錯誤: {e}")
    
    # B. 檢查並讀取網址
    if os.path.exists(url_file):
        with open(url_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip().startswith("http")]
        if urls:
            try:
                web_docs = SimpleWebPageReader(html_to_text=True).load_data(urls)
                all_docs.extend(web_docs)
            except Exception as e:
                st.warning(f"部分網址載入失敗: {e}")

    if not all_docs:
        return None

    return VectorStoreIndex.from_documents(all_docs)

# --- 4. 側邊欄診斷資訊 ---
with st.sidebar:
    st.header("📋 系統狀態")
    
    # 檢查 data 目錄
    if not os.path.exists(data_dir):
        st.error("❌ 找不到 'data' 資料夾")
    else:
        files = os.listdir(data_dir)
        if not files:
            st.warning("⚠️ 'data' 資料夾內沒有檔案")
        else:
            st.success(f"✅ 偵測到 {len(files)} 個檔案")
            with st.expander("檔案清單"):
                for f in files: st.write(f"- {f}")

    # 檢查網址檔案
    if os.path.exists(url_file):
        with open(url_file, "r") as f:
            count = len([l for l in f if l.strip()])
        st.success(f"✅ 偵測到 {count} 個待爬取網址")
    
    st.info("💡 提示：更新 GitHub 上的檔案後，重新整理網頁即可生效。")

# --- 5. 對話邏輯 ---
index = build_index()

if index:
    # 建立搜尋引擎
    query_engine = index.as_query_engine(similarity_top_k=5)

    # 聊天紀錄管理
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
            with st.spinner("正在搜尋文件..."):
                response = query_engine.query(prompt)
                st.markdown(str(response))
                st.session_state.messages.append({"role": "assistant", "content": str(response)})
else:
    st.warning("知識庫目前是空的。請確保 GitHub 上的 'data' 資料夾內有 PDF/TXT 檔案，且 'urls.txt' 內有網址。")
