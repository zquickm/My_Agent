<script setup lang="ts">
defineProps<{ name: string }>()

// 24×24 描边图标：每个名字对应一组 path d，避免引图标库
const paths: Record<string, string[]> = {
  chat: ['M6 4h12a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-7l-5 4v-4H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z'],
  home: ['M3 11l9-8 9 8', 'M5 10v10h14V10'],
  book: ['M4 19.5A2.5 2.5 0 0 1 6.5 17H20', 'M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z'],
  zap: ['M13 2 3 14h9l-1 8 10-12h-9l1-8z'],
  tool: ['M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z'],
  grid: ['M4 4h7v7H4z', 'M13 4h7v7h-7z', 'M4 13h7v7H4z', 'M13 13h7v7h-7z'],
  store: ['M4 9l1.6-5h12.8L20 9', 'M4 9h16', 'M5 9v11h14V9', 'M10 20v-6h4v6'],
  plug: ['M9 7V3', 'M15 7V3', 'M7 7h10v4a5 5 0 0 1-10 0z', 'M12 16v5'],
  gauge: ['M12 15l3.5-5.5', 'M4 15a8 8 0 1 1 16 0'],
  user: ['M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8z', 'M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6'],
  plus: ['M12 5v14', 'M5 12h14'],
  sparkle: ['M12 3l2.2 6.8L21 12l-6.8 2.2L12 21l-2.2-6.8L3 12l6.8-2.2z'],
  refresh: ['M21 12a9 9 0 1 1-2.64-6.36', 'M21 3v6h-6'],
  send: ['M22 2 11 13', 'M22 2 15 22 11 13 2 9 22 2z'],
  panel: ['M3 5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z', 'M9.5 3v18', 'M17 9.5 14.5 12l2.5 2.5'],
}
</script>

<template>
  <svg
    class="icon"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path v-for="(d, i) in paths[name]" :key="i" :d="d" />
  </svg>
</template>

<style scoped>
.icon { display: block; }
</style>
