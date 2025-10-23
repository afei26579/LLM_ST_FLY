<template>
  <div class="style-selector">
    <!-- 第一行：诗词风格 + 诗词格式 -->
    <div class="selector-row">
      <div class="selector-item">
        <label class="selector-label">
          <span class="icon">📝</span>
          诗词风格：
        </label>
        <CustomSelect
          v-model="localPoetryStyle"
          :options="poetryStyleOptions"
          placeholder="请选择"
        />
      </div>

      <div class="selector-item">
        <label class="selector-label">
          <span class="icon">📜</span>
          诗词格式：
        </label>
        <CustomSelect
          v-model="localPoetryFormat"
          :options="poetryFormatOptions"
          placeholder="请选择"
        />
      </div>
    </div>

    <!-- 第二行：绘画风格 + 图像尺寸 -->
    <div class="selector-row">
      <div class="selector-item">
        <label class="selector-label">
          <span class="icon">🎨</span>
          绘画风格：
        </label>
        <CustomSelect
          v-model="localPaintingStyle"
          :options="paintingStyleOptions"
          placeholder="请选择"
        />
      </div>

      <div class="selector-item">
        <label class="selector-label">
          <span class="icon">📐</span>
          图像尺寸：
        </label>
        <div class="size-selector-wrapper">
          <button 
            class="size-trigger" 
            @click="toggleSizeDropdown"
            :class="{ 'is-open': showSizeDropdown }"
            type="button"
          >
            <span class="selected-size-text">{{ currentSizeLabel }}</span>
            <div class="size-icon-wrapper">
              <div class="aspect-ratio-icon" :class="currentAspectClass"></div>
              <svg 
                class="dropdown-arrow" 
                :class="{ 'rotated': showSizeDropdown }"
                xmlns="http://www.w3.org/2000/svg" 
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                stroke-width="2" 
                stroke-linecap="round" 
                stroke-linejoin="round"
              >
                <polyline points="6,9 12,15 18,9"></polyline>
              </svg>
            </div>
          </button>
          
          <transition name="dropdown">
            <div v-if="showSizeDropdown" class="size-dropdown">
              <div class="dropdown-content">
                <div 
                  v-for="size in imageSizeOptions" 
                  :key="size.value"
                  class="size-dropdown-item"
                  :class="{ 'active': localImageSize === size.value }"
                  @click="selectSize(size.value)"
                >
                  <span class="size-label">{{ size.label }}</span>
                  <div class="aspect-ratio-icon" :class="getAspectClass(size.aspect_ratio)"></div>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import CustomSelect from '@/components/CustomSelect.vue'
import { POETRY_STYLES, POETRY_FORMATS, PAINTING_STYLES, IMAGE_SIZES } from '../types'
import type { PoetryStyleType, PoetryFormatType, PaintingStyleType } from '../types'

interface Props {
  poetryStyle: PoetryStyleType
  poetryFormat: PoetryFormatType
  paintingStyle: PaintingStyleType
  imageSize: string
}

interface Emits {
  (e: 'update:poetryStyle', value: PoetryStyleType): void
  (e: 'update:poetryFormat', value: PoetryFormatType): void
  (e: 'update:paintingStyle', value: PaintingStyleType): void
  (e: 'update:imageSize', value: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const showSizeDropdown = ref(false)
const sizeSelectRef = ref<HTMLElement>()

// 转换选项格式为 CustomSelect 需要的格式
const poetryStyleOptions = computed(() => 
  POETRY_STYLES.map(style => ({
    value: style.value,
    label: `${style.label} - ${style.description}`
  }))
)

const poetryFormatOptions = computed(() => 
  POETRY_FORMATS.map(format => ({
    value: format.value,
    label: `${format.label} - ${format.description}`
  }))
)

const paintingStyleOptions = computed(() => 
  PAINTING_STYLES.map(style => ({
    value: style.value,
    label: `${style.label} - ${style.description}`
  }))
)

const localPoetryStyle = computed({
  get: () => props.poetryStyle,
  set: (value) => emit('update:poetryStyle', value as PoetryStyleType)
})

const localPoetryFormat = computed({
  get: () => props.poetryFormat,
  set: (value) => emit('update:poetryFormat', value as PoetryFormatType)
})

const localPaintingStyle = computed({
  get: () => props.paintingStyle,
  set: (value) => emit('update:paintingStyle', value as PaintingStyleType)
})

const localImageSize = computed({
  get: () => props.imageSize,
  set: (value) => emit('update:imageSize', value)
})

// 图像尺寸相关
const imageSizeOptions = IMAGE_SIZES

const currentSizeLabel = computed(() => {
  const size = IMAGE_SIZES.find(s => s.value === props.imageSize)
  return size?.label || props.imageSize
})

const currentAspectClass = computed(() => {
  const size = IMAGE_SIZES.find(s => s.value === props.imageSize)
  return getAspectClass(size?.aspect_ratio || '1:1')
})

const toggleSizeDropdown = () => {
  showSizeDropdown.value = !showSizeDropdown.value
}

const selectSize = (value: string) => {
  emit('update:imageSize', value)
  showSizeDropdown.value = false
}

const getAspectClass = (ratio: string) => {
  switch (ratio) {
    case '1:1': return 'ratio-square'
    case '16:9': return 'ratio-landscape'
    case '9:16': return 'ratio-portrait'
    case '4:3': return 'ratio-landscape-43'
    case '3:4': return 'ratio-portrait-34'
    default: return 'ratio-square'
  }
}

// 点击外部关闭下拉
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.size-selector-wrapper')) {
    showSizeDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.style-selector {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
}

.selector-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.selector-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.selector-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  flex-shrink: 0;
}

.icon {
  font-size: 1rem;
}

/* 尺寸选择器样式 */
.size-selector-wrapper {
  position: relative;
  width: 100%;
}

.size-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--card-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--card-shadow);
  text-align: left;
}

.size-trigger:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-alpha);
}

.size-trigger.is-open {
  border-color: var(--color-primary);
  box-shadow: var(--card-shadow), 0 0 0 2px rgba(94, 155, 255, 0.1);
}

.selected-size-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.size-icon-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dropdown-arrow {
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.size-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  z-index: 1000;
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  max-height: 300px;
  overflow-y: auto;
}

.dropdown-content {
  padding: 0.5rem;
}

.size-dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  color: var(--color-text);
  font-size: 1rem;
  margin-bottom: 0.25rem;
}

.size-dropdown-item:hover {
  background: var(--color-primary-alpha);
}

.size-dropdown-item.active {
  background: var(--color-primary-alpha);
  color: var(--color-primary);
  font-weight: 500;
}

.size-label {
  flex: 1;
}

/* 比例示意图 */
.aspect-ratio-icon {
  width: 28px;
  height: 18px;
  border: 2px solid currentColor;
  border-radius: 3px;
  background-color: rgba(94, 155, 255, 0.1);
  flex-shrink: 0;
}

.ratio-square {
  width: 18px;
  height: 18px;
}

.ratio-landscape {
  width: 28px;
  height: 16px;
}

.ratio-portrait {
  width: 16px;
  height: 28px;
}

.ratio-landscape-43 {
  width: 24px;
  height: 18px;
}

.ratio-portrait-34 {
  width: 18px;
  height: 24px;
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 滚动条 */
.size-dropdown::-webkit-scrollbar {
  width: 8px;
}

.size-dropdown::-webkit-scrollbar-track {
  background: var(--input-background);
  border-radius: 4px;
}

.size-dropdown::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 4px;
  transition: background 0.3s ease;
}

.size-dropdown::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

.size-dropdown {
  scrollbar-width: thin;
  scrollbar-color: var(--color-primary-alpha) var(--input-background);
}

@media (max-width: 768px) {
  .selector-row {
    grid-template-columns: 1fr;
  }
  
  .selector-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .selector-label {
    margin-bottom: 0.25rem;
  }
}
</style>

