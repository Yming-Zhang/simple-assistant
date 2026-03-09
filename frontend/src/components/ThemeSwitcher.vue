<template>
  <div class="theme-switcher" :class="{ compact }">
    <button
      v-for="opt in themeOptions"
      :key="opt.value"
      class="theme-btn"
      :class="{ active: settingsStore.theme === opt.value }"
      :title="opt.label"
      @click="applyTheme(opt.value)"
    >
      <span class="theme-dot" :style="{ background: opt.preview }" />
      <span v-if="!compact" class="theme-label">{{ opt.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useSettingsStore } from '@/stores/settings'
import { useTheme, themeOptions } from '@/composables/useTheme'

defineProps<{
  compact?: boolean
}>()

const settingsStore = useSettingsStore()
const { applyTheme } = useTheme()
</script>

<style scoped>
.theme-switcher {
  display: flex;
  gap: 6px;
  align-items: center;
}

.theme-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  border: 1.5px solid transparent;
  background: var(--card-bg);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.theme-btn:hover {
  background: var(--card-bg-hover);
  border-color: var(--border-color);
}

.theme-btn.active {
  border-color: var(--accent-color);
  background: var(--accent-light);
  color: var(--accent-color);
  font-weight: 500;
}

.theme-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 1.5px solid var(--border-color);
}

.theme-btn.active .theme-dot {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px var(--accent-light);
}

/* 紧凑模式 */
.compact .theme-btn {
  padding: 3px;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  justify-content: center;
}
.compact .theme-dot {
  width: 16px;
  height: 16px;
}
.compact .theme-label {
  display: none;
}
</style>
