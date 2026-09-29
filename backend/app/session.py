"""事件溯源会话日志：只增不改（append-only），一切皆投影。

Phase 4 升级为写穿（write-through）：事件先落 SQLite 再进内存。
推给前端的事件一定已经在库里——崩溃窗口为零。
"""
from app import store
from app.events import Event


class SessionLog:
    def __init__(self, session_id: str, history: list[Event] | None = None) -> None:
        self.session_id = session_id
        self._events: list[Event] = history or []
        self._seq = self._events[-1].seq + 1 if self._events else 1

    async def append(self, type_: str, agent: str = "assistant", **payload) -> Event:
        ev = Event(type=type_, agent=agent, payload=payload, seq=self._seq)
        self._seq += 1
        await store.save_event(self.session_id, ev)   # 先落库
        self._events.append(ev)                        # 再进内存
        return ev

    @property
    def events(self) -> list[Event]:
        return list(self._events)   # 副本：外部只能读


class SessionManager:
    """内存是缓存，磁盘是真相。重启后第一次 get 自动从库重建。"""

    def __init__(self) -> None:
        self._cache: dict[str, SessionLog] = {}

    async def get(self, session_id: str) -> SessionLog:
        if session_id not in self._cache:
            self._cache[session_id] = SessionLog(
                session_id, await store.load_events(session_id))
        return self._cache[session_id]


def to_llm_messages(events: list[Event]) -> list[dict]:
    """投影：事件流 → OpenAI messages（Phase 3 版，原样保留）。

    规则：user_message → user 消息；连续 text_delta 合并成一条
    assistant 文本；连续 tool_call 并入同一条 assistant 消息的
    tool_calls；tool_result → role:"tool" 消息。
    agent_start/end、done、error 不参与投影。
    """
    import json
    messages: list[dict] = []
    buf: str | None = None
    pending_calls: list[dict] = []

    def flush_assistant() -> None:
        nonlocal buf, pending_calls
        if buf or pending_calls:
            msg: dict = {"role": "assistant", "content": buf or ""}
            if pending_calls:
                msg["tool_calls"] = pending_calls
            messages.append(msg)
        buf, pending_calls = None, []

    for ev in events:
        if ev.type == "user_message":
            flush_assistant()
            messages.append({"role": "user", "content": ev.payload["content"]})
        elif ev.type == "text_delta":
            buf = (buf or "") + ev.payload["content"]
        elif ev.type == "tool_call":
            pending_calls.append({
                "id": ev.payload["call_id"],
                "type": "function",
                "function": {
                    "name": ev.payload["name"],
                    "arguments": json.dumps(ev.payload["arguments"], ensure_ascii=False),
                },
            })
        elif ev.type == "tool_result":
            flush_assistant()
            messages.append({
                "role": "tool",
                "tool_call_id": ev.payload["call_id"],
                "content": ev.payload["output"],
            })
    flush_assistant()
    return messages