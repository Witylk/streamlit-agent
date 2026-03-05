import streamlit as st
from langchain_openai import ChatOpenAI
from config.settings import LLMConfig
from utils.memory import get_memory

def render():
    st.title("🤖 EDA 智能咨询 (GitHub Model 驱动)")
    st.info("当前模式：纯 AI 推理模式（无联网延迟，基于 GPT-4o 内部知识库）")

    msgs, memory = get_memory(session_key="ai_chat_history")
    
    # 渲染历史消息
    for msg in msgs.messages:
        st.chat_message(msg.type).write(msg.content)

    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)

        # 直接调用你已经在 config 里配置好的 GitHub API
        llm = ChatOpenAI(**LLMConfig.get_llm_params(temperature=0.7))
        
        with st.chat_message("assistant"):
            # 这里的 response 直接来自你的 GitHub API，不走搜索工具
            response = llm.invoke(prompt) 
            st.write(response.content)
            # 保存记忆
            msgs.add_user_message(prompt)
            msgs.add_ai_message(response.content)