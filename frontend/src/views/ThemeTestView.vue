<template>
  <div class="theme-test-container">
    <div class="test-header">
      <h1>主题测试页面</h1>
      <p>当前主题: {{ themeStore.theme.label }}</p>
    </div>

    <div class="test-content">
      <div class="test-section">
        <h2>颜色测试</h2>
        <div class="color-grid">
          <div class="color-item">
            <div class="color-box primary"></div>
            <span>主色调</span>
          </div>
          <div class="color-item">
            <div class="color-box secondary"></div>
            <span>次要色</span>
          </div>
          <div class="color-item">
            <div class="color-box accent"></div>
            <span>强调色</span>
          </div>
          <div class="color-item">
            <div class="color-box success"></div>
            <span>成功色</span>
          </div>
          <div class="color-item">
            <div class="color-box warning"></div>
            <span>警告色</span>
          </div>
          <div class="color-item">
            <div class="color-box error"></div>
            <span>错误色</span>
          </div>
        </div>
      </div>

      <div class="test-section">
        <h2>卡片测试</h2>
        <div class="cards-grid">
          <div class="test-card">
            <h3>测试卡片 1</h3>
            <p>这是一个测试卡片，用于验证主题样式是否正确应用。</p>
            <button class="btn btn-primary">主要按钮</button>
          </div>
          <div class="test-card">
            <h3>测试卡片 2</h3>
            <p>卡片背景、边框和阴影应该根据当前主题自动调整。</p>
            <button class="btn btn-secondary">次要按钮</button>
          </div>
        </div>
      </div>

      <div class="test-section">
        <h2>文本测试</h2>
        <div class="text-samples">
          <p class="text-primary">主要文本颜色</p>
          <p class="text-secondary">次要文本颜色</p>
          <p class="text-muted">静音文本颜色</p>
        </div>
      </div>

      <div class="test-section">
        <h2>快速主题切换</h2>
        <div class="theme-buttons">
          <button 
            v-for="theme in themeStore.themeList" 
            :key="theme.name"
            @click="themeStore.setTheme(theme.name as any)"
            :class="['theme-btn', { active: themeStore.currentTheme === theme.name }]"
          >
            {{ theme.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
</script>

<style scoped>
.theme-test-container {
  padding: 2rem;
  background: var(--color-background);
  color: var(--color-text);
  min-height: 100vh;
}

.test-header {
  text-align: center;
  margin-bottom: 3rem;
}

.test-header h1 {
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.test-content {
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 3rem;
  padding: 2rem;
  background: var(--card-background);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
}

.test-section h2 {
  color: var(--color-text);
  margin-bottom: 1.5rem;
  border-bottom: 2px solid var(--color-primary);
  padding-bottom: 0.5rem;
}

.color-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
}

.color-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.color-box {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  border: 2px solid var(--color-border);
}

.color-box.primary { background: var(--color-primary); }
.color-box.secondary { background: var(--color-secondary); }
.color-box.accent { background: var(--color-accent); }
.color-box.success { background: var(--color-success); }
.color-box.warning { background: var(--color-warning); }
.color-box.error { background: var(--color-error); }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.test-card {
  padding: 1.5rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
}

.test-card h3 {
  color: var(--color-text);
  margin-bottom: 1rem;
}

.test-card p {
  color: var(--color-textSecondary);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--button-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--button-primaryHover);
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--button-secondary);
  color: white;
}

.btn-secondary:hover {
  background: var(--button-secondaryHover);
  transform: translateY(-1px);
}

.text-samples {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.text-primary {
  color: var(--color-text);
  font-size: 1.1rem;
  font-weight: 500;
}

.text-secondary {
  color: var(--color-textSecondary);
  font-size: 1rem;
}

.text-muted {
  color: var(--color-textSecondary);
  font-size: 0.9rem;
  opacity: 0.7;
}

.theme-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.theme-btn {
  padding: 0.75rem 1.5rem;
  border: 2px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.theme-btn:hover {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: white;
  transform: translateY(-2px);
}

.theme-btn.active {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: white;
  box-shadow: 0 4px 12px rgba(var(--color-primary), 0.3);
}

/* 未来科技主题特殊效果 */
.theme-future .test-card {
  box-shadow: 
    var(--card-shadow),
    0 0 20px rgba(0, 212, 255, 0.1);
}

.theme-future .color-box {
  box-shadow: 0 0 10px rgba(0, 212, 255, 0.2);
}

.theme-future .theme-btn.active {
  box-shadow: 
    0 4px 12px rgba(0, 212, 255, 0.3),
    0 0 20px rgba(255, 0, 110, 0.2);
}
</style>