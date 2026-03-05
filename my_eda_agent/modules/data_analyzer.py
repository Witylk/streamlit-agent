import os
import streamlit as st
import pandas as pd
from langchain.agents import AgentType
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_openai import ChatOpenAI

# 🔌 核心调用：接入配置中心
from config.settings import LLMConfig

FILE_FORMATS = {"csv": pd.read_csv, "xls": pd.read_excel, "xlsx": pd.read_excel}

@st.cache_data(ttl="2h")
def load_data(uploaded_file):
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext in FILE_FORMATS:
        return FILE_FORMATS[ext](uploaded_file)
    return None

def render():
    st.title("📊 芯片数据表格分析")
    st.markdown("上传功耗、面积或时序报告，让大模型自动编写代码进行数据透视。")

    uploaded_file = st.file_uploader("上传数据文件", type=list(FILE_FORMATS.keys()))
    if not uploaded_file:
        return

    df = load_data(uploaded_file)
    with st.expander("预览当前加载的数据 (前 3 行)", expanded=False):
        st.dataframe(df.head(3))

    if "pandas_messages" not in st.session_state or st.button("清空对话历史"):
        # 🧠 调用 1：获取专家身份，作为对话的开场白或背景音
        expert_greeting = LLMConfig.get_system_prompt("data_expert")
        st.session_state["pandas_messages"] = [
            {"role": "assistant", "content": f"{expert_greeting}\n\n数据已加载，你想分析什么？"}
        ]

    for msg in st.session_state["pandas_messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input(placeholder="比如：计算面积列的总和"):
        st.session_state["pandas_messages"].append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # 🧠 调用 2：动态获取 LLM 参数，强制 temperature=0 保证严谨
        llm_params = LLMConfig.get_llm_params(temperature=0.0) 
        llm = ChatOpenAI(**llm_params)

        pandas_df_agent = create_pandas_dataframe_agent(
            llm, df, verbose=True, 
            agent_type=AgentType.OPENAI_FUNCTIONS, 
            allow_dangerous_code=True
        )

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = pandas_df_agent.run(st.session_state["pandas_messages"], callbacks=[st_cb])
            st.session_state["pandas_messages"].append({"role": "assistant", "content": response})
            st.write(response)