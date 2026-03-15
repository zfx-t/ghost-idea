from typing import Generator, Any, AsyncGenerator
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from agents.tools import tools
from agents.response import AgentResponse,system_prompt_text
from utils.env_utils import SILICONFLOW_API_KEY, SILICONFLOW_API_BASE, DASHSCOPE_API_KEY, DASHCOPE_API_BASE
from langchain.agents import create_agent
# 如果你使用的是 langgraph，通常从这里导入 create_react_agent
# from langgraph.prebuilt import create_react_agent

# 1. 初始化 LLM (使用 ChatDeepSeek 以支持 reasoning_content 思维链提取)
# llm = ChatDeepSeek(
#     model="moonshotai/Kimi-K2-Thinking",
#     api_key=SILICONFLOW_API_KEY,
#     api_base=SILICONFLOW_API_BASE,
#     temperature=0.9, # 0.9 比较高，适合创意发散，结合下面的严密逻辑框架效果会很好
# )
llm = ChatOpenAI(
    model="qwen3.5-plus",
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHCOPE_API_BASE,
    temperature=1.0,
)

# 绑定工具的 LLM (用于前期的聊天和发散)
llm_with_tools = llm.bind_tools(tools)
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

# 3. 实例化 SystemMessage
sysmsg = SystemMessage(content=system_prompt_text)

# 4. 创建 Agent 
# 注意：具体的传参方式取决于你使用的 create_agent 是怎么封装的。
# 如果是 LangGraph 的 create_react_agent，通常是通过 state_modifier 传入：
agent = create_agent(
    llm,
    tools=tools,
    system_prompt=sysmsg
)


async def chat_with_agent(messages: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
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


