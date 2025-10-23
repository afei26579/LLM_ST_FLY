<template>
  <div class="poetry-painting-view">
    <!-- 头部 -->
    <div class="header">
      <div class="agent-info">
        <div class="avatar">🎨</div>
        <div class="info-text">
          <h1 class="title">诗词绘画大师</h1>
          <p class="subtitle">以诗绘画，以画入诗，意境交融 ✨</p>
        </div>
      </div>

      <button @click="newConversation" class="new-conversation-btn">
        <span>➕</span>
        新建创作
      </button>
    </div>

    <!-- 进度步骤（生成时显示） -->
    <transition name="collapse">
      <div v-if="isGenerating" class="progress-bar">
        <div class="progress-steps-inline">
          <div
            v-for="step in steps"
            :key="step.key"
            :class="['step-inline', { done: step.done, active: !step.done && steps.find(s => s.done)?.key !== 'completed' }]"
          >
            <span class="step-icon">{{ step.done ? '✓' : '○' }}</span>
            <span class="step-label">{{ step.label }}</span>
          </div>
        </div>
      </div>
    </transition>

    <!-- 主内容区 -->
    <div class="main-content" :class="{ 'has-work': hasCurrentWork || isGenerating }">
      <!-- 左侧：创作输入（初始状态）或作品展示 -->
      <div v-if="!hasCurrentWork && !isGenerating" class="creation-panel-full">
        <div class="panel-header">
          <h2 class="panel-title">📝 创作主题</h2>
          <div class="settings-wrapper">
            <button @click="showSettings = !showSettings" class="settings-btn" type="button">
              <span class="settings-icon">⚙️</span>
              设置
            </button>
            
            <!-- 设置弹出菜单 -->
            <transition name="settings-dropdown">
              <div v-if="showSettings" class="settings-dropdown">
              <div class="settings-content">
                <h4 class="settings-title">创作设置</h4>
                
                <div class="setting-row">
                  <label class="setting-label">
                    <span class="icon">📝</span>
                    诗词风格：
                  </label>
                  <CustomSelect
                    v-model="poetryStyle"
                    :options="poetryStyleOptions"
                    placeholder="请选择"
                  />
                </div>

                <div class="setting-row">
                  <label class="setting-label">
                    <span class="icon">📜</span>
                    诗词格式：
                  </label>
                  <CustomSelect
                    v-model="poetryFormat"
                    :options="poetryFormatOptions"
                    placeholder="请选择"
                  />
                </div>

                <div class="setting-row">
                  <label class="setting-label">
                    <span class="icon">🎨</span>
                    绘画风格：
                  </label>
                  <CustomSelect
                    v-model="paintingStyle"
                    :options="paintingStyleOptions"
                    placeholder="请选择"
                  />
                </div>

                <div class="setting-row">
                  <label class="setting-label">
                    <span class="icon">📐</span>
                    图像尺寸：
                  </label>
                  <CustomSelect
                    v-model="imageSize"
                    :options="imageSizeOptions"
                    placeholder="请选择"
                  />
                </div>
              </div>
            </div>
          </transition>
          </div>
        </div>

        <div class="input-container">
          <textarea
            v-model="userInput"
            placeholder="请输入您想创作的主题，例如：&#10;• 春江花月夜&#10;• 秋日登高远望&#10;• 梅花傲雪&#10;• 江南水乡..."
            class="input-textarea"
            @keydown.ctrl.enter="handleCreate"
          />

          <button
            @click="handleCreate"
            :disabled="!userInput.trim()"
            class="create-btn"
          >
            🚀 开始创作
          </button>
        </div>
      </div>

      <!-- 作品展示区（创作后） -->
      <transition name="fade">
        <div v-if="currentWork" class="work-display-area">
          <!-- 诗词和画作在同一个框中 -->
          <div class="work-container">
            <!-- 诗词展示 -->
            <div class="poetry-section">
              <PoetryDisplay
                :poetry="currentWork.poetry"
                :painting-style="currentWork.painting.style"
              />
            </div>

            <!-- 画作展示 -->
            <div class="painting-section">
              <PaintingDisplay
                :painting="currentWork.painting"
                :poetry="currentWork.poetry.content"
              />
            </div>
          </div>

          <!-- 优化输入（独立区域） -->
          <div v-if="!isGenerating" class="feedback-section-outside">
            <h3 class="feedback-title">💡 优化建议</h3>
            <div class="feedback-input-group">
              <textarea
                v-model="feedbackText"
                placeholder="对作品有什么优化建议？例如：诗词风格更豪放、画面色彩更淡雅..."
                class="feedback-textarea-inline"
              />
              <button
                @click="handleIterate"
                :disabled="!feedbackText.trim()"
                class="iterate-btn-inline"
              >
                ✨ 优化作品
              </button>
            </div>
          </div>
        </div>
      </transition>

      <!-- 右侧：创作历史 -->
      <div class="history-panel">
        <h3 class="history-title">🖼️ 创作历史</h3>
        
        <div v-if="workList && workList.length > 0" class="history-list">
          <div
            v-for="work in workList"
            :key="work.id"
            :class="['history-item', { active: currentWorkId === work.id }]"
            @click="selectWork(work)"
          >
            <div class="history-image" v-if="work.painting_local_path || work.painting_url">
              <img
                :src="getWorkImageUrl(work)"
                :alt="work.poetry_theme || '未命名'"
                loading="lazy"
                @error="handleImageError"
              />
            </div>
            <div class="history-image-placeholder" v-else>
              <span>📜</span>
            </div>
            <div class="history-info">
              <h4 class="history-work-title">{{ work.poetry_theme || '未命名主题' }}</h4>
              <p class="history-work-meta">
                {{ work.poetry_style }} · {{ formatDate(work.created_at) }}
              </p>
            </div>
          </div>
        </div>

        <div v-else class="history-empty">
          <div class="empty-icon">📜</div>
          <p>还没有创作记录</p>
          <small>开始您的第一次创作吧</small>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePoetryPainting } from './hooks/usePoetryPainting'
import CustomSelect from '@/components/CustomSelect.vue'
import PoetryDisplay from './components/PoetryDisplay.vue'
import PaintingDisplay from './components/PaintingDisplay.vue'
import { POETRY_STYLES, POETRY_FORMATS, PAINTING_STYLES, IMAGE_SIZES } from './types'

const {
  userInput,
  poetryStyle,
  poetryFormat,
  paintingStyle,
  imageSize,
  isGenerating,
  currentStep,
  currentWork,
  currentWorkId,
  workList,
  conversationId,
  conversations,
  hasCurrentWork,
  createWork,
  iterateWork,
  selectWork,
  rateWork,
  newConversation
} = usePoetryPainting()

const feedbackText = ref('')
const showSettings = ref(false)

// 转换选项格式
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

const imageSizeOptions = computed(() => 
  IMAGE_SIZES.map(size => ({
    value: size.value,
    label: size.label
  }))
)

const steps = computed(() => {
  const stepOrder = [
    'intent_recognizing', 'intent_recognized',
    'poetry_creating', 'poetry_created',
    'analyzing', 'poetry_analyzed',
    'painting_generating', 'painting_generated',
    'completed'
  ]
  const currentIndex = stepOrder.indexOf(currentStep.value)
  
  return [
    {
      key: 'intent',
      label: '理解意图',
      done: currentIndex >= stepOrder.indexOf('intent_recognized')
    },
    {
      key: 'poetry',
      label: '创作诗词',
      done: currentIndex >= stepOrder.indexOf('poetry_created')
    },
    {
      key: 'analysis',
      label: '意境分析',
      done: currentIndex >= stepOrder.indexOf('poetry_analyzed')
    },
    {
      key: 'painting',
      label: '绘制画作',
      done: currentIndex >= stepOrder.indexOf('painting_generated')
    },
    {
      key: 'completed',
      label: '完成',
      done: currentStep.value === 'completed'
    }
  ]
})

const currentStepText = computed(() => {
  const step = steps.value.find(s => s.key === currentStep.value)
  return step?.label || '处理中'
})

const handleCreate = async () => {
  showSettings.value = false  // 关闭设置菜单
  await createWork()
  feedbackText.value = ''
}

const handleIterate = async () => {
  if (!feedbackText.value.trim()) return
  await iterateWork(feedbackText.value)
  feedbackText.value = ''
}

// 点击外部关闭设置菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.settings-wrapper')) {
    showSettings.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 获取作品图片URL
const getWorkImageUrl = (work: any) => {
  if (!work) return ''
  
  if (work.painting_local_path) {
    return `http://localhost:8000/media/${work.painting_local_path}`
  }
  return work.painting_url_full || work.painting_url || ''
}

// 格式化日期
const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '未知'
  try {
    return dateStr.substring(0, 10)
  } catch {
    return '未知'
  }
}

// 图片加载错误处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style scoped>
.poetry-painting-view {
  max-width: 1600px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
  background: var(--color-background);
  min-height: 100vh;
}

/* 头部样式 */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid var(--color-border);
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.avatar {
  width: 4rem;
  height: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.info-text .title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--header-text);
  margin-bottom: 0.5rem;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 1rem;
}

.new-conversation-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: transform 0.2s, box-shadow 0.2s;
}

.new-conversation-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

/* 进度条（生成时显示） */
.progress-bar {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1rem 1.5rem;
  margin-bottom: 1.5rem;
}

.progress-steps-inline {
  display: flex;
  justify-content: space-around;
  align-items: center;
  gap: 1rem;
}

.step-inline {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  opacity: 0.5;
  transition: all 0.3s;
}

.step-inline.done {
  opacity: 1;
}

.step-inline.active {
  opacity: 1;
}

.step-inline .step-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  font-size: 1rem;
  color: var(--color-text-secondary);
  transition: all 0.3s;
}

.step-inline.done .step-icon {
  background: var(--button-primary);
  border-color: var(--button-primary);
  color: white;
}

.step-inline.active .step-icon {
  border-color: var(--button-primary);
  color: var(--button-primary);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.step-inline .step-label {
  font-size: 0.85rem;
  color: var(--color-text);
  text-align: center;
}

/* 主内容区 */
.main-content {
  display: grid;
  gap: 1.5rem;
  margin: 1rem 0;
}

/* 初始状态：左侧创作面板 + 右侧历史 */
.main-content:not(.has-work) {
  grid-template-columns: 1fr 300px;
}

/* 创作后：左侧作品展示 + 右侧历史 */
.main-content.has-work {
  grid-template-columns: 1fr 260px;
}

.creation-panel-full {
  background: var(--color-surface);
  border-radius: 1rem;
  padding: 2rem;
  border: 1px solid var(--color-border);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-title {
  font-size: 1.3rem;
  margin: 0;
  color: var(--color-text);
}

.settings-wrapper {
  position: relative;
}

.input-container {
  margin-bottom: 1.5rem;
}

.settings-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  color: var(--color-text);
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.settings-btn:hover {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
}

.settings-icon {
  font-size: 1rem;
}

/* 设置弹出菜单 */
.settings-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 1000;
  margin-top: 0.5rem;
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  box-shadow: var(--card-shadow);
  min-width: 350px;
}

.settings-content {
  padding: 1rem;
}

.settings-title {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: var(--color-text);
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--color-border);
}

.setting-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  min-width: 85px;
}

.setting-label .icon {
  font-size: 0.9rem;
}

/* 设置下拉动画 */
.settings-dropdown-enter-active,
.settings-dropdown-leave-active {
  transition: all 0.2s ease;
}

.settings-dropdown-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.settings-dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.input-textarea {
  width: 100%;
  min-height: 150px;
  padding: 1rem;
  border: 1px solid var(--input-border);
  border-radius: 0.5rem;
  background: var(--input-background);
  color: var(--color-text);
  font-size: 1rem;
  resize: vertical;
  margin-bottom: 1rem;
  transition: border-color 0.3s;
}

.input-textarea:focus {
  outline: none;
  border-color: var(--button-primary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.input-textarea:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.create-btn {
  width: 100%;
  padding: 0.875rem;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.create-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.create-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.generating {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}



/* 作品展示区 */
.work-display-area {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 作品容器（诗词和画作在同一个框中） */
.work-container {
  background: var(--color-surface);
  border-radius: 1rem;
  border: 1px solid var(--color-border);
  padding: 2rem;
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 2rem;
}

.poetry-section {
  /* 诗词部分 */
}

.painting-section {
  /* 画作部分 */
}

.feedback-section-outside {
  background: var(--color-surface);
  border-radius: 0.75rem;
  padding: 1.5rem;
  border: 1px solid var(--color-border);
}

.feedback-title {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.feedback-input-group {
  display: flex;
  gap: 0.75rem;
}

.feedback-textarea-inline {
  flex: 1;
  min-height: 60px;
  padding: 0.75rem;
  border: 1px solid var(--input-border);
  border-radius: 0.5rem;
  background: var(--input-background);
  color: var(--color-text);
  font-size: 0.9rem;
  resize: vertical;
}

.feedback-textarea-inline:focus {
  outline: none;
  border-color: var(--button-secondary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.iterate-btn-inline {
  padding: 0.75rem 1.5rem;
  background: var(--button-secondary);
  color: var(--button-secondaryText);
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.iterate-btn-inline:hover:not(:disabled) {
  box-shadow: var(--button-shadow);
}

.iterate-btn-inline:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 历史面板 */
.history-panel {
  background: var(--color-surface);
  border-radius: 1rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  max-height: 800px;
  overflow-y: auto;
}

.history-title {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
  color: var(--color-text);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.5rem;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.history-item:hover {
  transform: translateX(2px);
  box-shadow: var(--card-shadow);
}

.history-item.active {
  border-color: var(--button-primary);
  background: var(--color-primary-light);
}

.history-image,
.history-image-placeholder {
  width: 60px;
  height: 60px;
  border-radius: 0.4rem;
  overflow: hidden;
  flex-shrink: 0;
}

.history-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.history-image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background);
  border: 1px dashed var(--color-border);
  font-size: 2rem;
  opacity: 0.6;
}

.history-info {
  flex: 1;
  min-width: 0;
}

.history-work-title {
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-work-meta {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.history-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: var(--color-text-secondary);
}

.history-empty .empty-icon {
  font-size: 3rem;
  margin-bottom: 0.75rem;
  opacity: 0.5;
}

.history-empty p {
  margin: 0 0 0.25rem 0;
  color: var(--color-text);
}

.history-empty small {
  font-size: 0.85rem;
}

/* 历史面板滚动条 */
.history-panel::-webkit-scrollbar {
  width: 6px;
}

.history-panel::-webkit-scrollbar-track {
  background: var(--color-background);
  border-radius: 3px;
}

.history-panel::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 3px;
}

.history-panel::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

/* 过渡动画 */
.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.3s ease;
}

.collapse-enter-from,
.collapse-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式 */
@media (max-width: 1024px) {
  .main-content:not(.has-work),
  .main-content.has-work {
    grid-template-columns: 1fr;
  }

  .work-container {
    grid-template-columns: 1fr;
  }

  .history-panel {
    order: 1;
    max-height: 400px;
  }

  .creation-panel-full,
  .work-display-area {
    order: 2;
  }
}

@media (max-width: 640px) {
  .poetry-painting-view {
    padding: 1rem;
  }

  .header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .creation-bar {
    padding: 0.75rem 1rem;
  }

  .settings-dropdown,
  .settings-dropdown-mini {
    min-width: 300px;
  }
}
</style>

