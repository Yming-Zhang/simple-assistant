<template>
  <div class="floating-wrapper">
    <div class="floating-capsule" @click="emit('expand')">
      <!-- 品牌 / 图标 -->
      <span class="capsule-logo">✦</span>

      <!-- 引导文案 -->
      <span class="capsule-text">有什么可以帮你的？</span>

      <!-- 右侧操作 -->
      <div class="capsule-actions" @click.stop>
        <button class="capsule-btn mic-btn" @click="toggleMic" :class="{ recording: isRecording }" title="语音">
          <svg width="16" height="16" viewBox="0 0 16 16">
            <rect x="5" y="1.5" width="6" height="8" rx="3" stroke="currentColor" stroke-width="1.3" fill="none"/>
            <path d="M3.5 8a4.5 4.5 0 009 0" stroke="currentColor" stroke-width="1.3" fill="none" stroke-linecap="round"/>
            <line x1="8" y1="12.5" x2="8" y2="14.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
          <span v-if="isRecording" class="rec-pulse" />
        </button>
        <button class="capsule-btn expand-btn" @click="emit('expand')" title="展开">
          <svg width="16" height="16" viewBox="0 0 16 16"><path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { api } from '@/utils/bridge'

const emit = defineEmits<{ expand: [] }>()
const isRecording = ref(false)

function toggleMic() {
  isRecording.value = !isRecording.value
  isRecording.value ? api.startRecording() : api.stopRecording()
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
  cursor: pointer;
  transition: all var(--transition-normal);
  user-select: none;
  animation: bounceIn 0.4s ease;
}

.floating-capsule:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.capsule-logo {
  font-size: 22px;
  background: var(--accent-gradient);
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

.capsule-actions {
  display: flex;
  gap: 4px;
  margin-left: 4px;
}

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
}
.capsule-btn:hover {
  background: var(--card-bg-hover);
  color: var(--text-primary);
}

.mic-btn.recording {
  color: var(--error-color);
}

.rec-pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid var(--error-color);
  animation: pulse 1.2s ease-in-out infinite;
  pointer-events: none;
}

.expand-btn {
  color: var(--accent-color);
}
</style>
