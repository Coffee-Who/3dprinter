import streamlit as st
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.readers.web import SimpleWebPageReader
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# --- 1. 基本頁面設定 ---
st.set_page_config(page_title="AI 知識庫助手", layout="wide")
st.title("🤖 3D Printer 知識庫搜尋")

# --- 2. 設定模型 (LLM 與 中文優化 Embedding) ---
# 從 Streamlit Secrets 讀取 API Key
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("請在 Streamlit Secrets 中設定 GROQ_API_KEY")
    st.stop()

# 設定大腦 (Groq LLM)
Settings.llm = Groq(model="llama3-70b-8192", api_key=api_key)

# 設定搜尋索引大腦 (針對中文優化的 Embedding 模型)
# 使用 BAAI/bge-small-zh-v1.5，這對中文語意搜尋效果非常好
@st.cache_resource
def load_embed_model():
    return HuggingFaceEmbedding(model_name="BAAI/bge-small-zh-v1.5")

Settings.embed_model = load_embed_model()

# --- 3. 資料載入與索引建立 ---
@st.cache_resource(show_spinner="正在載入知識庫資料，請稍候...")
def initialize_index():
    all_docs = []
    
    # A. 讀取 data/ 資料夾內的所有文件 (PDF, Docx, TXT)
    data_dir = "./data"
    if os.path.exists(data_dir) and os.listdir(data_dir):
        file_docs = SimpleDirectoryReader(data_dir).load_data()
        all_docs.extend(file_docs)
        st.sidebar.success(f"成功載入 {len(os.listdir(data_dir))} 份文件")
    else:
        st.sidebar.warning("警告：data 資料夾是空的或不存在")

    # B. 讀取 urls.txt 內的網址內容
    url_file = "urls.txt"
    if os.path.exists(url_file):
        with open(url_file, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip().startswith("http")]
        
        if urls:
            try:
                web_docs = SimpleWebPageReader(html_to_text=True).load_data(urls)
                all_docs.extend(web_docs)
                st.sidebar.success(f"成功載入 {len(urls)} 個網址內容")
            except Exception as e:
                st.sidebar.error(f"網址載入失敗: {e}")

    if not all_docs:
        st.error("目前沒有任何資料可供搜尋，請檢查 GitHub 上的 data/ 或 urls.txt")
        return None

    # 建立向量索引
    index = VectorStoreIndex.from_documents(all_docs)
    return index

# 初始化索引
index = initialize_index()

# --- 4. 對話介面實作 ---
if index:
    # 建立查詢引擎 (similarity_top_k=5 代表搜尋最相關的 5 個段落)
    query_engine = index.as_query_engine(similarity_top_k=5)

    # 初始化對話紀錄
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 顯示歷史訊息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 使用者輸入框
    if prompt := st.chat_input("請輸入關於 3D Printer 的問題..."):
        # 顯示使用者訊息
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 產生 AI 回答
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                response = query_engine.query(prompt)
                full_response = str(response)
                st.markdown(full_response)
                
                # 將來源加入展開視窗 (可選)
                if hasattr(response, 'source_nodes'):
                    with st.expander("查看參考來源"):
                        for node in response.source_nodes:
                            st.write(f"相關度評分: {node.score:.2f}")
                            st.text(node.node.get_content()[:200] + "...")

        st.session_state.messages.append({"role": "assistant", "content": full_response})
else:
    st.info("請在 GitHub 儲存庫中建立 'data' 資料夾並放入文件，即可開始使用。")

# --- 5. 側邊欄狀態顯示 ---
with st.sidebar:
    st.divider()
    st.caption("資料更新說明：")
    st.info("若要新增資料，請直接上傳檔案至 GitHub 的 data/ 資料夾，或修改 urls.txt。重新整理此頁面即可生效。")
