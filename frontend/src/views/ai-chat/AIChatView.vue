<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useConversations } from '@/composables/useConversations'
import { useChat } from '@/composables/useChat'
import { focusInput as focusInputElement } from '@/utils/messageUtils'
import { apiService } from '@/services/api'

// 导入子组件
import WelcomeMessage from './components/WelcomeMessage.vue'
import MessageList from './components/MessageList.vue'
import ChatInput from './components/ChatInput.vue'
import ChatSidebar from './components/ChatSidebar.vue'
import RenameDialog from '@/components/RenameDialog.vue'

// 状态管理
const authStore = useAuthStore()
const themeStore = useThemeStore()

// 组合式函数
const {
  conversations,
  isLoadingConversations,
  getFilteredConversations,
  loadConversationDetail,
  loadConversationsFromServer,
  deleteConversation,
  toggleConversationExpand,
  isConversationExpanded,
  isHistoryLoading,
  getUserQuestions,
  pinConversation,
  sortConversations,
  removeTempConversationFromCache
} = useConversations()

const {
  userInput,
  isLoading,
  activeConversationId,
  isCenterLayout,
  sendMessage,
  switchConversation,
  jumpToQuestion,
  skipTypingAnimation
} = useChat(removeTempConversationFromCache)

// 本地状态
const messageListRef = ref<InstanceType<typeof MessageList> | null>(null)
const chatInputRef = ref<InstanceType<typeof ChatInput> | null>(null)
const sidebarRef = ref<InstanceType<typeof ChatSidebar> | null>(null)

// 功能开关状态
const deepThinkingEnabled = ref(false)
const webSearchEnabled = ref(false)

// 重命名弹窗状态
const showRenameDialog = ref(false)
const renamingConversationId = ref<number | null>(null)
const renamingConversationTitle = ref('')

// 计算属性
const messages = computed(() => {
  const conversation = conversations.find(c => c.id === activeConversationId.value)
  return conversation ? conversation.messages : []
})

const filteredConversations = computed(() => {
  const searchQuery = sidebarRef.value?.searchQuery || ''
  const conversations = getFilteredConversations(searchQuery)
  // 过滤掉标题为"新对话"的对话
  return conversations.filter(conv => conv.title !== '新对话')
})

// 事件处理方法
const handleSendMessage = async () => {
  await sendMessage(conversations, (conversation) => {
    // 对话更新后的回调
    nextTick(() => {
      scrollToBottom()
      focusInputElement(chatInputRef.value?.inputElement || null)
    })
  }, {
    deepThinking: deepThinkingEnabled.value,
    webSearch: webSearchEnabled.value,
    sortConversations: sortConversations
  })
}

const handleSwitchConversation = async (id: number) => {
  await switchConversation(id, conversations, loadConversationDetail)
  nextTick(() => {
    scrollToBottom()
    focusInputElement(chatInputRef.value?.inputElement || null)
  })
}

const handleDeleteConversation = async (id: number) => {
  const success = await deleteConversation(id)
  if (success) {
    // 如果删除的是当前活动对话，准备新对话界面
    if (activeConversationId.value === id) {
      console.log("删除了当前活动对话，准备新对话界面")
      handleCreateNewConversation()
    }
  }
}

/**
 * 准备新对话界面
 * 不创建实际对话，只准备UI状态，对话将在用户发送第一条消息时创建
 * 
 * 新的流程：
 * 1. 用户点击"新建对话" → 调用此函数准备UI
 * 2. 用户输入消息并发送 → 在发送消息时动态创建实际对话
 * 3. 避免了创建无用的空对话，提升性能和用户体验
 */
const prepareNewConversationUI = () => {
  console.log("准备新对话界面")
  
  // 清空当前活动对话ID (重要：这样就不会有活动对话，触发居中布局)
  activeConversationId.value = null
  
  // 设置居中布局（显示欢迎界面）
  isCenterLayout.value = true
  
  // 重置输入框内容
  userInput.value = ''
  
  // 清除任何缓存的临时对话数据
  removeTempConversationFromCache()
  
  // 聚焦到输入框，方便用户立即开始输入
  nextTick(() => {
    focusInputElement(chatInputRef.value?.inputElement || null)
  })
}

/**
 * 处理新建对话点击事件
 */
const handleCreateNewConversation = () => {
  console.log("用户点击新建对话")
  
  // 直接准备新对话UI，不创建实际对话
  prepareNewConversationUI()
}

const handleJumpToQuestion = (conversationId: number, questionIndex: number) => {
  jumpToQuestion(conversationId, questionIndex, conversations, loadConversationDetail, scrollToQuestion)
}

// 处理新的对话操作
const handlePinConversation = async (id: number) => {
  const success = await pinConversation(id)
  if (!success) {
    console.error('置顶操作失败')
  }
}

const handleRenameConversation = async (id: number) => {
  const conversation = conversations.find(c => c.id === id)
  if (!conversation) return
  
  // 获取当前显示的标题（优先使用自定义标题）
  const currentTitle = conversation.custom_title || conversation.title
  
  // 显示重命名弹窗
  renamingConversationId.value = id
  renamingConversationTitle.value = currentTitle
  showRenameDialog.value = true
}

// 确认重命名
const confirmRename = async (newTitle: string) => {
  if (!renamingConversationId.value) return
  
  const conversation = conversations.find(c => c.id === renamingConversationId.value)
  if (!conversation) return
  
  const currentTitle = conversation.custom_title || conversation.title
  
  if (newTitle.trim() !== currentTitle) {
    try {
      // 调用API更新对话标题
      const response = await apiService.renameConversation(renamingConversationId.value, newTitle.trim())
      
      if (response.code === 200 || response.code === 0) {
        // 更新本地数据
        conversation.custom_title = newTitle.trim()
        conversation.display_title = newTitle.trim()
        console.log('重命名对话成功:', renamingConversationId.value, '新标题:', newTitle.trim())
      } else {
        console.error('重命名对话失败:', response.message)
        alert('重命名失败: ' + response.message)
      }
    } catch (error) {
      console.error('重命名对话失败:', error)
      alert('重命名失败，请稍后重试')
    }
  }
  
  // 重置状态
  renamingConversationId.value = null
  renamingConversationTitle.value = ''
}

const handleDownloadConversation = async (id: number) => {
  try {
    const conversation = conversations.find(c => c.id === id)
    if (!conversation) return
    
    // 创建下载内容
    const content = {
      title: conversation.title,
      id: conversation.id,
      created_at: (conversation as any).created_at || new Date().toISOString(),
      updated_at: (conversation as any).updated_at || new Date().toISOString(),
      messages: conversation.messages || []
    }
    
    // 创建文件并下载
    const blob = new Blob([JSON.stringify(content, null, 2)], { 
      type: 'application/json;charset=utf-8' 
    })
    const url = URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = `conversation_${conversation.title.replace(/[^\w\s-]/g, '').trim()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    console.log('下载对话:', id)
  } catch (error) {
    console.error('下载对话失败:', error)
  }
}

// 工具方法
const scrollToBottom = () => {
  messageListRef.value?.scrollToBottomContainer()
}

const focusInput = () => {
  chatInputRef.value?.focusInput()
}

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
    const messagesContainer = messageListRef.value?.messagesContainer
    const messageElements = messagesContainer?.querySelectorAll('.message-wrapper')
    if (messageElements && targetIndex < messageElements.length) {
      messageElements[targetIndex].scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

// 生命周期
onMounted(async () => {
  // 初始化主题
  themeStore.loadTheme()
  
  // 加载对话列表
  await loadConversationsFromServer()
  
  // 直接准备新对话界面，不需要检查缓存或创建实际对话
  console.log("页面初始化，准备新对话界面")
  prepareNewConversationUI()
})
</script>

<template>
  <div class="app-container">
    <!-- 聊天主区域 -->
    <div class="chat-container" :class="{ 'center-layout': isCenterLayout }">
      <!-- 居中布局内容包装器 -->
      <div v-if="isCenterLayout" class="center-content">
        <!-- 欢迎消息 -->
        <WelcomeMessage />
        
        <!-- 输入区域 -->
        <ChatInput
          ref="chatInputRef"
          v-model:user-input="userInput"
          v-model:deep-thinking-enabled="deepThinkingEnabled"
          v-model:web-search-enabled="webSearchEnabled"
          :is-loading="isLoading"
          :is-center-layout="isCenterLayout"
          @send-message="handleSendMessage"
        />
      </div>
      
      <!-- 常规布局 -->
      <template v-else>
        <!-- 消息列表 -->
        <MessageList
          ref="messageListRef"
          :messages="messages"
          :is-loading="isLoading"
          @skip-typing="skipTypingAnimation"
        />
        
        <!-- 输入区域 -->
        <ChatInput
          ref="chatInputRef"
          v-model:user-input="userInput"
          v-model:deep-thinking-enabled="deepThinkingEnabled"
          v-model:web-search-enabled="webSearchEnabled"
          :is-loading="isLoading"
          :is-center-layout="isCenterLayout"
          @send-message="handleSendMessage"
        />
      </template>
    </div>
    
    <!-- 侧边栏 -->
    <ChatSidebar
      ref="sidebarRef"
      :conversations="conversations"
      :active-conversation-id="activeConversationId"
      :is-loading-conversations="isLoadingConversations"
      :is-history-loading="isHistoryLoading"
      :filtered-conversations="filteredConversations"
      :is-conversation-expanded="isConversationExpanded"
      :get-user-questions="(id: number) => {
        const conv = conversations.find(c => c.id === id);
        if (!conv) return [];
        return getUserQuestions(conv).map(q => q.content);
      }"
      @create-new-conversation="handleCreateNewConversation"
      @switch-conversation="handleSwitchConversation"
      @delete-conversation="handleDeleteConversation"
      @toggle-conversation-expand="toggleConversationExpand"
      @jump-to-question="handleJumpToQuestion"
      @pin-conversation="handlePinConversation"
      @rename-conversation="handleRenameConversation"
      @download-conversation="handleDownloadConversation"
    />
    
    <!-- 重命名弹窗 -->
    <RenameDialog
      v-model:visible="showRenameDialog"
      title="重命名对话"
      :default-value="renamingConversationTitle"
      @confirm="confirmRename"
    />
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background: var(--color-background, #ffffff);
  overflow: hidden;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  background: var(--color-background, #ffffff);
  order: 1;
}

.chat-container.center-layout {
  justify-content: center;
  align-items: center;
  padding: 2rem;
  background: var(--color-background, linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%));
  position: relative;
  overflow: hidden;
}

/* 未来科技风背景特效 */
.chat-container.center-layout::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle at 30% 70%, 
    var(--color-primary, rgba(0, 245, 255, 0.1)) 0%, 
    transparent 50%
  ),
  radial-gradient(
    circle at 70% 30%, 
    var(--color-accent, rgba(255, 0, 128, 0.1)) 0%, 
    transparent 50%
  );
  animation: backgroundFloat 8s ease-in-out infinite;
  pointer-events: none;
  z-index: -1;
}

@keyframes backgroundFloat {
  0%, 100% {
    transform: rotate(0deg) translateX(0px);
  }
  50% {
    transform: rotate(180deg) translateX(20px);
  }
}

.center-content {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .app-container {
  flex-direction: column;
  }
}

@media (max-width: 768px) {
  .chat-container.center-layout {
  padding: 1rem;
  }
  
  .center-content {
    gap: 1rem;
  }
}

/* 全局霓虹滚动条样式 */
:deep(*::-webkit-scrollbar) {
  width: 8px;
  height: 8px;
}

:deep(*::-webkit-scrollbar-track) {
  background: var(--color-surface, #f1f1f1);
  border-radius: 10px;
}

:deep(*::-webkit-scrollbar-thumb) {
  background: var(--color-primary, linear-gradient(45deg, #00f5ff, #9d4edd));
  border-radius: 10px;
  box-shadow: 0 0 10px var(--color-primary, rgba(0, 245, 255, 0.5));
  transition: all 0.3s ease;
}

:deep(*::-webkit-scrollbar-thumb:hover) {
  background: var(--color-primary, linear-gradient(45deg, #00d4ff, #8b3fd9));
  box-shadow: 0 0 15px var(--color-primary, rgba(0, 245, 255, 0.8));
}

/* 针对Firefox的滚动条样式 */
:deep(*) {
  scrollbar-width: thin;
  scrollbar-color: var(--color-primary, #00f5ff) var(--color-surface, #f1f1f1);
}
</style>
