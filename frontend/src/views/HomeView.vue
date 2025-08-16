<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useConversations } from '../composables/useConversations'
import { useChat } from '../composables/useChat'
import { getGreeting, formatDate } from '../utils/dateUtils'
import { formatMessage, autoResizeTextarea, scrollToBottom, focusInput } from '../utils/messageUtils'

// 导入AI头像
import aiAvatar from '../assets/static/ai_touxiang.png'

// 状态管理
const authStore = useAuthStore()

// 组合式函数
const {
  conversations,
  isLoadingConversations,
  getFilteredConversations,
  createNewConversation,
  loadConversationDetail,
  loadConversationsFromServer,
  deleteConversation,
  clearConversationMessages,
  toggleConversationExpand,
  isConversationExpanded,
  isHistoryLoading,
  getUserQuestions
} = useConversations()

const {
  userInput,
  isLoading,
  activeConversationId,
  isCenterLayout,
  sendMessage,
  handleKeyDown,
  switchConversation,
  jumpToQuestion
} = useChat()

// 本地状态
const messagesContainer = ref<HTMLElement | null>(null)
const inputElement = ref<HTMLTextAreaElement | null>(null)
const searchQuery = ref('')

// 功能开关状态
const deepThinkingEnabled = ref(false)
const webSearchEnabled = ref(false)

// 计算属性
const userDisplayName = computed(() => {
  return authStore.userInfo?.nickname || authStore.userInfo?.username || '用户'
})

const greeting = computed(() => {
  return getGreeting()
})

const messages = computed(() => {
  const conversation = conversations.find(c => c.id === activeConversationId.value)
  return conversation ? conversation.messages : []
})

const filteredConversations = computed(() => {
  return getFilteredConversations(searchQuery.value)
})

// 方法
const handleSendMessage = async () => {
  await sendMessage(conversations, (conversation) => {
    // 对话更新后的回调
    nextTick(() => {
      scrollToBottomContainer()
      focusInputElement()
    })
  }, {
    deepThinking: deepThinkingEnabled.value,
    webSearch: webSearchEnabled.value
  })
}

const handleKeyDownEvent = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSendMessage()
  }
}

const handleSwitchConversation = async (id: number) => {
  await switchConversation(id, conversations, loadConversationDetail)
  nextTick(() => {
    scrollToBottomContainer()
    focusInputElement()
  })
}

const handleDeleteConversation = async (id: number) => {
  const success = await deleteConversation(id)
  if (success) {
    // 如果删除的是当前对话，切换到其他对话
    if (activeConversationId.value === id) {
      if (conversations.length > 0) {
        await handleSwitchConversation(conversations[0].id)
      } else {
        // 如果没有对话了，创建一个新对话
        await handleCreateNewConversation()
      }
    }
  }
}

const handleCreateNewConversation = async () => {
  // 如果当前对话是个空对话且是临时对话，就直接使用它
  if (activeConversationId.value !== null) {
    const activeConv = conversations.find(c => c.id === activeConversationId.value)
    if (activeConv && activeConv.messages.length === 0 && activeConv.isTemporary) {
      console.log("当前已有临时空对话，不创建新对话")
      isCenterLayout.value = true
      return activeConv
    }
  }

  const newConversation = await createNewConversation()
  if (newConversation) {
    // 切换到新对话
    activeConversationId.value = newConversation.id
    
    // 设置居中布局
    isCenterLayout.value = true
    
    // 重置输入框
    userInput.value = ''
    
    // 聚焦输入框
    nextTick(() => {
      focusInputElement()
    })
  }
}

const handleJumpToQuestion = (conversationId: number, questionIndex: number) => {
  jumpToQuestion(conversationId, questionIndex, conversations, loadConversationDetail, scrollToQuestion)
}

// 滚动到底部
const scrollToBottomContainer = () => {
  if (messagesContainer.value) {
    scrollToBottom(messagesContainer.value)
  }
}

// 聚焦输入框
const focusInputElement = () => {
  focusInput(inputElement.value)
}

// 滚动到特定问题
const scrollToQuestion = (questionIndex: number) => {
  nextTick(() => {
    const conversation = conversations.find(c => c.id === activeConversationId.value)
    if (!conversation || !conversation.messages) return
    
    // 找到用户问题在整个消息列表中的实际位置
    const userMessages = conversation.messages.filter(msg => msg.role === 'user')
    if (questionIndex >= userMessages.length) return
    
    const targetMessage = userMessages[questionIndex]
    const targetIndex = conversation.messages.findIndex(msg => 
      msg.role === targetMessage.role && 
      msg.content === targetMessage.content &&
      msg.timestamp === targetMessage.timestamp
    )
    
    if (targetIndex === -1) return
    
    // 找到对应的DOM元素并滚动
    const messageElements = messagesContainer.value?.querySelectorAll('.message-wrapper')
    if (messageElements && targetIndex < messageElements.length) {
      messageElements[targetIndex].scrollIntoView({ behavior: 'smooth', block: 'center' })
      
      // 添加高亮效果
      const messageEl = messageElements[targetIndex] as HTMLElement
      messageEl.classList.add('highlighted')
      
      // 3秒后移除高亮
      setTimeout(() => {
        messageEl.classList.remove('highlighted')
      }, 3000)
    }
  })
}

// 自动调整输入框高度
watch(userInput, () => {
  if (inputElement.value) {
    autoResizeTextarea(inputElement.value)
  }
})

// 组件挂载后，从后端加载对话历史并聚焦输入框
onMounted(async () => {
  await loadConversationsFromServer()
  
  // 无论是否有活动对话，都创建一个新的临时对话
  console.log("首次打开组件，创建新临时对话")
  await handleCreateNewConversation()
  
  focusInputElement()
  scrollToBottomContainer()
})
</script>

<template>
  <div class="app-container">
    <!-- 聊天主区域 -->
    <div class="chat-container" :class="{ 'center-layout': isCenterLayout }">
      <!-- 居中布局内容包装器 -->
      <div v-if="isCenterLayout" class="center-content">
        <!-- 欢迎信息 -->
        <div class="welcome-card">
          <h2>{{ greeting }}，{{ userDisplayName }}，欢迎使用AI助手</h2>
        </div>
        
        <!-- 输入区域 -->
        <div class="chat-input-container" :class="{ 'centered-input': isCenterLayout }">
          <div class="input-wrapper">
            <!-- 功能开关区域 -->
            <div class="feature-toggles">
              <button 
                class="toggle-btn" 
                :class="{ active: deepThinkingEnabled }"
                @click="deepThinkingEnabled = !deepThinkingEnabled"
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
                @click="webSearchEnabled = !webSearchEnabled"
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
              <textarea 
                v-model="userInput" 
                @keydown.enter="handleKeyDownEvent"
                placeholder="请输入问题..."
                rows="3"
                ref="inputElement"
                class="chat-input"
              ></textarea>
              <button 
                class="send-button" 
                @click="handleSendMessage"
                :disabled="isLoading || !userInput.trim()"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 常规布局 -->
      <template v-else>
        <!-- 聊天内容区域 -->
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
              <div class="avatar-container" :style="{ backgroundColor: authStore.userInfo?.avatar ? 'transparent' : '#1989fa' }">
                <img v-if="authStore.userInfo?.avatar" :src="authStore.userInfo.avatar" alt="User" class="avatar-img">
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
        
        <!-- 输入区域 -->
        <div class="chat-input-container" :class="{ 'centered-input': isCenterLayout }">
          <div class="input-wrapper">
            <!-- 功能开关区域 -->
            <div class="feature-toggles">
              <button 
                class="toggle-btn" 
                :class="{ active: deepThinkingEnabled }"
                @click="deepThinkingEnabled = !deepThinkingEnabled"
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
                @click="webSearchEnabled = !webSearchEnabled"
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
              <textarea 
                v-model="userInput" 
                @keydown.enter="handleKeyDownEvent"
                placeholder="请输入问题..."
                rows="3"
                ref="inputElement"
                class="chat-input"
              ></textarea>
              <button 
                class="send-button" 
                @click="handleSendMessage"
                :disabled="isLoading || !userInput.trim()"
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
    </div>
    
    <!-- 右侧功能区 -->
    <div class="sidebar-right">
      <div class="sidebar-header">
        <button class="new-chat-button" @click="handleCreateNewConversation">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>新建对话</span>
        </button>
        
        <div class="search-container">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索对话..." 
            class="search-input"
          />
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </div>
      </div>
      
      <div class="conversations-list">
        <h3 class="list-title">历史对话</h3>
        
        <!-- 加载状态 -->
        <div v-if="isLoadingConversations" class="loading-state">
          <div class="spinner"></div>
          <p>加载对话历史中...</p>
        </div>
        
        <div 
          v-for="conversation in filteredConversations.slice(0, 15)" 
          :key="conversation.id" 
          class="conversation-item"
          :class="{ 'active': conversation.id === activeConversationId }"
        >
          <div class="conversation-main">
            <div class="conversation-content" @click="handleSwitchConversation(conversation.id)">
              <div class="conversation-title">{{ conversation.title }}</div>
              <div class="conversation-preview">{{ conversation.preview }}</div>
              <div class="conversation-date">{{ formatDate(conversation.lastUpdated) }}</div>
            </div>
            <div class="conversation-actions">
              <button 
                v-if="conversation.message_count > 2"
                class="action-btn expand-btn" 
                title="展开历史问题"
                @click.stop="toggleConversationExpand(conversation.id)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline v-if="!isConversationExpanded(conversation.id)" points="6 9 12 15 18 9"></polyline>
                  <polyline v-else points="18 15 12 9 6 15"></polyline>
                </svg>
              </button>
              <button 
                class="action-btn delete-btn" 
                title="删除对话"
                @click.stop="handleDeleteConversation(conversation.id)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </div>
          
          <!-- 展开的用户问题历史 -->
          <div v-if="isConversationExpanded(conversation.id)" class="conversation-history">
            <div v-if="isHistoryLoading(conversation.id)" class="history-loading">
              <div class="history-spinner"></div>
              <span>加载历史问题中...</span>
            </div>
            <div v-else-if="getUserQuestions(conversation).length === 0" class="history-empty">
              没有找到用户问题
            </div>
            <div 
              v-else 
              v-for="(question, index) in getUserQuestions(conversation)" 
              :key="index" 
              class="history-question"
              @click.stop="handleJumpToQuestion(conversation.id, question.index)"
            >
              <div class="question-content">{{ question.content }}</div>
              <div class="question-time">{{ formatDate(question.timestamp) }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="filteredConversations.length === 0" class="no-results">
          没有找到匹配的对话
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100%;
  width: 100%;
  overflow: hidden;
  position: relative;
}

.sidebar-right {
  width: 300px;
  height: 100%;
  background-color: var(--color-background-soft, #f8fafc);
  border-left: none;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: absolute;
  right: 0;
  top: 0;
  z-index: 10;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: none;
}

.new-chat-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0.75rem;
  background: var(--color-primary, linear-gradient(90deg, #4f74e3 0%, #5e60ce 100%));
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 1rem;
}

.new-chat-button:hover {
  box-shadow: 0 4px 6px rgba(79, 116, 227, 0.2);
  transform: translateY(-1px);
}

.new-chat-button svg {
  margin-right: 0.5rem;
}

.search-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  padding-left: 2.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: var(--color-background-mute, #f1f3f4);
  color: var(--color-text, #333);
}

.search-input:focus {
  outline: none;
  border-color: transparent;
  box-shadow: 0 0 0 2px rgba(79, 116, 227, 0.2);
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-soft, #94a3b8);
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.list-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-soft, #64748b);
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.conversation-item {
  display: flex;
  flex-direction: column;
  border-radius: 6px;
  transition: background-color 0.2s;
  margin-bottom: 0.5rem;
  position: relative;
  border: none;
}

.conversation-item:hover {
  background-color: var(--color-background-mute, #f1f5f9);
}

.conversation-item.active {
  background-color: var(--color-background-soft, #e2e8f0);
}

.conversation-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  width: 100%;
}

.conversation-content {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.conversation-title {
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--color-text, #333);
}

.conversation-preview {
  font-size: 0.875rem;
  color: var(--color-text-soft, #64748b);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-date {
  font-size: 0.75rem;
  color: var(--color-text-soft, #94a3b8);
  margin-top: 0.25rem;
}

.conversation-actions {
  display: flex;
  gap: 0.5rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .conversation-actions {
  opacity: 1;
}

.action-btn {
  background: transparent;
  border: none;
  color: var(--color-text-soft, #64748b);
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--color-text, #334155);
}

.action-btn.delete-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.loading-state p {
  margin-top: 1rem;
  color: var(--color-text-soft, #64748b);
  font-size: 0.875rem;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(79, 116, 227, 0.2);
  border-top-color: var(--color-primary, #4f74e3);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {transform: rotate(360deg);}
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.no-results {
  padding: 2rem 0;
  text-align: center;
  color: var(--color-text-soft, #64748b);
  font-size: 0.875rem;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
  overflow: hidden;
  margin-right: 300px;
  transition: all 0.3s ease;
}

.chat-container.center-layout {
  justify-content: center;
  align-items: center;
  display: flex;
  flex-direction: column;
}

.chat-container.center-layout .chat-messages {
  justify-content: center;
  align-items: center;
  flex: 0;
  margin-bottom: 0;
  padding-top: 0;
  height: auto;
}

.welcome-card {
  text-align: center;
  padding: 2rem;
  margin-bottom: 2rem;
  background-color: transparent;
  border-radius: 0.75rem;
  max-width: 80%;
  animation: fade-in 0.5s ease-out;
  box-shadow: none;
}

.welcome-card h2 {
  margin-bottom: 0;
  color: var(--color-text, #334155);
  font-size: 2rem;
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

@keyframes blink {
  0% { opacity: 0.6; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
  100% { opacity: 0.6; transform: scale(1); }
}

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

.chat-container.center-layout .center-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  padding: 0 1rem;
  margin-top: -25vh;
}

.chat-container.center-layout .chat-input-container {
  position: relative;
  margin-top: 0;
  width: 100%;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: var(--color-background-soft, #f5f5f5);
}

.expand-btn {
  background: transparent;
  border: none;
  color: var(--color-text-soft, #64748b);
  padding: 0.25rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.expand-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
  color: var(--color-text, #334155);
}

.conversation-history {
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.5rem;
  background-color: var(--color-background-mute, #edf2f7);
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
}

.history-question {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: var(--color-background, #ffffff);
  border-left: 3px solid var(--color-primary, #4f74e3);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.history-question:hover {
  background-color: var(--color-background-soft, #f8fafc);
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.history-question:last-child {
  margin-bottom: 0;
}

.question-content {
  font-size: 14px;
  color: var(--color-text, #334155);
  margin-bottom: 8px;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.question-time {
  font-size: 12px;
  color: var(--color-text-soft, #94a3b8);
  display: flex;
  align-items: center;
}

.question-time::before {
  content: '';
  display: inline-block;
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='12' height='12' stroke='%2394a3b8' stroke-width='2' fill='none' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'%3E%3C/circle%3E%3Cpolyline points='12 6 12 12 16 14'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: center;
  margin-right: 4px;
}

.history-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 1rem;
  color: var(--color-text-soft, #64748b);
  font-size: 0.875rem;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  margin: 0.5rem 0;
}

.history-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(79, 116, 227, 0.2);
  border-top-color: var(--color-primary, #4f74e3);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.history-empty {
  text-align: center;
  padding: 1rem;
  color: var(--color-text-soft, #64748b);
  font-size: 0.875rem;
  background-color: var(--color-background, #ffffff);
  border-radius: 6px;
  border-left: 3px solid var(--color-border, #cbd5e1);
  margin: 0.5rem 0;
}

.highlighted {
  animation: highlight-pulse 3s ease;
}

@keyframes highlight-pulse {
  0% { background-color: rgba(79, 116, 227, 0.1); }
  50% { background-color: rgba(79, 116, 227, 0.2); }
  100% { background-color: transparent; }
}

@media (max-width: 768px) {
  .sidebar-right {
    width: 100%;
    height: 100%;
    position: fixed;
    transform: translateX(100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar-right.show {
    transform: translateX(0);
  }
  
  .chat-container {
    margin-right: 0;
  }
  
  .chat-input-container.centered-input {
    max-width: 90%;
  }
}
</style>
