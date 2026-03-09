<template>
  <div class="sidebar">
    <el-tabs v-model="activeTab" type="border-card" class="sidebar-tabs">
      <el-tab-pane label="历史" name="history">
        <div class="history-header">
          <el-button size="small" type="primary" @click="handleNewConversation">
            + 新建会话
          </el-button>
        </div>
        <div class="history-list">
          <div v-if="chatStore.conversationList.length === 0" class="empty-hint">
            暂无历史会话
          </div>
          <div
            v-for="item in chatStore.conversationList"
            :key="item.id"
            class="history-item"
            :class="{ active: chatStore.activeConversationId === item.id }"
            @click="handleSwitchConversation(item.id)"
          >
            <div class="history-title">{{ item.title || '新对话' }}</div>
            <div class="history-meta">
              <span class="history-count">{{ item.message_count || 0 }} 条消息</span>
              <span class="history-date">{{ formatDate(item.updated_at) }}</span>
            </div>
            <div v-if="item.preview" class="history-preview">{{ item.preview }}</div>
            <div class="history-actions">
              <el-button
                size="small"
                text
                @click.stop="handleRename(item)"
              >重命名</el-button>
              <el-button
                size="small"
                text
                type="danger"
                @click.stop="handleDelete(item.id)"
              >删除</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="设置" name="settings">
        <div class="settings-panel">
          <el-form label-position="top">
            <el-form-item label="主题">
              <el-select v-model="settingsStore.theme" style="width: 100%" @change="onThemeChange">
                <el-option label="蓝色渐变" value="blue-gradient" />
                <el-option label="粉色渐变" value="pink-gradient" />
                <el-option label="纯白" value="pure-white" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="模型">
              <el-select v-model="settingsStore.model" style="width: 100%" @change="onSettingChange">
                <el-option label="Qwen 3.5 4B" value="qwen3.5" />
                <el-option label="Qwen 2.5 VL" value="qwen2.5-vl" />
                <el-option label="GPT-4" value="gpt-4" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="温度">
              <el-slider v-model="settingsStore.temperature" :min="0" :max="1" :step="0.1" @change="onSettingChange" />
            </el-form-item>
            
            <el-form-item label="显示思考过程">
              <el-switch v-model="settingsStore.showThinkingChain" @change="onSettingChange" />
            </el-form-item>

            <el-divider>语音设置</el-divider>

            <el-form-item label="语音回复">
              <el-switch v-model="settingsStore.voiceReplyEnabled" @change="onSettingChange" />
            </el-form-item>
            
            <el-form-item label="仅语音唤醒时播报">
              <el-switch
                v-model="settingsStore.voiceReplyOnlyWhenWakeByVoice"
                :disabled="!settingsStore.voiceReplyEnabled"
                @change="onSettingChange"
              />
            </el-form-item>
            
            <el-form-item label="语音音量">
              <el-slider
                v-model="settingsStore.voiceReplyVolume"
                :min="0" :max="1" :step="0.1"
                :disabled="!settingsStore.voiceReplyEnabled"
                @change="onSettingChange"
              />
            </el-form-item>

            <el-divider>高级</el-divider>

            <el-form-item label="Whisper 路径">
              <el-input
                v-model="settingsStore.whisperPath"
                placeholder="留空使用默认"
                @blur="onSettingChange"
              />
            </el-form-item>
            
            <el-form-item label="默认窗口模式">
              <el-select v-model="settingsStore.defaultWindowMode" style="width: 100%" @change="onSettingChange">
                <el-option label="展开态" value="expanded" />
                <el-option label="悬浮态" value="floating" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useSettingsStore } from '@/stores/settings'
import { useChatStore } from '@/stores/chat'
import type { ConversationSummary } from '@/types'

const activeTab = ref('history')
const settingsStore = useSettingsStore()
const chatStore = useChatStore()

onMounted(async () => {
  // 加载真实设置
  await settingsStore.loadSettings()
  // 加载真实会话列表
  await chatStore.loadConversationList()
  // 自动切换到最近的会话（如果还没有激活的会话）
  if (!chatStore.activeConversationId && chatStore.conversationList.length > 0) {
    await chatStore.switchConversation(chatStore.conversationList[0].id)
  }
})

// ---- 会话操作 ----

async function handleNewConversation() {
  await chatStore.createNewConversation()
}

async function handleSwitchConversation(convId: string) {
  await chatStore.switchConversation(convId)
}

async function handleRename(item: ConversationSummary) {
  try {
    const { value } = await ElMessageBox.prompt('请输入新名称', '重命名会话', {
      inputValue: item.title,
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    if (value && value.trim()) {
      const ok = await chatStore.renameConversation(item.id, value.trim())
      if (ok) {
        ElMessage.success('重命名成功')
      }
    }
  } catch {
    // 用户取消
  }
}

async function handleDelete(convId: string) {
  try {
    await ElMessageBox.confirm('确定删除此会话吗？', '删除会话', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    const ok = await chatStore.deleteConversation(convId)
    if (ok) {
      ElMessage.success('已删除')
    }
  } catch {
    // 用户取消
  }
}

// ---- 设置操作 ----

function onThemeChange() {
  settingsStore.setTheme(settingsStore.theme)
}

function onSettingChange() {
  settingsStore.saveSettings()
}

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - d.getTime()
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    if (diffDays === 0) {
      return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    } else if (diffDays === 1) {
      return '昨天'
    } else if (diffDays < 7) {
      return `${diffDays} 天前`
    } else {
      return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    }
  } catch {
    return dateStr
  }
}
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

.history-header {
  padding: 8px;
  text-align: center;
}

.history-list {
  padding: 8px;
}

.empty-hint {
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 24px 0;
}

.history-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 6px;
  border: 1px solid transparent;
  transition: all 0.2s;
}

.history-item:hover {
  background: #f5f7fa;
}

.history-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}

.history-title {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.history-preview {
  font-size: 12px;
  color: #a8abb2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

.history-actions {
  display: none;
  margin-top: 4px;
}

.history-item:hover .history-actions {
  display: flex;
  gap: 4px;
}

.settings-panel {
  padding: 16px;
}
</style>
