<template>
  <div class="thinking-chain">
    <div
      v-for="(event, idx) in events"
      :key="idx"
      class="step"
      :class="event.type"
    >
      <div class="step-indicator">
        <span class="step-dot" />
        <span v-if="idx < events.length - 1" class="step-line" />
      </div>
      <div class="step-body">
        <div class="step-header">
          <span class="step-icon">{{ getIcon(event.type) }}</span>
          <span class="step-label">{{ getLabel(event.type) }}</span>
        </div>
        <div class="step-detail">{{ getDetail(event) }}</div>
      </div>
    </div>
    <div v-if="events.length === 0" class="thinking-empty">
      暂无思考过程
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AgentEvent, AgentEventType } from '@/types'

defineProps<{ events: AgentEvent[] }>()

function getIcon(type: AgentEventType | string): string {
  const m: Record<string, string> = { thinking: '💭', tool_start: '🔧', tool_result: '✅', reply: '💬', error: '❌' }
  return m[type] || '📍'
}

function getLabel(type: AgentEventType | string): string {
  const m: Record<string, string> = { thinking: '推理', tool_start: '调用工具', tool_result: '工具结果', reply: '回复', error: '错误' }
  return m[type] || String(type)
}

function getDetail(event: AgentEvent): string {
  const d = event.data
  if (typeof d === 'string') return d
  if (d.reasoning) return d.reasoning
  if (d.result) return d.result
  if (d.error) return d.error
  if (d.name) return `${d.name}(${JSON.stringify(d.args || {})})`
  return JSON.stringify(d)
}
</script>

<style scoped>
.thinking-chain {
  font-size: 12px;
}

.step {
  display: flex;
  gap: 10px;
  min-height: 32px;
}

/* 时间线指示器 */
.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 14px;
  flex-shrink: 0;
  padding-top: 5px;
}
.step-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--accent-color);
  flex-shrink: 0;
}
.step.error .step-dot {
  background: var(--error-color);
}
.step-line {
  flex: 1;
  width: 1.5px;
  background: var(--border-color);
  margin-top: 3px;
}

/* 内容 */
.step-body {
  flex: 1;
  min-width: 0;
  padding-bottom: 10px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 2px;
}

.step-icon {
  font-size: 12px;
}
.step-label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.step-detail {
  color: var(--text-primary);
  line-height: 1.5;
  word-break: break-word;
  white-space: pre-wrap;
}

.step.error .step-detail {
  color: var(--error-color);
}

.thinking-empty {
  text-align: center;
  color: var(--text-tertiary);
  padding: 12px 0;
}
</style>
