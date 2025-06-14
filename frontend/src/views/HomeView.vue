<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, watch } from 'vue'

const userInput = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputElement = ref<HTMLTextAreaElement | null>(null)

// 聊天消息
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// 初始化一些示例消息
const messages = reactive<ChatMessage[]>([
  {
    role: 'assistant',
    content: '你好！我是AI助手，有什么我可以帮助你的吗？'
  }
])

// 发送消息
const sendMessage = async () => {
  const content = userInput.value.trim()
  if (!content || isLoading.value) return
  
  // 添加用户消息
  messages.push({
    role: 'user',
    content
  })
  
  userInput.value = ''
  
  // 自动滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 模拟AI回复
  isLoading.value = true
  setTimeout(() => {
    messages.push({
      role: 'assistant',
      content: simulateAIResponse(content)
    })
    
    isLoading.value = false
    
    // 自动滚动到底部
    nextTick(() => {
      scrollToBottom()
      focusInput()
    })
  }, 1000)
}

// 处理键盘事件
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 滚动到底部
const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 聚焦输入框
const focusInput = () => {
  inputElement.value?.focus()
}

// 简单格式化消息（支持换行）
const formatMessage = (text: string) => {
  return text.replace(/\n/g, '<br>')
}

// 自动调整输入框高度
watch(userInput, () => {
  if (inputElement.value) {
    inputElement.value.style.height = 'auto'
    inputElement.value.style.height = `${inputElement.value.scrollHeight}px`
  }
})

// 模拟AI回复
const simulateAIResponse = (input: string): string => {
  const responses = [
    `我理解您的问题是关于"${input}"。这是一个很好的问题！`,
    `关于"${input}"，我想提供以下信息给您参考...`,
    `您问的"${input}"是一个很有深度的问题。从多个角度来看...`,
    `"${input}"是一个值得探讨的话题。根据我的理解...`,
    `感谢您的提问。关于"${input}"，我可以这样解释...`
  ]
  
  return responses[Math.floor(Math.random() * responses.length)]
}

// 组件挂载后，聚焦输入框
onMounted(() => {
  focusInput()
  scrollToBottom()
})
</script>

<template>
  <div class="chat-container">
    <!-- 聊天内容区域 -->
    <div class="chat-messages" ref="messagesContainer">
      <div v-for="(message, index) in messages" :key="index" 
           :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']">
        <div class="message-header">
          <div class="avatar">
            <span v-if="message.role === 'user'">👤</span>
            <span v-else>🤖</span>
          </div>
          <div class="sender">{{ message.role === 'user' ? '你' : 'AI助手' }}</div>
        </div>
        <div class="message-content" v-html="formatMessage(message.content)"></div>
      </div>
      
      <!-- 加载中状态 -->
      <div v-if="isLoading" class="message ai-message loading">
        <div class="message-header">
          <div class="avatar">🤖</div>
          <div class="sender">AI助手</div>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="chat-input-container">
      <div class="input-wrapper">
        <textarea 
          v-model="userInput" 
          @keydown.enter="handleKeyDown"
          placeholder="请输入问题..."
          rows="1"
          ref="inputElement"
          class="chat-input"
        ></textarea>
        <button 
          class="send-button" 
          @click="sendMessage"
          :disabled="isLoading || !userInput.trim()"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
      <div class="input-info">
        按 Enter 发送，Shift + Enter 换行
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
  overflow: hidden;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message {
  max-width: 85%;
  padding: 1rem;
  border-radius: 0.5rem;
  animation: fade-in 0.3s ease-out;
  line-height: 1.6;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-message {
  align-self: flex-end;
  background-color: #1a73e8;
  color: white;
  border-bottom-right-radius: 0;
}

.ai-message {
  align-self: flex-start;
  background-color: #f1f3f4;
  color: #202124;
  border-bottom-left-radius: 0;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.avatar {
  margin-right: 0.5rem;
  font-size: 1.2rem;
}

.message-content {
  font-size: 1rem;
}

.chat-input-container {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #fff;
  padding: 0.5rem;
}

.chat-input {
  flex-grow: 1;
  border: none;
  outline: none;
  padding: 0.5rem;
  resize: none;
  font-family: inherit;
  font-size: 1rem;
  max-height: 200px;
  background: transparent;
}

.send-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1a73e8;
}

.send-button:hover {
  background-color: #f5f5f5;
  border-radius: 50%;
}

.send-button:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.input-info {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #666;
  text-align: right;
}

/* 加载动画 */
.loading .message-content {
  display: flex;
  align-items: center;
}

.typing-indicator {
  display: flex;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: #606060;
  border-radius: 50%;
  display: inline-block;
  margin: 0 2px;
  opacity: 0.6;
  animation: blink 1.4s infinite both;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
  100% { opacity: 0.6; transform: scale(1); }
}
</style>
