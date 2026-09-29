"""SQLite 事件存储：events 表就是系统的全部记忆。

append-only，和内存版同一个心智模型——只是把日志放到了磁盘上。
ponytail: 每次操作新开连接，聊天量级足够；升级路径是共享一个
aiosqlite 连接（它自带写队列）。
"""
import json
from pathlib import Path

import aiosqlite

from app.events import Event

DB_PATH = Path(__file__).resolve().parent.parent / "my_agent.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    type TEXT NOT NULL,
    agent TEXT NOT NULL,
    payload TEXT NOT NULL,
    ts REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id, seq);
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)


async def save_event(session_id: str, ev: Event) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO events (session_id, seq, type, agent, payload, ts) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, ev.seq, ev.type, ev.agent,
             json.dumps(ev.payload, ensure_ascii=False), ev.ts),
        )
        await db.commit()


async def load_events(session_id: str) -> list[Event]:
    """按会话取全部事件，按 seq 排序——这就是"从日志重建"的原料。"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT seq, type, agent, payload, ts FROM events WHERE session_id = ? ORDER BY seq",
            (session_id,),
        ) as cur:
            rows = await cur.fetchall()
    return [
        Event(type=r["type"], agent=r["agent"], payload=json.loads(r["payload"]),
              seq=r["seq"], ts=r["ts"])
        for r in rows
    ]


async def list_sessions() -> list[dict]:
    """会话列表：id、事件数、最后活动时间、标题（取第一条用户消息）。"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT session_id, COUNT(*) AS n, MAX(ts) AS updated "
            "FROM events GROUP BY session_id ORDER BY updated DESC"
        ) as cur:
            rows = await cur.fetchall()
        out = []
        for r in rows:
            async with db.execute(
                "SELECT payload FROM events WHERE session_id = ? AND type = 'user_message' "
                "ORDER BY seq LIMIT 1",
                (r["session_id"],),
            ) as cur:
                row = await cur.fetchone()
            title = json.loads(row["payload"]).get("content", "")[:30] if row else "(空会话)"
            out.append({"session_id": r["session_id"], "title": title,
                        "n_events": r["n"], "updated": r["updated"]})
    return out