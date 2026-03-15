from typing import Generator, Any, AsyncGenerator
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from agents.tools import tools
from agents.response import AgentResponse, system_prompt_template
from agents.ciyun import CiyunSingleton
from utils.env_utils import (
    SILICONFLOW_API_KEY,
    SILICONFLOW_API_BASE,
    DASHSCOPE_API_KEY,
    DASHCOPE_API_BASE,
)
from langchain.agents import create_agent

llm = ChatOpenAI(
    model="qwen3.5-plus",
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHCOPE_API_BASE,
    temperature=1.0,
)
# 绑定结构化输出的 LLM (用于最终的收敛定稿)
parser = PydanticOutputParser(pydantic_object=AgentResponse)
prompt = PromptTemplate.from_template(
    """
    请分析以下输入：
    {input}
    
    {format_instructions}
    """
)
prompt = prompt.partial(format_instructions=parser.get_format_instructions())
llm_with_structured_output = prompt | llm | parser

# 3. 创建 Agent (system_prompt 会在每次调用时动态注入词云)
agent = create_agent(
    llm,
    # tools=tools,
    system_prompt=None,  # 将在 chat_with_agent 中动态设置
)


async def chat_with_agent(messages: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
    # 从单例中获取词云数据
    ciyun_data = CiyunSingleton.ciyun_tags_string
    if not ciyun_data:
        ciyun_data = "暂无词云数据"

    # 动态注入词云到模板
    system_prompt_text = system_prompt_template.format(Word_Cloud_Tags=ciyun_data)
    messages.insert(0, {"role": "system", "content": system_prompt_text})
    """异步流式对话，包含原生思考过程 (token 级输出)"""

    # 状态标记：用来判断是否需要输出 <think> 标签
    is_thinking = False
    has_finished_thinking = False

    async for event in agent.astream_events({"messages": messages}, version="v2"):
        if event["event"] == "on_chat_model_stream":
            chunk = event["data"]["chunk"]

            # 1. 尝试提取原生的思考过程 (针对支持 reasoning_content 的模型)
            reasoning = chunk.additional_kwargs.get("reasoning_content", "")
            if reasoning:
                # 第一次遇到思考内容时，先抛出一个前置标签
                if not is_thinking:
                    yield "<think>\n"
                    is_thinking = True

                # 持续输出思考过程
                yield reasoning

            # 2. 提取最终的正式回复内容
            content = chunk.content
            if content:
                # 如果之前在思考，现在开始输出正文了，需要先闭合 </think> 标签
                if is_thinking and not has_finished_thinking:
                    yield "\n</think>\n\n"
                    has_finished_thinking = True

                # 持续输出正式内容
                yield content
