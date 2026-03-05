import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

def get_memory(session_key="chat_history"):
    """
    获取带有 Streamlit 状态绑定的对话记忆组件。
    不同模块可以传入不同的 session_key 以隔离对话历史。
    """
    msgs = StreamlitChatMessageHistory(key=session_key)
    memory = ConversationBufferMemory(
        chat_memory=msgs, 
        return_messages=True, 
        memory_key="chat_history", 
        output_key="output"
    )
    return msgs, memory