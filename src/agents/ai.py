from typing import Generator, Any, AsyncGenerator
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from utils.env_utils import SILICONFLOW_API_KEY, SILICONFLOW_API_BASE

llm = init_chat_model(
    model="Qwen/Qwen3-VL-32B-Instruct",
    model_provider="openai",
    api_key=SILICONFLOW_API_KEY,
    base_url=SILICONFLOW_API_BASE,
    max_tokens=2048,
    temperature=0.9,
)

agent = create_agent(llm)



async def chat_with_agent(messages: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
    """异步流式对话，token 级输出"""
    async for event in agent.astream_events({"messages": messages}, version="v2"):
        if event["event"] == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield content
