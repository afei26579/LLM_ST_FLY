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
            <div class="message-content" 
                 :class="{ 'typing-animation': isLoading && index === messages.length - 1 }"
                 v-html="formatMessage(message.content)"
                 @click="handleMessageClick(message, index)"
                 :title="isLoading && index === messages.length - 1 ? '点击立即显示完整内容' : ''">
            </div>
            <div class="message-time" v-if="message.timestamp">{{ formatDate(message.timestamp) }}</div>
          </div>
        </div>
      </template>
      
      <!-- 用户消息 -->
      <template v-else>
        <div class="message-with-name user-message-container">
          <div class="user-name-avatar">
            <div class="avatar-name user-name">{{ userDisplayName }}</div>
            <div class="avatar-container" :style="{ backgroundColor: userAvatar ? 'transparent' : '#1989fa' }">
              <img v-if="userAvatar" :src="userAvatar" alt="User" class="avatar-img">
              <span v-else class="user-avatar">{{ userDisplayName.slice(0, 1) }}</span>
            </div>
          </div>
          <div class="message user-message">
            <div class="message-content" v-html="formatMessage(message.content)"></div>
            <div class="message-time" v-if="message.timestamp">{{ formatDate(message.timestamp) }}</div>
          </div>
        </div>
      </template>
    </div>
    
    <!-- AI回复中状态 - 只在消息列表为空或最后一条不是AI消息时显示 -->
    <div v-if="isLoading && (!messages.length || messages[messages.length - 1]?.role === 'user')" 
         class="message-wrapper ai-message-wrapper">
      <div class="avatar-container">
        <img :src="aiAvatar" alt="AI" class="avatar-img">
      </div>
      <div class="message-with-name">
        <div class="avatar-name">AI助手</div>
        <div class="message ai-message">
          <div class="ai-status">
            <div class="typing-dots">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { formatMessage, scrollToBottom } from '@/utils/messageUtils'
import { formatDate } from '@/utils/dateUtils'
import aiAvatar from '@/assets/static/ai_touxiang.png'

// Types are imported from composables
type Message = any // Will use the type from useChat composable

// Props
interface Props {
  messages: any[]
  isLoading: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  skipTyping: []
}>()

// State
const authStore = useAuthStore()
const messagesContainer = ref<HTMLElement | null>(null)
const expandedThinking = ref<Record<number, boolean>>({})

// Computed
const userDisplayName = computed(() => {
  return authStore.userInfo?.nickname || authStore.userInfo?.username || '用户'
})

const userAvatar = computed(() => {
  return authStore.userInfo?.avatar
})

// Methods
const toggleThinking = (index: number) => {
  expandedThinking.value[index] = !expandedThinking.value[index]
}

const handleMessageClick = (message: any, index: number) => {
  // 如果是最后一条消息且正在加载中（打字机效果），则跳过动画
  if (props.isLoading && index === props.messages.length - 1 && message.role === 'assistant') {
    emit('skipTyping')
  }
}

const scrollToBottomContainer = () => {
  if (messagesContainer.value) {
    scrollToBottom(messagesContainer.value)
  }
}

// Expose methods
defineExpose({
  scrollToBottomContainer,
  messagesContainer
})

// Auto scroll when new messages arrive
nextTick(() => {
  scrollToBottomContainer()
})
</script>

<style scoped>
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  scroll-behavior: smooth;
  background: var(--color-background, #ffffff);
}

/* 霓虹滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: var(--color-surface, #f1f1f1);
  border-radius: 10px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: var(--color-primary, linear-gradient(45deg, #00f5ff, #9d4edd, #ff0080));
  border-radius: 10px;
  box-shadow: 0 0 10px var(--color-primary, rgba(0, 245, 255, 0.5));
  animation: scrollbarGlow 2s ease-in-out infinite alternate;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary, linear-gradient(45deg, #00d4ff, #8b3fd9, #e6006b));
  box-shadow: 0 0 15px var(--color-primary, rgba(0, 245, 255, 0.8));
}

@keyframes scrollbarGlow {
  0% {
    box-shadow: 0 0 10px var(--color-primary, rgba(0, 245, 255, 0.3));
  }
  100% {
    box-shadow: 0 0 20px var(--color-primary, rgba(0, 245, 255, 0.7));
  }
}

.message-wrapper {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  animation: fadeInUp 0.3s ease-out;
  margin-bottom: 1rem;
}

.message-wrapper.highlighted {
  background: rgba(255, 235, 59, 0.2);
  border-radius: 12px;
  padding: 0.5rem;
  margin: -0.5rem -0.5rem 0.5rem -0.5rem;
  transition: background-color 0.3s ease;
}

.user-message-wrapper {
  flex-direction: row-reverse;
  justify-content: flex-start; /* 用户消息靠右对齐 */
}

.user-message-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  max-width: calc(100% - 50px);
}

.user-name-avatar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem; /* 改为下边距，因为现在在上面 */
}

.user-name-avatar .avatar-container {
  width: 32px;
  height: 32px;
  font-size: 0.875rem;
}

.avatar-container {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e9ecef;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar {
  color: white;
  font-weight: 600;
  font-size: 1rem;
}

.message-with-name {
  max-width: calc(100% - 50px);
  display: flex;
  flex-direction: column;
}

.user-message-wrapper .message-with-name {
  align-items: flex-end; /* 用户消息内容右对齐 */
}

.user-message-wrapper .user-name-avatar {
  flex-direction: row; /* 用户名在左，头像在右 */
}

.message-wrapper:not(.user-message-wrapper) .message-with-name {
  align-items: flex-start; /* AI消息内容左对齐 */
}

.avatar-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text, #495057);
  margin-bottom: 0.5rem;
}

.user-name {
  text-align: right;
}

.message {
  padding: 1rem 1.5rem;
  border-radius: 20px;
  position: relative;
  display: inline-block;
  max-width: min(1200px, 92%); /* 设置更大的最大宽度1200px，或容器的92% */
  min-width: 60px; /* 减小最小宽度，允许更短的消息 */
  width: fit-content; /* 根据内容自适应宽度 */
  word-break: keep-all; /* 避免单词和中文被打断 */
  overflow-wrap: break-word; /* 只在超长单词时才换行 */
  white-space: normal; /* 正常的空白符处理，自动换行 */
  line-height: 1.6;
}

.ai-message {
  background: var(--color-surface, #f8f9fa);
  border: 1px solid var(--color-border, #e9ecef);
  border-bottom-left-radius: 8px;
  color: var(--color-text, #1f2937);
  position: relative;
}

.user-message {
  background: var(--button-primary, linear-gradient(135deg, #007bff, #0056b3));
  color: white;
  border-bottom-right-radius: 8px;
  position: relative;
  overflow: hidden;
  white-space: normal; /* 确保用户消息正常换行 */
}

/* 用户消息闪光特效 */
.user-message::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  animation: messageShimmer 3s ease-in-out infinite;
}

@keyframes messageShimmer {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
}

.thinking-section {
  margin-bottom: 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  overflow: hidden;
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  cursor: pointer;
  transition: background-color 0.3s ease;
  border-bottom: 1px solid #dee2e6;
}

.thinking-header:hover {
  background: #e9ecef;
}

.thinking-icon {
  color: #007bff;
}

.expand-icon {
  margin-left: auto;
  transition: transform 0.3s ease;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.thinking-content {
  background: white;
  animation: slideDown 0.3s ease-out;
}

.thinking-text {
  padding: 1rem;
  color: #6c757d;
  font-size: 0.875rem;
  line-height: 1.6;
}

.message-content {
  font-size: 1rem;
  /* 继承父元素 .message 的换行设置 */
}

/* 打字中的消息添加交互提示 */
.ai-message .message-content.typing-animation {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.ai-message .message-content.typing-animation:hover {
  background-color: rgba(0, 123, 255, 0.05);
  border-radius: 8px;
}

.message-content.typing-animation {
  position: relative;
}

.message-content.typing-animation::after {
  content: '▊';
  animation: blink 1s infinite;
  color: #007bff;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.6;
  margin-top: 0.5rem;
}

.user-message .message-time {
  text-align: right;
  color: rgba(255, 255, 255, 0.8);
}

.ai-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.typing-dots {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}

.dot {
  width: 6px;
  height: 6px;
  background: #007bff;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    max-height: 0;
    opacity: 0;
  }
  to {
    max-height: 500px;
    opacity: 1;
  }
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 消息时间戳样式 */
.message-meta {
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-message-wrapper .message-meta {
  justify-content: flex-end; /* 用户消息的元信息右对齐 */
}

.message-wrapper:not(.user-message-wrapper) .message-meta {
  justify-content: flex-start; /* AI消息的元信息左对齐 */
}

/* 主题样式已由CSS变量控制 */

/* 时间戳样式 */
.message-time {
  font-size: 0.75rem;
  color: var(--color-textSecondary, #6c757d);
  margin-top: 0.25rem;
}

.user-message-wrapper .message-time {
  text-align: right; /* 用户消息时间戳右对齐 */
}

.message-wrapper:not(.user-message-wrapper) .message-time {
  text-align: left; /* AI消息时间戳左对齐 */
}

/* 移动端适配 */
@media (max-width: 768px) {
  .chat-messages {
    padding: 0.75rem;
    gap: 0.75rem;
  }
  
  .message-wrapper {
    gap: 0.5rem;
  }
  
  .avatar-container {
    width: 32px;
    height: 32px;
  }
  
  .message {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    max-width: min(700px, 95%); /* 移动端最大宽度700px或95% */
    min-width: 80px; /* 移动端调整最小宽度 */
  }
  
  .message-with-name {
    max-width: calc(100% - 40px);
  }
  
  .user-name-avatar .avatar-container {
    width: 28px;
    height: 28px;
    font-size: 0.75rem;
  }
  
  .message-time {
    font-size: 0.6875rem;
  }
}
</style>
