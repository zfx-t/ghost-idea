from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from utils.env_utils import SILICONFLOW_API_BASE, SILICONFLOW_API_KEY

from pydantic import BaseModel, Field
from typing import List


# 定义单个大类别的结构
class TagCategory(BaseModel):
    category_name: str = Field(
        description="大类别名称，例如：'目标人群'、'情绪/痛点'等"
    )
    tags: List[str] = Field(
        description="该类别下的具体词条列表，包含 10-15 个极具网感的标签"
    )


# 定义最终输出的整体结构（包含多个大类别）
class TagCloudResponse(BaseModel):
    categories: List[TagCategory] = Field(description="所有词云大类别的集合")


ciyun_llm = ChatDeepSeek(
    model="Pro/MiniMaxAI/MiniMax-M2.5",
    api_key=SILICONFLOW_API_KEY,
    api_base=SILICONFLOW_API_BASE,
    reasoning_effort="medium",  # 中等程度的思考，适合生成有创意但不失逻辑的内容
    temperature=0.6,
)

parser = PydanticOutputParser(pydantic_object=TagCloudResponse)

ciyun_template = """
# Role: 赛博产品经理 & 互联网亚文化观察家

## Profile
你是一个深谙互联网抽象文化、拒绝任何爹味和套路化表达的创意大师。你擅长捕捉现代人最幽微的情绪、最尴尬的场景和最垂直的圈层。你的任务是为一个特定的【主题】生成用于前端交互的“词云占位词库（Tags）”。

## 🎯 核心原则 (Critical Rules)
1. **绝对禁止宏大叙事与宽泛标签：** 禁用“年轻人”、“上班族”、“白领”、“开心”、“焦虑”等毫无画面感的大词。
2. **追求极致的颗粒度与反差感：** 词汇必须自带画面、情绪甚至气味。越垂直、越奇葩、越能引发共鸣越好。
3. **网感与时代气息：** 熟练运用当代互联网语境下的黑话、自嘲、发疯文学和梗。

## 📥 输入变量
- **当前需要生成的词云主题：** [在此处填写你的主题，例如：AI时代的原住民 / 硬核开发者 / 搞钱打工人]

## 🛠️ 输出维度与要求 (生成以下 4 个维度的词库，每个维度生成 5 个词)

### 1. 👥 目标人群词云库 (Target Audience)
- **要求：** 主打颗粒度细，挖掘圈层和亚文化，定义某种特定的“生存状态”。
- **❌ 错误示范：** 程序员、学生、创业者。
- **✅ 正确示范：** 秃头运维、早八特种兵、赛博缝合怪、糊弄学大师、大厂边缘人。

### 2. 🎭 情绪/痛点词云库 (Emotion & Pain Point)
- **要求：** 主打情绪价值与精神状态。包含负面宣泄、隐秘欲望或迷惑的心理活动。
- **❌ 错误示范：** 压力大、想赚钱、无聊。
- **✅ 正确示范：** 间歇性发疯、迫切想装杯、精神内耗中、强迫症狂喜、大脑空空、试图逆天改命。

### 3. 📍 奇葩场景词云库 (Context & Scenario)
- **要求：** 主打极其具体的物理或社交微场景。充满高压、尴尬、私密或碎片化的时刻。
- **❌ 错误示范：** 在办公室、在家里、睡觉前。
- **✅ 正确示范：** 带薪拉屎中、过年亲戚催婚现场、早高峰挤地铁被夹、被老板 PUA 现场、二手鱼塘极限拉扯。

### 4. 🪀 反常规/魔法触媒 (The "Digital Toy" Twist)
- **要求：** 主打“无用但有趣”的表现形式、整蛊机制或反常规的交互设定。
- **❌ 错误示范：** 提高效率、智能推荐、数据分析。
- **✅ 正确示范：** 阴阳怪气、同归于尽、赛博赛博木鱼、像素废土风、弹幕护体、大声密谋、强制社交。

## 📤 输出格式
{format_instructions}
"""

prompt = PromptTemplate(
    template=ciyun_template,
    input_variables=[],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

ciyun_chain = prompt | ciyun_llm | parser

async def get_tag_cloud():
        """获取词云库的函数接口"""
        response = ciyun_chain.invoke({})
        
        # 按类别分组拼接，保留类别属性信息
        category_strings = []
        for category in response.categories:
            # 格式：类别名：标签 1, 标签 2, 标签 3
            category_str = f"{category.category_name}: {','.join(category.tags)}"
            category_strings.append(category_str)
        
        # 不同类别之间用分号分隔
        CiyunSingleton.ciyun_tags_string = "; ".join(category_strings)
        
        return CiyunSingleton.ciyun_tags_string
# 词云单例类
class CiyunSingleton:
    ciyun_tags_string: str = ""  # 用于存储逗号分隔的词云字符串，供系统提示动态注入
    
    