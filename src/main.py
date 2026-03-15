import asyncio
from tui.tui_app import chat_loop
from agents.ai import chat_with_agent
from agents.ciyun import get_tag_cloud, CiyunSingleton


async def async_main():
    # 先等待词云初始化完成
    console = Console()
    console.print("[yellow]正在初始化词云库...[/]")
    await get_tag_cloud()
    console.print("[green]词云库初始化完成！[/]")

    # 词云完成后才开始对话
    await chat_loop(on_message=chat_with_agent, title="Ghost Idea Generator")


if __name__ == "__main__":
    from rich.console import Console

    asyncio.run(
        async_main(),
    )
