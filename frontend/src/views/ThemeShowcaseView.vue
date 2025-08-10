<template>
  <div class="theme-showcase">
    <div class="showcase-header">
      <h1>主题系统展示</h1>
      <p>体验我们精心设计的三种主题风格</p>
      <div class="header-actions">
        <ThemeToggle :show-label="true" size="large" />
      </div>
    </div>

    <div class="showcase-content">
      <!-- 主题预览卡片 -->
      <section class="section">
        <h2>主题预览</h2>
        <div class="theme-previews">
          <div 
            v-for="theme in themeStore.themeList" 
            :key="theme.name"
            class="theme-card"
            :class="{ active: themeStore.currentTheme === theme.name }"
            @click="themeStore.setTheme(theme.name as any)"
          >
            <ThemePreview :theme="theme" />
          </div>
        </div>
      </section>

      <!-- 颜色系统展示 -->
      <section class="section">
        <h2>颜色系统</h2>
        <div class="color-system">
          <div class="color-category">
            <h3>主要颜色</h3>
            <div class="color-grid">
              <div class="color-item">
                <div class="color-swatch primary"></div>
                <div class="color-info">
                  <span class="color-name">主色调</span>
                  <span class="color-value">{{ themeStore.theme.colors.primary }}</span>
                </div>
              </div>
              <div class="color-item">
                <div class="color-swatch secondary"></div>
                <div class="color-info">
                  <span class="color-name">次要色</span>
                  <span class="color-value">{{ themeStore.theme.colors.secondary }}</span>
                </div>
              </div>
              <div class="color-item">
                <div class="color-swatch accent"></div>
                <div class="color-info">
                  <span class="color-name">强调色</span>
                  <span class="color-value">{{ themeStore.theme.colors.accent }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="color-category">
            <h3>状态颜色</h3>
            <div class="color-grid">
              <div class="color-item">
                <div class="color-swatch success"></div>
                <div class="color-info">
                  <span class="color-name">成功</span>
                  <span class="color-value">{{ themeStore.theme.colors.success }}</span>
                </div>
              </div>
              <div class="color-item">
                <div class="color-swatch warning"></div>
                <div class="color-info">
                  <span class="color-name">警告</span>
                  <span class="color-value">{{ themeStore.theme.colors.warning }}</span>
                </div>
              </div>
              <div class="color-item">
                <div class="color-swatch error"></div>
                <div class="color-info">
                  <span class="color-name">错误</span>
                  <span class="color-value">{{ themeStore.theme.colors.error }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 组件展示 -->
      <section class="section">
        <h2>组件展示</h2>
        <div class="component-showcase">
          <!-- 按钮组件 -->
          <div class="component-group">
            <h3>按钮</h3>
            <div class="button-group">
              <button class="btn btn-primary">主要按钮</button>
              <button class="btn btn-secondary">次要按钮</button>
              <button class="btn btn-outline">边框按钮</button>
              <button class="btn btn-text">文本按钮</button>
            </div>
          </div>

          <!-- 卡片组件 -->
          <div class="component-group">
            <h3>卡片</h3>
            <div class="card-group">
              <div class="demo-card">
                <div class="card-header">
                  <h4>标准卡片</h4>
                  <span class="card-badge">新</span>
                </div>
                <div class="card-content">
                  <p>这是一个标准的卡片组件，展示了当前主题的卡片样式。</p>
                </div>
                <div class="card-footer">
                  <button class="btn btn-sm btn-primary">操作</button>
                </div>
              </div>

              <div class="demo-card elevated">
                <div class="card-header">
                  <h4>悬浮卡片</h4>
                  <span class="card-badge success">推荐</span>
                </div>
                <div class="card-content">
                  <p>这是一个带有阴影效果的悬浮卡片，适合重要内容展示。</p>
                </div>
                <div class="card-footer">
                  <button class="btn btn-sm btn-secondary">查看详情</button>
                </div>
              </div>
            </div>
          </div>

          <!-- 表单组件 -->
          <div class="component-group">
            <h3>表单</h3>
            <div class="form-demo">
              <div class="form-group">
                <label>输入框</label>
                <input type="text" placeholder="请输入内容" />
              </div>
              <div class="form-group">
                <label>选择框</label>
                <select>
                  <option>选项一</option>
                  <option>选项二</option>
                  <option>选项三</option>
                </select>
              </div>
              <div class="form-group">
                <label>文本域</label>
                <textarea placeholder="请输入详细描述"></textarea>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 主题特性 -->
      <section class="section">
        <h2>主题特性</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <h3>三种风格</h3>
            <p>浅色、深色、未来科技三种精心设计的主题风格</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3>实时切换</h3>
            <p>无需刷新页面，主题切换即时生效</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">💾</div>
            <h3>自动保存</h3>
            <p>用户偏好自动保存，下次访问时恢复</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔧</div>
            <h3>易于扩展</h3>
            <p>基于CSS变量，开发者可轻松添加新主题</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '../stores/theme'
import ThemeToggle from '../components/ThemeToggle.vue'
import ThemePreview from '../components/ThemePreview.vue'

const themeStore = useThemeStore()
</script>

<style scoped>
.theme-showcase {
  min-height: 100vh;
  background: var(--color-background);
  color: var(--color-text);
}

.showcase-header {
  text-align: center;
  padding: 3rem 2rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  position: relative;
  overflow: hidden;
}

.showcase-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.showcase-header > * {
  position: relative;
  z-index: 1;
}

.showcase-header h1 {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.showcase-header p {
  font-size: 1.25rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  justify-content: center;
}

.showcase-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.section {
  margin-bottom: 4rem;
}

.section h2 {
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 2rem;
  color: var(--color-primary);
  border-bottom: 2px solid var(--color-primary);
  padding-bottom: 0.5rem;
}

.theme-previews {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.theme-card {
  cursor: pointer;
  transition: transform 0.2s ease;
  border-radius: 12px;
  overflow: hidden;
}

.theme-card:hover {
  transform: translateY(-4px);
}

.theme-card.active {
  box-shadow: 0 0 0 3px var(--color-primary);
}

.color-system {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.color-category h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.color-grid {
  display: grid;
  gap: 1rem;
}

.color-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.color-swatch {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  border: 2px solid var(--color-border);
  flex-shrink: 0;
}

.color-swatch.primary { background: var(--color-primary); }
.color-swatch.secondary { background: var(--color-secondary); }
.color-swatch.accent { background: var(--color-accent); }
.color-swatch.success { background: var(--color-success); }
.color-swatch.warning { background: var(--color-warning); }
.color-swatch.error { background: var(--color-error); }

.color-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.color-name {
  font-weight: 500;
  color: var(--color-text);
}

.color-value {
  font-size: 0.875rem;
  color: var(--color-textSecondary);
  font-family: monospace;
}

.component-showcase {
  display: grid;
  gap: 3rem;
}

.component-group h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.button-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  font-size: 0.875rem;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary);
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.btn-secondary {
  background: var(--color-secondary);
  color: white;
}

.btn-secondary:hover {
  background: var(--color-secondary);
  filter: brightness(1.1);
  transform: translateY(-1px);
}

.btn-outline {
  background: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

.btn-outline:hover {
  background: var(--color-primary);
  color: white;
  transform: translateY(-1px);
}

.btn-text {
  background: transparent;
  color: var(--color-primary);
  border: none;
}

.btn-text:hover {
  background: rgba(var(--color-primary-rgb), 0.1);
  transform: translateY(-1px);
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
}

.card-group {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.demo-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.demo-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--card-shadow);
}

.demo-card.elevated {
  box-shadow: var(--card-shadow);
}

.card-header {
  padding: 1.5rem 1.5rem 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h4 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
}

.card-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--color-primary);
  color: white;
}

.card-badge.success {
  background: var(--color-success);
}

.card-content {
  padding: 1rem 1.5rem;
}

.card-content p {
  margin: 0;
  color: var(--color-textSecondary);
  line-height: 1.6;
}

.card-footer {
  padding: 0 1.5rem 1.5rem;
}

.form-demo {
  display: grid;
  gap: 1.5rem;
  max-width: 400px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: var(--color-text);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 2rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  transition: all 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--card-shadow);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.feature-card p {
  color: var(--color-textSecondary);
  line-height: 1.6;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .showcase-header {
    padding: 2rem 1rem;
  }
  
  .showcase-header h1 {
    font-size: 2rem;
  }
  
  .showcase-content {
    padding: 1rem;
  }
  
  .button-group {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .card-group {
    grid-template-columns: 1fr;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
}

/* 未来科技主题特殊效果 */
.theme-future .showcase-header {
  background: linear-gradient(135deg, #00d4ff, #ff006e);
  position: relative;
}

.theme-future .showcase-header::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 0, 110, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(0, 212, 255, 0.2) 0%, transparent 50%);
  animation: futureBg 10s ease-in-out infinite alternate;
}

@keyframes futureBg {
  0% { opacity: 0.5; }
  100% { opacity: 0.8; }
}

.theme-future .demo-card {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
}

.theme-future .demo-card:hover {
  box-shadow: 0 0 30px rgba(0, 212, 255, 0.2);
}

.theme-future .feature-card:hover {
  box-shadow: 
    var(--card-shadow),
    0 0 20px rgba(0, 212, 255, 0.2);
}
</style>
