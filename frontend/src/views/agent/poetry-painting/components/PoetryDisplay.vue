<template>
  <div class="poetry-display">
    <div class="poetry-header">
      <h2 class="poetry-title">{{ poetry.title || '无题' }}</h2>
      <div class="poetry-meta">
        <span class="meta-tag">{{ poetry.style }}</span>
        <span class="meta-tag">{{ getFormatLabel(poetry.format) }}</span>
        <span class="meta-tag">{{ paintingStyleLabel }}</span>
      </div>
    </div>

    <div class="poetry-content" @mouseenter="showAnalysis = true" @mouseleave="showAnalysis = false">
      <p v-for="(line, index) in poetryLines" :key="index" class="poetry-line">
        {{ line }}
      </p>
      
      <!-- 悬停显示赏析 -->
      <transition name="analysis-fade">
        <div v-if="showAnalysis && poetry.analysis" class="poetry-analysis-overlay">
      <h3 class="analysis-title">📖 赏析</h3>

      <div class="analysis-section">
        <h4>意象</h4>
        <div class="imagery-list">
          <div v-for="(img, index) in poetry.analysis.imagery" :key="index" class="imagery-item">
            <strong>{{ img.name }}</strong>
            <span v-if="img.meaning">: {{ img.meaning }}</span>
          </div>
        </div>
      </div>

      <div class="analysis-section">
        <h4>情感基调</h4>
        <p>{{ poetry.analysis.emotion }}</p>
      </div>

      <div v-if="poetry.analysis.rhetoric.length" class="analysis-section">
        <h4>修辞手法</h4>
        <div class="rhetoric-list">
          <span v-for="(r, index) in poetry.analysis.rhetoric" :key="index" class="rhetoric-tag">
            {{ r }}
          </span>
        </div>
      </div>

      <div v-if="poetry.analysis.allusion?.length" class="analysis-section">
        <h4>典故引用</h4>
        <div v-for="(allusion, index) in poetry.analysis.allusion" :key="index" class="allusion-item">
          <strong>{{ allusion.reference }}</strong>: {{ allusion.meaning }}
        </div>
      </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { Poetry } from '../types'
import { POETRY_FORMATS, PAINTING_STYLES } from '../types'

interface Props {
  poetry: Poetry
  paintingStyle?: string
}

const props = defineProps<Props>()
defineEmits<{
  (e: 'update'): void
}>()

const showAnalysis = ref(false)

const poetryLines = computed(() => {
  return props.poetry.content.split('\n').filter(line => line.trim())
})

const toggleAnalysis = () => {
  showAnalysis.value = !showAnalysis.value
}

const getFormatLabel = (format: string) => {
  const found = POETRY_FORMATS.find(f => f.value === format)
  return found?.label || format
}

const paintingStyleLabel = computed(() => {
  if (!props.paintingStyle) return ''
  const found = PAINTING_STYLES.find(s => s.value === props.paintingStyle)
  return found?.label || props.paintingStyle
})
</script>

<style scoped>
.poetry-display {
  /* 移除边框和背景，由父容器提供 */
  padding: 0;
}

.poetry-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--color-border);
}

.poetry-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.5rem;
  font-family: 'KaiTi', 'STKaiti', serif;
}

.poetry-meta {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.meta-tag {
  padding: 0.25rem 0.75rem;
  background: var(--color-primary-light);
  border-radius: 1rem;
  font-size: 0.85rem;
  color: var(--button-primary);
}

.poetry-content {
  position: relative;
  margin: 2rem 0;
  text-align: center;
  padding: 1rem;
  border-radius: 0.5rem;
  transition: background 0.3s;
}

.poetry-content:hover {
  background: var(--color-background);
}

.poetry-line {
  font-size: 1.2rem;
  line-height: 2;
  color: var(--color-text);
  font-family: 'KaiTi', 'STKaiti', serif;
  margin: 0.5rem 0;
}

.poetry-analysis-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  border-radius: 0.5rem;
  overflow-y: auto;
  z-index: 10;
}

/* 赏析淡入淡出动画 */
.analysis-fade-enter-active,
.analysis-fade-leave-active {
  transition: opacity 0.3s ease;
}

.analysis-fade-enter-from,
.analysis-fade-leave-to {
  opacity: 0;
}

.analysis-title {
  font-size: 1.2rem;
  color: white;
  margin-bottom: 1rem;
}

.analysis-section {
  margin-bottom: 1rem;
}

.analysis-section {
  color: rgba(255, 255, 255, 0.95);
}

.analysis-section h4 {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 0.5rem;
}

.imagery-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.imagery-item {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.25rem;
  color: rgba(255, 255, 255, 0.95);
}

.rhetoric-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.rhetoric-tag {
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 0.25rem;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.95);
}

.allusion-item {
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.25rem;
  margin-bottom: 0.5rem;
  color: rgba(255, 255, 255, 0.95);
}
</style>

