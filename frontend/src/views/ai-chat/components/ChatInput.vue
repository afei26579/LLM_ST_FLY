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
      
      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-container">
          <textarea 
            v-model="userInput" 
            @keydown.enter="handleKeyDown"
            placeholder="请输入问题..."
            rows="3"
            ref="inputElement"
            class="chat-input"
          ></textarea>
          
          <!-- 输入框内的按钮组 -->
          <div class="input-buttons">
            <button 
              class="input-icon-button send-button" 
              @click="handleSendMessage"
              :disabled="isLoading || !userInput.trim()"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, computed } from 'vue'
import { autoResizeTextarea } from '@/utils/messageUtils'

// Props
interface Props {
  userInput: string
  isLoading: boolean
  isCenterLayout: boolean
  deepThinkingEnabled: boolean
  webSearchEnabled: boolean
}

const props = defineProps<Props>()

// Emits
interface Emits {
  (e: 'update:userInput', value: string): void
  (e: 'update:deepThinkingEnabled', value: boolean): void
  (e: 'update:webSearchEnabled', value: boolean): void
  (e: 'sendMessage'): void
}

const emit = defineEmits<Emits>()

// Refs
const inputElement = ref<HTMLTextAreaElement | null>(null)

// Computed
const userInput = computed({
  get: () => props.userInput,
  set: (value) => emit('update:userInput', value)
})

const deepThinkingEnabled = computed({
  get: () => props.deepThinkingEnabled,
  set: (value) => emit('update:deepThinkingEnabled', value)
})

const webSearchEnabled = computed({
  get: () => props.webSearchEnabled,
  set: (value) => emit('update:webSearchEnabled', value)
})

// Methods
const toggleDeepThinking = () => {
  deepThinkingEnabled.value = !deepThinkingEnabled.value
}

const toggleWebSearch = () => {
  webSearchEnabled.value = !webSearchEnabled.value
}

const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSendMessage()
  }
}

const handleSendMessage = () => {
  emit('sendMessage')
}

const focusInput = () => {
  nextTick(() => {
    inputElement.value?.focus()
  })
}

// Watch
watch(userInput, () => {
  if (inputElement.value) {
    autoResizeTextarea(inputElement.value)
  }
})

// Expose methods
defineExpose({
  focusInput,
  inputElement
})
</script>

<style scoped>
.chat-input-container {
  padding: 1rem;
  background: var(--color-surface, #f8f9fa);
  border-top: 1px solid var(--color-border, #e9ecef);
  position: sticky;
  bottom: 0;
  z-index: 10;
}

.chat-input-container.centered-input {
  background: transparent;
  border: none;
  position: static;
  padding: 0;
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  background: var(--card-background, white);
  border-radius: 24px;
  padding: 1rem;
  box-shadow: var(--card-shadow, 0 4px 20px rgba(0, 0, 0, 0.1));
  border: 1px solid transparent;
  background-clip: padding-box;
  position: relative;
}

/* 未来科技风输入框特效 */
.input-wrapper::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  background: var(--color-border, #e9ecef);
  border-radius: 25px;
  z-index: -1;
  animation: inputGlow 2s ease-in-out infinite alternate;
}

@keyframes inputGlow {
  0% {
    opacity: 0.6;
  }
  100% {
    opacity: 1;
  }
}

.feature-toggles {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border, #e9ecef);
  background: var(--color-background, white);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.875rem;
  color: var(--color-textSecondary, #6c757d);
}

.toggle-btn:hover {
  background: var(--color-surface, #f8f9fa);
  border-color: var(--color-border, #dee2e6);
}

.toggle-btn.active {
  background: var(--color-primary, #007bff);
  border-color: var(--color-primary, #007bff);
  color: white;
}

.toggle-btn svg {
  transition: transform 0.3s ease;
}

.toggle-btn:hover svg {
  transform: scale(1.1);
}

.input-area {
  position: relative;
}

.input-container {
  position: relative;
  display: flex;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  padding: 1rem 48px 1rem 1rem; /* 右侧留出空间给发送按钮 */
  border: 1px solid var(--color-border, #e9ecef);
  border-radius: 20px; /* 更圆的圆角 */
  resize: none;
  outline: none;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.5;
  min-height: 60px;
  max-height: 200px;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
  background: var(--color-background, white);
  color: var(--color-text, #1f2937);
}

.input-buttons {
  position: absolute;
  right: 8px;
  bottom: 8px;
  display: flex;
  gap: 4px;
  align-items: center;
}

.chat-input:focus {
  border-color: var(--color-primary, #007bff);
  box-shadow: 
    0 0 0 3px var(--color-primary, rgba(0, 123, 255, 0.1)),
    0 0 20px var(--color-primary, rgba(0, 245, 255, 0.3)),
    inset 0 0 20px var(--color-primary, rgba(0, 245, 255, 0.1));
  animation: inputFocusGlow 1.5s ease-in-out infinite alternate;
}

@keyframes inputFocusGlow {
  0% {
    box-shadow: 
      0 0 0 3px var(--color-primary, rgba(0, 123, 255, 0.1)),
      0 0 20px var(--color-primary, rgba(0, 245, 255, 0.2)),
      inset 0 0 20px var(--color-primary, rgba(0, 245, 255, 0.05));
  }
  100% {
    box-shadow: 
      0 0 0 3px var(--color-primary, rgba(0, 123, 255, 0.2)),
      0 0 30px var(--color-primary, rgba(0, 245, 255, 0.4)),
      inset 0 0 30px var(--color-primary, rgba(0, 245, 255, 0.15));
  }
}

.chat-input::placeholder {
  color: var(--color-textSecondary, #6c757d);
}

.input-icon-button {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
}

.send-button {
  background: var(--button-primary, #007bff);
  color: white;
  position: relative;
  overflow: hidden;
}

.send-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transform: rotate(45deg);
  transition: all 0.3s ease;
  opacity: 0;
}

.send-button:hover:not(:disabled) {
  background: var(--button-primaryHover, #0056b3);
  transform: scale(1.1);
  box-shadow: 0 0 15px var(--color-primary, rgba(0, 245, 255, 0.5));
}

.send-button:hover:not(:disabled)::before {
  opacity: 1;
  left: 100%;
}

.send-button:disabled {
  background: var(--color-textSecondary, #6c757d);
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 768px) {
  .chat-input-container {
    padding: 0.75rem;
  }
  
  .input-wrapper {
    padding: 0.75rem;
  }
  
  .feature-toggles {
    gap: 0.25rem;
  }
  
  .toggle-btn {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
  }
}

/* 主题样式已由CSS变量控制 */
</style>
