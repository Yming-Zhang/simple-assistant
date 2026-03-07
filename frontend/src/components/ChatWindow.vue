<template>
  <div class="chat-window">
    <el-container class="chat-container">
      <el-aside width="260px" class="chat-sidebar">
        <Sidebar />
      </el-aside>
      
      <el-container class="chat-main">
        <el-header class="chat-header">
          <div class="header-left">
            <span class="header-title">Simple Assistant</span>
          </div>
          <div class="header-right">
            <el-button size="small" circle @click="emit('minimize')">
              <el-icon><Minus /></el-icon>
            </el-button>
            <el-button size="small" circle @click="emit('close')">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
        </el-header>
        
        <el-main class="chat-messages" ref="messagesContainerRef">
          <div class="messages-list">
            <MessageBubble v-for="msg in chatStore.messages" :key="msg.id" :message="msg" />
            <div v-if="chatStore.isLoading && chatStore.currentThinkingChain.length > 0 && settingsStore.showThinkingChain" class="current-thinking">
              <el-divider content-position="left">🔄 当前思考过程</el-divider>
              <ThinkingChain :events="chatStore.currentThinkingChain" />
            </div>
          </div>
        </el-main>
        
        <StatusBar />
        
        <el-footer class="chat-footer">
          <InputArea />
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch, nextTick, ref } from 'vue'
import { useChatStore } from '@/stores/chat'
import { useSettingsStore } from '@/stores/settings'
import { registerCallbacks } from '@/utils/bridge'
import { Minus, Close } from '@element-plus/icons-vue'
import Sidebar from './Sidebar.vue'
import MessageBubble from './MessageBubble.vue'
import InputArea from './InputArea.vue'
import StatusBar from './StatusBar.vue'
import ThinkingChain from './ThinkingChain.vue'

const chatStore = useChatStore()
const settingsStore = useSettingsStore()
const messagesContainerRef = ref<HTMLElement>()

const emit = defineEmits<{
  minimize: []
  close: []
}>()

onMounted(() => {
  registerCallbacks()
  scrollToBottom()
})

watch(() => chatStore.messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

watch(() => chatStore.currentThinkingChain, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

function scrollToBottom() {
  if (messagesContainerRef.value) {
    messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight
  }
}
</script>

<style scoped>
.chat-window {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.chat-container {
  height: 100%;
}

.chat-sidebar {
  height: 100%;
}

.chat-main {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-header {
  height: 50px;
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 8px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #f5f7fa;
}

.messages-list {
  min-height: 100%;
}

.current-thinking {
  margin-top: 16px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chat-footer {
  height: auto;
  padding: 0;
}
</style>
