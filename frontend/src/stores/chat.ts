import { ref } from 'vue'
import { defineStore } from 'pinia'
import { streamChat, loadHistory, fetchSessions, type ChatEvent, type SessionInfo } from '../api/chat'

export interface ChatNode {
  seq: number
  role: 'user' | 'assistant'
  text: string
  done: boolean
}

function currentSessionId(): string {
  // 当前会话 id 存 localStorage：刷新页面不丢
  let id = localStorage.getItem('my_agent_session')
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem('my_agent_session', id)
  }
  return id
}

export const useChatStore = defineStore('chat', () => {
  const nodes = ref<ChatNode[]>([])
  const busy = ref(false)
  const error = ref('')
  const sessionId = ref(currentSessionId())
  const sessions = ref<SessionInfo[]>([])
  let openSeq: number | null = null

  function fold(ev: ChatEvent) {
    switch (ev.type) {
      case 'user_message':
        nodes.value.push({ seq: ev.seq, role: 'user', text: String(ev.payload.content ?? ''), done: true })
        break
      case 'agent_start':
        nodes.value.push({ seq: ev.seq, role: 'assistant', text: '', done: false })
        openSeq = ev.seq
        break
      case 'text_delta': {
        const node = nodes.value.find((n) => n.seq === openSeq)
        if (node) node.text += String(ev.payload.content ?? '')
        break
      }
      case 'agent_end': {
        const node = nodes.value.find((n) => n.seq === openSeq)
        if (node) node.done = true
        openSeq = null
        break
      }
      case 'error':
        error.value = String(ev.payload.message ?? '未知错误')
        break
    }
  }

  function resetView() {
    nodes.value = []
    openSeq = null
    error.value = ''
  }

  // 界面恢复 = 对历史事件重放同一个折叠器。fold 一行没改——投影的幂等性
  async function init() {
    resetView()
    try {
      for (const ev of await loadHistory(sessionId.value)) fold(ev)
    } catch { /* 新会话还没有历史，正常 */ }
    sessions.value = await fetchSessions().catch(() => sessions.value)
  }

  async function switchSession(id: string) {
    if (!id || id === sessionId.value) return
    sessionId.value = id
    localStorage.setItem('my_agent_session', id)
    await init()
  }

  async function newSession() {
    sessionId.value = crypto.randomUUID()
    localStorage.setItem('my_agent_session', sessionId.value)
    resetView()
    sessions.value = await fetchSessions().catch(() => sessions.value)
  }

  async function send(content: string) {
    if (busy.value || !content.trim()) return
    busy.value = true
    error.value = ''
    try {
      await streamChat(sessionId.value, content, fold)
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    } finally {
      busy.value = false
      sessions.value = await fetchSessions().catch(() => sessions.value)
    }
  }

  return { nodes, busy, error, sessionId, sessions, init, switchSession, newSession, send }
})