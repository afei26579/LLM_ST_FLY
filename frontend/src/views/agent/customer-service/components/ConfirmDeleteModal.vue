<template>
  <teleport to="body">
    <transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click="handleClose">
        <div class="modal-container" @click.stop>
          <!-- 头部 -->
          <div class="modal-header">
            <div class="header-icon danger">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.46 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
                <path d="M12 9v4"/>
                <path d="m12 17 .01 0"/>
              </svg>
            </div>
            <div class="header-content">
              <h2 class="modal-title">{{ title || '确认删除' }}</h2>
              <p class="modal-subtitle">此操作不可撤销，请谨慎操作</p>
            </div>
            <button @click="handleClose" class="btn-close">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          <!-- 内容 -->
          <div class="modal-body">
            <div class="warning-content">
              <div class="warning-message">
                <p class="primary-message">{{ message }}</p>
                <div v-if="details" class="details-list">
                  <ul>
                    <li v-for="detail in details" :key="detail">{{ detail }}</li>
                  </ul>
                </div>
              </div>
              
              <!-- 危险提示 -->
              <div class="danger-notice">
                <div class="notice-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                </div>
                <span>删除后数据将无法恢复</span>
              </div>
            </div>
          </div>

          <!-- 底部按钮 -->
          <div class="modal-footer">
            <button @click="handleClose" class="btn-cancel">
              <span>取消</span>
            </button>
            <button 
              @click="handleConfirm" 
              :disabled="isDeleting"
              class="btn-danger"
            >
              <span v-if="!isDeleting" class="btn-content">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3,6 5,6 21,6"/>
                  <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1,2-2h4a2,2 0 0,1,2,2v2"/>
                  <line x1="10" y1="11" x2="10" y2="17"/>
                  <line x1="14" y1="11" x2="14" y2="17"/>
                </svg>
                确认删除
              </span>
              <span v-else class="btn-loading">
                <span class="spinner-small"></span>
                删除中...
              </span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  isOpen: boolean
  title?: string
  message: string
  details?: string[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  confirm: []
  cancel: []
}>()

const isDeleting = ref(false)

const handleClose = () => {
  if (isDeleting.value) return
  emit('update:isOpen', false)
  emit('cancel')
}

const handleConfirm = async () => {
  isDeleting.value = true
  
  try {
    emit('confirm')
  } finally {
    // 让父组件控制关闭，这里只重置状态
    isDeleting.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(4px);
}

.modal-container {
  width: 90%;
  max-width: 480px;
  background: var(--color-surface);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  border: 1px solid var(--color-border);
}

/* 动画 */
.modal-enter-active, .modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(-20px);
}

/* 头部 */
.modal-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px 24px 0;
  position: relative;
}

.header-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 4px;
}

.header-icon.danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-error, #ef4444);
}

.header-content {
  flex: 1;
}

.modal-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
  line-height: 1.2;
}

.modal-subtitle {
  margin: 4px 0 0;
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.4;
}

.btn-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.btn-close:hover {
  background: var(--color-background);
  color: var(--color-text);
}

/* 内容 */
.modal-body {
  padding: 24px;
}

.warning-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.warning-message {
  line-height: 1.6;
}

.primary-message {
  margin: 0;
  font-size: 16px;
  color: var(--color-text);
  font-weight: 500;
}

.details-list {
  margin-top: 12px;
}

.details-list ul {
  margin: 0;
  padding-left: 20px;
  color: var(--color-text-secondary);
}

.details-list li {
  margin: 4px 0;
  font-size: 14px;
}

.danger-notice {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: var(--color-error, #ef4444);
  font-size: 14px;
  font-weight: 500;
}

.notice-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 底部 */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 0 24px 24px;
}

.btn-cancel,
.btn-danger {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 100px;
  height: 44px;
}

.btn-cancel {
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover {
  background: var(--color-surface);
  border-color: var(--color-text-secondary);
}

.btn-danger {
  background: var(--color-error, #ef4444);
  color: white;
  border: 1px solid var(--color-error, #ef4444);
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
  border-color: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.btn-danger:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
