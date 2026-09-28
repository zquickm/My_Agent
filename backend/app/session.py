"""事件溯源会话日志：只增不改（append-only），一切皆投影。

Phase 1 是内存版，重启即失忆——这是故意的，先把流跑通；
Phase 4 换 SQLite，append 和投影代码不变，只是 events 的存放位置变了。
"""
import itertools
import json

from app.events import Event


class SessionLog:
    def __init__(self) -> None:
        self._events: list[Event] = []
        self._seq = itertools.count(1)

    def append(self, type_: str, agent: str = "assistant", **payload) -> Event:
        ev = Event(type=type_, agent=agent, payload=payload, seq=next(self._seq))
        self._events.append(ev)
        return ev

    @property
    def events(self) -> list[Event]:
        return list(self._events)   # 返回副本：外部只能读，改不了日志


def to_llm_messages(events: list[Event]) -> list[dict]:
    """投影：事件流 → OpenAI messages 格式。

    规则：user_message → user 消息；连续 text_delta 合并成一条
    assistant 文本；连续 tool_call 并入同一条 assistant 消息的
    tool_calls；tool_result → role:"tool" 消息。
    agent_start/end、done、error 不参与投影。
    """
    messages: list[dict] = []
    buf: str | None = None          # 正在累积的 assistant 文本
    pending_calls: list[dict] = []  # 同一轮的工具调用

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
            flush_assistant()   # 调用先于结果落位
            messages.append({
                "role": "tool",
                "tool_call_id": ev.payload["call_id"],
                "content": ev.payload["output"],
            })
    flush_assistant()
    return messages