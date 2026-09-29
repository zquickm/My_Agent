<script setup lang="ts">
import AppIcon from './AppIcon.vue'

defineProps<{ active: string }>()
const emit = defineEmits<{ (e: 'select', key: string): void }>()

// 工作台的模块清单：全部是预留位，对应 FastGPT 工作台第二列
const groups: { key: string; label: string; icon: string; beta?: boolean }[][] = [
  [
    { key: 'skills', label: '技能', icon: 'zap' },
    { key: 'myTools', label: '我的工具', icon: 'tool' },
    { key: 'sysTools', label: '系统工具', icon: 'grid' },
  ],
  [
    { key: 'templates', label: '模板市场', icon: 'store' },
    { key: 'mcp', label: 'MCP 服务', icon: 'plug' },
    { key: 'eval', label: 'Agent 评测', icon: 'gauge', beta: true },
  ],
]
</script>

<template>
  <aside class="panel">
    <p class="panel-title">模块</p>
    <template v-for="(group, gi) in groups" :key="gi">
      <div v-if="gi" class="gap"></div>
      <button
        v-for="item in group"
        :key="item.key"
        class="row"
        :class="{ current: active === item.key }"
        @click="emit('select', item.key)"
      >
        <AppIcon :name="item.icon" /><span class="r-title">{{ item.label }}</span>
        <span v-if="item.beta" class="beta">Beta</span>
      </button>
    </template>
  </aside>
</template>

<style scoped>
.panel { width: 220px; flex: none; background: #fbfcfd; border-right: 1px solid #eef0f3; padding: 14px 10px; display: flex; flex-direction: column; gap: 4px; overflow-y: auto; }
.panel-title { margin: 0 4px 8px; font-size: 15px; font-weight: 700; color: #1f2329; }
.gap { height: 1px; background: #eef0f3; margin: 8px 4px; }

.row { display: flex; align-items: center; gap: 10px; padding: 10px 12px; border: none; background: transparent; border-radius: 9px; font-size: 14px; color: #3f4550; cursor: pointer; text-align: left; }
.row:hover { background: #f0f2f5; }
.row.current { background: #e9f1ff; color: #3370ff; font-weight: 600; }
.row .icon { width: 16px; height: 16px; flex: none; }
.r-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.beta { margin-left: auto; font-size: 10px; line-height: 1; padding: 3px 7px; border-radius: 99px; background: #e9f1ff; color: #3370ff; }
.row.current .beta { background: #fff; }
</style>
