<template>
  <div class="chat-input-container" :class="{ 'centered-input': isCenterLayout }">
    <div class="input-wrapper">
      <!-- 功能开关区域 -->
      <div class="feature-toggles">
        <button 
          class="toggle-btn" 
          :class="{ active: deepThinkingEnabled }"
          @click="toggleDeepThinking"
          title="深度思考模式"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 12l2 2 4-4"></path>
            <path d="M21 12c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path>
            <path d="M3 12c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path>
            <path d="M12 21c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path>
            <path d="M12 3c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path>
          </svg>
          <span>深度思考</span>
        </button>
        
        <button 
          class="toggle-btn" 
          :class="{ active: webSearchEnabled }"
          @click="toggleWebSearch"
          title="联网搜索"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="2" y1="12" x2="22" y2="12"></line>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
          </svg>
          <span>联网搜索</span>
        </button>
      </div>
      
      <!-- 选中文件显示区域 -->
      <div v-if="selectedFiles.length > 0" class="selected-files">
        <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
          <div class="file-info">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">({{ (file.size / 1024).toFixed(1) }}KB)</span>
          </div>
          <button class="remove-file-btn" @click="removeFile(index)" title="移除文件">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <textarea 
          v-model="inputValue" 
          @keydown="handleKeyDown"
          placeholder="请输入问题..."
          rows="3"
          ref="inputElement"
          class="chat-input"
        ></textarea>
        
        <!-- 隐藏的文件输入 -->
        <input 
          type="file" 
          ref="fileInputRef"
          @change="handleFileSelect"
          multiple
          accept="image/*,.pdf,.doc,.docx,.txt,.md"
          style="display: none;"
        />
        
        <!-- 上传附件按钮 -->
        <button 
          class="attachment-button" 
          @click="triggerFileSelect"
          title="上传附件"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66L9.64 16.2a2 2 0 0 1-2.83-2.83l8.49-8.49"></path>
          </svg>
        </button>
        
        <button 
          class="send-button" 
          @click="handleSend"
          :disabled="isLoading || !inputValue.trim()"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { autoResizeTextarea } from '../../../utils/messageUtils'

interface Props {
  userInput: string
  isLoading: boolean
  isCenterLayout: boolean
  deepThinkingEnabled: boolean
  webSearchEnabled: boolean
  selectedFiles: File[]
}

interface Emits {
  (e: 'update:userInput', value: string): void
  (e: 'update:deepThinkingEnabled', value: boolean): void
  (e: 'update:webSearchEnabled', value: boolean): void
  (e: 'update:selectedFiles', value: File[]): void
  (e: 'send-message'): void
  (e: 'key-down', event: KeyboardEvent): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const inputElement = ref<HTMLTextAreaElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const inputValue = computed({
  get: () => props.userInput,
  set: (value: string) => emit('update:userInput', value)
})

const deepThinkingEnabled = computed({
  get: () => props.deepThinkingEnabled,
  set: (value: boolean) => emit('update:deepThinkingEnabled', value)
})

const webSearchEnabled = computed({
  get: () => props.webSearchEnabled,
  set: (value: boolean) => emit('update:webSearchEnabled', value)
})

const selectedFiles = computed({
  get: () => props.selectedFiles,
  set: (value: File[]) => emit('update:selectedFiles', value)
})

// 方法
const handleSend = () => {
  emit('send-message')
}

const handleKeyDown = (e: KeyboardEvent) => {
  emit('key-down', e)
}

const toggleDeepThinking = () => {
  deepThinkingEnabled.value = !deepThinkingEnabled.value
}

const toggleWebSearch = () => {
  webSearchEnabled.value = !webSearchEnabled.value
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    const files = Array.from(target.files)
    selectedFiles.value = [...selectedFiles.value, ...files]
  }
}

// 触发文件选择
const triggerFileSelect = () => {
  fileInputRef.value?.click()
}

// 移除选中的文件
const removeFile = (index: number) => {
  const newFiles = [...selectedFiles.value]
  newFiles.splice(index, 1)
  selectedFiles.value = newFiles
}

// 自动调整输入框高度
watch(inputValue, () => {
  if (inputElement.value) {
    autoResizeTextarea(inputElement.value)
  }
})

// 聚焦输入框
const focusInput = () => {
  nextTick(() => {
    inputElement.value?.focus()
  })
}

// 暴露方法给父组件
defineExpose({
  focusInput,
  inputElement
})
</script>

<style scoped>
.chat-input-container {
  max-width: 1000px;
  margin-top: 1rem;
  padding: 1rem;
  background-color: transparent;
  border-radius: 0.5rem;
  box-shadow: none;
  width: 100%;
  transition: all 0.3s ease;
  margin: 1rem auto;
}

.chat-input-container.centered-input {
  max-width: 1000px;
  margin: 1rem auto;
  position: relative;
  z-index: 5;
}

.input-wrapper {
  display: flex;
  flex-direction: column;
  border: none;
  border-radius: 0.75rem;
  overflow: hidden;
  background-color: var(--color-background-mute, #f1f3f4);
  padding: 0.75rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  min-height: 60px;
}

.feature-toggles {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background-color: var(--color-background, #ffffff);
  border: 1px solid var(--color-border, #e2e8f0);
  border-radius: 1rem;
  font-size: 0.75rem;
  color: var(--color-text-soft, #64748b);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.toggle-btn:hover {
  background-color: var(--color-background-soft, #f8fafc);
  border-color: var(--color-primary, #4f74e3);
}

.toggle-btn.active {
  background-color: var(--color-primary, #4f74e3);
  border-color: var(--color-primary, #4f74e3);
  color: white;
}

.toggle-btn svg {
  flex-shrink: 0;
}

.selected-files {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0.5rem;
  background-color: var(--color-background, #ffffff);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border, #e2e8f0);
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  background-color: var(--color-background-soft, #f8fafc);
  border-radius: 0.375rem;
  border: 1px solid var(--color-border, #e2e8f0);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 0.875rem;
  color: var(--color-text, #334155);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 0.75rem;
  color: var(--color-text-soft, #64748b);
  white-space: nowrap;
}

.remove-file-btn {
  background: transparent;
  border: none;
  color: var(--color-text-soft, #64748b);
  padding: 0.25rem;
  border-radius: 0.25rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.remove-file-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.input-area {
  display: flex;
  align-items: flex-end;
  width: 100%;
}

.chat-input {
  flex-grow: 1;
  border: none;
  outline: none;
  padding: 0.75rem;
  resize: none;
  font-family: inherit;
  font-size: 1.1rem;
  max-height: 300px;
  background: transparent;
  width: 100%;
  line-height: 1.5;
  color: var(--color-text, #333);
}

.chat-input-container.centered-input .input-wrapper {
  min-height: 60px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.chat-input-container.centered-input .chat-input {
  font-size: 1.1rem;
}

.attachment-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-soft, #64748b);
  margin-right: 0.25rem;
  border-radius: 50%;
  transition: all 0.2s;
}

.attachment-button:hover {
  background-color: var(--color-background-mute, #f5f5f5);
  color: var(--color-primary, #1a73e8);
}

.send-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary, #1a73e8);
}

.send-button:hover {
  background-color: var(--color-background-mute, #f5f5f5);
  border-radius: 50%;
}

.send-button:disabled {
  color: var(--color-text-soft, #ccc);
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .chat-input-container.centered-input {
    max-width: 90%;
  }
  
  .feature-toggles {
    flex-wrap: wrap;
  }
  
  .toggle-btn {
    font-size: 0.7rem;
    padding: 0.25rem 0.5rem;
  }
}
</style>