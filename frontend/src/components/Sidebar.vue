<template>
  <div class="sidebar">
    <el-tabs v-model="activeTab" type="border-card" class="sidebar-tabs">
      <el-tab-pane label="历史" name="history">
        <div class="history-list">
          <div v-for="i in 5" :key="i" class="history-item">
            <div class="history-date">2026-03-07</div>
            <div class="history-title">对话 {{ i }}</div>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="设置" name="settings">
        <div class="settings-panel">
          <el-form label-position="top">
            <el-form-item label="模型">
              <el-select v-model="settingsStore.model" style="width: 100%">
                <el-option label="Qwen 3.5 4B" value="qwen3.5" />
                <el-option label="Qwen 2.5 VL" value="qwen2.5-vl" />
                <el-option label="GPT-4" value="gpt-4" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="温度">
              <el-slider v-model="settingsStore.temperature" :min="0" :max="1" :step="0.1" />
            </el-form-item>
            
            <el-form-item label="显示思考过程">
              <el-switch v-model="settingsStore.showThinkingChain" />
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const activeTab = ref('history')
const settingsStore = useSettingsStore()
</script>

<style scoped>
.sidebar {
  height: 100%;
  background: white;
  border-right: 1px solid #e4e7ed;
}

.sidebar-tabs {
  height: 100%;
}

.sidebar-tabs :deep(.el-tabs__content) {
  height: calc(100% - 60px);
  overflow-y: auto;
}

.history-list {
  padding: 8px;
}

.history-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 8px;
}

.history-item:hover {
  background: #f5f7fa;
}

.history-date {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.history-title {
  font-size: 14px;
  color: #303133;
}

.settings-panel {
  padding: 16px;
}
</style>
