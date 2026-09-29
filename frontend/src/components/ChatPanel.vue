<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '../stores/chat'
import AppIcon from './AppIcon.vue'

const store = useChatStore()

// 当前会话置顶（还没有事件进库时标题显示「新对话」），对应 FastGPT 首页的会话列表
const rows = computed(() => {
  const current = store.sessions.find((s) => s.session_id === store.sessionId)
    ?? { session_id: store.sessionId, title: '', n_events: 0, updated: 0 }
  return [current, ...store.sessions.filter((s) => s.session_id !== store.sessionId)]
})
</script>

<template>
  <aside class="panel">
    <p class="panel-title">聊天</p>
    <button class="new-chat" @click="store.newSession()">
      <AppIcon name="refresh" />新对话
    </button>
    <div class="rows">
      <button
        v-for="s in rows"
        :key="s.session_id"
        class="row"
        :class="{ current: s.session_id === store.sessionId }"
        @click="store.switchSession(s.session_id)"
      >
        <span class="r-title">{{ s.title || '新对话' }}</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.panel { width: 220px; flex: none; background: #fbfcfd; border-right: 1px solid #eef0f3; padding: 14px 10px; display: flex; flex-direction: column; gap: 12px; }
.panel-title { margin: 0 4px; font-size: 15px; font-weight: 700; color: #1f2329; }

.new-chat { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 9px 0; width: 100%; background: #fff; border: 1px solid #e2e6ee; border-radius: 10px; color: #3370ff; font-size: 13px; font-weight: 600; cursor: pointer; transition: border-color 0.15s, box-shadow 0.15s; }
.new-chat:hover { border-color: #3370ff; box-shadow: 0 2px 8px rgba(51, 112, 255, 0.12); }
.new-chat .icon { width: 15px; height: 15px; }

.rows { flex: 1; min-height: 0; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
.row { padding: 9px 12px; border: none; background: transparent; border-radius: 9px; font-size: 13px; color: #3f4550; cursor: pointer; text-align: left; }
.row:hover { background: #f0f2f5; }
.row.current { background: #e9f1ff; color: #3370ff; font-weight: 600; }
.r-title { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
