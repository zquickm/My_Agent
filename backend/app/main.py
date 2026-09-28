"""FastAPI 入口。Phase 3：/api/chat 背后是完整的 Agent 循环。"""
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.events import sse
from app.loop import run_turn
from app.session import SessionLog

app = FastAPI(title="My_Agent")
log = SessionLog()


class ChatRequest(BaseModel):
    content: str


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    def emit(type_: str, **payload) -> str:
        return sse(log.append(type_, **payload))

    async def stream():
        yield emit("user_message", content=req.content)
        yield emit("agent_start")
        try:
            async for frame in run_turn(log):
                yield frame
        except Exception as e:
            yield emit("error", message=str(e))
        yield emit("agent_end")
        yield emit("done")

    return StreamingResponse(stream(), media_type="text/event-stream")