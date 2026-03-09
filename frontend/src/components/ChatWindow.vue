<template>
  <div class="chat-window">
    <!-- 顶部标题栏（无边框拖拽区） -->
    <header class="title-bar drag-region">
      <div class="title-bar-left no-drag">
        <span class="app-logo">✦</span>
        <span class="app-title">Simple Assistant</span>
      </div>
      <div class="title-bar-center no-drag">
        <ThemeSwitcher compact />
      </div>
      <div class="title-bar-right no-drag">
        <button class="win-btn" title="最小化" @click="emit('minimize')">
          <svg width="12" height="12" viewBox="0 0 12 12"><rect y="5" width="12" height="2" rx="1" fill="currentColor"/></svg>
        </button>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="main-body">
      <!-- 侧栏 -->
      <aside class="sidebar-pane" :class="{ collapsed: !showSidebar }">
        <Sidebar v-if="showSidebar" @toggle="showSidebar = !showSidebar" />
      </aside>

      <!-- 侧栏折叠时的呼出按钮 -->
      <button v-if="!showSidebar" class="sidebar-toggle-btn" @click="showSidebar = true" title="展开侧栏">
        <svg width="16" height="16" viewBox="0 0 16 16"><path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      </button>

      <!-- 聊天主区 -->
      <div class="chat-pane">
        <!-- 消息列表 -->
        <div class="messages-area" ref="messagesRef">
          <!-- 空状态 -->
          <div v-if="chatStore.messages.length === 0 && !chatStore.isLoading" class="empty-state slide-up">
            <div class="empty-icon">✦</div>
            <div class="empty-title">有什么可以帮你的？</div>
            <div class="empty-hint">输入文字或按住录音开始对话</div>
          </div>

          <!-- 消息列表 -->
          <div class="messages-list">
            <MessageBubble v-for="msg in chatStore.messages" :key="msg.id" :message="msg" />

            <!-- 实时思考过程 -->
            <div v-if="chatStore.isLoading && chatStore.currentThinkingChain.length > 0" class="live-thinking slide-up">
              <ThinkingChain :events="chatStore.currentThinkingChain" />
            </div>
          </div>
        </div>

        <!-- 状态栏 -->
        <StatusBar />

        <!-- 输入区 -->
        <InputArea />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue'
import { useChatStore } from '@/stores/chat'
import Sidebar from './Sidebar.vue'
import MessageBubble from './MessageBubble.vue'
import InputArea from './InputArea.vue'
import StatusBar from './StatusBar.vue'
import ThinkingChain from './ThinkingChain.vue'
import ThemeSwitcher from './ThemeSwitcher.vue'

const chatStore = useChatStore()
const messagesRef = ref<HTMLElement>()
const showSidebar = ref(true)

const emit = defineEmits<{
  minimize: []
  close: []
}>()

onMounted(() => {
  scrollToBottom()
})

watch(() => chatStore.messages, () => {
  nextTick(scrollToBottom)
}, { deep: true })

watch(() => chatStore.currentThinkingChain, () => {
  nextTick(scrollToBottom)
}, { deep: true })

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-window {
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--app-bg);
}

/* ---- 标题栏（透明，与系统标题栏融合） ---- */
.title-bar {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background: transparent;
  flex-shrink: 0;
  gap: 12px;
  position: relative;
  z-index: 10;
}

.title-bar-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 180px;
  /* 为 macOS 原生红绿灯按钮留出空间（约 70px） */
  padding-left: 60px;
}

.app-logo {
  font-size: 18px;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}

.app-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.title-bar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.title-bar-right {
  display: flex;
  align-items: center;
  gap: 4px;
  min-width: 80px;
  justify-content: flex-end;
}

.win-btn {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  transition: all var(--transition-fast);
}
.win-btn:hover {
  background: var(--card-bg-hover);
  color: var(--text-primary);
}
.close-btn:hover {
  background: var(--error-color);
  color: white;
}

/* ---- 主体 ---- */
.main-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* ---- 侧栏 ---- */
.sidebar-pane {
  width: 260px;
  flex-shrink: 0;
  background: var(--sidebar-bg);
  backdrop-filter: var(--backdrop-blur);
  border-right: 1px solid var(--border-subtle);
  transition: width var(--transition-normal), opacity var(--transition-normal);
  overflow: hidden;
}
.sidebar-pane.collapsed {
  width: 0;
  border-right: none;
}

.sidebar-toggle-btn {
  position: absolute;
  top: 12px;
  left: 8px;
  z-index: 10;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}
.sidebar-toggle-btn:hover {
  color: var(--text-primary);
  background: var(--card-bg-hover);
}

/* ---- 聊天主区 ---- */
.chat-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.messages-list {
  max-width: 780px;
  margin: 0 auto;
}

/* ---- 空状态 ---- */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
  color: var(--text-tertiary);
}
.empty-icon {
  font-size: 48px;
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  opacity: 0.6;
}
.empty-title {
  font-size: 18px;
  font-weight: 500;
  color: var(--text-secondary);
}
.empty-hint {
  font-size: 13px;
}

/* ---- 实时思考 ---- */
.live-thinking {
  margin: 12px 0;
  padding: 12px 16px;
  background: var(--panel-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}
</style>
