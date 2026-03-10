<template>
  <div class="floating-wrapper">
    <div
      class="floating-capsule"
      :class="{ recording: isRecording, typing: mode === 'typing' }"
      @mousedown="onDragStart"
    >
      <!-- ===================== 录音态 ===================== -->
      <template v-if="isRecording">
        <span class="rec-icon-center">
          <svg width="22" height="22" viewBox="0 0 16 16">
            <rect x="5" y="1.5" width="6" height="8" rx="3" stroke="currentColor" stroke-width="1.3" fill="none"/>
            <path d="M3.5 8a4.5 4.5 0 009 0" stroke="currentColor" stroke-width="1.3" fill="none" stroke-linecap="round"/>
            <line x1="8" y1="12.5" x2="8" y2="14.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
          <span class="rec-pulse-ring" />
        </span>
        <span class="rec-label">正在聆听…</span>
        <button class="capsule-btn stop-btn capsule-clickable" @click.stop="stopRecording" title="停止">
          <svg width="14" height="14" viewBox="0 0 14 14"><rect x="2" y="2" width="10" height="10" rx="2" fill="currentColor"/></svg>
        </button>
      </template>

      <!-- ===================== 文字输入态 ===================== -->
      <template v-else-if="mode === 'typing'">
        <span class="capsule-logo-mini">✦</span>
        <input
          ref="inputRef"
          class="capsule-input capsule-clickable"
          v-model="inputText"
          placeholder="输入消息…"
          @keydown.enter.prevent="sendText"
          @keydown.esc="exitTyping"
          @click.stop
        />
        <button class="capsule-btn send-btn capsule-clickable" @click.stop="sendText" title="发送" :disabled="!inputText.trim()">
          <svg width="16" height="16" viewBox="0 0 16 16"><path d="M2 8l5-5v3.5h5v3H7V13z" fill="currentColor" transform="rotate(-90 8 8)"/></svg>
        </button>
        <button class="capsule-btn mic-btn-small capsule-clickable" @click.stop="startRecording" title="语音">
          <svg width="14" height="14" viewBox="0 0 16 16">
            <rect x="5" y="1.5" width="6" height="8" rx="3" stroke="currentColor" stroke-width="1.3" fill="none"/>
            <path d="M3.5 8a4.5 4.5 0 009 0" stroke="currentColor" stroke-width="1.3" fill="none" stroke-linecap="round"/>
            <line x1="8" y1="12.5" x2="8" y2="14.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
        </button>
      </template>

      <!-- ===================== 默认态 ===================== -->
      <template v-else>
        <span class="capsule-logo capsule-clickable" @click.stop="enterTyping">✦</span>
        <span class="capsule-text capsule-clickable" @click.stop="enterTyping">有什么可以帮你的？</span>
        <div class="capsule-actions">
          <button class="capsule-btn mic-btn capsule-clickable" @click.stop="startRecording" title="语音">
            <svg width="16" height="16" viewBox="0 0 16 16">
              <rect x="5" y="1.5" width="6" height="8" rx="3" stroke="currentColor" stroke-width="1.3" fill="none"/>
              <path d="M3.5 8a4.5 4.5 0 009 0" stroke="currentColor" stroke-width="1.3" fill="none" stroke-linecap="round"/>
              <line x1="8" y1="12.5" x2="8" y2="14.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
          </button>
          <button class="capsule-btn expand-btn capsule-clickable" @click.stop="emit('expand')" title="展开">
            <svg width="16" height="16" viewBox="0 0 16 16"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import { api } from '@/utils/bridge'
import { useChatStore } from '@/stores/chat'

const emit = defineEmits<{ expand: [] }>()
const chatStore = useChatStore()

// 三种模式：idle / typing / (recording 由 store 控制)
const mode = ref<'idle' | 'typing'>('idle')
const inputText = ref('')
const inputRef = ref<HTMLInputElement>()

// 录音状态使用全局 store
const isRecording = computed(() => chatStore.isRecording)

// 监听 store.isRecording 变化 → 当外部（唤醒）触发录音时自动开始
watch(isRecording, (recording) => {
  if (recording) {
    mode.value = 'idle'  // 录音态优先，退出文字输入态
    doStartRecording()
  }
})

// ---- 录音 ----
function startRecording() {
  chatStore.setRecording(true)
}

function doStartRecording() {
  api.startRecordingVad()
}

function stopRecording() {
  chatStore.setRecording(false)
  api.stopRecording()
}

// ---- 文字输入 ----
function enterTyping() {
  mode.value = 'typing'
  nextTick(() => inputRef.value?.focus())
}

function exitTyping() {
  mode.value = 'idle'
  inputText.value = ''
}

function sendText() {
  const text = inputText.value.trim()
  if (!text) return
  api.sendMessage(text)
  inputText.value = ''
  mode.value = 'idle'
  // 发送后自动展开到聊天窗口看结果
  emit('expand')
}

// ---- 拖拽逻辑 ----
const isDragging = ref(false)
let startX = 0
let startY = 0

function onDragStart(e: MouseEvent) {
  isDragging.value = true
  startX = e.screenX
  startY = e.screenY
  document.addEventListener('mousemove', onDragMove)
  document.addEventListener('mouseup', onDragEnd)
}

function onDragMove(e: MouseEvent) {
  if (!isDragging.value) return
  const dx = e.screenX - startX
  const dy = e.screenY - startY
  if (dx === 0 && dy === 0) return
  startX = e.screenX
  startY = e.screenY
  const pywebview = (window as any).pywebview
  if (pywebview?.api?.move_window) {
    pywebview.api.move_window(dx, dy)
  }
}

function onDragEnd() {
  isDragging.value = false
  document.removeEventListener('mousemove', onDragMove)
  document.removeEventListener('mouseup', onDragEnd)
}
</script>

<style scoped>
.floating-wrapper {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
}

/* ---- 胶囊基础 ---- */
.floating-capsule {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px 10px 14px;
  background: var(--floating-bg);
  backdrop-filter: var(--backdrop-blur);
  border-radius: var(--radius-pill);
  box-shadow: var(--floating-shadow);
  border: 1px solid var(--border-subtle);
  cursor: grab;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
  animation: bounceIn 0.4s ease;
  min-width: 200px;
}
.floating-capsule:active {
  cursor: grabbing;
}
.floating-capsule:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

/* ---- 录音态：主题渐变背景 ---- */
.floating-capsule.recording {
  background: var(--accent-gradient);
  border-color: transparent;
  box-shadow: 0 4px 24px rgba(var(--accent-rgb, 74, 144, 217), 0.35);
  animation: gradientPulse 2s ease-in-out infinite;
}
.floating-capsule.recording * {
  color: #fff;
}

/* ---- 文字输入态 ---- */
.floating-capsule.typing {
  min-width: 320px;
  padding: 6px 10px 6px 12px;
  gap: 6px;
}

/* ---- 默认态元素 ---- */
.capsule-logo {
  font-size: 22px;
  background: var(--accent-gradient);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}
.capsule-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}
.capsule-clickable {
  cursor: pointer;
}
.capsule-actions {
  display: flex;
  gap: 4px;
  margin-left: 4px;
}

/* ---- 录音态元素 ---- */
.rec-icon-center {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}
.rec-pulse-ring {
  position: absolute;
  inset: -4px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.5);
  animation: pulse 1.4s ease-in-out infinite;
  pointer-events: none;
}
.rec-label {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.02em;
  flex: 1;
}
.stop-btn {
  color: #fff !important;
  opacity: 0.8;
}
.stop-btn:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.2);
}

/* ---- 文字输入态元素 ---- */
.capsule-logo-mini {
  font-size: 16px;
  background: var(--accent-gradient);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
  flex-shrink: 0;
}
.capsule-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 13px;
  color: var(--text-primary);
  min-width: 0;
  padding: 4px 0;
}
.capsule-input::placeholder {
  color: var(--text-tertiary);
}
.send-btn {
  color: var(--accent-color);
}
.send-btn:disabled {
  opacity: 0.3;
  cursor: default;
}
.mic-btn-small {
  color: var(--text-tertiary);
}
.mic-btn-small:hover {
  color: var(--accent-color);
}

/* ---- 通用按钮 ---- */
.capsule-btn {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  transition: all var(--transition-fast);
  position: relative;
  flex-shrink: 0;
  background: transparent;
  border: none;
  padding: 0;
}
.capsule-btn:hover {
  background: var(--card-bg-hover);
  color: var(--text-primary);
}
.mic-btn:hover {
  color: var(--accent-color);
}
.expand-btn {
  color: var(--accent-color);
}

/* ---- 动画 ---- */
@keyframes gradientPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.85; }
}
</style>
