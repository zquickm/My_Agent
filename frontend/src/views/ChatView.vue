<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useChatStore } from '../stores/chat'
import AppIcon from '../components/AppIcon.vue'

const store = useChatStore()
const input = ref('')
const inputEl = ref<HTMLInputElement | null>(null)
const threadEl = ref<HTMLElement | null>(null)

const title = computed(
  () => store.sessions.find((s) => s.session_id === store.sessionId)?.title || '新对话',
)

onMounted(() => {
  store.init()
  inputEl.value?.focus()
})

async function submit() {
  const text = input.value.trim()
  if (!text) return
  input.value = ''
  await store.send(text)
  await nextTick()
  inputEl.value?.focus()
}

watch(
  () => store.nodes[store.nodes.length - 1]?.text,
  async () => {
    await nextTick()
    threadEl.value?.scrollTo({ top: threadEl.value.scrollHeight })
  },
)
</script>

<template>
  <div class="chat">
    <div class="chat-top">
      <span class="title">{{ title }}</span>
    </div>

    <div class="thread" ref="threadEl">
      <div v-if="store.nodes.length" class="thread-inner">
        <div v-for="node in store.nodes" :key="node.seq" class="bubble" :class="node.role">
          <span class="role">{{ node.role === 'user' ? '我' : 'Agent' }}</span>
          <p v-if="node.text || node.done">{{ node.text }}<span v-if="!node.done" class="cursor">▍</span></p>
          <div v-else class="dots" role="status" aria-label="正在思考"><i></i><i></i><i></i></div>
        </div>
      </div>

      <!-- 空态：对应 FastGPT 首页的 Logo + 问候语 -->
      <div v-else class="hero">
        <div class="brand-row">
          <span class="logo">M</span>
          <span class="name">My_Agent</span>
        </div>
        <p class="greeting">今天想做什么？</p>
      </div>

      <p v-if="store.error" class="error">出错了：{{ store.error }}</p>
    </div>

    <div class="composer-wrap">
      <form class="composer" @submit.prevent="submit">
        <input ref="inputEl" v-model="input" :disabled="store.busy" placeholder="发消息给 My_Agent" />
        <div class="composer-row">
          <span class="hint">回车发送</span>
          <button type="submit" class="send" :disabled="store.busy || !input.trim()" aria-label="发送">
            <AppIcon name="send" />
          </button>
        </div>
      </form>
      <p class="disclaimer">内容由 AI 生成，请注意甄别</p>
    </div>
  </div>
</template>

<style scoped>
.chat { flex: 1; min-height: 0; display: flex; flex-direction: column; background: #fff; }

.chat-top { flex: none; height: 56px; display: flex; align-items: center; justify-content: center; }
.title { font-size: 14px; color: #4b5563; }

.thread { flex: 1; min-height: 0; overflow-y: auto; padding: 8px 16px 16px; display: flex; flex-direction: column; }
.thread::-webkit-scrollbar { width: 8px; }
.thread::-webkit-scrollbar-thumb { background: #dfe3ea; border-radius: 4px; }
.thread-inner { width: 100%; max-width: 780px; margin: 0 auto; display: flex; flex-direction: column; gap: 14px; }

.bubble { max-width: 78%; padding: 10px 14px; border-radius: 14px; line-height: 1.65; font-size: 14px; animation: rise 0.22s ease-out; }
.bubble.user { align-self: flex-end; background: #3370ff; color: #fff; border-bottom-right-radius: 4px; }
.bubble.assistant { align-self: flex-start; background: #fff; border: 1px solid #e8ebf0; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(31, 35, 41, 0.04); }
.role { display: block; font-size: 11px; opacity: 0.55; margin-bottom: 3px; letter-spacing: 0.05em; }
.bubble p { margin: 0; white-space: pre-wrap; word-break: break-word; }
.cursor { animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0; } }
@keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }

.dots { display: inline-flex; gap: 4px; padding: 5px 0; }
.dots i { width: 6px; height: 6px; border-radius: 50%; background: currentColor; opacity: 0.35; animation: bounce 1.2s infinite; }
.dots i:nth-child(2) { animation-delay: 0.15s; }
.dots i:nth-child(3) { animation-delay: 0.3s; }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0); opacity: 0.35; } 30% { transform: translateY(-4px); opacity: 1; } }

.hero { margin: auto; text-align: center; }
.brand-row { display: flex; align-items: center; justify-content: center; gap: 12px; }
.logo { width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, #3370ff, #7c5cff); color: #fff; font-size: 20px; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.name { font-size: 26px; font-weight: 800; color: #1f2329; }
.greeting { margin: 14px 0 0; font-size: 20px; font-weight: 600; color: #1f2329; }

.composer-wrap { flex: none; padding: 0 16px 8px; }
.composer { width: min(780px, 100%); margin: 0 auto; background: #fff; border: 1px solid #e5e8ef; border-radius: 16px; box-shadow: 0 4px 18px rgba(31, 35, 41, 0.07); padding: 12px 14px 10px; display: flex; flex-direction: column; gap: 6px; }
.composer input { border: none; outline: none; font-size: 14px; color: #1f2329; background: transparent; padding: 2px 4px; font-family: inherit; }
.composer input::placeholder { color: #a0a6b0; }
.composer input:disabled { opacity: 0.6; }
.composer-row { display: flex; align-items: center; justify-content: space-between; }
.hint { font-size: 12px; color: #b0b6c0; }
.send { width: 36px; height: 36px; border: none; border-radius: 10px; background: #3370ff; color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.15s, transform 0.05s, opacity 0.15s; }
.send:hover:not(:disabled) { background: #2b5fd9; }
.send:active:not(:disabled) { transform: translateY(1px); }
.send:disabled { opacity: 0.4; cursor: not-allowed; }
.send .icon { width: 17px; height: 17px; }

.disclaimer { margin: 8px 0 0; text-align: center; font-size: 11px; color: #b9bfc9; }

.error { margin: 12px auto 0; color: #b3403a; background: #faeceb; border: 1px solid #f0d2d0; padding: 6px 14px; border-radius: 10px; font-size: 13px; }

@media (prefers-reduced-motion: reduce) {
  .bubble, .cursor, .dots i { animation: none; }
}
</style>
