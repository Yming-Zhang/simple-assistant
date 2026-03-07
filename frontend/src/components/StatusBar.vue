<template>
  <div class="status-bar">
    <div class="status-content">
      <span v-if="chatStore.isLoading" class="status-loading">
        <el-icon class="is-loading"><Loading /></el-icon>
        {{ getStatusText() }}
      </span>
      <span v-else class="status-idle">
        <el-icon><CircleCheck /></el-icon>
        就绪
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { Loading, CircleCheck } from '@element-plus/icons-vue'

const chatStore = useChatStore()

function getStatusText(): string {
  const thinking = chatStore.currentThinkingChain
  if (thinking.length > 0) {
    const lastEvent = thinking[thinking.length - 1]
    switch (lastEvent.type) {
      case 'thinking':
        return '思考中...'
      case 'tool_start':
        return '调用工具中...'
      case 'tool_result':
        return '工具执行完成'
      case 'error':
        return '发生错误'
      default:
        return '处理中...'
    }
  }
  return '处理中...'
}
</script>

<style scoped>
.status-bar {
  height: 32px;
  background: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  padding: 0 16px;
}

.status-content {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.status-loading {
  color: #409eff;
}

.status-idle {
  color: #67c23a;
}

.status-content .el-icon {
  font-size: 14px;
}
</style>
