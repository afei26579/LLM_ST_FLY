<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="confirm-overlay" @click.self="handleCancel">
        <div class="confirm-dialog">
          <div class="confirm-icon">
            <span class="icon-wrapper">{{ icon }}</span>
          </div>
          <div class="confirm-content">
            <h3 class="confirm-title">{{ title }}</h3>
            <p class="confirm-message">{{ message }}</p>
          </div>
          <div class="confirm-actions">
            <button @click="handleCancel" class="btn-cancel">
              {{ cancelText }}
            </button>
            <button @click="handleConfirm" class="btn-confirm" :class="confirmType">
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  isOpen?: boolean
  title?: string
  message?: string
  icon?: string
  confirmText?: string
  cancelText?: string
  confirmType?: 'primary' | 'danger' | 'warning'
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: false,
  title: '确认操作',
  message: '确定要执行此操作吗？',
  icon: '❓',
  confirmText: '确定',
  cancelText: '取消',
  confirmType: 'primary'
})

const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  'confirm': []
  'cancel': []
}>()

const handleConfirm = () => {
  emit('confirm')
  emit('update:isOpen', false)
}

const handleCancel = () => {
  emit('cancel')
  emit('update:isOpen', false)
}

// 监听 ESC 键关闭
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        handleCancel()
      }
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }
})
</script>

<style scoped>
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.confirm-dialog {
  background: var(--card-background);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  width: 100%;
  max-width: 420px;
  overflow: hidden;
  animation: dialog-appear 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes dialog-appear {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.confirm-icon {
  padding: 32px 32px 16px;
  text-align: center;
}

.icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-surface);
  font-size: 32px;
  animation: icon-bounce 0.5s ease-out;
}

@keyframes icon-bounce {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.confirm-content {
  padding: 0 32px 24px;
  text-align: center;
}

.confirm-title {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.confirm-message {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-textSecondary);
}

.confirm-actions {
  display: flex;
  gap: 12px;
  padding: 20px 32px 32px;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover {
  background: var(--color-background);
  transform: translateY(-1px);
}

.btn-confirm {
  background: var(--button-primary);
  color: var(--button-primaryText);
}

.btn-confirm:hover {
  background: var(--button-primaryHover);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(var(--color-primary-rgb, 94, 155, 255), 0.3);
}

.btn-confirm.danger {
  background: var(--button-error);
  color: var(--button-errorText);
}

.btn-confirm.danger:hover {
  background: var(--button-errorHover);
  box-shadow: 0 6px 20px rgba(var(--color-error-rgb, 248, 113, 113), 0.3);
}

.btn-confirm.warning {
  background: var(--button-warning);
  color: var(--button-warningText);
}

.btn-confirm.warning:hover {
  background: var(--button-warningHover);
  box-shadow: 0 6px 20px rgba(var(--color-warning-rgb, 251, 191, 36), 0.3);
}

/* 动画效果 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .confirm-dialog {
  animation: dialog-appear 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-leave-active .confirm-dialog {
  animation: dialog-disappear 0.2s ease-out;
}

@keyframes dialog-disappear {
  0% {
    opacity: 1;
    transform: scale(1);
  }
  100% {
    opacity: 0;
    transform: scale(0.9);
  }
}

/* 未来科技主题特殊效果 */
:deep(.theme-future) .confirm-dialog {
  box-shadow: 
    0 0 30px rgba(0, 212, 255, 0.15),
    0 0 60px rgba(255, 0, 110, 0.1),
    var(--card-shadow);
}

:deep(.theme-future) .icon-wrapper {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
}
</style>

