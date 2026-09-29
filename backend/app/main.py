"""FastAPI 入口。Phase 4：多会话 + SQLite 持久化。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app import store
from app.events import sse
from app.loop import run_turn
from app.session import SessionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await store.init_db()   # 启动时建表
    yield


app = FastAPI(title="My_Agent", lifespan=lifespan)
manager = SessionManager()


class ChatRequest(BaseModel):
    session_id: str
    content: str


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/sessions")
async def sessions():
    return await store.list_sessions()


@app.get("/api/sessions/{session_id}/events")
async def session_events(session_id: str):
    """原始事件流：前端拿它重放折叠器，恢复整个界面。"""
    return [ev.model_dump() for ev in await store.load_events(session_id)]


@app.post("/api/chat")
async def chat(req: ChatRequest):
    log = await manager.get(req.session_id)

    async def emit(type_: str, **payload) -> str:
        return sse(await log.append(type_, **payload))

    async def stream():
        yield await emit("user_message", content=req.content)
        yield await emit("agent_start")
        try:
            async for frame in run_turn(log):
                yield frame
        except Exception as e:
            yield await emit("error", message=str(e))
        yield await emit("agent_end")
        yield await emit("done")

    return StreamingResponse(stream(), media_type="text/event-stream")