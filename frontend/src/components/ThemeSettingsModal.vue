<template>
  <div v-if="isOpen" class="modal-overlay" @click="handleOverlayClick">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2 class="modal-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"></circle>
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
          </svg>
          主题设置
        </h2>
        <button class="close-btn" @click="$emit('close')">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="modal-content">
        <div class="theme-section">
          <h3 class="section-title">选择主题</h3>
          <p class="section-description">选择您喜欢的界面主题风格</p>
          
          <div class="theme-grid">
            <div 
              v-for="theme in themeStore.themeList" 
              :key="theme.name"
              class="theme-card"
              :class="{ 'active': themeStore.currentTheme === theme.name }"
              @click="selectTheme(theme.name as ThemeType)"
            >
              <div class="theme-preview">
                <div class="preview-header" :style="{ background: theme.header.background }">
                  <div class="preview-dot"></div>
                  <div class="preview-dot"></div>
                  <div class="preview-dot"></div>
                </div>
                <div class="preview-body">
                  <div class="preview-sidebar" :style="{ background: theme.sidebar.background }">
                    <div class="sidebar-item"></div>
                    <div class="sidebar-item active" :style="{ background: theme.sidebar.activeBackground }"></div>
                    <div class="sidebar-item"></div>
                  </div>
                  <div class="preview-content" :style="{ background: theme.colors.background }">
                    <div class="content-card" :style="{ background: theme.card.background }"></div>
                    <div class="content-card" :style="{ background: theme.card.background }"></div>
                  </div>
                </div>
              </div>
              
              <div class="theme-info">
                <h4 class="theme-name">{{ theme.label }}</h4>
                <div class="theme-colors">
                  <div 
                    class="color-dot" 
                    :style="{ background: theme.colors.primary }"
                  ></div>
                  <div 
                    class="color-dot" 
                    :style="{ background: theme.colors.accent }"
                  ></div>
                  <div 
                    class="color-dot" 
                    :style="{ background: theme.colors.success }"
                  ></div>
                </div>
              </div>
              
              <div v-if="themeStore.currentTheme === theme.name" class="selected-indicator">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div class="theme-features">
          <h3 class="section-title">主题特性</h3>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="5"></circle>
                  <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
                </svg>
              </div>
              <div class="feature-content">
                <h4>浅色主题</h4>
                <p>清新明亮，适合白天使用</p>
              </div>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                </svg>
              </div>
              <div class="feature-content">
                <h4>深色主题</h4>
                <p>护眼舒适，适合夜间使用</p>
              </div>
            </div>
            
            <div class="feature-item">
              <div class="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
              </div>
              <div class="feature-content">
                <h4>未来科技</h4>
                <p>炫酷科幻，彰显个性风格</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')">
          取消
        </button>
        <button class="btn btn-primary" @click="applyTheme">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          应用主题
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useThemeStore, type ThemeType } from '../stores/theme'

interface Props {
  isOpen: boolean
}

defineProps<Props>()
const emit = defineEmits<{
  close: []
  applied: [theme: ThemeType]
}>()

const themeStore = useThemeStore()
const selectedTheme = ref<ThemeType>(themeStore.currentTheme)

const selectTheme = (theme: ThemeType) => {
  selectedTheme.value = theme
  // 立即预览主题效果
  themeStore.setTheme(theme)
}

const applyTheme = () => {
  themeStore.setTheme(selectedTheme.value)
  emit('applied', selectedTheme.value)
  emit('close')
}

const handleOverlayClick = () => {
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-container {
  background: var(--card-background);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--color-textSecondary);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--color-border);
  color: var(--color-text);
}

.modal-content {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

.theme-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0 0 0.5rem 0;
}

.section-description {
  color: var(--color-textSecondary);
  margin: 0 0 1.5rem 0;
  font-size: 0.9rem;
}

.theme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.theme-card {
  border: 2px solid var(--color-border);
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  background: var(--color-surface);
}

.theme-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.theme-card.active {
  border-color: var(--color-primary);
  background: rgba(var(--color-primary), 0.05);
}

.theme-preview {
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.preview-header {
  height: 20px;
  display: flex;
  align-items: center;
  padding: 0 8px;
  gap: 4px;
}

.preview-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
}

.preview-body {
  display: flex;
  height: 60px;
}

.preview-sidebar {
  width: 30%;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-item {
  height: 8px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.2);
}

.sidebar-item.active {
  background: rgba(255, 255, 255, 0.4);
}

.preview-content {
  flex: 1;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.content-card {
  height: 20px;
  border-radius: 4px;
  background: rgba(0, 0, 0, 0.05);
}

.theme-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.theme-name {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text);
  margin: 0;
}

.theme-colors {
  display: flex;
  gap: 4px;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.selected-indicator {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-features {
  border-top: 1px solid var(--color-border);
  padding-top: 1.5rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  background: var(--color-surface);
}

.feature-icon {
  color: var(--color-primary);
  flex-shrink: 0;
}

.feature-content h4 {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text);
  margin: 0 0 0.25rem 0;
}

.feature-content p {
  font-size: 0.8rem;
  color: var(--color-textSecondary);
  margin: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-textSecondary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background: var(--color-border);
  color: var(--color-text);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--button-primaryHover);
  transform: translateY(-1px);
}
</style>