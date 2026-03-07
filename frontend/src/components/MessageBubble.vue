<template>
  <div class="message-bubble" :class="{ 'user-message': message.role === 'user', 'assistant-message': message.role === 'assistant' }">
    <div class="message-avatar">
      {{ message.role === 'user' ? '👤' : '🤖' }}
    </div>
    <div class="message-content">
      <div v-if="message.role === 'assistant' && message.thinkingChain && settingsStore.showThinkingChain" class="thinking-preview">
        <el-collapse>
          <el-collapse-item title="📝 思考过程">
            <ThinkingChain :events="message.thinkingChain" />
          </el-collapse-item>
        </el-collapse>
      </div>
      <div class="message-text" v-html="renderedContent"></div>
      <div v-if="message.images && message.images.length > 0" class="message-images">
        <img v-for="(img, idx) in message.images" :key="idx" :src="img" class="message-image" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { renderMarkdown } from '@/utils/markdown'
import ThinkingChain from './ThinkingChain.vue'
import type { Message } from '@/types'

const props = defineProps<{
  message: Message
}>()

const settingsStore = useSettingsStore()

const renderedContent = computed(() => {
  return renderMarkdown(props.message.content)
})
</script>

<style scoped>
.message-bubble {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  max-width: 100%;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message-content {
  max-width: calc(100% - 60px);
}

.thinking-preview {
  margin-bottom: 8px;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
}

.assistant-message .message-text {
  background: #f5f7fa;
  color: #303133;
}

.user-message .message-text {
  background: #409eff;
  color: white;
}

.message-text :deep(p) {
  margin: 0;
}

.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.message-images {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.message-image {
  max-width: 200px;
  max-height: 150px;
  border-radius: 8px;
  cursor: pointer;
}
</style>
