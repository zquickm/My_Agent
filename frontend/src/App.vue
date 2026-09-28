<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from './stores/chat'

const store = useChatStore()
const input = ref('')
const listEl = ref<HTMLElement | null>(null)

async function submit() {
  const text = input.value.trim()
  if (!text) return
  input.value = ''
  await store.send(text)
}

// 最后一条气泡的文本每变一次 → 等 DOM 更新后滚到底部
watch(
  () => store.nodes[store.nodes.length - 1]?.text,
  async () => {
    await nextTick()
    listEl.value?.scrollTo({ top: listEl.value.scrollHeight })
  },
)
</script>

<template>
  <div class="chat">
    <header>My_Agent</header>
    <div class="list" ref="listEl">
      <div v-for="node in store.nodes" :key="node.seq" class="bubble" :class="node.role">
        <span class="role">{{ node.role === 'user' ? '我' : 'Agent' }}</span>
        <p>{{ node.text }}<span v-if="!node.done" class="cursor">▍</span></p>
      </div>
      <p v-if="store.error" class="error">出错了：{{ store.error }}</p>
    </div>
    <form class="input-bar" @submit.prevent="submit">
      <input v-model="input" :disabled="store.busy" placeholder="输入消息，回车发送" />
      <button type="submit" :disabled="store.busy || !input.trim()">发送</button>
    </form>
  </div>
</template>

<style scoped>
.chat { display: flex; flex-direction: column; height: 100vh; }
header { padding: 12px 16px; background: #1f2937; color: #fff; font-weight: 600; }
.list { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }
.bubble { max-width: 80%; padding: 10px 14px; border-radius: 12px; line-height: 1.6; }
.bubble.user { align-self: flex-end; background: #3b82f6; color: #fff; }
.bubble.assistant { align-self: flex-start; background: #fff; border: 1px solid #e5e7eb; }
.role { display: block; font-size: 12px; opacity: 0.7; margin-bottom: 4px; }
.bubble p { margin: 0; white-space: pre-wrap; word-break: break-word; }
.cursor { animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0; } }
.error { color: #dc2626; }
.input-bar { display: flex; gap: 8px; padding: 12px; background: #fff; border-top: 1px solid #e5e7eb; }
.input-bar input { flex: 1; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; }
.input-bar button { padding: 10px 18px; border: none; border-radius: 8px; background: #3b82f6; color: #fff; cursor: pointer; }
.input-bar button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>