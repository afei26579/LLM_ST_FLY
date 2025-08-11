<template>
  <div class="button-showcase">
    <div class="page-header">
      <h1>按钮组件展示</h1>
      <p class="page-description">展示所有按钮变体在不同主题下的效果</p>
    </div>

    <!-- 主题切换器 -->
    <div class="theme-switcher">
      <h3>当前主题</h3>
      <div class="theme-buttons">
        <button 
          v-for="theme in themes" 
          :key="theme.value"
          :class="['theme-btn', { active: currentTheme === theme.value }]"
          @click="switchTheme(theme.value)"
        >
          {{ theme.label }}
        </button>
      </div>
    </div>

    <!-- 按钮变体展示 -->
    <div class="showcase-section">
      <h2>按钮变体</h2>
      <div class="button-grid">
        <div class="button-group">
          <h3>Primary 主要按钮</h3>
          <div class="buttons">
            <Button variant="primary" size="small">小号按钮</Button>
            <Button variant="primary" size="medium">中号按钮</Button>
            <Button variant="primary" size="large">大号按钮</Button>
          </div>
        </div>

        <div class="button-group">
          <h3>Secondary 次要按钮</h3>
          <div class="buttons">
            <Button variant="secondary" size="small">小号按钮</Button>
            <Button variant="secondary" size="medium">中号按钮</Button>
            <Button variant="secondary" size="large">大号按钮</Button>
          </div>
        </div>

        <div class="button-group">
          <h3>Success 成功按钮</h3>
          <div class="buttons">
            <Button variant="success" size="small">保存</Button>
            <Button variant="success" size="medium">提交</Button>
            <Button variant="success" size="large">确认</Button>
          </div>
        </div>

        <div class="button-group">
          <h3>Warning 警告按钮</h3>
          <div class="buttons">
            <Button variant="warning" size="small">警告</Button>
            <Button variant="warning" size="medium">注意</Button>
            <Button variant="warning" size="large">提醒</Button>
          </div>
        </div>

        <div class="button-group">
          <h3>Error 错误按钮</h3>
          <div class="buttons">
            <Button variant="error" size="small">删除</Button>
            <Button variant="error" size="medium">取消</Button>
            <Button variant="error" size="large">拒绝</Button>
          </div>
        </div>

        <div class="button-group">
          <h3>Info 信息按钮</h3>
          <div class="buttons">
            <Button variant="info" size="small">详情</Button>
            <Button variant="info" size="medium">查看</Button>
            <Button variant="info" size="large">了解更多</Button>
          </div>
        </div>

        <div class="button-group">
          <h3>Ghost 幽灵按钮</h3>
          <div class="buttons">
            <Button variant="ghost" size="small">取消</Button>
            <Button variant="ghost" size="medium">跳过</Button>
            <Button variant="ghost" size="large">忽略</Button>
          </div>
        </div>

        <div class="button-group">
          <h3>Outline 轮廓按钮</h3>
          <div class="buttons">
            <Button variant="outline" size="small">编辑</Button>
            <Button variant="outline" size="medium">修改</Button>
            <Button variant="outline" size="large">更新</Button>
          </div>
        </div>
      </div>
    </div>

    <!-- 按钮状态展示 */
    <div class="showcase-section">
      <h2>按钮状态</h2>
      <div class="state-grid">
        <div class="state-group">
          <h3>正常状态</h3>
          <div class="buttons">
            <Button variant="primary">正常按钮</Button>
            <Button variant="success">成功按钮</Button>
            <Button variant="error">错误按钮</Button>
          </div>
        </div>

        <div class="state-group">
          <h3>禁用状态</h3>
          <div class="buttons">
            <Button variant="primary" disabled>禁用按钮</Button>
            <Button variant="success" disabled>禁用成功</Button>
            <Button variant="error" disabled>禁用错误</Button>
          </div>
        </div>

        <div class="state-group">
          <h3>加载状态</h3>
          <div class="buttons">
            <Button variant="primary" loading>加载中...</Button>
            <Button variant="success" loading loading-text="保存中">保存</Button>
            <Button variant="info" loading loading-text="处理中">处理</Button>
          </div>
        </div>
      </div>
    </div>

    <!-- 特殊样式展示 */
    <div class="showcase-section">
      <h2>特殊样式</h2>
      <div class="special-grid">
        <div class="special-group">
          <h3>圆角按钮</h3>
          <div class="buttons">
            <Button variant="primary" rounded>圆角主要</Button>
            <Button variant="success" rounded>圆角成功</Button>
            <Button variant="error" rounded>圆角错误</Button>
          </div>
        </div>

        <div class="special-group">
          <h3>块级按钮</h3>
          <div class="buttons block-buttons">
            <Button variant="primary" block>块级主要按钮</Button>
            <Button variant="secondary" block>块级次要按钮</Button>
          </div>
        </div>
      </div>
    </div>

    <!-- 实际应用场景 -->
    <div class="showcase-section">
      <h2>实际应用场景</h2>
      <div class="scenario-grid">
        <div class="scenario-card">
          <h3>表单操作</h3>
          <div class="form-actions">
            <Button variant="primary">保存</Button>
            <Button variant="ghost">取消</Button>
            <Button variant="outline">重置</Button>
          </div>
        </div>

        <div class="scenario-card">
          <h3>数据操作</h3>
          <div class="data-actions">
            <Button variant="success" size="small">新增</Button>
            <Button variant="info" size="small">编辑</Button>
            <Button variant="warning" size="small">禁用</Button>
            <Button variant="error" size="small">删除</Button>
          </div>
        </div>

        <div class="scenario-card">
          <h3>确认对话框</h3>
          <div class="dialog-actions">
            <Button variant="error">确认删除</Button>
            <Button variant="ghost">取消</Button>
          </div>
        </div>

        <div class="scenario-card">
          <h3>导航操作</h3>
          <div class="nav-actions">
            <Button variant="outline">上一步</Button>
            <Button variant="primary">下一步</Button>
            <Button variant="success">完成</Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'
import Button from '@/components/ui/Button.vue'
import type { ThemeType } from '@/types/theme'

const themeStore = useThemeStore()
const currentTheme = ref<ThemeType>(themeStore.currentTheme)

const themes = [
  { label: '浅色主题', value: 'light' as ThemeType },
  { label: '深色主题', value: 'dark' as ThemeType },
  { label: '未来科技', value: 'future' as ThemeType }
]

const switchTheme = (theme: ThemeType) => {
  themeStore.setTheme(theme)
  currentTheme.value = theme
}
</script>

<style scoped>
.button-showcase {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  background-color: var(--color-background);
  color: var(--color-text);
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h1 {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.page-description {
  font-size: 1.125rem;
  color: var(--color-textSecondary);
  margin: 0;
}

.theme-switcher {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 3rem;
  text-align: center;
}

.theme-switcher h3 {
  margin: 0 0 1rem 0;
  color: var(--color-text);
}

.theme-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.theme-btn {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  background-color: var(--color-background);
  color: var(--color-text);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-btn:hover {
  background-color: var(--color-surface);
  border-color: var(--color-primary);
}

.theme-btn.active {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.showcase-section {
  margin-bottom: 3rem;
}

.showcase-section h2 {
  font-size: 1.875rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--color-border);
}

.button-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.button-group {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.button-group h3 {
  margin: 0 0 1rem 0;
  color: var(--color-text);
  font-size: 1.125rem;
  font-weight: 600;
}

.buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.state-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.state-group {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.state-group h3 {
  margin: 0 0 1rem 0;
  color: var(--color-text);
  font-size: 1.125rem;
  font-weight: 600;
}

.special-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.special-group {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.special-group h3 {
  margin: 0 0 1rem 0;
  color: var(--color-text);
  font-size: 1.125rem;
  font-weight: 600;
}

.block-buttons {
  flex-direction: column;
  gap: 0.75rem;
}

.scenario-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.scenario-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.scenario-card h3 {
  margin: 0 0 1rem 0;
  color: var(--color-text);
  font-size: 1.125rem;
  font-weight: 600;
}

.form-actions,
.data-actions,
.dialog-actions,
.nav-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  align-items: center;
}

.data-actions {
  justify-content: space-between;
}

.dialog-actions {
  justify-content: flex-end;
}

.nav-actions {
  justify-content: space-between;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .button-showcase {
    padding: 1rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .button-grid,
  .state-grid,
  .special-grid {
    grid-template-columns: 1fr;
  }
  
  .scenario-grid {
    grid-template-columns: 1fr;
  }
  
  .theme-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .buttons {
    justify-content: center;
  }
  
  .form-actions,
  .data-actions,
  .dialog-actions,
  .nav-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
}

/* 未来科技主题特殊效果 */
.theme-future .button-group,
.theme-future .state-group,
.theme-future .special-group,
.theme-future .scenario-card {
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.1),
    0 0 40px rgba(255, 0, 110, 0.05);
}

.theme-future .theme-switcher {
  box-shadow: 
    0 0 25px rgba(0, 212, 255, 0.15),
    0 0 50px rgba(255, 0, 110, 0.08);
}
</style>