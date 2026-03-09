<template>
  <div id="app" class="app-shell" :data-theme="settingsStore.theme">
    <transition name="mode" mode="out-in">
      <FloatingBar v-if="!isExpanded" key="floating" @expand="expandChat" />
      <ChatWindow v-else key="expanded" @minimize="minimizeChat" @close="closeChat" />
    </transition>
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

function onPyWebViewReady() {
  console.log('pywebviewready fired, loading data...')
  chatStore.loadConversationList().then(() => {
    if (!chatStore.activeConversationId && chatStore.conversationList.length > 0) {
      chatStore.switchConversation(chatStore.conversationList[0].id)
    }
  })
  settingsStore.loadSettings()
}

onMounted(() => {
  registerCallbacks()
  window.addEventListener('pywebviewready', onPyWebViewReady)
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
  try {
    const pywebview = (window as any).pywebview
    if (pywebview?.api?.close_window) {
      pywebview.api.close_window()
    } else {
      window.close()
    }
  } catch {
    window.close()
  }
}
</script>

<style>
.app-shell {
  height: 100%;
  width: 100%;
  background: var(--app-bg);
  overflow: hidden;
}

/* 悬浮 ↔ 展开 过渡动画 */
.mode-enter-active {
  animation: bounceIn 0.35s ease;
}
.mode-leave-active {
  animation: fadeIn 0.2s ease reverse;
}
</style>
