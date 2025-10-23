<template>
  <teleport to="body">
    <transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click="handleClose">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h2>🤖 新建客服助手</h2>
            <button @click="handleClose" class="btn-close">✕</button>
          </div>

          <div class="modal-body">
            <!-- 基本信息 -->
            <div class="form-section">
              <h3 class="section-title">基本信息</h3>
              
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">📝</span>
                  助手名称 <span class="required">*</span>
                </label>
                <input
                  v-model="formData.name"
                  type="text"
                  placeholder="例如：产品客服、售后支持"
                  class="form-input"
                  maxlength="200"
                />
              </div>

              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">😊</span>
                  头像
                </label>
                <div class="avatar-selector">
                  <button
                    v-for="emoji in avatarOptions"
                    :key="emoji"
                    :class="['avatar-option', { selected: formData.avatar === emoji }]"
                    @click="formData.avatar = emoji"
                  >
                    {{ emoji }}
                  </button>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">📄</span>
                  描述
                </label>
                <textarea
                  v-model="formData.description"
                  placeholder="简要描述此助手的职责和特点..."
                  class="form-textarea"
                  rows="2"
                ></textarea>
              </div>

              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">💬</span>
                  开场白 <span class="required">*</span>
                </label>
                <textarea
                  v-model="formData.greeting_message"
                  placeholder="例如：您好！我是产品客服助手，有什么可以帮您？"
                  class="form-textarea"
                  rows="2"
                ></textarea>
              </div>

              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">🎯</span>
                  系统提示词
                </label>
                <textarea
                  v-model="formData.system_prompt"
                  placeholder="定义AI的行为、语气和专业领域...&#10;例如：你是专业的售后客服，需要耐心、友好地解答用户问题..."
                  class="form-textarea"
                  rows="4"
                ></textarea>
              </div>
            </div>

            <!-- 知识库配置 -->
            <div class="form-section">
              <h3 class="section-title">知识库配置</h3>
              
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">📚</span>
                  关联知识库
                </label>
                <div class="kb-selector">
                  <div v-if="availableKnowledgeBases.length === 0" class="no-kb">
                    <p>暂无可用知识库</p>
                    <button @click="$emit('create-kb')" class="btn-create-kb">
                      创建知识库
                    </button>
                  </div>
                  <div v-else class="kb-checkboxes">
                    <label
                      v-for="kb in availableKnowledgeBases"
                      :key="kb.id"
                      class="kb-checkbox"
                    >
                      <input
                        type="checkbox"
                        :value="kb.id"
                        v-model="formData.knowledge_bases"
                      />
                      <span class="kb-label">
                        <span class="kb-name">{{ kb.name }}</span>
                        <span class="kb-meta">{{ kb.chunk_count || 0 }} 切片</span>
                      </span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- AI参数配置 -->
            <div class="form-section">
              <h3 class="section-title">AI参数配置</h3>
              
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">
                    <span class="label-icon">🧠</span>
                    AI模型
                  </label>
                  <select v-model="formData.model" class="form-select">
                    <option value="qwen-turbo">Qwen Turbo - 快速</option>
                    <option value="qwen-plus">Qwen Plus - 平衡</option>
                    <option value="qwen-max">Qwen Max - 高质量</option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">
                    <span class="label-icon">🎲</span>
                    创造性 ({{ formData.temperature.toFixed(1) }})
                  </label>
                  <input
                    v-model.number="formData.temperature"
                    type="range"
                    min="0"
                    max="2"
                    step="0.1"
                    class="form-range"
                  />
                  <div class="range-labels">
                    <span>保守</span>
                    <span>创新</span>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">🔍</span>
                  检索数量 (Top-K)
                </label>
                <input
                  v-model.number="formData.top_k"
                  type="number"
                  min="1"
                  max="20"
                  class="form-input"
                />
                <p class="form-hint">从知识库检索的切片数量（1-20）</p>
              </div>
            </div>

            <!-- 功能开关 -->
            <div class="form-section">
              <h3 class="section-title">功能开关</h3>
              
              <div class="switch-group">
                <label class="switch-item">
                  <input type="checkbox" v-model="formData.enable_knowledge_base" />
                  <span class="switch-slider"></span>
                  <span class="switch-label">
                    <span class="switch-icon">📚</span>
                    启用知识库检索
                  </span>
                </label>

                <label class="switch-item">
                  <input type="checkbox" v-model="formData.enable_order_query" />
                  <span class="switch-slider"></span>
                  <span class="switch-label">
                    <span class="switch-icon">📦</span>
                    启用订单查询
                  </span>
                </label>

                <label class="switch-item">
                  <input type="checkbox" v-model="formData.enable_human_handoff" />
                  <span class="switch-slider"></span>
                  <span class="switch-label">
                    <span class="switch-icon">🙋</span>
                    启用人工转接
                  </span>
                </label>

                <label class="switch-item">
                  <input type="checkbox" v-model="formData.is_default" />
                  <span class="switch-slider"></span>
                  <span class="switch-label">
                    <span class="switch-icon">⭐</span>
                    设为默认助手
                  </span>
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
              :disabled="!isFormValid || isSubmitting"
              class="btn-submit"
            >
              <span v-if="!isSubmitting">✅ 创建助手</span>
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
import { ref, computed, watch } from 'vue'

interface KnowledgeBase {
  id: number
  name: string
  chunk_count: number
  status: string
}

interface Props {
  isOpen: boolean
  availableKnowledgeBases: KnowledgeBase[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:isOpen': [value: boolean]
  submit: [data: any]
  'create-kb': []
}>()

const avatarOptions = ['🤖', '👨‍💼', '👩‍💼', '🛠️', '📞', '💬', '🎯', '⚡']

const formData = ref({
  name: '',
  description: '',
  avatar: '🤖',
  greeting_message: '您好！我是智能客服助手，有什么可以帮您的吗？',
  system_prompt: '',
  knowledge_bases: [] as number[],
  model: 'qwen-plus',
  temperature: 0.7,
  top_k: 3,
  enable_knowledge_base: true,
  enable_order_query: true,
  enable_human_handoff: true,
  is_default: false
})

const isSubmitting = ref(false)

const isFormValid = computed(() => {
  return formData.value.name.trim() && formData.value.greeting_message.trim()
})

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    // 弹窗打开时重置表单
    formData.value = {
      name: '',
      description: '',
      avatar: '🤖',
      greeting_message: '您好！我是智能客服助手，有什么可以帮您的吗？',
      system_prompt: '',
      knowledge_bases: [],
      model: 'qwen-plus',
      temperature: 0.7,
      top_k: 3,
      enable_knowledge_base: true,
      enable_order_query: true,
      enable_human_handoff: true,
      is_default: false
    }
  }
  // 无论打开还是关闭都重置提交状态
  isSubmitting.value = false
})

const handleClose = () => {
  emit('update:isOpen', false)
}

const handleSubmit = () => {
  if (!isFormValid.value) return

  isSubmitting.value = true
  
  // 发送提交事件给父组件
  emit('submit', { ...formData.value })
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
  max-width: 700px;
  max-height: 90vh;
  background: var(--color-surface);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
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
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.form-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--color-border);
}

.form-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.form-group {
  margin-bottom: 16px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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
.form-textarea,
.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--input-border);
  border-radius: 8px;
  background: var(--input-background);
  color: var(--color-text);
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.3s;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: var(--button-primary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.form-textarea {
  resize: vertical;
}

.form-hint {
  margin: 6px 0 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.avatar-selector {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
}

.avatar-option {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.avatar-option:hover {
  border-color: var(--button-primary);
  transform: scale(1.1);
}

.avatar-option.selected {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.form-range {
  width: 100%;
  margin: 8px 0;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.kb-selector {
  padding: 12px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.no-kb {
  text-align: center;
  padding: 20px;
  color: var(--color-text-secondary);
}

.btn-create-kb {
  margin-top: 12px;
  padding: 8px 16px;
  background: var(--button-secondary);
  color: var(--button-secondaryText);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.btn-create-kb:hover {
  box-shadow: var(--button-shadow);
}

.kb-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.kb-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.kb-checkbox:hover {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
}

.kb-checkbox input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.kb-label {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.kb-name {
  font-weight: 500;
  color: var(--color-text);
}

.kb-meta {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.switch-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.switch-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.switch-item:hover {
  background: var(--color-primary-alpha);
}

.switch-item input[type="checkbox"] {
  display: none;
}

.switch-slider {
  position: relative;
  width: 44px;
  height: 24px;
  background: var(--color-border);
  border-radius: 12px;
  transition: background 0.3s;
  flex-shrink: 0;
}

.switch-slider::before {
  content: '';
  position: absolute;
  width: 18px;
  height: 18px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s;
}

.switch-item input:checked + .switch-slider {
  background: var(--button-primary);
}

.switch-item input:checked + .switch-slider::before {
  transform: translateX(20px);
}

.switch-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text);
  flex: 1;
}

.switch-icon {
  font-size: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  background: var(--color-background);
  flex-shrink: 0;
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
  margin-right: 6px;
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

/* 滚动条样式 */
.modal-body::-webkit-scrollbar,
.kb-selector::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track,
.kb-selector::-webkit-scrollbar-track {
  background: var(--color-background);
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb,
.kb-selector::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 3px;
}
</style>

