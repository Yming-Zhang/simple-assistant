<template>
  <div class="sidebar">
    <!-- 顶部：新建对话 + 折叠 -->
    <div class="sidebar-header">
      <button class="new-chat-btn" @click="handleNewConversation" title="新建对话">
        <svg width="16" height="16" viewBox="0 0 16 16"><path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        <span>新对话</span>
      </button>
      <button class="icon-btn" @click="emit('toggle')" title="收起侧栏">
        <svg width="16" height="16" viewBox="0 0 16 16"><path d="M11 2L5 8l6 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
    </div>

    <!-- 会话列表 -->
    <div class="conversation-list">
      <div v-if="chatStore.conversationList.length === 0" class="empty-hint">
        暂无历史会话
      </div>
      <div
        v-for="item in chatStore.conversationList"
        :key="item.id"
        class="conv-item"
        :class="{ active: chatStore.activeConversationId === item.id }"
        @click="handleSwitch(item.id)"
      >
        <div class="conv-title text-ellipsis">{{ item.title || '新对话' }}</div>
        <div class="conv-meta">
          <span>{{ item.message_count || 0 }} 条</span>
          <span>{{ formatDate(item.updated_at) }}</span>
        </div>
        <!-- 操作按钮，hover 显示 -->
        <div class="conv-actions">
          <button class="conv-action-btn" @click.stop="handleRename(item)" title="重命名">
            <svg width="12" height="12" viewBox="0 0 12 12"><path d="M8.5 1.5l2 2L4 10H2v-2l6.5-6.5z" stroke="currentColor" stroke-width="1.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <button class="conv-action-btn delete" @click.stop="handleDelete(item.id)" title="删除">
            <svg width="12" height="12" viewBox="0 0 12 12"><path d="M2 3h8M4.5 3V2h3v1M3 3v7.5a.5.5 0 00.5.5h5a.5.5 0 00.5-.5V3" stroke="currentColor" stroke-width="1.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 底部：设置入口 -->
    <div class="sidebar-footer">
      <button class="settings-btn" @click="showSettings = !showSettings">
        <svg width="16" height="16" viewBox="0 0 16 16"><path d="M8 10a2 2 0 100-4 2 2 0 000 4z" stroke="currentColor" stroke-width="1.3" fill="none"/><path d="M13.7 6.3l-1-.2a4.8 4.8 0 00-.5-1.2l.5-.8a.5.5 0 00-.1-.6l-.7-.7a.5.5 0 00-.6-.1l-.8.5a4.8 4.8 0 00-1.2-.5l-.2-1a.5.5 0 00-.5-.4H7.4a.5.5 0 00-.5.4l-.2 1a4.8 4.8 0 00-1.2.5l-.8-.5a.5.5 0 00-.6.1l-.7.7a.5.5 0 00-.1.6l.5.8a4.8 4.8 0 00-.5 1.2l-1 .2a.5.5 0 00-.4.5v1a.5.5 0 00.4.5l1 .2a4.8 4.8 0 00.5 1.2l-.5.8a.5.5 0 00.1.6l.7.7a.5.5 0 00.6.1l.8-.5a4.8 4.8 0 001.2.5l.2 1a.5.5 0 00.5.4h1a.5.5 0 00.5-.4l.2-1a4.8 4.8 0 001.2-.5l.8.5a.5.5 0 00.6-.1l.7-.7a.5.5 0 00.1-.6l-.5-.8a4.8 4.8 0 00.5-1.2l1-.2a.5.5 0 00.4-.5v-1a.5.5 0 00-.4-.5z" stroke="currentColor" stroke-width="1.3" fill="none"/></svg>
        <span>设置</span>
      </button>
    </div>

    <!-- 设置面板（抽屉） -->
    <transition name="slide-panel">
      <div v-if="showSettings" class="settings-panel">
        <div class="settings-header">
          <span class="settings-title">设置</span>
          <button class="icon-btn" @click="showSettings = false">
            <svg width="14" height="14" viewBox="0 0 14 14"><path d="M1 1L13 13M13 1L1 13" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          </button>
        </div>

        <div class="settings-body">
          <!-- 主题 -->
          <div class="setting-group">
            <label class="setting-label">主题</label>
            <ThemeSwitcher />
          </div>

          <!-- 模型 -->
          <div class="setting-group">
            <label class="setting-label">模型</label>
            <select class="setting-select" v-model="settingsStore.model" @change="onSettingChange">
              <option value="qwen3.5">Qwen 3.5 4B</option>
              <option value="qwen2.5-vl">Qwen 2.5 VL</option>
              <option value="gpt-4">GPT-4</option>
            </select>
          </div>

          <!-- 温度 -->
          <div class="setting-group">
            <label class="setting-label">温度 <span class="setting-value">{{ settingsStore.temperature.toFixed(1) }}</span></label>
            <input type="range" class="setting-slider" v-model.number="settingsStore.temperature" min="0" max="1" step="0.1" @change="onSettingChange" />
          </div>

          <!-- 思考过程 -->
          <div class="setting-group row">
            <label class="setting-label">显示思考过程</label>
            <label class="toggle">
              <input type="checkbox" v-model="settingsStore.showThinkingChain" @change="onSettingChange" />
              <span class="toggle-slider" />
            </label>
          </div>

          <div class="setting-divider" />

          <!-- 语音回复 -->
          <div class="setting-group row">
            <label class="setting-label">语音回复</label>
            <label class="toggle">
              <input type="checkbox" v-model="settingsStore.voiceReplyEnabled" @change="onSettingChange" />
              <span class="toggle-slider" />
            </label>
          </div>

          <div class="setting-group row">
            <label class="setting-label">仅语音唤醒时播报</label>
            <label class="toggle">
              <input type="checkbox" v-model="settingsStore.voiceReplyOnlyWhenWakeByVoice" :disabled="!settingsStore.voiceReplyEnabled" @change="onSettingChange" />
              <span class="toggle-slider" />
            </label>
          </div>

          <div class="setting-group">
            <label class="setting-label">语音音量 <span class="setting-value">{{ settingsStore.voiceReplyVolume.toFixed(1) }}</span></label>
            <input type="range" class="setting-slider" v-model.number="settingsStore.voiceReplyVolume" min="0" max="1" step="0.1" :disabled="!settingsStore.voiceReplyEnabled" @change="onSettingChange" />
          </div>

          <div class="setting-divider" />

          <!-- 高级 -->
          <div class="setting-group">
            <label class="setting-label">Whisper 路径</label>
            <input type="text" class="setting-input" v-model="settingsStore.whisperPath" placeholder="留空使用默认" @blur="onSettingChange" />
          </div>

          <div class="setting-group">
            <label class="setting-label">默认窗口模式</label>
            <select class="setting-select" v-model="settingsStore.defaultWindowMode" @change="onSettingChange">
              <option value="expanded">展开态</option>
              <option value="floating">悬浮态</option>
            </select>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useSettingsStore } from '@/stores/settings'
import { useChatStore } from '@/stores/chat'
import ThemeSwitcher from './ThemeSwitcher.vue'
import type { ConversationSummary } from '@/types'

const emit = defineEmits<{ toggle: [] }>()
const settingsStore = useSettingsStore()
const chatStore = useChatStore()
const showSettings = ref(false)

onMounted(async () => {
  await settingsStore.loadSettings()
  await chatStore.loadConversationList()
  if (!chatStore.activeConversationId && chatStore.conversationList.length > 0) {
    await chatStore.switchConversation(chatStore.conversationList[0].id)
  }
})

async function handleNewConversation() {
  await chatStore.createNewConversation()
}

async function handleSwitch(convId: string) {
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
      if (ok) ElMessage.success('重命名成功')
    }
  } catch { /* cancelled */ }
}

async function handleDelete(convId: string) {
  try {
    await ElMessageBox.confirm('确定删除此会话吗？', '删除会话', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
    const ok = await chatStore.deleteConversation(convId)
    if (ok) ElMessage.success('已删除')
  } catch { /* cancelled */ }
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
    if (diffDays === 0) return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    if (diffDays === 1) return '昨天'
    if (diffDays < 7) return `${diffDays} 天前`
    return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  } catch { return dateStr }
}
</script>

<style scoped>
.sidebar {
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* ---- 顶部 ---- */
.sidebar-header {
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-chat-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  background: var(--accent-gradient);
  color: var(--text-inverse);
  font-size: 13px;
  font-weight: 500;
  transition: all var(--transition-fast);
}
.new-chat-btn:hover {
  background: var(--accent-gradient-hover);
  box-shadow: var(--shadow-sm);
}

.icon-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}
.icon-btn:hover {
  background: var(--card-bg-hover);
  color: var(--text-primary);
}

/* ---- 会话列表 ---- */
.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.empty-hint {
  text-align: center;
  color: var(--text-tertiary);
  font-size: 13px;
  padding: 32px 0;
}

.conv-item {
  position: relative;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  margin-bottom: 2px;
  transition: all var(--transition-fast);
}
.conv-item:hover {
  background: var(--card-bg-hover);
}
.conv-item.active {
  background: var(--accent-light);
}

.conv-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 3px;
}
.conv-item.active .conv-title {
  color: var(--accent-color);
}

.conv-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: var(--text-tertiary);
}

.conv-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: none;
  gap: 2px;
}
.conv-item:hover .conv-actions {
  display: flex;
}

.conv-action-btn {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  transition: all var(--transition-fast);
}
.conv-action-btn:hover {
  background: var(--card-bg);
  color: var(--text-primary);
}
.conv-action-btn.delete:hover {
  color: var(--error-color);
}

/* ---- 底部 ---- */
.sidebar-footer {
  padding: 8px 12px;
  border-top: 1px solid var(--border-subtle);
}

.settings-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px;
  transition: all var(--transition-fast);
}
.settings-btn:hover {
  background: var(--card-bg-hover);
  color: var(--text-primary);
}

/* ---- 设置面板 ---- */
.settings-panel {
  position: absolute;
  inset: 0;
  background: var(--panel-bg-solid);
  display: flex;
  flex-direction: column;
  z-index: 20;
}

.settings-header {
  padding: 12px 12px 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.settings-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.settings-body {
  flex: 1;
  overflow-y: auto;
  padding: 4px 16px 16px;
}

.setting-group {
  margin-bottom: 16px;
}
.setting-group.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.setting-label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
}
.setting-group.row .setting-label {
  margin-bottom: 0;
}

.setting-value {
  color: var(--accent-color);
  font-weight: 600;
}

.setting-select,
.setting-input {
  width: 100%;
  padding: 7px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: var(--input-bg);
  font-size: 13px;
  color: var(--text-primary);
  transition: border-color var(--transition-fast);
}
.setting-select:focus,
.setting-input:focus {
  border-color: var(--accent-color);
  outline: none;
}

.setting-slider {
  width: 100%;
  accent-color: var(--accent-color);
  height: 4px;
}

.setting-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 16px 0;
}

/* ---- Toggle switch ---- */
.toggle {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
  flex-shrink: 0;
}
.toggle input {
  opacity: 0;
  width: 0;
  height: 0;
}
.toggle-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: var(--border-color);
  border-radius: 20px;
  transition: background var(--transition-fast);
}
.toggle-slider::before {
  content: '';
  position: absolute;
  width: 16px;
  height: 16px;
  left: 2px;
  bottom: 2px;
  background: white;
  border-radius: 50%;
  transition: transform var(--transition-fast);
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.toggle input:checked + .toggle-slider {
  background: var(--accent-color);
}
.toggle input:checked + .toggle-slider::before {
  transform: translateX(16px);
}
.toggle input:disabled + .toggle-slider {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ---- 设置面板动画 ---- */
.slide-panel-enter-active {
  animation: slideRight 0.25s ease;
}
.slide-panel-leave-active {
  animation: slideRight 0.2s ease reverse;
}
@keyframes slideRight {
  from { transform: translateX(-100%); opacity: 0; }
  to   { transform: translateX(0);     opacity: 1; }
}
</style>
