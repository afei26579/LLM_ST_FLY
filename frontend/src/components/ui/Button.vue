<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="loading-spinner"></span>
    <slot v-if="!loading"></slot>
    <span v-if="loading && loadingText">{{ loadingText }}</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'ghost' | 'outline'
  size?: 'small' | 'medium' | 'large'
  disabled?: boolean
  loading?: boolean
  loadingText?: string
  block?: boolean
  rounded?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  disabled: false,
  loading: false,
  loadingText: '',
  block: false,
  rounded: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const buttonClasses = computed(() => {
  return [
    'btn',
    `btn-${props.variant}`,
    `btn-${props.size}`,
    {
      'btn-disabled': props.disabled,
      'btn-loading': props.loading,
      'btn-block': props.block,
      'btn-rounded': props.rounded
    }
  ]
})

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>

<style scoped>
/* 基础按钮样式 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  text-align: center;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  border: 1px solid transparent;
  transition: all 0.2s ease-in-out;
  text-decoration: none;
  outline: none;
  position: relative;
  overflow: hidden;
}

.btn:focus {
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb, 59, 130, 246), 0.2);
}

/* 尺寸变体 */
.btn-small {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  line-height: 1.25rem;
  border-radius: 0.375rem;
}

.btn-medium {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  line-height: 1.5rem;
  border-radius: 0.5rem;
}

.btn-large {
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
  line-height: 1.75rem;
  border-radius: 0.75rem;
}

/* 主要按钮 */
.btn-primary {
  background: var(--button-primary);
  color: var(--button-primaryText);
  border-color: var(--button-primary);
}

.btn-primary:hover:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-primaryHover);
  border-color: var(--button-primaryHover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb, 59, 130, 246), 0.3);
}

.btn-primary:active:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-primaryActive);
  border-color: var(--button-primaryActive);
  transform: translateY(0);
}

/* 次要按钮 */
.btn-secondary {
  background: var(--button-secondary);
  color: var(--button-secondaryText);
  border-color: var(--button-secondary);
}

.btn-secondary:hover:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-secondaryHover);
  border-color: var(--button-secondaryHover);
  transform: translateY(-1px);
}

.btn-secondary:active:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-secondaryActive);
  border-color: var(--button-secondaryActive);
  transform: translateY(0);
}

/* 成功按钮 */
.btn-success {
  background: var(--button-success);
  color: var(--button-successText);
  border-color: var(--button-success);
}

.btn-success:hover:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-successHover);
  border-color: var(--button-successHover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-success-rgb, 34, 197, 94), 0.3);
}

.btn-success:active:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-successActive);
  border-color: var(--button-successActive);
  transform: translateY(0);
}

/* 警告按钮 */
.btn-warning {
  background: var(--button-warning);
  color: var(--button-warningText);
  border-color: var(--button-warning);
}

.btn-warning:hover:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-warningHover);
  border-color: var(--button-warningHover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-warning-rgb, 251, 191, 36), 0.3);
}

.btn-warning:active:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-warningActive);
  border-color: var(--button-warningActive);
  transform: translateY(0);
}

/* 错误按钮 */
.btn-error {
  background: var(--button-error);
  color: var(--button-errorText);
  border-color: var(--button-error);
}

.btn-error:hover:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-errorHover);
  border-color: var(--button-errorHover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-error-rgb, 239, 68, 68), 0.3);
}

.btn-error:active:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-errorActive);
  border-color: var(--button-errorActive);
  transform: translateY(0);
}

/* 信息按钮 */
.btn-info {
  background: var(--button-info);
  color: var(--button-infoText);
  border-color: var(--button-info);
}

.btn-info:hover:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-infoHover);
  border-color: var(--button-infoHover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-info-rgb, 56, 189, 248), 0.3);
}

.btn-info:active:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-infoActive);
  border-color: var(--button-infoActive);
  transform: translateY(0);
}

/* 幽灵按钮 */
.btn-ghost {
  background: var(--button-ghost);
  color: var(--button-ghostText);
  border-color: var(--button-ghostBorder);
}

.btn-ghost:hover:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-ghostHover);
  color: var(--button-ghostText);
  transform: translateY(-1px);
}

.btn-ghost:active:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-ghostActive);
  transform: translateY(0);
}

/* 轮廓按钮 */
.btn-outline {
  background: var(--button-outline);
  color: var(--button-outlineText);
  border-color: var(--button-outlineBorder);
}

.btn-outline:hover:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-outlineHover);
  color: var(--button-outlineHoverText);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb, 59, 130, 246), 0.2);
}

.btn-outline:active:not(.btn-disabled):not(.btn-loading) {
  background: var(--button-outlineActive);
  transform: translateY(0);
}

/* 禁用状态 */
.btn-disabled {
  background: var(--button-primaryDisabled) !important;
  color: var(--button-disabledText) !important;
  border-color: var(--button-primaryDisabled) !important;
  cursor: not-allowed !important;
  opacity: 0.6;
  transform: none !important;
  box-shadow: none !important;
}

/* 加载状态 */
.btn-loading {
  cursor: wait;
  opacity: 0.8;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 块级按钮 */
.btn-block {
  display: flex;
  width: 100%;
}

/* 圆角按钮 */
.btn-rounded {
  border-radius: 9999px;
}

/* 未来科技主题特殊效果 */
.theme-future .btn:not(.btn-disabled):not(.btn-loading):hover {
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.3),
    0 4px 12px rgba(0, 0, 0, 0.2);
}

.theme-future .btn-primary:not(.btn-disabled):not(.btn-loading):hover {
  box-shadow: 
    0 0 25px rgba(0, 212, 255, 0.4),
    0 0 50px rgba(124, 58, 237, 0.2);
}

.theme-future .btn-success:not(.btn-disabled):not(.btn-loading):hover {
  box-shadow: 
    0 0 25px rgba(0, 255, 136, 0.4),
    0 4px 12px rgba(0, 0, 0, 0.2);
}

.theme-future .btn-error:not(.btn-disabled):not(.btn-loading):hover {
  box-shadow: 
    0 0 25px rgba(255, 0, 85, 0.4),
    0 4px 12px rgba(0, 0, 0, 0.2);
}

.theme-future .btn-warning:not(.btn-disabled):not(.btn-loading):hover {
  box-shadow: 
    0 0 25px rgba(255, 170, 0, 0.4),
    0 4px 12px rgba(0, 0, 0, 0.2);
}

/* 响应式设计 */
@media (max-width: 640px) {
  .btn-large {
    padding: 0.625rem 1.25rem;
    font-size: 1rem;
  }
  
  .btn-medium {
    padding: 0.5rem 0.875rem;
    font-size: 0.875rem;
  }
  
  .btn-small {
    padding: 0.375rem 0.625rem;
    font-size: 0.8125rem;
  }
}
</style>