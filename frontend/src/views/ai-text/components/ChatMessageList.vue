<template>
  <div class="chat-messages" ref="messagesContainer">
    <div v-for="(message, index) in messages" :key="index" 
         :class="['message-wrapper', message.role === 'user' ? 'user-message-wrapper' : 'ai-message-wrapper']">
      <!-- AI消息 -->
      <template v-if="message.role !== 'user'">
        <div class="avatar-container">
          <img :src="aiAvatar" alt="AI" class="avatar-img">
        </div>
        <div class="message-with-name">
          <div class="avatar-name">AI助手</div>
          <div class="message ai-message">
            <!-- 深度思考过程（如果有的话） -->
            <div v-if="message.thinking_process" class="thinking-section">
              <div class="thinking-header" @click="toggleThinking(index)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="thinking-icon">
                  <path d="M9 12l2 2 4-4"></path>
                  <path d="M21 12c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path>
                  <path d="M3 12c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path>
                  <path d="M12 21c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path>
                  <path d="M12 3c.552 0 1-.448 1-1s-.448-1-1-1-1 .448-1 1 .448 1 1 1z"></path>
                </svg>
                <span>深度思考过程</span>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
                     :class="['expand-icon', { 'expanded': expandedThinking[index] }]">
                  <polyline points="6,9 12,15 18,9"></polyline>
                </svg>
              </div>
              <div v-show="expandedThinking[index]" class="thinking-content">
                <div class="thinking-text" v-html="formatMessage(message.thinking_process)"></div>
              </div>
            </div>
            
            <!-- 主要回答内容 -->
            <div class="message-content" v-html="formatMessage(message.content)"></div>
            <div class="message-time" v-if="message.timestamp">{{ formatDate(message.timestamp) }}</div>
          </div>
        </div>
      </template>
      
      <!-- 用户消息 -->
      <template v-else>
        <div class="message-with-name">
          <div class="avatar-name user-name">{{ userDisplayName }}</div>
          <div class="message user-message">
            <div class="message-content" v-html="formatMessage(message.content)"></div>
            <div class="message-time" v-if="message.timestamp">{{ formatDate(message.timestamp) }}</div>
          </div>
        </div>
        <div class="avatar-container" :style="{ backgroundColor: userAvatar ? 'transparent' : '#1989fa' }">
          <img v-if="userAvatar" :src="userAvatar" alt="User" class="avatar-img">
          <span v-else class="user-avatar">{{ userDisplayName.slice(0, 1) }}</span>
        </div>
      </template>
    </div>
    
    <!-- 加载中状态 -->
    <div v-if="isLoading" class="message-wrapper ai-message-wrapper">
      <div class="avatar-container">
        <img :src="aiAvatar" alt="AI" class="avatar-img">
      </div>
      <div class="message-with-name">
        <div class="avatar-name">AI助手</div>
        <div class="message ai-message loading">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, reactive } from 'vue'
import { formatMessage } from '../../../utils/messageUtils'
import { formatDate } from '../../../utils/dateUtils'
import aiAvatar from '../../../assets/static/ai_touxiang.png'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  thinking_process?: string
  final_answer?: string
  has_structured_response?: boolean
}

interface Props {
  messages: Message[]
  isLoading: boolean
  userDisplayName: string
  userAvatar?: string
}

interface Emits {
  (e: 'scroll-to-bottom'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const messagesContainer = ref<HTMLElement | null>(null)

// 思考过程展开状态管理
const expandedThinking = reactive<Record<number, boolean>>({})

// 切换思考过程展开/收起状态
const toggleThinking = (index: number) => {
  expandedThinking[index] = !expandedThinking[index]
  // 展开后滚动到底部
  nextTick(() => {
    scrollToBottom()
  })
}

// 监听消息变化，自动滚动到底部
watch(() => props.messages.length, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

// 监听加载状态变化
watch(() => props.isLoading, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
  emit('scroll-to-bottom')
}

// 暴露方法给父组件
defineExpose({
  scrollToBottom,
  messagesContainer
})
</script>

<style scoped>
.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: var(--color-background-soft, #f5f5f5);
}

.message-wrapper {
  display: flex;
  margin-bottom: 25px;
  width: 100%;
  position: relative;
  animation: fade-in 0.3s ease-out;
  align-items: flex-start;
}

.user-message-wrapper {
  justify-content: flex-end;
}

.ai-message-wrapper {
  justify-content: flex-start;
}

.avatar-container {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar {
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.message-with-name {
  display: flex;
  flex-direction: column;
  max-width: 65%;
}

.avatar-name {
  font-size: 12px;
  color: var(--color-text-soft, #666);
  margin-bottom: 4px;
  padding-left: 8px;
}

.user-name {
  text-align: right;
  padding-right: 8px;
}

.user-message-wrapper .message-with-name {
  margin-right: 10px;
  align-items: flex-end;
}

.ai-message-wrapper .message-with-name {
  margin-left: 10px;
  align-items: flex-start;
}

.message {
  max-width: 100%;
  padding: 10px 16px;
  border-radius: 3px;
  position: relative;
  word-break: break-word;
}

.user-message {
  background-color: #95ec69;
  color: #000;
  border-top-right-radius: 0;
}

.ai-message {
  background-color: white;
  color: #000;
  border-top-left-radius: 0;
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
}

.user-message::after {
  content: '';
  position: absolute;
  top: 0;
  right: -10px;
  width: 0;
  height: 0;
  border-left: 10px solid #95ec69;
  border-top: 10px solid transparent;
}

.ai-message::before {
  content: '';
  position: absolute;
  top: 0;
  left: -10px;
  width: 0;
  height: 0;
  border-right: 10px solid white;
  border-top: 10px solid transparent;
}

.message-content {
  font-size: 16px;
  line-height: 1.5;
}

.message-time {
  font-size: 12px;
  color: var(--color-text-soft, #999);
  margin-top: 5px;
  text-align: right;
}

.loading {
  min-width: 80px;
}

.typing-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background-color: var(--color-text-soft, #bbb);
  border-radius: 50%;
  display: inline-block;
  margin: 0 2px;
  animation: blink 1.4s infinite both;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes blink {
  0% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
  100% { opacity: 0.6; transform: scale(1); }
}

.highlighted {
  animation: highlight-pulse 3s ease;
}

@keyframes highlight-pulse {
  0% { background-color: rgba(79, 116, 227, 0.1); }
  50% { background-color: rgba(79, 116, 227, 0.2); }
  100% { background-color: transparent; }
}

/* 深度思考过程样式 */
.thinking-section {
  margin-bottom: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background-color: #f8f9fa;
}

.thinking-header {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s ease;
  border-radius: 6px 6px 0 0;
}

.thinking-header:hover {
  background-color: #e9ecef;
}

.thinking-icon {
  margin-right: 6px;
  color: #6c757d;
}

.thinking-header span {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #495057;
}

.expand-icon {
  transition: transform 0.2s ease;
  color: #6c757d;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.thinking-content {
  border-top: 1px solid #e0e0e0;
  background-color: #ffffff;
  border-radius: 0 0 6px 6px;
}

.thinking-text {
  padding: 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #495057;
  white-space: pre-wrap;
  border-left: 3px solid #007bff;
  background-color: #f8f9fa;
  margin: 0;
}

.thinking-text::before {
  content: "💭 ";
  margin-right: 4px;
}
</style>