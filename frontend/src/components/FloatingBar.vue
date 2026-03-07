<template>
  <div class="floating-bar" @click="emit('expand')">
    <div class="floating-icon">🤖</div>
    <span class="floating-text">Simple Assistant</span>
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  expand: []
}>()
</script>

<style scoped>
.floating-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  transition: all 0.3s;
}

.floating-bar:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.floating-icon {
  font-size: 24px;
}

.floating-text {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}
</style>
