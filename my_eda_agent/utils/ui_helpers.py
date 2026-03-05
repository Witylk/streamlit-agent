import os
import sys
import streamlit as st

# 🛠️ 核心修复：动态把当前项目根目录强制加入 Python 系统路径
# 这样无论你在哪个文件夹执行 streamlit run，它都能准确找到 modules 和 config
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 1. 页面全局配置 (必须放在 Python 代码最顶端)
st.set_page_config(
    page_title="My EDA Agent | 芯片智能平台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 动态导入业务模块 (有了上面的保护，这里就不会再报错了)
from modules import data_analyzer, doc_reader, web_search

# 3. 侧边栏导航控制
with st.sidebar:
    st.title("🛠️ EDA 导航控制台")
    st.markdown("---")
    
    app_mode = st.radio(
        "请选择智能分析引擎：",
        [
            "🏠 平台主页", 
            "📊 数据表格分析 (Data Expert)", 
            "📄 文档智能阅读 (Doc Expert)",
            "🌐 联网搜索助手 (Web Expert)"
        ]
    )
    
    st.markdown("---")
    st.caption("运行环境: Poetry 虚拟环境")
    st.caption("平台状态: 核心配置已解耦接入")

# 4. 路由调度分发
if app_mode == "🏠 平台主页":
    st.title("🤖 欢迎使用 My EDA Agent")
    st.markdown("""
    这是一个模块化的智能分析终端，专为复杂的芯片后端数据与文档设计。
    
    **✅ 已上线的分析引擎：**
    * **📊 数据表格分析**：上传报表，自动编写代码执行深度数据分析。
    * **📄 文档智能阅读**：上传 PDF 规范文档，精准提取底层技术参数。
    * **🌐 联网搜索助手**：实时抓取网络资源，辅助排查技术报错。
    
    👈 **请在左侧侧边栏选择你需要的工具开始工作。**
    """)

elif app_mode == "📊 数据表格分析 (Data Expert)":
    data_analyzer.render()

elif app_mode == "📄 文档智能阅读 (Doc Expert)":
    doc_reader.render()

elif app_mode == "🌐 联网搜索助手 (Web Expert)":
    web_search.render()