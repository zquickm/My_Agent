"""工具注册表 + 执行流水线。

@tool 装饰器把"pydantic 参数模型 + 函数"注册进表，pydantic 自动
生成 JSON Schema 喂给 LLM。执行统一走流水线：
权限门控 → 参数校验 → 执行 → 输出截断，任何工具都不例外。
"""
import asyncio
import inspect
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel

_TOOLS: dict[str, dict] = {}   # name -> {description, args_model, schema, func}

MAX_OUTPUT_CHARS = 4000        # 输出截断线：防超长结果撑爆上下文


def tool(description: str):
    """@tool("描述") 装饰器。函数签名固定为 f(args: 某个 pydantic 模型)。"""
    def decorator(fn: Callable):
        args_model = inspect.signature(fn).parameters["args"].annotation
        _TOOLS[fn.__name__] = {
            "description": description,
            "args_model": args_model,
            "schema": args_model.model_json_schema(),
            "func": fn,
        }
        return fn
    return decorator


def openai_schemas() -> list[dict]:
    """注册表 → OpenAI tools 参数格式。"""
    return [
        {"type": "function",
         "function": {"name": name, "description": t["description"],
                      "parameters": t["schema"]}}
        for name, t in _TOOLS.items()
    ]


async def execute(name: str, arguments: dict, allowed: set[str] | None = None) -> str:
    """执行流水线。任何失败都变成字符串返回给模型（它可以据此调整），绝不抛异常打断循环。"""
    if allowed is not None and name not in allowed:          # 1) 权限门控
        return f"权限拒绝：当前 agent 无权使用工具 {name}"
    t = _TOOLS.get(name)
    if t is None:
        return f"未知工具：{name}"
    try:
        model = t["args_model"].model_validate(arguments)    # 2) 参数校验
        result = await asyncio.to_thread(t["func"], model)   # 3) 执行（同步函数丢线程池，不卡事件循环）
        text = str(result)
        if len(text) > MAX_OUTPUT_CHARS:                     # 4) 输出截断
            text = text[:MAX_OUTPUT_CHARS] + f"\n…[输出超长已截断，原始 {len(text)} 字符]"
        return text
    except Exception as e:
        return f"工具执行出错：{type(e).__name__}: {e}"


# ================= 起步工具（自己往下面加） =================

class TimeArgs(BaseModel):
    pass


@tool("获取当前本地时间")
def get_current_time(args: TimeArgs) -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ReadFileArgs(BaseModel):
    path: str   # 相对 backend/ 的路径，如 "app/config.py"


_PROTECTED = {".env", ".git"}   # 黑名单：密钥和版本库不进对话


@tool("读取项目内的文本文件，返回文件内容")
def read_file(args: ReadFileArgs) -> str:
    root = Path(__file__).resolve().parent.parent        # backend/
    p = (root / args.path).resolve()
    if not p.is_relative_to(root):                       # 防路径穿越：../ 逃出项目目录
        return f"拒绝访问：{args.path} 在项目目录之外"
    if any(part in _PROTECTED for part in p.parts):      # 防读密钥
        return "拒绝访问：受保护路径"
    return p.read_text(encoding="utf-8", errors="replace")