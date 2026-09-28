"""通用 Agent 循环：调 LLM → 要工具就执行 → 回填 → 再调 → 直到最终回答。

Phase 5 的多 Agent 会复用这个循环——delegate 只是众多工具之一，
专家 Agent 也靠它驱动。这就是"注册表与驱动器分离"的驱动器。
"""
from collections.abc import AsyncIterator

from app import llm, tools
from app.events import sse
from app.session import SessionLog, to_llm_messages

SYSTEM_PROMPT = (
    "你是 My_Agent，一个能调用工具的助手。"
    "需要事实信息时先调用工具，基于工具结果回答，不要编造。"
)


async def run_turn(log: SessionLog) -> AsyncIterator[str]:
    while True:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *to_llm_messages(log.events),
        ]
        finish: str | None = None
        calls: list = []
        async for ch in llm.stream_completion(messages, tools.openai_schemas()):
            if ch.text:
                yield sse(log.append("text_delta", content=ch.text))
            if ch.finish:
                finish, calls = ch.finish, ch.tool_calls

        if finish != "tool_calls" or not calls:
            break   # 模型不再要工具 = 最终回答已流式输出完毕

        for call in calls:
            yield sse(log.append("tool_call", call_id=call.id,
                                 name=call.name, arguments=call.arguments))
            output = await tools.execute(call.name, call.arguments)
            yield sse(log.append("tool_result", call_id=call.id,
                                 name=call.name, output=output))
        # 回到顶部：投影函数已把工具结果变成 messages，带着结果再问模型