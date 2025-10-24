<template>
  <div class="create-assistant-form">
    <div class="form-header">
      <div class="header-left">
        <button @click="$emit('cancel')" class="btn-back">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回
        </button>
        <h2>🤖 创建智能助手</h2>
      </div>

      <!-- 步骤导航 -->
      <div class="steps-nav">
        <div :class="['step-item', { active: currentStep === 'basic', completed: currentStep === 'ai-params' || currentStep === 'conversation' }]">
          <div class="step-circle">{{ currentStep === 'ai-params' || currentStep === 'conversation' ? '✓' : '1' }}</div>
          <div class="step-label">基本信息</div>
        </div>
        <div class="step-line"></div>
        <div :class="['step-item', { active: currentStep === 'ai-params', completed: currentStep === 'conversation' }]">
          <div class="step-circle">{{ currentStep === 'conversation' ? '✓' : '2' }}</div>
          <div class="step-label">AI参数</div>
        </div>
        <div class="step-line"></div>
        <div :class="['step-item', { active: currentStep === 'conversation' }]">
          <div class="step-circle">3</div>
          <div class="step-label">对话配置</div>
        </div>
      </div>
    </div>

    <div class="form-content">
      <!-- 第一步：基本信息 -->
      <div v-if="currentStep === 'basic'" class="form-section">
        
        <div class="form-group">
          <label class="required">助手名称</label>
          <input
            v-model="formData.name"
            type="text"
            placeholder="例如：产品客服助手"
            maxlength="30"
            class="form-input"
          />
          <span class="char-count">{{ formData.name.length }}/30</span>
        </div>

        <div class="form-group">
          <label class="required">助手头像</label>
          <div class="avatar-selector">
            <button
              v-for="emoji in avatarOptions"
              :key="emoji"
              :class="['avatar-option', { selected: formData.avatar === emoji }]"
              @click="formData.avatar = emoji"
              type="button"
            >
              {{ emoji }}
            </button>
          </div>
        </div>

        <!-- 知识库关联 -->
        <div class="form-group">
          <label>关联知识库</label>
          <div class="kb-selector-box">
            <div v-if="availableKnowledgeBases.length > 0" class="kb-list">
              <div
                v-for="kb in availableKnowledgeBases"
                :key="kb.id"
                class="kb-item"
              >
                <label class="kb-checkbox">
                  <input
                    type="checkbox"
                    :value="kb.id"
                    v-model="formData.knowledge_base_ids"
                  />
                  <span class="checkbox-custom"></span>
                  <div class="kb-info">
                    <div class="kb-name">📚 {{ kb.name }}</div>
                    <div class="kb-meta">
                      文档: {{ kb.document_count || 0 }} | 切片: {{ kb.chunk_count || 0 }}
                    </div>
                  </div>
                </label>
              </div>
            </div>
            <div v-else class="empty-kb">
              <p>暂无可用知识库</p>
              <button @click="$emit('create-kb')" class="btn-create-kb">
                创建知识库
              </button>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>助手描述</label>
          <textarea
            v-model="formData.description"
            placeholder="简要描述该助手的功能和特点..."
            maxlength="100"
            rows="3"
            class="form-textarea"
          ></textarea>
          <span class="char-count">{{ formData.description.length }}/100</span>
        </div>
      </div>

      <!-- 第二步：AI参数 -->
      <div v-if="currentStep === 'ai-params'" class="form-section">
        <h3>⚙️ AI参数</h3>
        
        <div class="form-group">
          <label class="required">开场白</label>
          <textarea
            v-model="formData.greeting_message"
            @input="handleGreetingInput"
            placeholder="欢迎语，用户开始对话时显示..."
            maxlength="200"
            rows="3"
            class="form-textarea"
          ></textarea>
          <div class="input-footer">
            <small class="input-hint">💡 开场白会根据助手名称自动生成，您也可以自定义</small>
            <span class="char-count-inline">{{ formData.greeting_message.length }}/200</span>
          </div>
        </div>

        <div class="form-group">
          <label>系统提示词</label>
          <textarea
            v-model="formData.system_prompt"
            placeholder="定义助手的角色、专业领域和回答风格..."
            maxlength="500"
            rows="5"
            class="form-textarea"
          ></textarea>
          <span class="char-count">{{ formData.system_prompt.length }}/500</span>
        </div>
      </div>

      <!-- 第三步：对话配置 -->
      <div v-if="currentStep === 'conversation'" class="form-section">
        <h3>💬 对话配置</h3>
        
        <div class="form-group">
          <label>模型选择</label>
          <select v-model="formData.model" class="form-select">
            <option value="qwen-turbo">Turbo (快速响应)</option>
            <option value="qwen-plus">Plus (平衡性能)</option>
            <option value="qwen-max">Max (最佳效果)</option>
          </select>
        </div>

        <div class="form-group">
          <label>温度参数: {{ formData.temperature }}</label>
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
            <span>创造</span>
          </div>
        </div>

        <div class="form-group">
          <label>检索数量 (Top-K)</label>
          <input
            v-model.number="formData.top_k"
            type="number"
            min="1"
            max="10"
            class="form-input"
          />
        </div>
      </div>

      <!-- 功能开关 -->
      <!--div class="form-section">
        <h3>功能模块</h3>
        
        <div class="switches">
          <label class="switch-item">
            <input type="checkbox" v-model="formData.enable_knowledge_base" />
            <span class="switch-custom"></span>
            <div class="switch-info">
              <div class="switch-name">知识库检索</div>
              <div class="switch-desc">从关联的知识库中检索相关信息</div>
            </div>
          </label>

          <label class="switch-item">
            <input type="checkbox" v-model="formData.enable_order_query" />
            <span class="switch-custom"></span>
            <div class="switch-info">
              <div class="switch-name">订单查询</div>
              <div class="switch-desc">支持查询订单状态和物流信息</div>
            </div>
          </label>

          <label class="switch-item">
            <input type="checkbox" v-model="formData.enable_human_handoff" />
            <span class="switch-custom"></span>
            <div class="switch-info">
              <div class="switch-name">人工转接</div>
              <div class="switch-desc">复杂问题自动转接人工客服</div>
            </div>
          </label>

          <label class="switch-item">
            <input type="checkbox" v-model="formData.is_default" />
            <span class="switch-custom"></span>
            <div class="switch-info">
              <div class="switch-name">设为默认助手</div>
              <div class="switch-desc">用户访问时默认使用此助手</div>
            </div>
          </label>
        </div>
      </div-->
    </div>

    <div class="form-footer">
      <div class="footer-left">
        <button
          v-if="currentStep !== 'basic'"
          @click="prevStep"
          class="btn-secondary"
        >
          上一步
        </button>
      </div>
      <div class="footer-right">
        <button
          @click="$emit('cancel')"
          class="btn-cancel"
        >
          取消
        </button>
        <button
          v-if="currentStep !== 'conversation'"
          @click="nextStep"
          :disabled="!canProceed"
          class="btn-primary"
        >
          下一步
        </button>
        <button
          v-else
          @click="handleSubmit"
          :disabled="!isValid || loading"
          class="btn-primary"
        >
          <span v-if="!loading">创建助手</span>
          <span v-else>创建中...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

interface KnowledgeBase {
  id: number
  name: string
  document_count: number
  chunk_count: number
  status: string
}

const props = defineProps<{
  availableKnowledgeBases: KnowledgeBase[]
}>()

const emit = defineEmits<{
  submit: [data: any]
  cancel: []
  'create-kb': []
}>()

const loading = ref(false)
const currentStep = ref('basic')
const greetingEdited = ref(false) // 标记开场白是否被手动编辑过

const steps = [
  { id: 'basic', title: '基本信息', desc: '设置助手名称和头像' },
  { id: 'ai-params', title: 'AI参数', desc: '配置模型和参数' },
  { id: 'conversation', title: '对话配置', desc: '设置对话和功能' }
]

const avatarOptions = ['🤖', '👨‍💼', '👩‍💼', '🎯', '📱', '💬', '🎓', '⚡']

const formData = ref({
  name: '',
  avatar: '🤖',
  description: '',
  greeting_message: '',
  system_prompt: '你是一个专业、友好的客服助手。请基于用户问题提供准确、详细的回答。',
  knowledge_base_ids: [] as number[],
  model: 'qwen-plus',
  temperature: 0.7,
  top_k: 3
})

const isValid = computed(() => {
  return formData.value.name.trim().length > 0 &&
         formData.value.greeting_message.trim().length > 0
})

const canProceed = computed(() => {
  if (currentStep.value === 'basic') {
    return formData.value.name.trim().length > 0
  }
  return true
})

const nextStep = () => {
  const stepIndex = steps.findIndex(s => s.id === currentStep.value)
  if (stepIndex < steps.length - 1) {
    currentStep.value = steps[stepIndex + 1].id
  }
}

const prevStep = () => {
  const stepIndex = steps.findIndex(s => s.id === currentStep.value)
  if (stepIndex > 0) {
    currentStep.value = steps[stepIndex - 1].id
  }
}

const handleSubmit = () => {
  if (!isValid.value || loading.value) return
  
  loading.value = true
  emit('submit', {
    ...formData.value,
    name: formData.value.name.trim(),
    description: formData.value.description.trim(),
    greeting_message: formData.value.greeting_message.trim(),
    system_prompt: formData.value.system_prompt.trim()
  })
  
  setTimeout(() => {
    loading.value = false
  }, 2000)
}

// 生成默认开场白
const generateDefaultGreeting = (name: string) => {
  return name.trim() ? `您好！我是${name.trim()}，有什么可以帮您的吗？` : ''
}

// 监听助手名称变化，自动更新开场白
watch(() => formData.value.name, (newName) => {
  // 只在开场白未被手动编辑时自动更新
  if (!greetingEdited.value) {
    formData.value.greeting_message = generateDefaultGreeting(newName)
  }
})

// 监听开场白输入框的手动编辑
const handleGreetingInput = () => {
  const currentGreeting = formData.value.greeting_message
  const expectedGreeting = generateDefaultGreeting(formData.value.name)
  
  // 只有当内容与自动生成的不同时，才标记为已编辑
  if (currentGreeting !== expectedGreeting) {
    greetingEdited.value = true
  }
}
</script>

<style scoped>
.create-assistant-form {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  margin: 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 30px;
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-back:hover {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
  color: var(--button-primary);
}

.form-header h2 {
  margin: 0;
  font-size: 24px;
  color: var(--color-text);
}

/* 步骤导航 */
.steps-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background);
  border: 2px solid var(--color-border);
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s;
}

.step-item.active .step-circle {
  background: var(--button-primary);
  border-color: var(--button-primary);
  color: white;
}

.step-item.completed .step-circle {
  background: var(--color-success, #10b981);
  border-color: var(--color-success, #10b981);
  color: white;
}

.step-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.step-item.active .step-label {
  color: var(--button-primary);
  font-weight: 600;
}

.step-item.completed .step-label {
  color: var(--color-success, #10b981);
}

.step-line {
  width: 40px;
  height: 2px;
  background: var(--color-border);
  margin-bottom: 20px;
}

.form-content {
  flex: 1;
  overflow-y: auto;
  padding: 30px;
}

.form-section {
  margin-bottom: 32px;
  padding-bottom: 32px;
  border-bottom: 1px solid var(--color-border);
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h3 {
  margin: 0 0 20px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.form-group {
  margin-bottom: 24px;
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.form-group label.required::after {
  content: ' *';
  color: var(--color-error, #ef4444);
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 12px 16px;
  background: var(--input-background);
  border: 1px solid var(--input-border);
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-text);
  font-family: inherit;
  transition: all 0.2s;
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

.char-count {
  position: absolute;
  bottom: -20px;
  right: 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.input-hint {
  display: block;
  font-size: 12px;
  color: var(--color-text-secondary);
  font-style: italic;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  gap: 12px;
}

.char-count-inline {
  font-size: 12px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

/* 头像选择器 */
.avatar-selector {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.avatar-option {
  width: 60px;
  height: 60px;
  font-size: 32px;
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-option:hover {
  border-color: var(--button-primary);
  transform: scale(1.1);
}

.avatar-option.selected {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

/* 知识库选择框 */
.kb-selector-box {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
  background: var(--color-background);
  max-height: 240px;
  overflow-y: auto;
}

.kb-selector-box::-webkit-scrollbar {
  width: 6px;
}

.kb-selector-box::-webkit-scrollbar-track {
  background: transparent;
}

.kb-selector-box::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

.kb-selector-box::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

/* 知识库列表 */
.kb-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.kb-item {
  background: transparent;
  border-radius: 6px;
  padding: 10px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.kb-item:hover {
  background: var(--color-primary-alpha);
  border-color: var(--input-border);
}

.kb-checkbox {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.kb-checkbox input[type="checkbox"] {
  position: absolute;
  opacity: 0;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid var(--input-border);
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kb-checkbox input:checked + .checkbox-custom {
  background: var(--button-primary);
  border-color: var(--button-primary);
}

.kb-checkbox input:checked + .checkbox-custom::after {
  content: '✓';
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.kb-info {
  flex: 1;
}

.kb-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 4px;
}

.kb-meta {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.empty-kb {
  text-align: center;
  padding: 24px;
}

.empty-kb p {
  margin: 0 0 16px;
  color: var(--color-text-secondary);
}

.btn-create-kb {
  padding: 10px 24px;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-create-kb:hover {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

/* 范围滑块 */
.form-range {
  width: 100%;
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
}

.form-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  background: var(--button-primary);
  border-radius: 50%;
  cursor: pointer;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
}


.kb-section {
  margin-top: 24px;
}

.kb-section > label {
  display: block;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.function-switches {
  margin-top: 24px;
}

.function-switches > label {
  display: block;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  border-top: 1px solid var(--color-border);
}

.footer-left {
  display: flex;
  gap: 12px;
}

.footer-right {
  display: flex;
  gap: 12px;
  margin-left: auto;
}

.btn-secondary,
.btn-primary,
.btn-cancel {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
  color: var(--button-primary);
}

.btn-cancel {
  background: var(--color-background);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn-cancel:hover {
  background: #fee;
  border-color: #fcc;
  color: #c33;
}

.btn-primary {
  background: var(--button-primary);
  color: var(--button-primaryText);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 滚动条样式 */
.form-content::-webkit-scrollbar {
  width: 6px;
}

.form-content::-webkit-scrollbar-track {
  background: var(--color-surface);
}

.form-content::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 3px;
}
</style>

