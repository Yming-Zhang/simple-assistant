<template>
  <div class="msg-row" :class="[message.role, message.status]">
    <!-- 头像 -->
    <div class="msg-avatar">
      <span v-if="message.role === 'user'" class="avatar-icon user-avatar">U</span>
      <span v-else class="avatar-icon bot-avatar">✦</span>
    </div>

    <!-- 内容区 -->
    <div class="msg-body">
      <!-- 思考过程（默认折叠） -->
      <div v-if="message.role === 'assistant' && message.thinkingChain && message.thinkingChain.length > 0 && settingsStore.showThinkingChain" class="thinking-fold">
        <button class="thinking-toggle" @click="showThinking = !showThinking">
          <svg width="12" height="12" viewBox="0 0 12 12" :class="{ rotated: showThinking }"><path d="M4 2l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
          <span>思考过程（{{ message.thinkingChain.length }} 步）</span>
        </button>
        <transition name="fold">
          <div v-if="showThinking" class="thinking-content">
            <ThinkingChain :events="message.thinkingChain" />
          </div>
        </transition>
      </div>

      <!-- 消息气泡 -->
      <div class="msg-bubble">
        <div class="markdown-body" v-html="renderedContent" />
      </div>

      <!-- 图片附件 -->
      <div v-if="message.images && message.images.length > 0" class="msg-images">
        <img v-for="(img, idx) in message.images" :key="idx" :src="img" class="msg-image" />
      </div>

      <!-- 状态指示 -->
      <div v-if="message.status === 'streaming'" class="msg-status streaming">
        <span class="typing-dot" /><span class="typing-dot" /><span class="typing-dot" />
      </div>
      <div v-else-if="message.status === 'error'" class="msg-status error">
        发送失败
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { renderMarkdown } from '@/utils/markdown'
import ThinkingChain from './ThinkingChain.vue'
import type { Message } from '@/types'

const props = defineProps<{
  message: Message
}>()

const settingsStore = useSettingsStore()
const showThinking = ref(false)

const renderedContent = computed(() => renderMarkdown(props.message.content))
</script>

<style scoped>
.msg-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  animation: slideUp 0.25s ease;
}

/* 用户消息靠右 */
.msg-row.user {
  flex-direction: row-reverse;
}

/* ---- 头像 ---- */
.msg-avatar {
  flex-shrink: 0;
  margin-top: 2px;
}
.avatar-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
}
.user-avatar {
  background: var(--accent-gradient);
  color: var(--text-inverse);
}
.bot-avatar {
  background: var(--card-bg);
  color: var(--accent-color);
  font-size: 16px;
}

/* ---- 消息体 ---- */
.msg-body {
  max-width: 75%;
  min-width: 60px;
}

/* ---- 气泡 ---- */
.msg-bubble {
  padding: 10px 14px;
  border-radius: var(--radius-md);
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
}

.msg-row.assistant .msg-bubble {
  background: var(--assistant-bubble-bg);
  color: var(--assistant-bubble-text);
  border: 1px solid var(--border-subtle);
  border-top-left-radius: 4px;
}

.msg-row.user .msg-bubble {
  background: var(--user-bubble-bg);
  color: var(--user-bubble-text);
  border-top-right-radius: 4px;
}

/* 用户气泡内代码反色 */
.msg-row.user .msg-bubble :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

/* ---- 思考过程折叠 ---- */
.thinking-fold {
  margin-bottom: 6px;
}

.thinking-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  color: var(--text-tertiary);
  transition: all var(--transition-fast);
}
.thinking-toggle:hover {
  background: var(--card-bg-hover);
  color: var(--text-secondary);
}
.thinking-toggle svg {
  transition: transform var(--transition-fast);
}
.thinking-toggle svg.rotated {
  transform: rotate(90deg);
}

.thinking-content {
  margin-top: 4px;
  padding: 8px 12px;
  background: var(--card-bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
}

.fold-enter-active, .fold-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}
.fold-enter-from, .fold-leave-to {
  opacity: 0;
  max-height: 0;
}
.fold-enter-to, .fold-leave-from {
  opacity: 1;
  max-height: 500px;
}

/* ---- 图片 ---- */
.msg-images {
  display: flex;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
}
.msg-image {
  max-width: 200px;
  max-height: 150px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: transform var(--transition-fast);
}
.msg-image:hover {
  transform: scale(1.03);
}

/* ---- 状态 ---- */
.msg-status {
  margin-top: 4px;
  font-size: 11px;
}
.msg-status.error {
  color: var(--error-color);
}
.msg-status.streaming {
  display: flex;
  gap: 3px;
  padding: 4px 0;
}
.typing-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--text-tertiary);
  animation: pulse 1.2s ease-in-out infinite;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }
</style>
