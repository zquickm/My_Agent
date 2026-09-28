"""LLM 客户端：OpenAI 兼容接口的薄封装。

stream_completion 负责协议细节：把流里的文本增量和
tool_call 参数碎片重装成完整对象，交给上层（loop.py）。
"""
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from openai import AsyncOpenAI

from app.config import API_KEY, BASE_URL, MODEL

client = AsyncOpenAI(api_key=API_KEY, base_url=BASE_URL)


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMChunk:
    text: str | None = None
    finish: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


async def stream_completion(
    messages: list[dict], tools_schema: list[dict] | None = None
) -> AsyncIterator[LLMChunk]:
    stream = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
        tools=tools_schema or None,
    )
    pending: dict[int, dict] = {}   # 参数碎片装配台：index -> {id, name, args}

    async for chunk in stream:
        if not chunk.choices:
            continue
        choice = chunk.choices[0]
        delta = choice.delta
        if delta.content:
            yield LLMChunk(text=delta.content)
        for tc in delta.tool_calls or []:
            slot = pending.setdefault(tc.index, {"id": "", "name": "", "args": ""})
            if tc.id:
                slot["id"] = tc.id
            if tc.function:
                if tc.function.name:
                    slot["name"] += tc.function.name
                if tc.function.arguments:
                    slot["args"] += tc.function.arguments
        if choice.finish_reason:
            calls = []
            for s in pending.values():
                try:
                    args = json.loads(s["args"] or "{}")
                except json.JSONDecodeError:
                    args = {}
                calls.append(ToolCall(id=s["id"], name=s["name"], arguments=args))
            yield LLMChunk(finish=choice.finish_reason, tool_calls=calls)