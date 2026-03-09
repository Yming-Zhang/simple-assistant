<template>
  <div id="app">
    <div v-if="!isExpanded" class="floating-container">
      <FloatingBar @expand="expandChat" />
    </div>
    <div v-else class="chat-container">
      <ChatWindow @minimize="minimizeChat" @close="closeChat" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import FloatingBar from './components/FloatingBar.vue'
import ChatWindow from './components/ChatWindow.vue'
import { registerCallbacks } from '@/utils/bridge'
import { useChatStore } from '@/stores/chat'
import { useSettingsStore } from '@/stores/settings'

const isExpanded = ref(true)
const chatStore = useChatStore()
const settingsStore = useSettingsStore()

// pywebviewready 保证 API 已就绪再加载数据
function onPyWebViewReady() {
  console.log('pywebviewready fired, loading data...')
  chatStore.loadConversationList().then(() => {
    // 自动切换到最近的会话
    if (!chatStore.activeConversationId && chatStore.conversationList.length > 0) {
      chatStore.switchConversation(chatStore.conversationList[0].id)
    }
  })
  settingsStore.loadSettings()
}

onMounted(() => {
  // 注册 Python→JS 回调
  registerCallbacks()
  // 监听 pywebviewready 事件
  window.addEventListener('pywebviewready', onPyWebViewReady)
  // 如果 pywebview.api 已经存在（事件已触发过），立即加载
  if ((window as any).pywebview?.api) {
    onPyWebViewReady()
  }
})

function expandChat() {
  isExpanded.value = true
}

function minimizeChat() {
  isExpanded.value = false
}

function closeChat() {
  console.log('Close chat')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
  overflow: hidden;
}

.floating-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.1);
}

.chat-container {
  height: 100%;
  width: 100%;
}
</style>
