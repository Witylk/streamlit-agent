import os
import tempfile
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 🔌 核心调用：接入配置中心
from config.settings import LLMConfig
from utils.memory import get_memory
from utils.streaming import StreamHandler, PrintRetrievalHandler

@st.cache_resource(ttl="1h")
def configure_retriever(uploaded_files):
    docs = []
    temp_dir = tempfile.TemporaryDirectory()
    for file in uploaded_files:
        temp_filepath = os.path.join(temp_dir.name, file.name)
        with open(temp_filepath, "wb") as f:
            f.write(file.getvalue())
        docs.extend(PyPDFLoader(temp_filepath).load())

    splits = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(splits, embeddings).as_retriever(search_kwargs={"k": 3})

def render():
    st.title("📄 芯片规范文档智能解析")
    
    uploaded_files = st.file_uploader("上传 PDF 文件", type=["pdf"], accept_multiple_files=True)
    if not uploaded_files:
        return

    retriever = configure_retriever(uploaded_files)
    msgs, memory = get_memory(session_key="doc_chat_history")

    # 🧠 调用 1：动态获取 LLM 参数 (稍微放宽一点温度用于文本总结)
    llm = ChatOpenAI(**LLMConfig.get_llm_params(temperature=0.1))
    
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm, retriever=retriever, memory=memory, verbose=True
    )

    if len(msgs.messages) == 0 or st.button("清空文档对话记录"):
        msgs.clear()
        # 🧠 调用 2：获取文档专家身份
        expert_prompt = LLMConfig.get_system_prompt("doc_expert")
        msgs.add_ai_message(f"✅ {expert_prompt}\n\n文档已加载，请提问。")

    for msg in msgs.messages:
        st.chat_message("user" if msg.type == "human" else "assistant").write(msg.content)

    if user_query := st.chat_input(placeholder="比如：提取第 3 页的寄存器位宽"):
        st.chat_message("user").write(user_query)
        with st.chat_message("assistant"):
            retrieval_handler = PrintRetrievalHandler(st.container())
            stream_handler = StreamHandler(st.empty())
            qa_chain.run(user_query, callbacks=[retrieval_handler, stream_handler])