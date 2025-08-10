# 主题系统使用说明

## 概述

本项目实现了一个完整的主题切换系统，支持三种预设主题：浅色主题、深色主题和未来科技主题。

## 功能特性

### 1. 三种预设主题

- **浅色主题 (Light)**: 清新明亮，适合白天使用
- **深色主题 (Dark)**: 护眼舒适，适合夜间使用  
- **未来科技主题 (Future)**: 炫酷科幻，彰显个性风格

### 2. 主题切换方式

#### 方式一：通过侧边栏菜单
1. 点击侧边栏底部的用户头像
2. 在下拉菜单中选择"主题设置"
3. 在弹出的主题设置窗口中选择喜欢的主题
4. 点击"应用主题"按钮确认

#### 方式二：通过测试页面
1. 访问 `/theme-test` 页面
2. 在页面底部的"快速主题切换"区域直接点击主题按钮

### 3. 主题特色

#### 浅色主题
- 背景色：纯白色 (#ffffff)
- 主色调：蓝色 (#3b82f6)
- 适合：白天办公、长时间阅读

#### 深色主题
- 背景色：深蓝灰 (#0f172a)
- 主色调：亮蓝色 (#5e9bff)
- 适合：夜间使用、护眼需求

#### 未来科技主题
- 背景色：深黑色 (#0a0a0f)
- 主色调：青蓝色 (#00d4ff)
- 特效：霓虹发光、渐变边框
- 适合：个性展示、科技感需求

## 技术实现

### 1. 文件结构
```
frontend/
├── src/
│   ├── stores/
│   │   └── theme.ts              # 主题状态管理
│   ├── components/
│   │   ├── SideNav.vue           # 侧边栏（含主题切换入口）
│   │   └── ThemeSettingsModal.vue # 主题设置弹窗
│   ├── styles/
│   │   └── themes.css            # 主题CSS变量定义
│   └── views/
│       └── ThemeTestView.vue     # 主题测试页面
```

### 2. 核心技术

#### CSS变量系统
所有主题颜色都通过CSS变量定义：
```css
:root {
  --color-primary: #5e9bff;
  --color-background: #0f172a;
  --sidebar-background: linear-gradient(180deg, #1a2233 0%, #0c1425 100%);
  /* ... 更多变量 */
}
```

#### 主题切换逻辑
```typescript
// 设置主题
const setTheme = (theme: ThemeType) => {
  currentTheme.value = theme
  localStorage.setItem('app-theme', theme)
  applyTheme()
}

// 应用主题到CSS变量
const applyTheme = () => {
  const theme = themes[currentTheme.value]
  const root = document.documentElement
  
  Object.entries(theme.colors).forEach(([key, value]) => {
    root.style.setProperty(`--color-${key}`, value)
  })
}
```

### 3. 状态管理

使用Pinia进行主题状态管理：
```typescript
export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref<ThemeType>('dark')
  
  const setTheme = (theme: ThemeType) => { /* ... */ }
  const loadTheme = () => { /* ... */ }
  
  return { currentTheme, setTheme, loadTheme }
})
```

## 开发指南

### 1. 在组件中使用主题

#### 获取主题状态
```vue
<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()

// 获取当前主题
console.log(themeStore.currentTheme) // 'light' | 'dark' | 'future'

// 获取主题配置
console.log(themeStore.theme.label) // '深色主题'
</script>
```

#### 切换主题
```vue
<template>
  <button @click="switchTheme">切换到浅色主题</button>
</template>

<script setup lang="ts">
const switchTheme = () => {
  themeStore.setTheme('light')
}
</script>
```

### 2. 在样式中使用主题变量

```vue
<style scoped>
.my-component {
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  box-shadow: var(--card-shadow);
}

.my-button {
  background: var(--button-primary);
  color: white;
}

.my-button:hover {
  background: var(--button-primaryHover);
}
</style>
```

### 3. 添加新主题

1. 在 `theme.ts` 中的 `themes` 对象添加新主题配置
2. 在 `themes.css` 中添加对应的CSS类
3. 更新 `ThemeType` 类型定义

```typescript
// 1. 添加类型
export type ThemeType = 'light' | 'dark' | 'future' | 'custom'

// 2. 添加主题配置
const themes: Record<ThemeType, ThemeConfig> = {
  // ... 现有主题
  custom: {
    name: 'custom',
    label: '自定义主题',
    colors: {
      primary: '#ff6b6b',
      // ... 其他颜色配置
    }
  }
}
```

```css
/* 3. 添加CSS类 */
.theme-custom {
  --color-primary: #ff6b6b;
  /* ... 其他变量 */
}
```

## 最佳实践

### 1. 颜色使用规范
- 优先使用语义化的颜色变量（如 `--color-primary`）
- 避免硬编码颜色值
- 确保颜色在所有主题下都有良好的对比度

### 2. 组件设计
- 所有组件都应支持主题切换
- 使用CSS变量而不是固定颜色
- 考虑不同主题下的视觉效果

### 3. 性能优化
- 主题切换使用CSS变量，无需重新渲染组件
- 主题配置缓存在localStorage中
- 避免频繁的主题切换操作

## 故障排除

### 1. 主题不生效
- 检查是否正确引入了 `themes.css`
- 确认CSS变量名称是否正确
- 检查浏览器控制台是否有错误

### 2. 样式异常
- 确认组件使用了正确的CSS变量
- 检查是否有样式覆盖问题
- 验证主题配置是否完整

### 3. 持久化问题
- 检查localStorage是否可用
- 确认主题加载逻辑是否正确执行
- 验证主题名称是否匹配

## 更新日志

### v1.0.0 (2024-01-10)
- ✨ 实现三种预设主题
- ✨ 添加主题切换界面
- ✨ 支持主题持久化
- ✨ 完整的CSS变量系统
- ✨ 未来科技主题特效
- 📝 完善的文档和测试页面