from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.ai import chat_with_agent
import asyncio

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


@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        messages = [{"role": "user", "content": request.message}]
        
        full_response = ""
        async for chunk in chat_with_agent(messages):
            full_response += chunk
        
        return ChatResponse(
            response=full_response,
            conversationId=request.conversationId,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
