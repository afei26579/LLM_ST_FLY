<template>
  <div class="painting-display">
    

    <div class="painting-container">
      <img
        v-if="painting.url"
        :src="painting.url"
        :alt="painting.description"
        class="painting-image"
        @click="openFullscreen"
      />
      <div v-else class="painting-placeholder">
        <span class="placeholder-icon">🖼️</span>
        <p>画作生成中...</p>
      </div>
      
      <!-- 悬浮操作按钮 -->
      <div v-if="painting.url" class="painting-overlay-actions">
        <button @click="copyPrompt" class="overlay-btn" title="复制绘画提示词">
          📋
        </button>
        <button @click="downloadPainting" class="overlay-btn" title="下载图片">
          ⬇️
        </button>
      </div>
    </div>

    <!-- 全屏查看 -->
    <Teleport to="body">
      <div v-if="showFullscreen" class="fullscreen-overlay" @click="closeFullscreen">
        <img :src="painting.url" alt="全屏查看" class="fullscreen-image" />
        <button class="close-btn" @click="closeFullscreen">✕</button>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import type { Painting } from '../types'
import { PAINTING_STYLES } from '../types'

interface Props {
  painting: Painting
  poetry?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update'): void
}>()

const toast = useToast()
const showFullscreen = ref(false)

const getStyleLabel = (style: string) => {
  const found = PAINTING_STYLES.find(s => s.value === style)
  return found?.label || style
}

const downloadPainting = (event: Event) => {
  event.stopPropagation()
  if (!props.painting.url) return

  const link = document.createElement('a')
  link.href = props.painting.url
  link.download = `poetry-painting-${Date.now()}.png`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  toast.success('图片下载成功！')
}

const copyPrompt = async (event: Event) => {
  event.stopPropagation()
  if (!props.painting.prompt) return

  try {
    await navigator.clipboard.writeText(props.painting.prompt)
    toast.success('提示词已复制到剪贴板！')
  } catch (error) {
    console.error('复制失败:', error)
    toast.error('复制失败，请重试')
  }
}

const openFullscreen = () => {
  showFullscreen.value = true
}

const closeFullscreen = () => {
  showFullscreen.value = false
}
</script>

<style scoped>
.painting-display {
  /* 移除边框和背景，由父容器提供 */
  padding: 0;
}

.painting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.painting-title {
  font-size: 1.4rem;
  color: var(--color-text);
  font-weight: 600;
}

.painting-style-tag {
  padding: 0.25rem 0.75rem;
  background: var(--color-primary-light);
  border-radius: 1rem;
  font-size: 0.85rem;
  color: var(--button-primary);
}

.painting-container {
  position: relative;
  margin-bottom: 1.5rem;
  border-radius: 0.5rem;
  overflow: hidden;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  box-shadow: var(--card-shadow);
}

.painting-image {
  width: 100%;
  height: auto;
  display: block;
  cursor: pointer;
  transition: transform 0.3s;
}

.painting-image:hover {
  transform: scale(1.02);
}

/* 悬浮操作按钮 */
.painting-overlay-actions {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.3s;
}

.painting-container:hover .painting-overlay-actions {
  opacity: 1;
}

.overlay-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  border: none;
  border-radius: 50%;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.3s;
}

.overlay-btn:hover {
  background: var(--button-primary);
  transform: scale(1.1);
}

.painting-placeholder {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  color: var(--color-text-secondary);
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}


/* 全屏查看 */
.fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
}

.fullscreen-image {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.close-btn {
  position: absolute;
  top: 2rem;
  right: 2rem;
  width: 3rem;
  height: 3rem;
  border: none;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  transition: background 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>

