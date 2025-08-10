<template>
  <div class="theme-toggle">
    <button 
      class="theme-toggle-btn"
      @click="toggleTheme"
      :title="`切换到${getNextThemeLabel()}`"
    >
      <div class="theme-icon">
        <svg v-if="themeStore.currentTheme === 'light'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"></circle>
          <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
        </svg>
        <svg v-else-if="themeStore.currentTheme === 'dark'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
      </div>
      <span class="theme-label" v-if="showLabel">{{ themeStore.theme.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '../stores/theme'
import type { ThemeType } from '../types/theme'

interface Props {
  showLabel?: boolean
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  showLabel: false,
  size: 'medium'
})

const themeStore = useThemeStore()

// 主题切换顺序：light -> dark -> future -> light
const themeOrder: ThemeType[] = ['light', 'dark', 'future']

const toggleTheme = () => {
  const currentIndex = themeOrder.indexOf(themeStore.currentTheme)
  const nextIndex = (currentIndex + 1) % themeOrder.length
  const nextTheme = themeOrder[nextIndex]
  
  themeStore.setTheme(nextTheme)
}

const getNextThemeLabel = () => {
  const currentIndex = themeOrder.indexOf(themeStore.currentTheme)
  const nextIndex = (currentIndex + 1) % themeOrder.length
  const nextTheme = themeOrder[nextIndex]
  
  const labels = {
    light: '浅色主题',
    dark: '深色主题',
    future: '未来科技主题'
  }
  
  return labels[nextTheme]
}
</script>

<style scoped>
.theme-toggle {
  display: inline-block;
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.875rem;
  font-weight: 500;
}

.theme-toggle-btn:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb), 0.3);
}

.theme-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.theme-toggle-btn:hover .theme-icon {
  transform: rotate(15deg);
}

.theme-label {
  white-space: nowrap;
}

/* 尺寸变体 */
.theme-toggle[data-size="small"] .theme-toggle-btn {
  padding: 0.375rem;
  font-size: 0.75rem;
}

.theme-toggle[data-size="small"] .theme-icon svg {
  width: 16px;
  height: 16px;
}

.theme-toggle[data-size="large"] .theme-toggle-btn {
  padding: 0.75rem 1rem;
  font-size: 1rem;
}

.theme-toggle[data-size="large"] .theme-icon svg {
  width: 24px;
  height: 24px;
}

/* 未来科技主题特殊效果 */
.theme-future .theme-toggle-btn {
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
}

.theme-future .theme-toggle-btn:hover {
  box-shadow: 
    0 4px 12px rgba(0, 212, 255, 0.4),
    0 0 20px rgba(255, 0, 110, 0.3);
}

/* 动画效果 */
@keyframes themeSwitch {
  0% { transform: scale(1) rotate(0deg); }
  50% { transform: scale(1.1) rotate(180deg); }
  100% { transform: scale(1) rotate(360deg); }
}

.theme-toggle-btn:active .theme-icon {
  animation: themeSwitch 0.6s ease-in-out;
}
</style>