# CustomSelect 自定义下拉组件

## 📋 组件概述

`CustomSelect.vue` 是一个完全自定义的下拉选择组件，用于替代原生的 `<select>` 元素。完美适配项目的三种主题（light、dark、future），提供一致的用户体验。

## ✨ 特性

- ✅ 完全自定义样式，不受浏览器原生限制
- ✅ 完美适配 light、dark、future 三种主题
- ✅ 支持 v-model 双向绑定
- ✅ 下拉动画效果
- ✅ 点击外部自动关闭
- ✅ 自定义滚动条样式
- ✅ 活跃选项高亮显示
- ✅ Hover 交互效果
- ✅ TypeScript 类型支持

## 📦 基本用法

```vue
<template>
  <CustomSelect 
    v-model="selectedValue"
    :options="options"
    placeholder="请选择"
  />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CustomSelect from '@/components/CustomSelect.vue'

const selectedValue = ref('option1')

const options = [
  { value: 'option1', label: '选项 1' },
  { value: 'option2', label: '选项 2' },
  { value: 'option3', label: '选项 3' }
]
</script>
```

## 🔧 Props

| 属性 | 类型 | 必填 | 默认值 | 说明 |
|-----|------|-----|--------|-----|
| `modelValue` | `string` | ✅ | - | 当前选中的值（v-model） |
| `options` | `SelectOption[]` | ✅ | - | 选项数组 |
| `placeholder` | `string` | ❌ | '请选择' | 未选中时的占位文本 |

### SelectOption 类型

```typescript
interface SelectOption {
  value: string  // 选项的值
  label: string  // 选项的显示文本
}
```

## 📤 Events

| 事件名 | 参数 | 说明 |
|--------|-----|------|
| `update:modelValue` | `value: string` | 选中值变化时触发 |

## 🎨 主题适配

组件使用 CSS 变量自动适配主题，无需额外配置：

- `--card-background` - 背景色
- `--color-text` - 文字颜色
- `--color-border` - 边框颜色
- `--color-primary` - 主题色
- `--color-primary-alpha` - 半透明主题色
- `--card-shadow` - 阴影效果

## 💡 实际应用示例

### 在 AI 音频页面中的使用

```vue
<template>
  <!-- 语音类型选择 -->
  <div class="setting-group">
    <label>语音类型：</label>
    <CustomSelect 
      v-model="textToSpeechForm.voice"
      :options="voiceOptions"
    />
  </div>
</template>

<script setup lang="ts">
const voiceOptions = [
  { value: 'Cherry', label: '芊悦 - 阳光积极、亲切自然小姐姐' },
  { value: 'Ethan', label: '晨煦 - 阳光、温暖、活力、朝气' },
  // ... 更多选项
]

const textToSpeechForm = reactive({
  voice: 'Cherry'
})
</script>
```

## 🎯 功能详解

### 1. 双向绑定

组件支持 `v-model`，当选中值改变时自动触发更新：

```vue
<CustomSelect v-model="myValue" :options="myOptions" />
```

### 2. 点击外部关闭

组件自动监听全局点击事件，点击组件外部区域时自动关闭下拉菜单。

### 3. 键盘导航

组件内部使用标准的 button 元素，支持键盘 Tab 导航。

### 4. 下拉动画

使用 Vue 的 `<transition>` 组件实现平滑的展开/收起动画：

```css
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}
```

### 5. 活跃选项高亮

当前选中的选项会自动高亮显示，使用主题色标识。

## 🔄 与原生 select 的对比

| 特性 | 原生 select | CustomSelect |
|-----|-----------|--------------|
| 样式定制 | ❌ 受限 | ✅ 完全自定义 |
| 主题适配 | ❌ 困难 | ✅ 完美适配 |
| 下拉样式 | ❌ 浏览器控制 | ✅ 完全可控 |
| 动画效果 | ❌ 无 | ✅ 流畅动画 |
| 滚动条样式 | ❌ 系统默认 | ✅ 自定义样式 |
| 跨浏览器一致性 | ❌ 差异大 | ✅ 完全一致 |

## 🎨 样式定制

如需进一步定制样式，可以在父组件中覆盖以下类：

```vue
<style scoped>
/* 覆盖触发按钮样式 */
:deep(.select-trigger) {
  /* 自定义样式 */
}

/* 覆盖下拉项样式 */
:deep(.dropdown-item) {
  /* 自定义样式 */
}
</style>
```

## 📱 响应式设计

组件自动适应父容器宽度（`width: 100%`），并支持移动端触摸操作。

## ⚠️ 注意事项

1. **选项数量**：如果选项过多（超过10个），建议添加搜索功能
2. **长文本**：选项文本过长会自动省略（`text-overflow: ellipsis`）
3. **z-index**：下拉菜单 z-index 为 1000，确保不会被其他元素遮挡

## 🔧 后续扩展建议

如需更多功能，可以考虑添加：

- ✨ 搜索过滤功能
- ✨ 多选支持
- ✨ 分组选项
- ✨ 自定义选项渲染
- ✨ 键盘上下键导航
- ✨ 禁用状态
- ✨ 加载状态

## 📝 更新日志

### v1.0.0 (2025-10-16)
- ✅ 初始版本发布
- ✅ 支持基本的单选功能
- ✅ 完美适配三种主题
- ✅ 在 AI 音频页面中使用

---

**创建时间**: 2025-10-16  
**作者**: AI Assistant  
**文件路径**: `frontend/src/components/CustomSelect.vue`

