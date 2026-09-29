<script setup lang="ts">
import AppIcon from './AppIcon.vue'

defineProps<{ active: string }>()
const emit = defineEmits<{ (e: 'navigate', key: string): void }>()

// 最左全局导航：首页=聊天，工作台=模块区，知识库为预留位
const items = [
  { key: 'home', label: '首页', icon: 'chat' },
  { key: 'workbench', label: '工作台', icon: 'grid' },
  { key: 'kb', label: '知识库', icon: 'book' },
]
</script>

<template>
  <aside class="nav">
    <div class="brand">
      <span class="logo">M</span>
      <span class="name">My_Agent</span>
    </div>
    <nav>
      <button
        v-for="item in items"
        :key="item.key"
        class="nav-item"
        :class="{ active: active === item.key }"
        @click="emit('navigate', item.key)"
      >
        <AppIcon :name="item.icon" /><span>{{ item.label }}</span>
      </button>
    </nav>
    <div class="spacer"></div>
    <button class="nav-item" :class="{ active: active === 'account' }" @click="emit('navigate', 'account')">
      <AppIcon name="user" /><span>账号</span>
    </button>
  </aside>
</template>

<style scoped>
.nav { width: 216px; flex: none; background: #f9fafb; border-right: 1px solid #eef0f3; padding: 14px 12px; display: flex; flex-direction: column; }

.brand { display: flex; align-items: center; gap: 10px; padding: 2px 4px 14px; }
.logo { width: 30px; height: 30px; border-radius: 9px; background: linear-gradient(135deg, #3370ff, #7c5cff); color: #fff; font-weight: 800; font-size: 14px; display: flex; align-items: center; justify-content: center; }
.name { font-size: 16px; font-weight: 800; color: #1f2329; }

nav { display: flex; flex-direction: column; gap: 4px; }
.nav-item { display: flex; align-items: center; gap: 10px; width: 100%; padding: 10px 12px; border: none; background: transparent; border-radius: 9px; font-size: 14px; color: #3f4550; cursor: pointer; text-align: left; transition: background 0.15s, color 0.15s; }
.nav-item:hover { background: #eef1f5; }
.nav-item.active { background: #e9f1ff; color: #3370ff; font-weight: 600; }
.nav-item .icon { width: 17px; height: 17px; }

.spacer { flex: 1; }
</style>
