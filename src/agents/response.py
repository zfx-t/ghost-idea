from pydantic import BaseModel, Field
from typing import List, Literal

# --- 子模型定义（对应思维框架的各个部分） ---

class BrainstormIdea(BaseModel):
    """第二步：初步场景碰撞构想"""
    dimension: Literal["个人/校园痛点", "反常规/搞怪", "社会/效率工具"] = Field(
        description="该构想所属的维度"
    )
    project_name: str = Field(description="初步构想的项目名称")
    one_line_description: str = Field(
        description="一句话描述，格式：用[该技术]解决[某痛点/制造某效果]"
    )

class ProjectPitch(BaseModel):
    """第三步：最优项目的电梯演讲"""
    pain_point: str = Field(description="痛点/痒点分析：为什么大家会想用它？")
    core_gameplay: str = Field(description="核心玩法/功能：用户怎么玩？交互流程是怎样的？")
    tech_justification: str = Field(description="为什么用这个新技术：它在其中发挥了什么不可替代的作用？")

class MVPRoadmap(BaseModel):
    """第四步：MVP 开发路线"""
    timeline_48h: List[str] = Field(
        description="48小时周末开发计划，拆分为关键节点，例如：['周五晚：环境搭建与核心API测试', '周六：...', '周日：...']"
    )
    tech_stack: List[str] = Field(
        description="前后端及相关辅助技术栈推荐，例如：['FastAPI', 'Next.js', 'Vercel']"
    )
    biggest_pitfall: str = Field(description="开发过程中可能遇到的最大技术坑点及避坑建议")

# --- 主模型定义 ---

class AgentResponse(BaseModel):
    """极客产品经理的最终完整输出"""
    
    # 步骤 1
    tech_superpower: str = Field(
        description="用一句话总结该技术的核心优势（它最擅长干什么？比老技术强在哪？）"
    )
    
    # 步骤 2
    brainstorming_ideas: List[BrainstormIdea] = Field(
        description="3个不同维度的初步项目构想",
        min_items=3, 
        max_items=3
    )
    
    # 步骤 3
    best_project_name: str = Field(description="最终选定的最优项目的名称")
    best_project_pitch: ProjectPitch = Field(description="最优项目的详细 Pitch（电梯演讲）")
    
    # 步骤 4
    mvp_roadmap: MVPRoadmap = Field(description="周末 48 小时 MVP 开发路线")
    
    # 附加信息（保留你原有的优秀字段）
    keywords: List[str] = Field(
        description="项目的创新关键词，例如：['AI', '情绪价值', '赛博朋克', '效率']"
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
