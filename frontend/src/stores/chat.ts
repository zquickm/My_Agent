import { ref } from 'vue'
import { defineStore } from 'pinia'
import { streamChat, type ChatEvent } from '../api/chat'

// 界面上的一个"气泡"，由事件折叠而成
export interface ChatNode {
  seq: number
  role: 'user' | 'assistant'
  text: string
  done: boolean
}

export const useChatStore = defineStore('chat', () => {
  const nodes = ref<ChatNode[]>([])
  const busy = ref(false)
  const error = ref('')
  let openSeq: number | null = null // 正在生成的 assistant 气泡的 seq

  // 折叠器：一条事件进来，更新节点列表。后端事件流的前端投影
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
      // done 是流结束信号，UI 无需处理
    }
  }

  async function send(content: string) {
    if (busy.value || !content.trim()) return
    busy.value = true // 发送期间禁用输入：后端现在是单会话内存日志，避免并发把顺序写乱（Phase 4 放开）
    error.value = ''
    try {
      await streamChat(content, fold)
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    } finally {
      busy.value = false
    }
  }

  return { nodes, busy, error, send }
})