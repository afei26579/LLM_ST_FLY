<template>
  <teleport to="body">
    <transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click="handleClose">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2>📚 新建知识库</h2>
            <button @click="handleClose" class="btn-close">✕</button>
          </div>

          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">📝</span>
                知识库名称 <span class="required">*</span>
              </label>
              <input
                v-model="formData.name"
                type="text"
                placeholder="例如：产品知识库"
                class="form-input"
                maxlength="200"
              />
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">📄</span>
                描述
              </label>
              <textarea
                v-model="formData.description"
                placeholder="简要描述此知识库的用途..."
                class="form-textarea"
                rows="3"
              ></textarea>
            </div>

            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">📋</span>
                知识库格式 <span class="required">*</span>
              </label>
              <div class="format-options">
                <label 
                  v-for="format in formatOptions" 
                  :key="format.value"
                  class="format-option"
                  :class="{ active: formData.format === format.value }"
                >
                  <input
                    type="radio"
                    :value="format.value"
                    v-model="formData.format"
                  />
                  <div class="option-content">
                    <div class="option-icon">{{ format.icon }}</div>
                    <div class="option-info">
                      <div class="option-title">{{ format.label }}</div>
                      <div class="option-desc">{{ format.description }}</div>
                      <div class="option-formats">
                        支持：{{ format.formats.join('、') }}
                      </div>
                    </div>
                  </div>
                </label>
              </div>
            </div>

            
          </div>

          <div class="modal-footer">
            <button @click="handleClose" class="btn-cancel">
              取消
            </button>
            <button
              @click="handleSubmit"
              :disabled="!formData.name.trim() || isSubmitting"
              class="btn-submit"
            >
              <span v-if="!isSubmitting">✅ 创建</span>
              <span v-else>
                <span class="spinner-small"></span> 创建中...
              </span>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  submit: [data: { name: string; description: string; format: string }]
}>()

const formData = ref({
  name: '',
  description: '',
  format: 'text'
})

// 格式选项
const formatOptions = [
  {
    value: 'text',
    label: '文本格式',
    icon: '📝',
    description: '适用于纯文本文档、文章、手册等',
    formats: ['TXT', 'MD', 'PDF', 'DOCX']
  },
  {
    value: 'structured',
    label: '结构化格式',
    icon: '📊',
    description: '适用于表格、数据库、API文档等',
    formats: ['CSV', 'JSON', 'XML', 'XLSX', 'HTML']
  },
  {
    value: 'image',
    label: '图片格式',
    icon: '🖼️',
    description: '适用于图表、截图、设计稿等',
    formats: ['PNG', 'JPG', 'JPEG', 'GIF', 'WEBP']
  }
]

const isSubmitting = ref(false)

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    // 弹窗打开时重置表单
    formData.value = {
      name: '',
      description: '',
      format: 'text'
    }
  }
  // 无论打开还是关闭都重置提交状态
  isSubmitting.value = false
})

const handleClose = () => {
  emit('update:isOpen', false)
}

const handleSubmit = () => {
  if (!formData.value.name.trim()) return

  isSubmitting.value = true
  
  // 发送提交事件给父组件
  emit('submit', {
    name: formData.value.name.trim(),
    description: formData.value.description.trim(),
    format: formData.value.format
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-container {
  width: 90%;
  max-width: 600px;
  background: var(--color-surface);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.btn-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 18px;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.btn-close:hover {
  background: var(--color-error, #dc3545);
  color: white;
}

.modal-body {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.label-icon {
  font-size: 16px;
}

.required {
  color: var(--color-error, #dc3545);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--input-border);
  border-radius: 8px;
  background: var(--input-background);
  color: var(--color-text);
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.3s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--button-primary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

/* 格式选择样式 */
.format-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.format-option {
  position: relative;
  display: block;
  cursor: pointer;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  background: var(--input-background);
  transition: all 0.3s;
}

.format-option:hover {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
}

.format-option.active {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.format-option input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.option-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.option-icon {
  font-size: 32px;
  line-height: 1;
  flex-shrink: 0;
}

.option-info {
  flex: 1;
}

.option-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.option-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
  line-height: 1.4;
}

.option-formats {
  font-size: 12px;
  color: var(--button-primary);
  font-weight: 500;
}

.format-option.active .option-title {
  color: var(--button-primary);
}

.format-option.active .option-formats {
  font-weight: 600;
}

.form-info {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: var(--color-primary-alpha);
  border-radius: 8px;
  border-left: 3px solid var(--button-primary);
}

.info-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.info-text {
  flex: 1;
  font-size: 13px;
  color: var(--color-text);
}

.info-text p {
  margin: 0 0 8px;
}

.info-text ul {
  margin: 0;
  padding-left: 20px;
}

.info-text li {
  margin-bottom: 4px;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  background: var(--color-background);
}

.btn-cancel,
.btn-submit {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-cancel {
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover {
  background: var(--color-border);
}

.btn-submit {
  background: var(--button-primary);
  color: var(--button-primaryText);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinner-small {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s, opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
  opacity: 0;
}
</style>

