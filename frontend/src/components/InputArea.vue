<template>
  <div class="input-area" :class="{ 'drag-over': isDragOver }"
       @dragover.prevent="handleDragOver"
       @dragleave="handleDragLeave"
       @drop.prevent="handleDrop"
       @paste="handlePaste">
    <div v-if="selectedImages.length > 0" class="image-preview-container">
      <div v-for="(img, idx) in selectedImages" :key="idx" class="image-preview">
        <img :src="img" class="preview-thumb" />
        <el-button type="danger" size="small" circle class="remove-btn" @click="removeImage(idx)">
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>
    
    <div class="input-row">
      <div class="input-actions">
        <el-button size="small" circle @click="triggerImageUpload">
          <el-icon><Picture /></el-icon>
        </el-button>
        <input ref="imageInputRef" type="file" accept="image/*" multiple style="display: none" @change="handleImageSelect" />
        <el-button size="small" circle @click="toggleRecording" :type="isRecording ? 'danger' : ''">
          <el-icon><Microphone /></el-icon>
        </el-button>
      </div>
      
      <el-input
        v-model="inputText"
        type="textarea"
        :rows="1"
        autosize
        placeholder="输入消息..."
        @keydown.enter.prevent="handleSend"
        class="message-input"
      />
      
      <el-button type="primary" size="small" @click="handleSend" :loading="chatStore.isLoading">
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useChatStore } from '@/stores/chat'
import { Picture, Microphone, Close } from '@element-plus/icons-vue'
import { fileToBase64, isValidImageType } from '@/utils/image'
import { api } from '@/utils/bridge'

const chatStore = useChatStore()

const inputText = ref('')
const selectedImages = ref<string[]>([])
const isRecording = ref(false)
const isDragOver = ref(false)
const imageInputRef = ref<HTMLInputElement>()

function triggerImageUpload() {
  imageInputRef.value?.click()
}

async function handleImageSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    await addImages(Array.from(target.files))
  }
  target.value = ''
}

async function addImages(files: File[]) {
  for (const file of files) {
    if (isValidImageType(file)) {
      const base64 = await fileToBase64(file)
      selectedImages.value.push(base64)
    }
  }
}

function removeImage(index: number) {
  selectedImages.value.splice(index, 1)
}

function handleDragOver() {
  isDragOver.value = true
}

function handleDragLeave() {
  isDragOver.value = false
}

async function handleDrop(event: DragEvent) {
  isDragOver.value = false
  if (event.dataTransfer?.files) {
    await addImages(Array.from(event.dataTransfer.files))
  }
}

async function handlePaste(event: ClipboardEvent) {
  if (event.clipboardData?.files && event.clipboardData.files.length > 0) {
    await addImages(Array.from(event.clipboardData.files))
  }
}

function toggleRecording() {
  isRecording.value = !isRecording.value
  if (isRecording.value) {
    api.startRecording()
  } else {
    api.stopRecording()
  }
}

function handleSend() {
  const text = inputText.value.trim()
  if (!text && selectedImages.value.length === 0) return
  
  api.sendMessage(text, selectedImages.value.length > 0 ? selectedImages.value : undefined)
  
  inputText.value = ''
  selectedImages.value = []
}
</script>

<style scoped>
.input-area {
  background: white;
  border-top: 1px solid #e4e7ed;
  padding: 12px 16px;
}

.input-area.drag-over {
  background: #ecf5ff;
}

.image-preview-container {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.image-preview {
  position: relative;
}

.preview-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.remove-btn {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 20px;
  height: 20px;
  padding: 0;
}

.input-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.message-input {
  flex: 1;
}

.message-input :deep(.el-textarea__inner) {
  resize: none;
  border-radius: 16px;
}
</style>
