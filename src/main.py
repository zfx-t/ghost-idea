import asyncio
from utils.env_utils import SILICONFLOW_API_KEY, SILICONFLOW_API_BASE
from tui.tui_app import chat_loop
from agents.ai import agent, chat_with_agent

def main():
    chat_loop("简单对话系统", on_message=lambda msg: agent.stream(msg))


async def async_main():
    await chat_loop("简单对话系统", on_message=chat_with_agent)


if __name__ == "__main__":
    asyncio.run(async_main())
