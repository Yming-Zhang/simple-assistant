<template>
  <div id="app" class="app-shell" :data-theme="settingsStore.theme" :data-mode="isExpanded ? 'normal' : 'float'">
    <transition name="mode" mode="out-in">
      <FloatingBar v-if="!isExpanded" key="floating" @expand="expandChat" />
      <ChatWindow v-else key="expanded" @minimize="minimizeChat" @close="closeChat" />
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
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
  // 二次保障：确保 macOS 标题栏已透明化
  const pywebview = (window as any).pywebview
  if (pywebview?.api?.ensure_titlebar) {
    pywebview.api.ensure_titlebar()
  }
  chatStore.loadConversationList().then(() => {
    if (!chatStore.activeConversationId && chatStore.conversationList.length > 0) {
      chatStore.switchConversation(chatStore.conversationList[0].id)
    }
  })
  settingsStore.loadSettings()
}

// 同步 float-mode 到 html 根元素，确保 html/body 也能透明
watch(isExpanded, (expanded) => {
  document.documentElement.classList.toggle('float-mode', !expanded)
}, { immediate: true })

onMounted(() => {
  registerCallbacks()
  window.addEventListener('pywebviewready', onPyWebViewReady)
  if ((window as any).pywebview?.api) {
    onPyWebViewReady()
  }
})

async function expandChat() {
  try {
    const pywebview = (window as any).pywebview
    if (pywebview?.api?.exit_float_mode) {
      await pywebview.api.exit_float_mode()
    }
  } catch (e) {
    console.warn('exit_float_mode failed:', e)
  }
  isExpanded.value = true
}

async function minimizeChat() {
  isExpanded.value = false
  try {
    const pywebview = (window as any).pywebview
    if (pywebview?.api?.enter_float_mode) {
      // 给 Vue 一帧时间渲染 FloatingBar 再缩小窗口
      await new Promise(r => setTimeout(r, 50))
      await pywebview.api.enter_float_mode()
    }
  } catch (e) {
    console.warn('enter_float_mode failed:', e)
  }
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
