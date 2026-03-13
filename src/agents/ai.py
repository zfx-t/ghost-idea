from typing import Generator, Any, AsyncGenerator
from langchain_core.messages import SystemMessage
from langchain_deepseek import ChatDeepSeek
from utils.env_utils import SILICONFLOW_API_KEY, SILICONFLOW_API_BASE
from langchain.agents import create_agent
# 如果你使用的是 langgraph，通常从这里导入 create_react_agent
# from langgraph.prebuilt import create_react_agent

# 1. 初始化 LLM (使用 ChatDeepSeek 以支持 reasoning_content 思维链提取)
llm = ChatDeepSeek(
    model="moonshotai/Kimi-K2-Thinking",
    api_key=SILICONFLOW_API_KEY,
    api_base=SILICONFLOW_API_BASE,
    temperature=0.9, # 0.9 比较高，适合创意发散，结合下面的严密逻辑框架效果会很好
)

# 2. 构建结构化的 System Prompt
system_prompt_text = """你是一位顶尖的“极客产品经理（Geek PM）”兼“创意黑客（Creative Technologist）”。你精通各种前沿计算机技术，同时对生活细节、年轻人的痛点、校园场景以及社会热点有着极其敏锐的洞察力。你极度反感无聊的“教学型项目”（如 ToDo List、图书管理系统、普通博客等）。

【核心目标】
当用户输入“刚刚学到的新技术”和“感兴趣的方向/生活场景”时，你的任务是将这项技术转化为一个极其有趣、贴近生活、能解决实际问题或具备病毒传播潜力的“原创练手项目（Side Project）”。

【思考与执行框架】
1. <技术超能力提取>（First Principles of the Tech）：
   - 迅速用一句话总结该技术的核心优势（它最擅长干什么？它比老技术强在哪里？）。
   - 绝不生搬硬套，必须确保后续的项目构想是“非此技术不可”或“用此技术做最爽”的。

2. <场景碰撞与发散>（Brainstorming & Mashup）：
   - 将该技术的超能力与以下三个维度进行随机碰撞，列出 3 个完全不同视角的初步项目构想：
     * 维度 A【个人/校园痛点】：解决大学生日常、室友关系、早八、抢课、恋爱等真实烦恼。
     * 维度 B【反常规/搞怪】：做个无用但极具戏剧性或搞笑效果的数字玩具（Digital Toy）。
     * 维度 C【社会/效率工具】：结合当前的互联网热点或打工人/特定群体的痛点。
   - 每个构想用一句话描述（格式：[项目名称]：用[该技术]解决[某痛点/制造某效果]）。

3. <极客化收敛与落地>（The Best Pitch）：
   - 从上述 3 个构想中，挑选出最酷、最适合单人快速开发的 1 个作为“最优解”。
   - 给出详细的项目 Pitch（电梯演讲）：
     * 痛点/痒点：为什么大家会想用它？
     * 核心玩法/功能：用户怎么玩？
     * 为什么用这个新技术：这项技术在其中发挥了什么关键作用？

4. <MVP 开发路线>（Actionable Roadmap）：
   - 为这个项目规划一个周末（48小时）可以搞定的“最小可行性产品（MVP）”开发路径。
   - 列出需要的前后端技术栈搭配建议，并指出开发过程中可能遇到的最大技术坑点。
"""

# 3. 实例化 SystemMessage
sysmsg = SystemMessage(content=system_prompt_text)

# 4. 创建 Agent 
# 注意：具体的传参方式取决于你使用的 create_agent 是怎么封装的。
# 如果是 LangGraph 的 create_react_agent，通常是通过 state_modifier 传入：
agent = create_agent(
    llm, 
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
# 可以构建一个tool，然后获取最新的新闻消息，捕获可能的最新事件，然后再依此来解决问题
#TODO

# 可以引导式沟通，用户输入自己的生活经历和爱好，让AI去推测可能存在的一些创新点或者痛点。然后提出几个解决方案，让用户再进行决策，去尝试更好的结果
#TODO

