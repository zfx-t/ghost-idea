from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults
# ==========================================
# TODO 1: 联网获取最新资讯的 Tool
# ==========================================
@tool
def search_latest_trends(query: str) -> str:
    """
    当需要结合当前互联网热点、最新技术新闻或社会现象来构思项目时，调用此工具。
    输入具体的查询词，例如 '2024大学生最新痛点' 或 'AI 热门开源项目'。
    """
    # 使用 DuckDuckGo 作为免费的搜索平替，实际生产中可换成 Tavily 或 SerpAPI
    search = DuckDuckGoSearchResults(max_results=3)
    return search.invoke(query)

tools = [search_latest_trends]

# 可以引导式沟通，用户输入自己的生活经历和爱好，让AI去推测可能存在的一些创新点或者痛点。然后提出几个解决方案，让用户再进行决策，去尝试更好的结果
#TODO
