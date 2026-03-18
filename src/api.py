from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.ai import chat_with_agent
import asyncio
import json

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
