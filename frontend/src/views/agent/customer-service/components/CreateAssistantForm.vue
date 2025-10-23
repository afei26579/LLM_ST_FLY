<template>
  <div class="create-assistant-form">
    <div class="form-header">
      <button @click="$emit('cancel')" class="btn-back">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7"/>
        </svg>
        返回
      </button>
      <h2>🤖 创建智能助手</h2>
    </div>

    <div class="form-content">
      <!-- 基本信息 -->
      <div class="form-section">
        <h3>基本信息</h3>
        
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

      <!-- 对话配置 -->
      <div class="form-section">
        <h3>对话配置</h3>
        
        <div class="form-group">
          <label class="required">开场白</label>
          <textarea
            v-model="formData.greeting_message"
            placeholder="欢迎语，用户开始对话时显示..."
            maxlength="200"
            rows="3"
            class="form-textarea"
          ></textarea>
          <span class="char-count">{{ formData.greeting_message.length }}/200</span>
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

      <!-- 知识库关联 -->
      <div class="form-section">
        <h3>知识库关联</h3>
        
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

      <!-- AI参数 -->
      <div class="form-section">
        <h3>AI参数</h3>
        
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
      <div class="form-section">
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
      </div>
    </div>

    <div class="form-footer">
      <button @click="$emit('cancel')" class="btn-secondary">
        取消
      </button>
      <button
        @click="handleSubmit"
        :disabled="!isValid || loading"
        class="btn-primary"
      >
        <span v-if="!loading">创建助手</span>
        <span v-else>创建中...</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

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

const avatarOptions = ['🤖', '👨‍💼', '👩‍💼', '🎯', '📱', '💬', '🎓', '⚡']

const formData = ref({
  name: '',
  avatar: '🤖',
  description: '',
  greeting_message: '您好！我是智能客服助手，有什么可以帮您的吗？',
  system_prompt: '你是一个专业、友好的客服助手。请基于用户问题提供准确、详细的回答。',
  knowledge_base_ids: [] as number[],
  model: 'qwen-plus',
  temperature: 0.7,
  top_k: 3,
  enable_knowledge_base: true,
  enable_order_query: false,
  enable_human_handoff: true,
  is_default: false
})

const isValid = computed(() => {
  return formData.value.name.trim().length > 0 &&
         formData.value.greeting_message.trim().length > 0
})

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
  gap: 16px;
  padding: 20px 30px;
  border-bottom: 1px solid var(--color-border);
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

/* 知识库列表 */
.kb-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.kb-item {
  background: var(--color-background);
  border-radius: 8px;
  padding: 12px;
  transition: all 0.2s;
}

.kb-item:hover {
  background: var(--color-primary-alpha);
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
  padding: 32px;
  background: var(--color-background);
  border-radius: 8px;
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

/* 开关列表 */
.switches {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.switch-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--color-background);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.switch-item:hover {
  background: var(--color-primary-alpha);
}

.switch-item input[type="checkbox"] {
  position: absolute;
  opacity: 0;
}

.switch-custom {
  position: relative;
  width: 48px;
  height: 28px;
  background: var(--color-border);
  border-radius: 14px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.switch-custom::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  transition: all 0.2s;
}

.switch-item input:checked + .switch-custom {
  background: var(--button-primary);
}

.switch-item input:checked + .switch-custom::after {
  left: 23px;
}

.switch-info {
  flex: 1;
}

.switch-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 4px;
}

.switch-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 30px;
  border-top: 1px solid var(--color-border);
}

.btn-secondary,
.btn-primary {
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

