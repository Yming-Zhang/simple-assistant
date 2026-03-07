<template>
  <div class="thinking-chain">
    <div v-for="(event, idx) in events" :key="idx" class="thinking-item" :class="event.type">
      <div class="thinking-icon">{{ getEventIcon(event.type) }}</div>
      <div class="thinking-content">
        <div class="thinking-label">{{ getEventLabel(event.type) }}</div>
        <div class="thinking-data">{{ getEventData(event) }}</div>
      </div>
    </div>
    <div v-if="events.length === 0" class="thinking-empty">
      暂无思考过程
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AgentEvent, AgentEventType } from '@/types'

const props = defineProps<{
  events: AgentEvent[]
}>()

function getEventIcon(type: AgentEventType | string): string {
  const iconMap: Record<string, string> = {
    thinking: '💭',
    tool_start: '🔧',
    tool_result: '✅',
    reply: '💬',
    error: '❌'
  }
  return iconMap[type] || '📍'
}

function getEventLabel(type: AgentEventType | string): string {
  const labelMap: Record<string, string> = {
    thinking: '思考中',
    tool_start: '调用工具',
    tool_result: '工具结果',
    reply: '回复',
    error: '错误'
  }
  return labelMap[type] || type
}

function getEventData(event: AgentEvent): string {
  const data = event.data
  if (typeof data === 'string') {
    return data
  }
  if (data.reasoning) {
    return data.reasoning
  }
  if (data.result) {
    return data.result
  }
  if (data.error) {
    return data.error
  }
  if (data.name) {
    return `${data.name}(${JSON.stringify(data.args || {})})`
  }
  return JSON.stringify(data)
}
</script>

<style scoped>
.thinking-chain {
  padding: 8px 0;
}

.thinking-item {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.thinking-item:last-child {
  border-bottom: none;
}

.thinking-icon {
  font-size: 18px;
  flex-shrink: 0;
  width: 24px;
  text-align: center;
}

.thinking-content {
  flex: 1;
  min-width: 0;
}

.thinking-label {
  font-size: 12px;
  font-weight: 600;
  color: #909399;
  margin-bottom: 2px;
}

.thinking-data {
  font-size: 13px;
  color: #303133;
  word-break: break-word;
  line-height: 1.5;
}

.thinking-item.error .thinking-data {
  color: #f56c6c;
}

.thinking-empty {
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 16px 0;
}
</style>
