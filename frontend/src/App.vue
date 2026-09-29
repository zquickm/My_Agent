<script setup lang="ts">
import { ref } from 'vue'
import AppIcon from './components/AppIcon.vue'
import SideBar from './components/SideBar.vue'
import ChatPanel from './components/ChatPanel.vue'
import ModulePanel from './components/ModulePanel.vue'
import ChatView from './views/ChatView.vue'

const section = ref('home') // 首页（聊天）| 工作台 | 知识库 | 账号
const activeModule = ref('skills') // 工作台下当前选中的模块
const navHidden = ref(false) // 最左全局导航栏折叠状态

// 预留模块的展示名；后续每接入一个后端能力，就把对应的占位分支换成真视图组件
const labels: Record<string, string> = {
  skills: '技能',
  myTools: '我的工具',
  sysTools: '系统工具',
  templates: '模板市场',
  mcp: 'MCP 服务',
  eval: 'Agent 评测',
  kb: '知识库',
  account: '账号',
}
</script>

<template>
  <div class="shell">
    <SideBar v-if="!navHidden" :active="section" @navigate="section = $event" />

    <!-- 导航栏折叠开关：固定在品牌行位置，收起后停留在原处（落在聊天面板头部行） -->
    <button
      class="nav-toggle"
      :class="{ flipped: navHidden }"
      :title="navHidden ? '展开导航栏' : '收起导航栏'"
      @click="navHidden = !navHidden"
    >
      <AppIcon name="panel" />
    </button>

    <!-- 第二列：随分区切换的上下文面板（首页=聊天列表，工作台=模块清单） -->
    <ChatPanel v-if="section === 'home'" />
    <ModulePanel v-else-if="section === 'workbench'" :active="activeModule" @select="activeModule = $event" />

    <main class="main">
      <ChatView v-if="section === 'home'" />
      <div v-else class="placeholder">
        <div class="panel-card placeholder-card">
          <AppIcon name="sparkle" class="ph-icon" />
          <h2>{{ labels[section === 'workbench' ? activeModule : section] || '' }}</h2>
          <p>接口已预留，后端能力就绪后在此接入</p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; height: 100vh; overflow: hidden; position: relative; }

/* 导航栏折叠开关，钉在品牌行 Logo 右侧的固定坐标（SideBar 的品牌行是确定布局） */
.nav-toggle { position: absolute; left: 154px; top: 17px; width: 28px; height: 28px; border: none; background: transparent; border-radius: 7px; color: #6b7280; cursor: pointer; display: flex; align-items: center; justify-content: center; z-index: 10; transition: background 0.15s, color 0.15s; }
.nav-toggle:hover { background: #eef1f5; color: #3370ff; }
.nav-toggle .icon { width: 17px; height: 17px; transition: transform 0.15s; }
.nav-toggle.flipped .icon { transform: scaleX(-1); }

.main { flex: 1; min-width: 0; display: flex; flex-direction: column; background: #fff; }

.placeholder { flex: 1; display: flex; align-items: center; justify-content: center; padding: 24px; background: #f7f8fa; }
.placeholder-card { padding: 56px 72px; }
.ph-icon { width: 30px; height: 30px; color: #7c5cff; }
.placeholder-card h2 { margin: 14px 0 8px; font-size: 20px; color: #23262e; }
.placeholder-card p { margin: 0; font-size: 13px; color: #8a9099; }
</style>
