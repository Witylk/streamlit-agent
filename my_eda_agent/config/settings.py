import os

class LLMConfig:
    # 优先从环境变量读取，防止 Token 泄露；如果没有配置环境变量，则使用默认值
    API_KEY = os.getenv("GITHUB_PAT", "github_copilot_api_key_placeholder")
    
    # GitHub Models 官方标准接口地址
    BASE_URL = "https://models.inference.ai.azure.com"
    MODEL_NAME = "gpt-4o"


    @classmethod
    def get_system_prompt(cls, mode="general"):
        """定义 AI 的专家身份"""
        prompts = {
            "general": "你是一个专业的 EDA (Electronic Design Automation) 辅助助手。",
            "data_expert": """你是一位资深的芯片后端数据分析专家。
                你的任务是分析 EDA 工具（如 Innovus, PrimeTime, Genus）输出的报告。
                请严格基于数据回答，使用专业术语（如时序违例、功耗密度、利用率）。
                如果需要写 Python 代码分析数据，请确保代码高效且带有中文注释。""",
            "doc_expert": """你是一位精通集成电路规范的文档专家。
                你正在协助工程师阅读芯片手册（Spec）和寄存器定义。
                请准确提取技术指标（电压、频率、面积）和寄存器位偏移。
                如果文档内容冲突，请予以提示，不要猜测。"""
        }
        return prompts.get(mode, prompts["general"])

    @classmethod
    def get_llm_params(cls, **kwargs):
        """返回统一的 LLM 实例化参数字典，支持动态覆盖"""
        params = {
            "model_name": cls.MODEL_NAME,
            "openai_api_key": cls.API_KEY,
            "base_url": cls.BASE_URL,
            "temperature": 0.0, # 保证芯片数据处理的确定性
            "streaming": True,
            "default_headers": {"Authorization": f"Bearer {cls.API_KEY}"}
        }
        # 如果 kwargs 中传入了特定参数，会在这里覆盖默认值
        params.update(kwargs)
        return params