"""事件词汇表：整个系统只说这一种"语言"。

UI 渲染、LLM 历史、会话恢复，全部从同一份事件流投影出来——
事件是唯一事实，其余皆是视图。
"""
import time

from pydantic import BaseModel, Field

# Phase 1 用到的类型；Phase 3 会加入 tool_call / tool_result
EVENT_TYPES = (
    "user_message",   # payload: content   用户发言
    "agent_start",    #                    agent 开始处理这一轮
    "text_delta",     # payload: content   回答的文本增量
    "agent_end",      #                    agent 本轮结束
    "error",          # payload: message   出错
    "done",           #                    整轮结束（SSE 流的收尾信号）
    "tool_call",      # payload: call_id, name, arguments
    "tool_result"     # payload: call_id, name, output
)


class Event(BaseModel):
    type: str
    agent: str = "assistant"   # 谁产生的。Phase 5 多 agent 时它是主角，现在先统一默认值
    payload: dict = {}
    seq: int = 0               # 在会话日志里的序号，append 时分配
    ts: float = Field(default_factory=time.time)

def sse(ev: Event) -> str:
    """一条事件 → 一帧 SSE（data: {json} + 空行）。"""
    return f"data: {ev.model_dump_json()}\n\n"