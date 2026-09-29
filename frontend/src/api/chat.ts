export interface ChatEvent {
  type: string
  agent: string
  payload: Record<string, unknown>
  seq: number
  ts: number
}

export interface SessionInfo {
  session_id: string
  title: string
  n_events: number
  updated: number
}

export async function streamChat(
  sessionId: string,
  content: string,
  onEvent: (ev: ChatEvent) => void,
): Promise<void> {
  const resp = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, content }),
  })
  if (!resp.ok || !resp.body) throw new Error(`请求失败：${resp.status}`)

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
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

export async function loadHistory(sessionId: string): Promise<ChatEvent[]> {
  const resp = await fetch(`/api/sessions/${sessionId}/events`)
  if (!resp.ok) throw new Error(`加载历史失败：${resp.status}`)
  return resp.json()
}

export async function fetchSessions(): Promise<SessionInfo[]> {
  const resp = await fetch('/api/sessions')
  if (!resp.ok) throw new Error(`加载会话列表失败：${resp.status}`)
  return resp.json()
}