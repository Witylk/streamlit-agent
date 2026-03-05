import os
import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler

class StreamHandler(BaseCallbackHandler):
    """用于实现大模型打字机流式输出的组件"""
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
        self.run_id_ignore_token = None

    def on_llm_start(self, serialized: dict, prompts: list, **kwargs):
        # 避免在 RAG 链中重复打印被重写的提示词
        if prompts[0].startswith("Human"):
            self.run_id_ignore_token = kwargs.get("run_id")

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        if self.run_id_ignore_token == kwargs.get("run_id", False):
            return
        self.text += token
        self.container.markdown(self.text)

class PrintRetrievalHandler(BaseCallbackHandler):
    """用于在界面上展示 RAG 文档检索过程的组件"""
    def __init__(self, container):
        self.status = container.status("**正在检索相关底层数据/文档...**")

    def on_retriever_start(self, serialized: dict, query: str, **kwargs):
        self.status.write(f"**分析检索意图:** {query}")
        self.status.update(label=f"**正在匹配上下文:** {query}")

    def on_retriever_end(self, documents, **kwargs):
        for idx, doc in enumerate(documents):
            source = os.path.basename(doc.metadata.get("source", "未知来源"))
            self.status.write(f"**找到关键片段 {idx + 1} (来源: {source})**")
            self.status.markdown(doc.page_content)
        self.status.update(state="complete")