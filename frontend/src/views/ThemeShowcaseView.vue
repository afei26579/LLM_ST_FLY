<template>
  <div class="theme-showcase">
    <div class="showcase-header">
      <h1>主题系统展示</h1>
      <div class="header-actions">
        <ThemeToggle :show-label="true" size="large" />
      </div>
    </div>

    <div class="showcase-content">
      <!-- 主题预览卡片 -->
      <section class="section">
        <h2>主题预览</h2>
        <div class="theme-previews">
          <div v-for="theme in themeStore.themeList" :key="theme.name" class="theme-card"
            :class="{ active: themeStore.currentTheme === theme.name }" @click="themeStore.setTheme(theme.name as any)">
            <ThemePreview :theme="theme" />
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
              <div class="form-row">
                <div class="form-group">
                  <label>文本输入</label>
                  <input type="text" placeholder="请输入文字" />
                </div>
                <div class="form-group">
                  <label>密码输入</label>
                  <input type="password" placeholder="请输入文字" />
                </div>
              </div>



            </div>

            <div class="form-row">
              <div class="form-group">
                <label>单选框</label>
                <div class="radio-group">
                  <label class="radio-item">
                    <input type="radio" name="gender" value="male" />
                    <span class="radio-custom"></span>
                    <span class="radio-label">男</span>
                  </label>
                  <label class="radio-item">
                    <input type="radio" name="gender" value="female" />
                    <span class="radio-custom"></span>
                    <span class="radio-label">女</span>
                  </label>
                  <label class="radio-item">
                    <input type="radio" name="gender" value="other" />
                    <span class="radio-custom"></span>
                    <span class="radio-label">其他</span>
                  </label>
                </div>
              </div>

              <div class="form-group">
                <label>复选框</label>
                <div class="checkbox-group">
                  <label class="checkbox-item">
                    <input type="checkbox" value="reading" />
                    <span class="checkbox-custom"></span>
                    <span class="checkbox-label">阅读</span>
                  </label>
                  <label class="checkbox-item">
                    <input type="checkbox" value="music" />
                    <span class="checkbox-custom"></span>
                    <span class="checkbox-label">音乐</span>
                  </label>
                  <label class="checkbox-item">
                    <input type="checkbox" value="sports" />
                    <span class="checkbox-custom"></span>
                    <span class="checkbox-label">运动</span>
                  </label>
                  <label class="checkbox-item">
                    <input type="checkbox" value="travel" />
                    <span class="checkbox-custom"></span>
                    <span class="checkbox-label">旅行</span>
                  </label>
                </div>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>开关</label>
                <div class="switch-group">
                  <label class="switch-item">
                    <span class="switch-label">接收通知</span>
                    <div class="switch">
                      <input type="checkbox" />
                      <span class="switch-slider"></span>
                    </div>
                  </label>

                </div>
              </div>

              <div class="form-group">
                <label>滑块</label>
                <div class="range-group">
                  <input type="range" min="0" max="100" value="50" class="range-slider" />
                  <div class="range-labels">
                    <span>0</span>
                    <span>50</span>
                    <span>100</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-group">
              <label>文本域</label>
              <textarea placeholder="请输入多行文本内容..."></textarea>
            </div>



            <div class="form-actions">
              <button class="btn btn-primary">提交</button>
              <button class="btn btn-secondary">重置</button>
            </div>
          </div>
        </div>
      </section>

      <!-- 按钮组件展示 -->
      <section class="section">
        <h2>按钮组件展示</h2>

        <!-- 按钮变体展示 -->
        <div class="button-showcase-section">
          <h3>按钮变体</h3>
          <div class="button-showcase-grid">
            <div class="button-showcase-group">
              <h4>Primary 主要按钮</h4>
              <div class="button-showcase-buttons">
                <Button variant="primary" size="small">小号按钮</Button>
                <Button variant="primary" size="medium">中号按钮</Button>
                <Button variant="primary" size="large">大号按钮</Button>
              </div>
            </div>

            <div class="button-showcase-group">
              <h4>Secondary 次要按钮</h4>
              <div class="button-showcase-buttons">
                <Button variant="secondary" size="small">小号按钮</Button>
                <Button variant="secondary" size="medium">中号按钮</Button>
                <Button variant="secondary" size="large">大号按钮</Button>
              </div>
            </div>

            <div class="button-showcase-group">
              <h4>Success 成功按钮</h4>
              <div class="button-showcase-buttons">
                <Button variant="success" size="small">保存</Button>
                <Button variant="success" size="medium">提交</Button>
                <Button variant="success" size="large">确认</Button>
              </div>
            </div>

            <div class="button-showcase-group">
              <h4>Warning 警告按钮</h4>
              <div class="button-showcase-buttons">
                <Button variant="warning" size="small">警告</Button>
                <Button variant="warning" size="medium">注意</Button>
                <Button variant="warning" size="large">提醒</Button>
              </div>
            </div>

            <div class="button-showcase-group">
              <h4>Error 错误按钮</h4>
              <div class="button-showcase-buttons">
                <Button variant="error" size="small">删除</Button>
                <Button variant="error" size="medium">取消</Button>
                <Button variant="error" size="large">拒绝</Button>
              </div>
            </div>

            <div class="button-showcase-group">
              <h4>Info 信息按钮</h4>
              <div class="button-showcase-buttons">
                <Button variant="info" size="small">详情</Button>
                <Button variant="info" size="medium">查看</Button>
                <Button variant="info" size="large">了解更多</Button>
              </div>
            </div>

            <div class="button-showcase-group">
              <h4>Ghost 幽灵按钮</h4>
              <div class="button-showcase-buttons">
                <Button variant="ghost" size="small">取消</Button>
                <Button variant="ghost" size="medium">跳过</Button>
                <Button variant="ghost" size="large">忽略</Button>
              </div>
            </div>

            <div class="button-showcase-group">
              <h4>Outline 轮廓按钮</h4>
              <div class="button-showcase-buttons">
                <Button variant="outline" size="small">编辑</Button>
                <Button variant="outline" size="medium">修改</Button>
                <Button variant="outline" size="large">更新</Button>
              </div>
            </div>
          </div>
        </div>

        <!-- 按钮状态展示 -->
        <div class="button-showcase-section">
          <h3>按钮状态</h3>
          <div class="button-state-grid">
            <div class="button-state-group">
              <h4>正常状态</h4>
              <div class="button-showcase-buttons">
                <Button variant="primary">正常按钮</Button>
                <Button variant="success">成功按钮</Button>
                <Button variant="error">错误按钮</Button>
              </div>
            </div>

            <div class="button-state-group">
              <h4>禁用状态</h4>
              <div class="button-showcase-buttons">
                <Button variant="primary" disabled>禁用按钮</Button>
                <Button variant="success" disabled>禁用成功</Button>
                <Button variant="error" disabled>禁用错误</Button>
              </div>
            </div>

            <div class="button-state-group">
              <h4>加载状态</h4>
              <div class="button-showcase-buttons">
                <Button variant="primary" loading>加载中...</Button>
                <Button variant="success" loading loading-text="保存中">保存</Button>
                <Button variant="info" loading loading-text="处理中">处理</Button>
              </div>
            </div>
          </div>
        </div>

        <!-- 特殊样式展示 -->
        <div class="button-showcase-section">
          <h3>特殊样式</h3>
          <div class="button-special-grid">
            <div class="button-special-group">
              <h4>圆角按钮</h4>
              <div class="button-showcase-buttons">
                <Button variant="primary" rounded>圆角主要</Button>
                <Button variant="success" rounded>圆角成功</Button>
                <Button variant="error" rounded>圆角错误</Button>
              </div>
            </div>

            <div class="button-special-group">
              <h4>块级按钮</h4>
              <div class="button-showcase-buttons button-block-buttons">
                <Button variant="primary" block>块级主要按钮</Button>
                <Button variant="secondary" block>块级次要按钮</Button>
              </div>
            </div>
          </div>
        </div>

        <!-- 实际应用场景 -->
        <div class="button-showcase-section">
          <h3>实际应用场景</h3>
          <div class="button-scenario-grid">
            <div class="button-scenario-card">
              <h4>表单操作</h4>
              <div class="button-form-actions">
                <Button variant="primary">保存</Button>
                <Button variant="ghost">取消</Button>
                <Button variant="outline">重置</Button>
              </div>
            </div>

            <div class="button-scenario-card">
              <h4>数据操作</h4>
              <div class="button-data-actions">
                <Button variant="success" size="small">新增</Button>
                <Button variant="info" size="small">编辑</Button>
                <Button variant="warning" size="small">禁用</Button>
                <Button variant="error" size="small">删除</Button>
              </div>
            </div>

            <div class="button-scenario-card">
              <h4>确认对话框</h4>
              <div class="button-dialog-actions">
                <Button variant="error">确认删除</Button>
                <Button variant="ghost">取消</Button>
              </div>
            </div>

            <div class="button-scenario-card">
              <h4>导航操作</h4>
              <div class="button-nav-actions">
                <Button variant="outline">上一步</Button>
                <Button variant="primary">下一步</Button>
                <Button variant="success">完成</Button>
              </div>
            </div>
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
import Button from '../components/ui/Button.vue'

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
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent)) !important;
  color: white !important;
  position: fixed !important;
  top: 0 !important;
  left: 250px !important;
  /* 避开左侧导航栏 */
  right: 0 !important;
  z-index: 1000 !important;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
  backdrop-filter: blur(10px);
  width: calc(100% - 250px) !important;
  /* 计算正确的宽度 */
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

.showcase-header>* {
  position: relative;
  z-index: 1;
}

.showcase-header h1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.header-actions {
  display: flex;
  justify-content: center;
}

.showcase-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  margin-top: 120px;
  /* 为固定头部留出空间 */
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
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
  padding: 0;
  justify-items: center;
}

.theme-card {
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 16px;
  position: relative;
  padding: 4px;
  margin: 0;
  width: 100%;
  max-width: 320px;
  background: transparent;
}

.theme-card:hover {
  transform: translateY(-4px);
}

.theme-card.active {
  background: var(--color-primary);
  border-radius: 16px;
  padding: 4px;
}

.theme-card.active :deep(.theme-preview) {
  border-radius: 12px;
  border: none;
}

.theme-card :deep(.theme-preview) {
  border-radius: 12px;
  border: 2px solid var(--color-border);
}

/* 响应式调整 */
@media (max-width: 1024px) {
  .theme-previews {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .theme-previews {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding: 0 1rem;
  }

  .theme-card {
    max-width: 100%;
  }
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

.color-swatch.primary {
  background: var(--color-primary);
}

.color-swatch.secondary {
  background: var(--color-secondary);
}

.color-swatch.accent {
  background: var(--color-accent);
}

.color-swatch.success {
  background: var(--color-success);
}

.color-swatch.warning {
  background: var(--color-warning);
}

.color-swatch.error {
  background: var(--color-error);
}

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

}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group>label {
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 0.5rem;
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
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
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

/* 单选框样式 */
.radio-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.radio-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
  margin-bottom: 0 !important;
}

.radio-item input[type="radio"] {
  display: none;
}

.radio-custom {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-radius: 50%;
  background: var(--color-surface);
  position: relative;
  transition: all 0.2s ease;
}

.radio-item input[type="radio"]:checked+.radio-custom {
  border-color: var(--color-primary);
  background: var(--color-primary);
}

.radio-item input[type="radio"]:checked+.radio-custom::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: white;
}

.radio-label {
  color: var(--color-text);
  font-size: 0.875rem;
}

/* 复选框样式 */
.checkbox-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: normal;
  margin-bottom: 0 !important;
}

.checkbox-item input[type="checkbox"] {
  display: none;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-surface);
  position: relative;
  transition: all 0.2s ease;
}

.checkbox-item input[type="checkbox"]:checked+.checkbox-custom {
  border-color: var(--color-primary);
  background: var(--color-primary);
}

.checkbox-item input[type="checkbox"]:checked+.checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 12px;
  font-weight: bold;
}

.checkbox-label {
  color: var(--color-text);
  font-size: 0.875rem;
}

/* 开关样式 */
.switch-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  font-weight: normal;
  margin-bottom: 0 !important;
}

.switch-label {
  color: var(--color-text);
  font-size: 0.875rem;
}

.switch {
  position: relative;
  width: 44px;
  height: 24px;
}

.switch input[type="checkbox"] {
  display: none;
}

.switch-slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--color-border);
  border-radius: 24px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.switch-slider::before {
  content: '';
  position: absolute;
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.switch input[type="checkbox"]:checked+.switch-slider {
  background: var(--color-primary);
}

.switch input[type="checkbox"]:checked+.switch-slider::before {
  transform: translateX(20px);
}

/* 滑块样式 */
.range-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.range-slider {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--color-border);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
}

.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.range-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary);
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-textSecondary);
}

/* 特殊输入框样式 */
.form-group input[type="date"],
.form-group input[type="time"],
.form-group input[type="color"],
.form-group input[type="file"] {
  cursor: pointer;
}

.form-group input[type="color"] {
  width: 60px;
  height: 40px;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
}

.form-group input[type="file"] {
  padding: 0.5rem;
  background: var(--color-background);
}

.form-group input[type="file"]::-webkit-file-upload-button {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 0.5rem;
  font-size: 0.875rem;
}

.form-group input[type="file"]::-webkit-file-upload-button:hover {
  background: var(--button-primaryHover);
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--color-border);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .radio-group,
  .checkbox-group {
    flex-direction: column;
    gap: 0.75rem;
  }

  .form-actions {
    justify-content: center;
  }
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
    left: 0 !important;
    width: 100% !important;
    padding: 1rem;
  }

  .theme-future .showcase-header {
    left: 0 !important;
    width: 100% !important;
  }

  .showcase-header h1 {
    font-size: 1.5rem;
  }

  .showcase-content {
    margin-top: 80px;
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

/* 中等屏幕适配 */
@media (max-width: 1024px) and (min-width: 769px) {
  .showcase-header {
    left: 200px !important;
    width: calc(100% - 200px) !important;
  }

  .theme-future .showcase-header {
    left: 200px !important;
    width: calc(100% - 200px) !important;
  }
}

/* 未来科技主题特殊效果 */
.theme-future .showcase-header {
  background: linear-gradient(135deg, #00d4ff, #ff006e) !important;
  position: fixed !important;
  top: 0 !important;
  left: 250px !important;
  right: 0 !important;
  z-index: 1000 !important;
  width: calc(100% - 250px) !important;
  color: white !important;
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
  pointer-events: none;
}

@keyframes futureBg {
  0% {
    opacity: 0.5;
  }

  100% {
    opacity: 0.8;
  }
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

/* 按钮展示样式 */
.button-showcase-section {
  margin-bottom: 3rem;
}

.button-showcase-section h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.5rem;
}

.button-showcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.button-showcase-group {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.button-showcase-group h4 {
  margin: 0 0 1rem 0;
  color: var(--color-text);
  font-size: 1.125rem;
  font-weight: 600;
}

.button-showcase-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.button-state-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.button-state-group {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.button-state-group h4 {
  margin: 0 0 1rem 0;
  color: var(--color-text);
  font-size: 1.125rem;
  font-weight: 600;
}

.button-special-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.button-special-group {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.button-special-group h4 {
  margin: 0 0 1rem 0;
  color: var(--color-text);
  font-size: 1.125rem;
  font-weight: 600;
}

.button-block-buttons {
  flex-direction: column;
  gap: 0.75rem;
}

.button-scenario-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.button-scenario-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.button-scenario-card h4 {
  margin: 0 0 1rem 0;
  color: var(--color-text);
  font-size: 1.125rem;
  font-weight: 600;
}

.button-form-actions,
.button-data-actions,
.button-dialog-actions,
.button-nav-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.button-data-actions {
  justify-content: space-between;
}

.button-dialog-actions {
  justify-content: flex-end;
}

.button-nav-actions {
  justify-content: space-between;
}

/* 响应式设计 - 按钮展示 */
@media (max-width: 768px) {

  .button-showcase-grid,
  .button-state-grid,
  .button-special-grid {
    grid-template-columns: 1fr;
  }

  .button-scenario-grid {
    grid-template-columns: 1fr;
  }

  .button-showcase-buttons {
    justify-content: center;
  }

  .button-form-actions,
  .button-data-actions,
  .button-dialog-actions,
  .button-nav-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
}

/* 未来科技主题特殊效果 - 按钮展示 */
.theme-future .button-showcase-group,
.theme-future .button-state-group,
.theme-future .button-special-group,
.theme-future .button-scenario-card {
  box-shadow:
    0 0 20px rgba(0, 212, 255, 0.1),
    0 0 40px rgba(255, 0, 110, 0.05);
}
</style>
