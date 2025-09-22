<script setup lang="ts">
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useConversations } from '../../composables/useConversations'
import { useChat } from '../../composables/useChat'
import { getGreeting, formatDate } from '../../utils/dateUtils'
import { formatMessage, autoResizeTextarea, scrollToBottom, focusInput } from '../../utils/messageUtils'

// 导入AI头像
import aiAvatar from '../../assets/static/ai_touxiang.png'

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
  toggleConversationExpand,
  isConversationExpanded,
  isHistoryLoading,
  getUserQuestions,
  saveTempConversationToCache,
  loadTempConversationFromCache,
  removeTempConversationFromCache
} = useConversations()

const {
  userInput,
  isLoading,
  activeConversationId,
  isCenterLayout,
  sendMessage,
  switchConversation,
  jumpToQuestion
} = useChat(removeTempConversationFromCache)

// 本地状态
const messagesContainer = ref<HTMLElement | null>(null)
const inputElement = ref<HTMLTextAreaElement | null>(null)
const searchQuery = ref('')

// 功能开关状态
const deepThinkingEnabled = ref(false)
const webSearchEnabled = ref(false)

// 附件上传相关状态
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFiles = ref<File[]>([])

// 计算属性

/**
 * 用户显示名称
 * 获取用户的显示名称，优先使用昵称，其次用户名，最后使用默认值
 */
const userDisplayName = computed(() => {
  return authStore.userInfo?.nickname || authStore.userInfo?.username || '用户'
})

/**
 * 问候语
 * 根据当前时间生成相应的问候语（早上好、下午好等）
 */
const greeting = computed(() => {
  return getGreeting()
})

/**
 * 当前对话的消息列表
 * 获取当前活动对话的所有消息
 */
const messages = computed(() => {
  const conversation = conversations.find(c => c.id === activeConversationId.value)
  return conversation ? conversation.messages : []
})

/**
 * 过滤后的对话列表
 * 根据搜索查询条件过滤对话列表
 */
const filteredConversations = computed(() => {
  return getFilteredConversations(searchQuery.value)
})

// 方法

/**
 * 处理发送消息
 * 调用聊天功能发送用户输入的消息，并在完成后滚动到底部和聚焦输入框
 */
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

/**
 * 处理键盘按下事件
 * 当用户按下Enter键（非Shift+Enter）时发送消息
 */
const handleKeyDownEvent = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSendMessage()
  }
}

/**
 * 处理切换对话
 * 切换到指定ID的对话，并在完成后滚动到底部和聚焦输入框
 */
const handleSwitchConversation = async (id: number) => {
  await switchConversation(id, conversations, loadConversationDetail)
  nextTick(() => {
    scrollToBottomContainer()
    focusInputElement()
  })
}

/**
 * 处理删除对话
 * 删除指定ID的对话，如果删除的是当前对话则创建新对话
 */
const handleDeleteConversation = async (id: number) => {
  const success = await deleteConversation(id)
  if (success) {
    // 如果删除的是当前对话，切换到其他对话
    if (activeConversationId.value === id) {
      await handleCreateNewConversation()
    }
  }
}

/**
 * 处理创建新对话
 * 创建一个新的对话，如果当前已有空的临时对话则直接使用
 */
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
    
    // 如果是临时对话，保存到缓存
    if (newConversation.isTemporary) {
      saveTempConversationToCache(newConversation)
    }
    
    // 聚焦输入框
    nextTick(() => {
      focusInputElement()
    })
  }
}

/**
 * 处理跳转到特定问题
 * 跳转到指定对话中的特定问题位置
 */
const handleJumpToQuestion = (conversationId: number, questionIndex: number) => {
  jumpToQuestion(conversationId, questionIndex, conversations, loadConversationDetail, scrollToQuestion)
}

/**
 * 处理文件选择
 * 当用户选择文件后，将文件添加到选中文件列表
 */
const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    // 将FileList转换为数组并添加到选中文件列表
    selectedFiles.value = [...Array.from(target.files)]
    
    // 重新创建input元素以允许重复选择同一文件
    if (fileInputRef.value) {
      const newInput = document.createElement('input')
      newInput.type = 'file'
      newInput.multiple = true
      newInput.addEventListener('change', handleFileSelect)
      fileInputRef.value.parentNode?.replaceChild(newInput, fileInputRef.value)
      fileInputRef.value = newInput
    }
  }
}

/**
 * 触发文件选择对话框
 * 当用户点击上传按钮时，触发隐藏的文件选择输入框
 */
const triggerFileSelect = () => {
  fileInputRef.value?.click()
}

/**
 * 移除指定的选中文件
 * 从选中文件列表中移除指定索引的文件
 */
const removeSelectedFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
}

/**
 * 清空所有选中的文件
 * 清空选中文件列表
 */
const clearSelectedFiles = () => {
  selectedFiles.value = []
}

/**
 * 滚动到底部
 * 将消息容器滚动到最底部
 */
const scrollToBottomContainer = () => {
  if (messagesContainer.value) {
    scrollToBottom(messagesContainer.value)
  }
}

/**
 * 滚动到特定问题
 * 将消息容器滚动到特定问题位置并添加高亮效果
 */
const scrollToQuestion = (element: HTMLElement) => {
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    
    // 添加高亮效果
    element.classList.add('highlight')
    setTimeout(() => {
      element.classList.remove('highlight')
    }, 2000)
  }
}

/**
 * 聚焦输入框
 * 使输入框获得焦点
 */
const focusInputElement = () => {
  if (inputElement.value) {
    focusInput(inputElement.value)
  }
}

/**
 * 处理用户输入
 * 监听用户输入变化，自动调整输入框高度
 */
const handleUserInput = (e: Event) => {
  const target = e.target as HTMLTextAreaElement
  autoResizeTextarea(target)
}

/**
 * 监听输入框内容变化
 * 当输入框内容变化时，处理临时对话缓存
 */
watch(userInput, (newValue) => {
  // 如果当前对话是临时对话且用户输入了内容，保存到缓存
  if (activeConversationId.value !== null) {
    const activeConv = conversations.find(c => c.id === activeConversationId.value)
    if (activeConv && activeConv.isTemporary && newValue.trim()) {
      saveTempConversationToCache(activeConv)
    }
  }
})

/**
 * 组件挂载时的生命周期钩子
 * 加载对话历史、处理缓存的临时对话、初始化UI状态
 */
onMounted(async () => {
  try {
    // 尝试从缓存加载临时对话
    const tempConversation = loadTempConversationFromCache()
    if (tempConversation) {
      conversations.push(tempConversation)
      activeConversationId.value = tempConversation.id
      isCenterLayout.value = true
    } else {
      // 创建新的临时对话
      await handleCreateNewConversation()
    }
    
    // 加载用户的对话历史
    await loadConversationsFromServer()
    
    // 聚焦输入框
    focusInputElement()
  } catch (error) {
    console.error('加载对话历史失败:', error)
    // 如果加载失败，创建一个新的临时对话
    await handleCreateNewConversation()
  }
})
</script>

<template>
  <div class="chat-container">
    <!-- 聊天主区域 -->
    <div class="chat-main" :class="{ 'center-layout': isCenterLayout }">
      <!-- 居中布局内容包装器 -->
      <div v-if="isCenterLayout" class="center-content-wrapper">
        <!-- 欢迎信息卡片 -->
        <div class="welcome-card">
          <img src="../../assets/static/ai_touxiang.png" alt="AI助手" class="welcome-image">
          <h1 class="welcome-title">AI助手</h1>
          <p class="welcome-subtitle">{{ greeting }}, {{ userDisplayName }}！</p>
          <p class="welcome-description">我是你的AI助手，可以回答问题、提供建议、协助写作等。</p>
          <div class="welcome-features">
            <div class="feature-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
              </svg>
              <span>智能对话</span>
            </div>
            <div class="feature-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9.4 16.6 4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4z"></path>
                <path d="M14.6 16.6l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"></path>
              </svg>
              <span>快速搜索</span>
            </div>
            <div class="feature-item">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
              <span>深度思考</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 常规对话布局 -->
      <div v-else class="chat-content">
        <!-- 消息列表 -->
        <div ref="messagesContainer" class="chat-messages">
          <!-- 消息渲染 -->
          <div v-for="(message, index) in messages" :key="index" class="message-wrapper">
            <!-- 用户消息 -->
            <div v-if="message.role === 'user'" class="message user-message">
              <div class="avatar-container">
                <div class="avatar user-avatar">{{ userDisplayName.charAt(0) }}</div>
              </div>
              <div class="message-content">
                <div class="message-bubble">
                  <div v-html="formatMessage(message.content)"></div>
                </div>
                <div class="message-time">{{ formatDate(message.timestamp) }}</div>
              </div>
            </div>

            <!-- AI消息 -->
            <div v-else class="message ai-message">
              <div class="avatar-container">
                <div class="avatar ai-avatar">
                  <img :src="aiAvatar" alt="AI">
                </div>
              </div>
              <div class="message-content">
                <div class="message-bubble">
                  <div v-if="isLoading && index === messages.length - 1" class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                  </div>
                  <div v-else-if="message.thinking_process && message.is_thinking" class="thinking-process">
                    <div class="thinking-header">正在思考...</div>
                    <div v-html="formatMessage(message.thinking_process)"></div>
                  </div>
                  <div v-else v-html="formatMessage(message.content)"></div>
                </div>
                <div class="message-time">{{ formatDate(message.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-container">
          <!-- 功能开关区域 -->
          <div class="feature-toggle-area">
            <button 
              class="feature-toggle-btn" 
              :class="{ 'active': deepThinkingEnabled }"
              @click="deepThinkingEnabled = !deepThinkingEnabled"
              title="启用深度思考模式"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <circle cx="12" cy="12" r="6"></circle>
                <circle cx="12" cy="12" r="2"></circle>
              </svg>
              <span>深度思考</span>
            </button>
            <button 
              class="feature-toggle-btn" 
              :class="{ 'active': webSearchEnabled }"
              @click="webSearchEnabled = !webSearchEnabled"
              title="启用联网搜索"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              <span>联网搜索</span>
            </button>
          </div>

          <!-- 选中文件显示区域 -->
          <div v-if="selectedFiles.length > 0" class="selected-files">
            <div class="selected-files-header">
              <span>已选择 {{ selectedFiles.length }} 个文件</span>
              <button class="clear-files-btn" @click="clearSelectedFiles" title="清空所有文件">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            <div class="files-list">
              <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
                <div class="file-info">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">{{ (file.size / 1024).toFixed(1) }}KB</span>
                </div>
                <button class="remove-file-btn" @click="removeSelectedFile(index)" title="移除文件">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- 输入框区域 -->
          <div class="input-wrapper">
            <textarea
              ref="inputElement"
              v-model="userInput"
              class="chat-input"
              placeholder="输入问题..."
              rows="1"
              @keydown="handleKeyDownEvent"
              @input="handleUserInput"
              :disabled="isLoading"
            ></textarea>
            <div class="input-actions">
              <button 
                class="action-btn file-upload-btn"
                @click="triggerFileSelect"
                :disabled="isLoading"
                title="上传文件"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="7 10 12 15 17 10"></polyline>
                  <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
              </button>
              <button 
                class="action-btn send-btn"
                @click="handleSendMessage"
                :disabled="isLoading || !userInput.trim()"
                title="发送消息 (Enter)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
          </div>
          <input 
            ref="fileInputRef"
            type="file"
            multiple
            class="hidden-file-input"
            @change="handleFileSelect"
          />
        </div>
      </div>
    </div>

    <!-- 右侧功能区 -->
    <div class="chat-sidebar">
      <!-- 新建对话按钮 -->
      <div class="sidebar-header">
        <button 
          class="new-conversation-btn"
          @click="handleCreateNewConversation"
          :disabled="isLoading"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          <span>新建对话</span>
        </button>
      </div>

      <!-- 搜索容器 -->
      <div class="search-container">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input 
          type="text" 
          v-model="searchQuery"
          class="search-input"
          placeholder="搜索对话..."
        />
        <button 
          v-if="searchQuery"
          class="clear-search-btn"
          @click="searchQuery = ''"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- 历史对话列表 -->
      <div class="conversations-list">
        <div v-if="isLoadingConversations || isHistoryLoading" class="loading-container">
          <div class="loading-spinner"></div>
          <span class="loading-text">加载中...</span>
        </div>
        <div v-else-if="filteredConversations.length === 0" class="empty-container">
          <div class="empty-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
            </svg>
          </div>
          <p class="empty-text">
            {{ searchQuery ? '没有找到匹配的对话' : '暂无对话历史' }}
          </p>
          <p class="empty-hint">
            {{ searchQuery ? '尝试使用其他关键词搜索' : '开始您的第一次对话吧' }}
          </p>
        </div>
        <div v-else class="conversations-scroll">
          <div 
            v-for="conversation in filteredConversations"
            :key="conversation.id"
            class="conversation-item"
            :class="{ 'active': activeConversationId === conversation.id, 'temporary': conversation.isTemporary }"
            @click="handleSwitchConversation(conversation.id)"
          >
            <div class="conversation-header">
              <h3 class="conversation-title">{{ conversation.title }}</h3>
              <button 
                class="delete-conversation-btn"
                @click.stop="handleDeleteConversation(conversation.id)"
                title="删除对话"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
            <div class="conversation-preview">
              <p class="preview-text">{{ conversation.preview || '新对话' }}</p>
              <span class="conversation-date">{{ formatDate(conversation.lastUpdated || conversation.created_at) }}</span>
            </div>
            <div v-if="conversation.id !== activeConversationId && !conversation.isTemporary" class="conversation-actions">
              <button 
                class="expand-conversation-btn"
                @click.stop="toggleConversationExpand(conversation.id)"
                title="展开对话内容"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>
            </div>
            <div 
              v-if="isConversationExpanded(conversation.id) && conversation.id !== activeConversationId && !conversation.isTemporary"
              class="conversation-content-preview"
            >
              <div class="question-item" v-for="(question, qIndex) in getUserQuestions(conversation.id)" :key="qIndex">
                <div class="question-text">{{ question.content }}</div>
                <div class="question-date">{{ formatDate(question.timestamp) }}</div>
                <button 
                  class="jump-to-question-btn"
                  @click.stop="handleJumpToQuestion(conversation.id, qIndex)"
                  title="跳转到该问题"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m12 19-7-7 7-7"></path>
                    <path d="M19 12H5"></path>
                  </svg>
                </button>
              </div>
              <div v-if="getUserQuestions(conversation.id).length === 0" class="empty-questions">
                <p>暂无问题</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 侧边栏样式 */
.chat-sidebar {
  width: 300px;
  height: 100vh;
  background: #ffffff;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.new-conversation-btn {
  width: 100%;
  padding: 12px 16px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #333333;
  transition: all 0.2s ease;
}

.new-conversation-btn:hover:not(:disabled) {
  background: #e8e8e8;
  border-color: #d0d0d0;
}

.new-conversation-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-container {
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.search-container svg {
  position: absolute;
  left: 32px;
  top: 50%;
  transform: translateY(-50%);
  color: #888888;
}

.search-input {
  width: 100%;
  padding: 10px 16px 10px 40px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  border-color: #4a9eff;
}

.clear-search-btn {
  position: absolute;
  right: 32px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #888888;
  transition: color 0.2s ease;
}

.clear-search-btn:hover {
  color: #555555;
}

/* 对话列表样式 */
.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  margin-bottom: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fafafa;
  border: 1px solid transparent;
}

.conversation-item:hover {
  background: #f0f0f0;
  border-color: #e0e0e0;
}

.conversation-item.active {
  background: #e6f3ff;
  border-color: #4a9eff;
}

.conversation-item.temporary {
  opacity: 0.8;
  background: #fff5f5;
}

.conversation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.conversation-title {
  font-size: 14px;
  font-weight: 600;
  color: #333333;
  margin: 0;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.delete-conversation-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #888888;
  opacity: 0;
  transition: all 0.2s ease;
  border-radius: 4px;
}

.conversation-item:hover .delete-conversation-btn {
  opacity: 1;
}

.delete-conversation-btn:hover {
  background: #ff4757;
  color: #ffffff;
}

.conversation-preview {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.preview-text {
  font-size: 12px;
  color: #666666;
  margin: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
}

.conversation-date {
  font-size: 11px;
  color: #999999;
  white-space: nowrap;
}

/* 对话展开内容样式 */
.conversation-actions {
  display: flex;
  justify-content: flex-end;
}

.expand-conversation-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #888888;
  transition: color 0.2s ease;
  border-radius: 4px;
}

.expand-conversation-btn:hover {
  background: #e0e0e0;
  color: #555555;
}

.conversation-content-preview {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
}

.question-item {
  margin-bottom: 12px;
  padding: 8px;
  background: #ffffff;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
  position: relative;
}

.question-text {
  font-size: 12px;
  color: #444444;
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.question-date {
  font-size: 11px;
  color: #999999;
}

.jump-to-question-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  padding: 4px;
  opacity: 0;
  transition: all 0.2s ease;
}

.question-item:hover .jump-to-question-btn {
  opacity: 1;
}

.jump-to-question-btn:hover {
  background: #4a9eff;
  color: #ffffff;
}

.empty-questions {
  text-align: center;
  padding: 16px;
  color: #999999;
  font-size: 12px;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 12px;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4a9eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #666666;
  font-size: 14px;
}

/* 聊天容器样式 */
.chat-container {
  display: flex;
  height: 100vh;
  background: #f7f9fc;
}

.chat-main {
  flex: 1;
  display: flex;
  position: relative;
}

/* 居中布局样式 */
.chat-main.center-layout {
  align-items: center;
  justify-content: center;
  background: #f7f9fc;
}

.center-content-wrapper {
  max-width: 600px;
  padding: 40px;
  width: 100%;
}

.welcome-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 48px;
  text-align: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e8e8;
}

.welcome-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 24px;
  object-fit: cover;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #333333;
  margin: 0 0 8px 0;
}

.welcome-subtitle {
  font-size: 16px;
  color: #666666;
  margin: 0 0 16px 0;
}

.welcome-description {
  font-size: 14px;
  color: #888888;
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.welcome-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border-radius: 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  transition: all 0.2s ease;
}

.feature-item:hover {
  background: #e6f3ff;
  border-color: #4a9eff;
  transform: translateY(-2px);
}

.feature-item svg {
  color: #4a9eff;
}

.feature-item span {
  font-size: 12px;
  font-weight: 500;
  color: #333333;
}

/* 常规聊天布局 */
.chat-content {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  background: #ffffff;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 消息样式 */
.message-wrapper {
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.avatar-container {
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  overflow: hidden;
}

.user-avatar {
  background: #4a9eff;
}

.ai-avatar {
  background: #28a745;
}

.ai-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.user-message .message-content {
  margin-left: auto;
}

.message-bubble {
  background: #f0f0f0;
  padding: 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-wrap: break-word;
}

.user-message .message-bubble {
  background: #4a9eff;
  color: #ffffff;
}

.message-time {
  font-size: 11px;
  color: #999999;
  margin-top: 4px;
  text-align: right;
}

.user-message .message-time {
  color: #a0cfff;
}

/* AI回复状态样式 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  background: #888888;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-5px); }
}

.thinking-process {
  background: #f8f9fa;
  border-left: 3px solid #4a9eff;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.thinking-header {
  font-size: 12px;
  font-weight: 600;
  color: #4a9eff;
  margin-bottom: 8px;
}

/* 聊天输入容器样式 */
.chat-input-container {
  background: #ffffff;
  border-top: 1px solid #e0e0e0;
  padding: 16px 24px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 8px;
  transition: border-color 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: #4a9eff;
}

.chat-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  font-size: 14px;
  color: #333333;
  line-height: 1.4;
  padding: 12px;
  min-height: 40px;
  max-height: 120px;
}

.chat-input::placeholder {
  color: #999999;
}

.input-actions {
  display: flex;
  gap: 8px;
  align-items: flex-end;
  padding-bottom: 4px;
}

.action-btn {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  padding: 8px;
  color: #666666;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.action-btn:hover:not(:disabled) {
  background: #f0f0f0;
  color: #333333;
}

.send-btn:not(:disabled) {
  background: #4a9eff;
  color: #ffffff;
  border-color: #4a9eff;
}

.send-btn:not(:disabled):hover {
  background: #337ab7;
  border-color: #337ab7;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hidden-file-input {
  display: none;
}

/* 功能开关区域 */
.feature-toggle-area {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.feature-toggle-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: #666666;
  transition: all 0.2s ease;
}

.feature-toggle-btn:hover {
  background: #e9ecef;
  color: #333333;
}

.feature-toggle-btn.active {
  background: #4a9eff;
  color: #ffffff;
  border-color: #4a9eff;
}

/* 选中文件显示区域 */
.selected-files {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.selected-files-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.selected-files-header span {
  font-size: 12px;
  font-weight: 500;
  color: #333333;
}

.clear-files-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #888888;
  transition: color 0.2s ease;
}

.clear-files-btn:hover {
  color: #ff4757;
}

.files-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 8px 12px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.file-info svg {
  color: #888888;
}

.file-name {
  font-size: 12px;
  color: #333333;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 11px;
  color: #888888;
}

.remove-file-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: #888888;
  transition: color 0.2s ease;
}

.remove-file-btn:hover {
  color: #ff4757;
}

/* 空状态样式 */
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
}

.empty-icon {
  opacity: 0.2;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 16px;
  font-weight: 500;
  color: #666666;
  margin: 0;
}

.empty-hint {
  font-size: 14px;
  color: #999999;
  margin: 0;
  text-align: center;
}

/* 高亮动画效果 */
@keyframes highlight {
  0% { background-color: rgba(74, 158, 255, 0.2); }
  100% { background-color: transparent; }
}

.highlight {
  animation: highlight 2s ease-in-out;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .chat-container {
    flex-direction: column;
  }
  
  .chat-sidebar {
    width: 100%;
    height: auto;
    max-height: 200px;
  }
  
  .chat-main {
    height: calc(100vh - 200px);
  }
  
  .center-content-wrapper {
    padding: 20px;
  }
  
  .welcome-card {
    padding: 32px 24px;
  }
  
  .welcome-features {
    grid-template-columns: repeat(1, 1fr);
    gap: 16px;
  }
  
  .message-content {
    max-width: 85%;
  }
  
  .feature-toggle-area {
    flex-wrap: wrap;
  }
}

/* 确保滚动条样式统一 */
.chat-messages::-webkit-scrollbar,
.conversations-list::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track,
.conversations-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb,
.conversations-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.conversations-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>