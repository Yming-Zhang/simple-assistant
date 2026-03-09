<template>
  <div class="status-bar" v-if="chatStore.isLoading || hasError">
    <div class="status-inner">
      <template v-if="hasError">
        <span class="status-dot error" />
        <span class="status-text error">发生错误</span>
      </template>
      <template v-else-if="chatStore.isLoading">
        <span class="status-dot loading" />
        <span class="status-text">{{ statusText }}</span>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()

const hasError = computed(() => {
  const chain = chatStore.currentThinkingChain
  return chain.length > 0 && chain[chain.length - 1].type === 'error'
})

const statusText = computed(() => {
  const chain = chatStore.currentThinkingChain
  if (chain.length === 0) return '处理中…'
  const last = chain[chain.length - 1]
  switch (last.type) {
    case 'thinking': return '思考中…'
    case 'tool_start': return '调用工具…'
    case 'tool_result': return '工具执行完成'
    default: return '处理中…'
  }
})
</script>

<style scoped>
.status-bar {
  padding: 0 16px;
  height: 26px;
  display: flex;
  align-items: center;
  border-top: 1px solid var(--border-subtle);
  background: var(--panel-bg);
}

.status-inner {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.status-dot.loading {
  background: var(--accent-color);
  animation: pulse 1.2s ease-in-out infinite;
}
.status-dot.error {
  background: var(--error-color);
}

.status-text {
  font-size: 11px;
  color: var(--text-tertiary);
}
.status-text.error {
  color: var(--error-color);
}
</style>
