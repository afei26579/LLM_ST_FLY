<template>
  <div class="theme-preview" :class="`theme-${theme.name}`">
    <div class="preview-container">
      <!-- 模拟侧边栏 -->
      <div class="preview-sidebar">
        <div class="preview-logo">
          <div class="logo-icon"></div>
          <span class="logo-text">AI系统</span>
        </div>
        <div class="preview-nav">
          <div class="nav-item active">
            <div class="nav-icon"></div>
            <span>主页</span>
          </div>
          <div class="nav-item">
            <div class="nav-icon"></div>
            <span>用户管理</span>
          </div>
          <div class="nav-item">
            <div class="nav-icon"></div>
            <span>系统设置</span>
          </div>
        </div>
      </div>

      <!-- 模拟主内容区 -->
      <div class="preview-main">
        <!-- 模拟头部 -->
        <div class="preview-header">
          <div class="header-title">仪表板</div>
          <div class="header-actions">
            <div class="action-btn"></div>
            <div class="action-btn"></div>
          </div>
        </div>

        <!-- 模拟内容 -->
        <div class="preview-content">
          <div class="preview-cards">
            <div class="preview-card">
              <div class="card-header">
                <div class="card-title"></div>
                <div class="card-icon"></div>
              </div>
              <div class="card-content">
                <div class="card-text"></div>
                <div class="card-text short"></div>
              </div>
            </div>
            <div class="preview-card">
              <div class="card-header">
                <div class="card-title"></div>
                <div class="card-icon"></div>
              </div>
              <div class="card-content">
                <div class="card-text"></div>
                <div class="card-text short"></div>
              </div>
            </div>
          </div>

          <!-- 模拟按钮 -->
          <div class="preview-buttons">
            <div class="preview-btn primary"></div>
            <div class="preview-btn secondary"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主题标签 -->
    <div class="theme-label">
      <span class="theme-name">{{ theme.label }}</span>
      <div class="theme-colors">
        <div 
          class="color-dot" 
          v-for="(color, key) in displayColors" 
          :key="key"
          :style="{ backgroundColor: color }"
          :title="key"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ThemeConfig } from '../types/theme'

interface Props {
  theme: ThemeConfig
}

const props = defineProps<Props>()

// 显示的主要颜色
const displayColors = computed(() => ({
  主色: props.theme.colors.primary,
  背景: props.theme.colors.background,
  表面: props.theme.colors.surface,
  强调: props.theme.colors.accent
}))
</script>

<style scoped>
.theme-preview {
  width: 280px;
  height: 200px;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid transparent;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.theme-preview:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.preview-container {
  display: flex;
  height: 160px;
  background: var(--color-background);
}

/* 侧边栏预览 */
.preview-sidebar {
  width: 80px;
  background: var(--sidebar-background);
  padding: 8px;
  display: flex;
  flex-direction: column;
}

.preview-logo {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  gap: 6px;
}

.logo-icon {
  width: 16px;
  height: 16px;
  background: var(--color-primary);
  border-radius: 4px;
}

.logo-text {
  font-size: 10px;
  color: var(--sidebar-text);
  font-weight: 600;
}

.preview-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 8px;
  color: var(--sidebar-text);
  transition: background-color 0.2s;
}

.nav-item.active {
  background: var(--sidebar-activeBackground);
  color: var(--sidebar-activeText);
}

.nav-icon {
  width: 8px;
  height: 8px;
  background: currentColor;
  border-radius: 2px;
  opacity: 0.7;
}

/* 主内容区预览 */
.preview-main {
  flex: 1;
  background: var(--color-background);
  display: flex;
  flex-direction: column;
}

.preview-header {
  height: 32px;
  background: var(--header-background);
  border-bottom: 1px solid var(--header-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
}

.header-title {
  font-size: 10px;
  font-weight: 600;
  color: var(--header-text);
}

.header-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  width: 16px;
  height: 16px;
  background: var(--color-primary);
  border-radius: 3px;
  opacity: 0.8;
}

.preview-content {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preview-cards {
  display: flex;
  gap: 8px;
}

.preview-card {
  flex: 1;
  background: var(--card-background);
  border: 1px solid var(--card-border);
  border-radius: 6px;
  padding: 8px;
  box-shadow: var(--card-shadow);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.card-title {
  width: 40px;
  height: 8px;
  background: var(--color-text);
  border-radius: 2px;
  opacity: 0.8;
}

.card-icon {
  width: 12px;
  height: 12px;
  background: var(--color-primary);
  border-radius: 2px;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-text {
  height: 4px;
  background: var(--color-textSecondary);
  border-radius: 2px;
  opacity: 0.6;
}

.card-text.short {
  width: 60%;
}

.preview-buttons {
  display: flex;
  gap: 6px;
  margin-top: auto;
}

.preview-btn {
  width: 40px;
  height: 16px;
  border-radius: 4px;
}

.preview-btn.primary {
  background: var(--button-primary);
}

.preview-btn.secondary {
  background: var(--button-secondary);
}

/* 主题标签 */
.theme-label {
  height: 40px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.theme-name {
  font-size: 12px;
  font-weight: 600;
  color: #333;
}

.theme-colors {
  display: flex;
  gap: 4px;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* 主题特定样式 */
.theme-light {
  border-color: #e5e7eb;
}

.theme-light:hover {
  border-color: #3b82f6;
}

.theme-dark {
  border-color: #374151;
}

.theme-dark:hover {
  border-color: #5e9bff;
}

.theme-future {
  border-color: #1f2937;
  position: relative;
}

.theme-future:hover {
  border-color: #00d4ff;
  box-shadow: 
    0 8px 25px rgba(0, 0, 0, 0.15),
    0 0 20px rgba(0, 212, 255, 0.3);
}

.theme-future::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #00d4ff, #ff006e, #00d4ff);
  border-radius: 14px;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.theme-future:hover::before {
  opacity: 0.6;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .theme-preview {
    width: 240px;
    height: 180px;
  }
  
  .preview-container {
    height: 140px;
  }
  
  .preview-sidebar {
    width: 60px;
    padding: 6px;
  }
  
  .logo-text {
    display: none;
  }
}
</style>