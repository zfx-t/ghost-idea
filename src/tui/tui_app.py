#!/usr/bin/env python3
"""简单的 TUI 对话系统"""

from typing import Callable, Optional, Generator, AsyncGenerator
import asyncio
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import box
from rich.live import Live
from rich.text import Text

console = Console()


def stream_print(text: str, prefix: str = "", color: str = "blue", speed: float = 0.1):
    """流式打印文本，打字机效果"""
    with Live(
        "", console=console, refresh_per_second=30, vertical_overflow="visible"
    ) as live:
        output = Text()
        output.append(prefix, style=f"bold {color}")
        output.append(" ")
        live.update(output)

        for char in text:
            output.append(char, style=color)
            live.update(output)
            time.sleep(speed)


async def chat_loop(
    title: str = "TUI 对话", on_message: Optional[Callable] = None
) -> None:
    """
    异步 TUI 对话循环，支持实时流式显示

    Args:
        title: 对话框标题
        on_message: 异步回调函数，接收消息历史列表，返回 AsyncGenerator[str, None]
    """
    messages = []

    while True:
        console.clear()
        console.print(Panel(title, border_style="cyan", box=box.DOUBLE))
        console.print()

        for msg in messages[-8:]:
            role = "你" if msg["role"] == "user" else "助手"
            color = "green" if msg["role"] == "user" else "blue"
            console.print(f"[bold {color}]{role}:[/] {msg['content']}")
        console.print()

        try:
            user_input = Prompt.ask("[yellow]输入[/yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[red]再见！[/]")
            break

        if user_input.lower() in ["quit", "exit", "q"]:
            console.print("[green]再见！[/]")
            break

        messages.append({"role": "user", "content": user_input})

        if on_message:
            full_reply = ""
            output = Text()
            output.append("助手:", style="bold blue")
            output.append(" ")
            with Live(
                output,
                console=console,
                refresh_per_second=30,
                vertical_overflow="visible",
                transient=True,
            ) as live:
                async for chunk in on_message(messages):
                    full_reply += chunk
                    output.append(chunk, style="blue")
                    live.update(output, refresh=True)
            messages.append({"role": "ai", "content": full_reply})
        else:
            messages.append({"role": "ai", "content": "请提供 on_message 回调函数"})


if __name__ == "__main__":
    chat_loop("简单对话系统")
