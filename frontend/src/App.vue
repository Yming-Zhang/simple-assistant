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
import { ref } from 'vue'
import FloatingBar from './components/FloatingBar.vue'
import ChatWindow from './components/ChatWindow.vue'

const isExpanded = ref(true)

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
