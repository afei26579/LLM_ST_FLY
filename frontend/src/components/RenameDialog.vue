<template>
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div v-if="visible" class="dialog-overlay" @click="handleOverlayClick">
        <div class="dialog-container" @click.stop>
          <div class="dialog-header">
            <h3 class="dialog-title">重命名对话</h3>
            <button class="close-btn" @click="handleCancel">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <div class="dialog-body">
            <label for="conversation-title" class="input-label">新标题</label>
            <input
              id="conversation-title"
              ref="inputRef"
              v-model="inputValue"
              type="text"
              class="dialog-input"
              placeholder="请输入新的对话标题"
              @keydown.enter="handleConfirm"
              @keydown.esc="handleCancel"
              maxlength="100"
            />
            <div class="input-hint">{{ inputValue.length }}/100</div>
          </div>
          
          <div class="dialog-footer">
            <button class="dialog-btn dialog-btn-cancel" @click="handleCancel">
              取消
            </button>
            <button 
              class="dialog-btn dialog-btn-confirm" 
              @click="handleConfirm"
              :disabled="!inputValue.trim()"
            >
              确认
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

interface Props {
  visible: boolean
  title: string
  defaultValue?: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'confirm', value: string): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  defaultValue: ''
})

const emit = defineEmits<Emits>()

const inputValue = ref('')
const inputRef = ref<HTMLInputElement | null>(null)

// 监听弹窗显示，重置输入值并聚焦
watch(() => props.visible, (newVal) => {
  if (newVal) {
    inputValue.value = props.defaultValue
    nextTick(() => {
      inputRef.value?.focus()
      inputRef.value?.select()
    })
  }
})

const handleConfirm = () => {
  const trimmedValue = inputValue.value.trim()
  if (trimmedValue) {
    emit('confirm', trimmedValue)
    emit('update:visible', false)
  }
}

const handleCancel = () => {
  emit('cancel')
  emit('update:visible', false)
}

const handleOverlayClick = () => {
  handleCancel()
}
</script>

<style scoped>
/* 遮罩层 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

/* 弹窗容器 */
.dialog-container {
  width: 100%;
  max-width: 480px;
  background: var(--card-background, #1e293b);
  border: 1px solid var(--card-border, #334155);
  border-radius: 16px;
  box-shadow: var(--card-shadow, 0 10px 15px -3px rgba(0, 0, 0, 0.3));
  overflow: hidden;
  animation: dialogSlideIn 0.3s ease-out;
}

@keyframes dialogSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* 弹窗头部 */
.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--card-border, #334155);
  background: var(--surface, #1e293b);
}

.dialog-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text, #e1e6f5);
  background: linear-gradient(90deg, var(--color-primary, #5e9bff), var(--color-accent, #a569ff));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--color-textSecondary, #94a3b8);
  cursor: pointer;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text, #e1e6f5);
}

/* 弹窗主体 */
.dialog-body {
  padding: 24px;
}

.input-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text, #e1e6f5);
}

.dialog-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 15px;
  color: var(--color-text, #e1e6f5);
  background: var(--surface, #1e293b);
  border: 2px solid var(--card-border, #334155);
  border-radius: 10px;
  outline: none;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.dialog-input:focus {
  border-color: var(--color-primary, #5e9bff);
  box-shadow: 0 0 0 3px rgba(94, 155, 255, 0.1);
}

.dialog-input::placeholder {
  color: var(--color-textSecondary, #94a3b8);
}

.input-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-textSecondary, #94a3b8);
  text-align: right;
}

/* 弹窗底部 */
.dialog-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: var(--surface, #1e293b);
  border-top: 1px solid var(--card-border, #334155);
}

.dialog-btn {
  flex: 1;
  padding: 10px 20px;
  font-size: 15px;
  font-weight: 500;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.dialog-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.dialog-btn:active::before {
  width: 300px;
  height: 300px;
}

.dialog-btn-cancel {
  background: transparent;
  color: var(--color-textSecondary, #94a3b8);
  border: 2px solid var(--card-border, #334155);
}

.dialog-btn-cancel:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--color-textSecondary, #94a3b8);
  color: var(--color-text, #e1e6f5);
}

.dialog-btn-confirm {
  background: var(--button-primary, linear-gradient(90deg, #5e9bff, #a569ff));
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(94, 155, 255, 0.3);
}

.dialog-btn-confirm:hover {
  background: var(--button-primaryHover, linear-gradient(90deg, #4f8aff, #9456ff));
  box-shadow: 0 6px 16px rgba(94, 155, 255, 0.4);
  transform: translateY(-1px);
}

.dialog-btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 过渡动画 */
.dialog-fade-enter-active,
.dialog-fade-leave-active {
  transition: opacity 0.3s ease;
}

.dialog-fade-enter-from,
.dialog-fade-leave-to {
  opacity: 0;
}

.dialog-fade-enter-active .dialog-container {
  animation: dialogSlideIn 0.3s ease-out;
}

.dialog-fade-leave-active .dialog-container {
  animation: dialogSlideOut 0.3s ease-out;
}

@keyframes dialogSlideOut {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
}

/* 未来科技主题特效 */
:global(.theme-future) .dialog-container {
  background: linear-gradient(135deg, #1e1b3a 0%, #2d1b4e 50%, #1b2942 100%);
  border: 1px solid rgba(0, 245, 255, 0.3);
  box-shadow: 
    0 0 25px rgba(0, 245, 255, 0.15),
    0 0 50px rgba(255, 0, 128, 0.08),
    0 8px 32px rgba(0, 0, 0, 0.4);
}

:global(.theme-future) .dialog-header,
:global(.theme-future) .dialog-footer {
  background: linear-gradient(135deg, #1a1733 0%, #281a42 50%, #1a2438 100%);
  border-color: rgba(0, 245, 255, 0.2);
}

:global(.theme-future) .dialog-input {
  background: linear-gradient(135deg, #1a1733 0%, #281a42 100%);
  border-color: rgba(0, 245, 255, 0.3);
}

:global(.theme-future) .dialog-input:focus {
  border-color: #00f5ff;
  box-shadow: 
    0 0 0 3px rgba(0, 245, 255, 0.1),
    0 0 20px rgba(0, 245, 255, 0.2);
}

:global(.theme-future) .dialog-btn-confirm {
  background: linear-gradient(90deg, #00f5ff 0%, #9d4edd 50%, #ff0080 100%);
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.4);
}

:global(.theme-future) .dialog-btn-confirm:hover {
  background: linear-gradient(90deg, #00d4ff 0%, #8b3fd9 50%, #e6006b 100%);
  box-shadow: 0 0 30px rgba(0, 245, 255, 0.6);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dialog-container {
    max-width: 100%;
    margin: 0 16px;
  }
  
  .dialog-header,
  .dialog-body,
  .dialog-footer {
    padding: 16px;
  }
}
</style>

