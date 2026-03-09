<template>
  <div class="input-area" :class="{ 'drag-over': isDragOver }"
       @dragover.prevent="handleDragOver"
       @dragleave="handleDragLeave"
       @drop.prevent="handleDrop"
       @paste="handlePaste">

    <!-- 图片预览 -->
    <div v-if="selectedImages.length > 0" class="image-previews">
      <div v-for="(img, idx) in selectedImages" :key="idx" class="img-thumb-wrap">
        <img :src="img" class="img-thumb" />
        <button class="img-remove" @click="removeImage(idx)">×</button>
      </div>
    </div>

    <div class="input-row">
      <!-- 左侧操作 -->
      <div class="input-tools">
        <button class="tool-btn" @click="triggerImageUpload" title="上传图片">
          <svg width="18" height="18" viewBox="0 0 18 18"><rect x="2" y="2" width="14" height="14" rx="2" stroke="currentColor" stroke-width="1.4" fill="none"/><circle cx="6.5" cy="6.5" r="1.5" fill="currentColor"/><path d="M2 13l4-4 3 3 2-2 5 5H3a1 1 0 01-1-1v-1z" fill="currentColor" opacity="0.3"/></svg>
        </button>
        <input ref="imageInputRef" type="file" accept="image/*" multiple style="display:none" @change="handleImageSelect" />

        <button class="tool-btn" :class="{ active: isRecording }" @click="toggleRecording" :title="isRecording ? '停止录音' : '语音'">
          <svg width="18" height="18" viewBox="0 0 18 18">
            <rect x="6" y="2" width="6" height="9" rx="3" stroke="currentColor" stroke-width="1.4" fill="none"/>
            <path d="M4 9a5 5 0 0010 0" stroke="currentColor" stroke-width="1.4" fill="none" stroke-linecap="round"/>
            <line x1="9" y1="14" x2="9" y2="16" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
          <span v-if="isRecording" class="rec-dot" />
        </button>
      </div>

      <!-- 输入框 -->
      <div class="textarea-wrap">
        <textarea
          ref="textareaRef"
          v-model="inputText"
          class="msg-textarea"
          placeholder="输入消息…  Enter 发送 / Shift+Enter 换行"
          rows="1"
          @keydown="handleKeydown"
          @input="autoResize"
        />
      </div>

      <!-- 发送按钮 -->
      <button class="send-btn" :class="{ disabled: !canSend }" @click="handleSend" :disabled="!canSend || chatStore.isLoading" title="发送">
        <svg v-if="!chatStore.isLoading" width="18" height="18" viewBox="0 0 18 18"><path d="M3 9l12-6-4 6 4 6L3 9z" fill="currentColor"/></svg>
        <span v-else class="is-spinning">
          <svg width="18" height="18" viewBox="0 0 18 18"><circle cx="9" cy="9" r="7" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="30 14" stroke-linecap="round"/></svg>
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { fileToBase64, isValidImageType } from '@/utils/image'
import { api } from '@/utils/bridge'

const chatStore = useChatStore()

const inputText = ref('')
const selectedImages = ref<string[]>([])
const isRecording = ref(false)
const isDragOver = ref(false)
const imageInputRef = ref<HTMLInputElement>()
const textareaRef = ref<HTMLTextAreaElement>()

const canSend = computed(() => inputText.value.trim() || selectedImages.value.length > 0)

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
  // Shift+Enter 自然换行，不处理
}

function autoResize() {
  const el = textareaRef.value
  if (el) {
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 150) + 'px'
  }
}

function handleSend() {
  const text = inputText.value.trim()
  if (!text && selectedImages.value.length === 0) return
  if (chatStore.isLoading) return

  api.sendMessage(text, selectedImages.value.length > 0 ? selectedImages.value : undefined)
  inputText.value = ''
  selectedImages.value = []
  nextTick(() => {
    if (textareaRef.value) textareaRef.value.style.height = 'auto'
  })
}

function triggerImageUpload() {
  imageInputRef.value?.click()
}

async function handleImageSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) await addImages(Array.from(target.files))
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

function handleDragOver() { isDragOver.value = true }
function handleDragLeave() { isDragOver.value = false }

async function handleDrop(event: DragEvent) {
  isDragOver.value = false
  if (event.dataTransfer?.files) await addImages(Array.from(event.dataTransfer.files))
}

async function handlePaste(event: ClipboardEvent) {
  if (event.clipboardData?.files && event.clipboardData.files.length > 0) {
    await addImages(Array.from(event.clipboardData.files))
  }
}

function toggleRecording() {
  isRecording.value = !isRecording.value
  isRecording.value ? api.startRecording() : api.stopRecording()
}
</script>

<style scoped>
.input-area {
  padding: 10px 16px 12px;
  background: var(--panel-bg);
  backdrop-filter: var(--backdrop-blur);
  border-top: 1px solid var(--border-subtle);
}
.input-area.drag-over {
  background: var(--accent-light);
}

/* ---- 图片预览 ---- */
.image-previews {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.img-thumb-wrap {
  position: relative;
}
.img-thumb {
  width: 52px;
  height: 52px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}
.img-remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--error-color);
  color: white;
  font-size: 12px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ---- 输入行 ---- */
.input-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.input-tools {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
  padding-bottom: 3px;
}

.tool-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  position: relative;
  transition: all var(--transition-fast);
}
.tool-btn:hover {
  background: var(--card-bg-hover);
  color: var(--text-primary);
}
.tool-btn.active {
  color: var(--error-color);
}

.rec-dot {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--error-color);
  animation: pulse 1s ease-in-out infinite;
}

/* ---- Textarea ---- */
.textarea-wrap {
  flex: 1;
  min-width: 0;
}

.msg-textarea {
  width: 100%;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  background: var(--input-bg);
  border: 1px solid var(--border-color);
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
  resize: none;
  max-height: 150px;
  transition: border-color var(--transition-fast);
}
.msg-textarea::placeholder {
  color: var(--text-tertiary);
}
.msg-textarea:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px var(--accent-light);
}

/* ---- 发送 ---- */
.send-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gradient);
  color: var(--text-inverse);
  flex-shrink: 0;
  transition: all var(--transition-fast);
}
.send-btn:hover:not(.disabled) {
  background: var(--accent-gradient-hover);
  box-shadow: var(--shadow-sm);
}
.send-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
