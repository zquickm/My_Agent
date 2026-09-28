// 前端事件类型：和后端 app/events.py 的字段一一对应
export interface ChatEvent {
  type: string
  agent: string
  payload: Record<string, unknown>
  seq: number
  ts: number
}

/**
 * 发一条消息，流式接收后端推来的每一条事件。
 * 每收到一帧就调用一次 onEvent。
 *
 * 为什么不用 EventSource？它只支持 GET、不能带 JSON body，
 * 所以 POST + 流式的标准做法是 fetch + ReadableStream 手动解析。
 */
export async function streamChat(
  content: string,
  onEvent: (ev: ChatEvent) => void,
): Promise<void> {
  const resp = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })
  if (!resp.ok || !resp.body) {
    throw new Error(`请求失败：${resp.status}`)
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    // stream:true 处理"一个汉字的字节被网络包劈成两半"的情况
    buffer += decoder.decode(value, { stream: true })

    // 关键逻辑：网络包和 SSE 帧不对齐——一个包里可能半帧、可能两帧半。
    // 所以先攒进 buffer，再按帧分隔符（空行 \n\n）循环切。
    let idx: number
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const frame = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      const line = frame.trim()
      if (!line.startsWith('data:')) continue
      onEvent(JSON.parse(line.slice(5).trim()) as ChatEvent)
    }
  }
}