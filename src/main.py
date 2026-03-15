import asyncio
from utils.env_utils import SILICONFLOW_API_KEY, SILICONFLOW_API_BASE
from tui.tui_app import chat_loop
from agents.ai import agent, chat_with_agent,llm_with_structured_output


async def async_main():
    await chat_loop("简单对话系统", on_message=chat_with_agent)


if __name__ == "__main__":
    # asyncio.run(async_main())
    # 2. 运行 Agent，获取最终自然语言回复
    response = agent.invoke({"messages": [{"role": "user", "content": "我正在学习 Vue 前端框架和 Golang 后端语言，请问有哪些适合新手的全栈实战项目推荐？"}]})
    print("=== Agent 原生回复（包含思考链） ===\n")
    print(f"response:{response}\n" )
    final_ai_message = response["messages"][-1].content
    print("=== 最终自然语言回复 ===\n")
    print(f"final_ai_message:{final_ai_message}\n" )
    # 3. 后处理：使用结构化 LLM 收敛定稿
    structured_result = llm_with_structured_output.invoke({"input": final_ai_message})
    print("=== 最终结构化输出 ===\n")
    print(f"structured_result:{structured_result}\n" )
