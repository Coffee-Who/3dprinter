from groq import Groq
import streamlit as st

@st.cache_resource
def get_groq_client():
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

def generate_answer(query: str, context_chunks: list) -> str:
    """根據搜尋到的段落生成回答"""
    client = get_groq_client()

    if not context_chunks:
        context = "（知識庫中未找到相關資料）"
    else:
        context = "\n\n---\n\n".join([
            f"【來源：{c.get('source_title', '未知')}】\n{c['content']}"
            for c in context_chunks
        ])

    system_prompt = """你是實威國際的 AI 知識庫助理。
你的任務是根據提供的知識庫內容回答使用者問題。

規則：
1. 優先使用知識庫內容回答，並標明來源
2. 若知識庫無相關資料，說明後用自身知識補充
3. 使用者用中文問，就用中文回答
4. 回答要清楚有條理，適當使用標題和條列
5. 跨語言理解：中文問題可對應英文資料回答"""

    user_prompt = f"""知識庫內容：
{context}

使用者問題：{query}

請根據以上知識庫內容回答，並標示資料來源。"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=2048,
        temperature=0.3
    )

    return response.choices[0].message.content
