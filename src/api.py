from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.ai import chat_with_agent
import asyncio
import json
import random

app = FastAPI(title="Ghost Idea API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    conversationId: str | None = None


class ChatResponse(BaseModel):
    response: str
    conversationId: str | None = None


class WordCloudRequest(BaseModel):
    words: list[str]


class WordCloudResponse(BaseModel):
    words: list[dict]


class GenerateWordsResponse(BaseModel):
    words: list[str]


async def generate_stream(messages: list):
    try:
        async for chunk in chat_with_agent(messages):
            data = json.dumps({"chunk": chunk})
            yield f"data: {data}\n\n"
            await asyncio.sleep(0.01)
    except Exception as e:
        data = json.dumps({"error": str(e)})
        yield f"data: {data}\n\n"
    yield "data: [DONE]\n\n"


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        messages = [{"role": "user", "content": request.message}]

        return StreamingResponse(
            generate_stream(messages),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


WORD_POOL = [
    "创意",
    "灵感",
    "创新",
    "思维",
    "想象",
    "未来",
    "科技",
    "智能",
    "数据",
    "算法",
    "设计",
    "艺术",
    "美学",
    "色彩",
    "视觉",
    "用户",
    "体验",
    "交互",
    "界面",
    "功能",
    "开发",
    "代码",
    "程序",
    "系统",
    "平台",
    "云端",
    "网络",
    "连接",
    "通信",
    "信息",
    "学习",
    "知识",
    "教育",
    "成长",
    "进步",
    "合作",
    "团队",
    "分享",
    "交流",
    "社区",
    "商业",
    "市场",
    "产品",
    "服务",
    "价值",
    "生活",
    "健康",
    "运动",
    "旅行",
    "探索",
]


@app.get("/wordcloud/generate")
async def generate_words():
    num_words = random.randint(3, 5)
    selected_words = random.sample(WORD_POOL, num_words)
    return GenerateWordsResponse(words=selected_words)


@app.post("/wordcloud/process")
async def process_words(request: WordCloudRequest):
    words_with_values = [
        {"text": word, "value": random.uniform(0.5, 1.5)} for word in request.words
    ]
    return WordCloudResponse(words=words_with_values)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
