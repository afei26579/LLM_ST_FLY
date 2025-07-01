<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, watch, computed } from 'vue'
import { apiService } from '../services/api'
import type { ChatMessage as ApiChatMessage } from '../services/api'
import { useAuthStore } from '../stores/auth'

// 导入AI头像
import aiAvatar from '../assets/static/ai_touxiang.png'

const userInput = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputElement = ref<HTMLTextAreaElement | null>(null)
const searchQuery = ref('')
const activeConversationId = ref<number | null>(null)
const authStore = useAuthStore()
const isCenterLayout = ref(false)
// 跟踪哪些对话展开了历史记录
const expandedConversations = ref<Set<number>>(new Set())
// 跟踪哪些对话正在加载历史记录
const loadingHistoryConversations = ref<Set<number>>(new Set())

// 根据当前时间获取问候语
const getGreeting = () => {
  const hour = new Date().getHours()
  if (hour >= 5 && hour < 12) {
    return '上午好'
  } else if (hour >= 12 && hour < 14) {
    return '中午好'
  } else if (hour >= 14 && hour < 18) {
    return '下午好'
  } else {
    return '晚上好'
  }
}

// 计算用户显示名称
const userDisplayName = computed(() => {
  return authStore.userInfo?.nickname || authStore.userInfo?.username || '用户'
})

// 计算问候语
const greeting = computed(() => {
  return getGreeting()
})

// 聊天消息（扩展API的ChatMessage类型）
interface ChatMessage extends ApiChatMessage {
  // 保持与API的ChatMessage兼容，同时可以添加UI特定的属性
}

// 对话类型（使用API中定义的类型）
import type { Conversation as ApiConversation } from '../services/api'

// 扩展API的Conversation类型，添加UI特定的属性
interface Conversation {
  id: number
  title: string
  messages: ChatMessage[]
  lastUpdated: Date
  preview: string
  message_count: number
  last_message?: ChatMessage
  isTemporary?: boolean // 是否为临时对话
}

// 历史对话列表
const conversations = reactive<Conversation[]>([])

// 加载状态
const isLoadingConversations = ref(false)

// 当前对话的消息
const messages = computed(() => {
  const conversation = conversations.find(c => c.id === activeConversationId.value)
  return conversation ? conversation.messages : []
})

// 过滤后的对话列表（用于搜索）
const filteredConversations = computed(() => {
  if (!searchQuery.value.trim()) {
    return conversations.slice().sort((a, b) => b.lastUpdated.getTime() - a.lastUpdated.getTime())
  }
  
  const query = searchQuery.value.toLowerCase()
  return conversations
    .filter(conversation => {
      // 搜索标题
      if (conversation.title.toLowerCase().includes(query)) return true
      
      // 搜索消息内容
      return conversation.messages.some(message => 
        message.content.toLowerCase().includes(query)
      )
    })
    .sort((a, b) => b.lastUpdated.getTime() - a.lastUpdated.getTime())
})

// 创建新对话 - 仅在前端创建临时对话
const createNewConversation = async () => {
  try {
    // 如果当前对话是个空对话且是临时对话，就直接使用它
    if (activeConversationId.value !== null) {
      const activeConv = conversations.find(c => c.id === activeConversationId.value)
      if (activeConv && activeConv.messages.length === 0 && activeConv.isTemporary) {
        console.log("当前已有临时空对话，不创建新对话")
        isCenterLayout.value = true
        return activeConv
      }
    }
    
    console.log("开始创建新对话（仅前端）")
    
    // 生成临时ID（负数，避免与后端ID冲突）
    const tempId = -Date.now()
    
    // 创建新对话（仅前端）
    const newConversation: Conversation = {
      id: tempId,
      title: '新对话',
      messages: [],
      lastUpdated: new Date(),
      preview: '开始一个新的对话',
      message_count: 0,
      last_message: undefined,
      isTemporary: true // 标记为临时对话
    }
    
    console.log("创建临时对话成功:", newConversation)
    
    // 添加到对话列表
    conversations.push(newConversation)
    
    // 切换到新对话
    activeConversationId.value = tempId
    
    // 设置居中布局
    isCenterLayout.value = true
    
    // 重置输入框
    userInput.value = ''
    
    // 聚焦输入框
    nextTick(() => {
      focusInput()
    })
    
    return newConversation
  } catch (error) {
    console.error('创建对话出现异常:', error)
    return null
  }
}

// 切换对话
const switchConversation = async (id: number) => {
  try {
    console.log("切换到对话:", id)
    
    if (!id) {
      console.error("无效的对话ID:", id)
      return
    }
    
    activeConversationId.value = id
    
    // 重置加载状态
    isLoading.value = false
    
    // 加载对话详情
    await loadConversationDetail(id)
    
    // 检查对话是否有消息，决定布局
    const conversation = conversations.find(c => c.id === id)
    isCenterLayout.value = conversation?.messages.length === 0
    
    // 滚动到底部
    nextTick(() => {
      scrollToBottom()
      focusInput()
    })
    
    console.log("对话切换完成:", id)
  } catch (error) {
    console.error("切换对话出错:", error)
  }
}

// 加载对话详情
const loadConversationDetail = async (conversationId: number) => {
  try {
    if (!conversationId) {
      console.error("无效的对话ID:", conversationId)
      return
    }
    
    console.log("开始加载对话详情:", conversationId)
    const response = await apiService.getConversation(conversationId)
    console.log("获取对话详情响应:", response)
    
    if (response.code === 200 && response.data) {
      const conv = response.data
      
      // 查找并更新本地对话
      const localConv = conversations.find(c => c.id === conv.id)
      if (localConv) {
        // 确保messages是数组
        if (Array.isArray(conv.messages)) {
          localConv.messages = conv.messages.map(msg => {
            // 确保每条消息都有timestamp属性
            return {
              ...msg,
              timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
            }
          })
        } else {
          localConv.messages = []
          console.warn("返回的messages不是数组:", conv.messages)
        }
        
        localConv.title = conv.title || '未命名对话'
        localConv.message_count = conv.message_count || 0
        console.log("更新本地对话成功:", conv.id, "消息数量:", localConv.messages.length)
      } else {
        console.error("找不到对应的本地对话:", conv.id, "当前对话列表:", conversations)
        
        // 如果找不到对话，添加到本地列表
        const newConv = {
          id: conv.id,
          title: conv.title || '未命名对话',
          messages: Array.isArray(conv.messages) ? conv.messages.map(msg => ({
            ...msg,
            timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
          })) : [],
          lastUpdated: new Date(conv.updated_at || new Date()),
          preview: conv.last_message?.content || '空对话',
          message_count: conv.message_count || 0,
          last_message: conv.last_message
        }
        
        conversations.push(newConv)
        console.log("添加新对话到本地列表:", newConv)
      }
    } else {
      console.error('加载对话详情失败:', response.message, response)
    }
  } catch (error) {
    console.error('加载对话详情失败:', error)
  }
}

// 发送消息
const sendMessage = async () => {
  const content = userInput.value.trim()
  if (!content || isLoading.value) return
  
  try {
    const timestamp = new Date()
    
    // 查找当前对话
    const conversation = conversations.find(c => c.id === activeConversationId.value)
    
    if (!conversation) {
      console.error('无法找到活动对话，ID:', activeConversationId.value)
      return
    }
    
    // 发送第一条消息时，切换布局
    if (conversation.messages.length === 0) {
      isCenterLayout.value = false
    }
    
    // 如果是临时对话，需要先创建真实对话
    if (conversation.isTemporary) {
      console.log("当前是临时对话，需要先创建真实对话")
      
      // 使用用户输入的消息作为对话标题
      const title = content.length > 50 ? content.substring(0, 50) + '...' : content
      console.log("使用消息作为对话标题:", title)
      
      // 创建真实对话，使用消息内容作为标题
      const response = await apiService.createConversation(title)
      console.log("~~~~~~~~~~~~~~~:", response)
      if (response.code === 201 && response.data && response.data.id) {
        // 更新临时对话为真实对话
        const realId = response.data.id
        conversation.id = realId
        conversation.isTemporary = false
        
        // 更新对话标题
        conversation.title = title
        
        // 更新活动对话ID
        activeConversationId.value = realId
        
        console.log("临时对话已转换为真实对话:", realId, "标题:", title)
      } else {
        console.error('创建真实对话失败:', response.message)
        return
      }
    }
    
    // 发送消息到对话
    sendMessageToConversation(conversation, content, timestamp)
  } catch (err) {
    console.error("发送消息过程中出错:", err)
    isLoading.value = false
  }
}

// 向指定对话发送消息
const sendMessageToConversation = async (conversation: Conversation, content: string, timestamp: Date) => {
  // 确保消息数组已初始化
  if (!conversation.messages) {
    conversation.messages = []
  }
  
  // 添加用户消息到本地UI
  conversation.messages.push({
    role: 'user',
    content,
    timestamp
  })
  
  // 更新预览和最后更新时间
  conversation.preview = content
  conversation.lastUpdated = timestamp
  conversation.message_count = (conversation.message_count || 0) + 1
  
  userInput.value = ''
  
  // 自动滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 调用实际的AI API
  isLoading.value = true
  
  try {
    // 准备发送到API的消息历史
    const apiMessages = conversation.messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }))
    
    console.log("发送聊天请求:", {
      messages: apiMessages,
      conversation_id: conversation.id
    })
    
    // 调用聊天API（包含对话ID）
    const response = await apiService.chatCompletion(apiMessages, conversation.id)
    console.log("聊天API响应:", response)
    
    if (response.code === 200 && response.data && response.data.content) {
      const responseContent = response.data.content
      const responseTimestamp = new Date()
      
      // 添加AI回复到本地UI
      conversation.messages.push({
        role: 'assistant',
        content: responseContent,
        timestamp: responseTimestamp
      })
      
      // 更新预览和最后更新时间
      conversation.preview = responseContent
      conversation.lastUpdated = responseTimestamp
      conversation.message_count = (conversation.message_count || 0) + 1
      
      // 如果是新对话，可能需要更新对话ID（如果后端创建了新对话）
      if (response.data.conversation_id && response.data.conversation_id !== conversation.id) {
        console.log("更新对话ID:", conversation.id, "->", response.data.conversation_id)
        conversation.id = response.data.conversation_id
        activeConversationId.value = response.data.conversation_id
      }
    } else {
      // API调用失败，显示错误消息
      conversation.messages.push({
        role: 'assistant',
        content: `抱歉，我遇到了一些问题。${response.message || '请稍后再试。'}`,
        timestamp: new Date()
      })
      conversation.message_count = (conversation.message_count || 0) + 1
    }
  } catch (error) {
    console.error('聊天API调用失败:', error)
    // 显示错误消息
    conversation.messages.push({
      role: 'assistant',
      content: '抱歉，我遇到了网络问题。请检查您的网络连接并稍后再试。',
      timestamp: new Date()
    })
    conversation.message_count = (conversation.message_count || 0) + 1
  } finally {
    isLoading.value = false
    
    // 自动滚动到底部
    nextTick(() => {
      scrollToBottom()
      focusInput()
    })
  }
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

// 格式化日期
const formatDate = (date: Date | undefined) => {
  if (!date) return ''
  
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (date >= today) {
    return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  } else if (date >= yesterday) {
    return `昨天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  } else {
    return `${date.getMonth() + 1}月${date.getDate()}日`
  }
}

// 自动调整输入框高度
watch(userInput, () => {
  if (inputElement.value) {
    inputElement.value.style.height = 'auto'
    inputElement.value.style.height = `${inputElement.value.scrollHeight}px`
  }
})

// 删除对话
const deleteConversation = async (id: number) => {
  try {
    const response = await apiService.deleteConversation(id)
    
    if (response.code === 200) {
      // 从本地列表中删除
      const index = conversations.findIndex(c => c.id === id)
      if (index !== -1) {
        conversations.splice(index, 1)
      }
      
      // 如果删除的是当前对话，切换到其他对话
      if (activeConversationId.value === id) {
        if (conversations.length > 0) {
          switchConversation(conversations[0].id)
        } else {
          // 如果没有对话了，创建一个新对话
          await createNewDefaultConversation()
        }
      }
    } else {
      console.error('删除对话失败:', response.message)
    }
  } catch (error) {
    console.error('删除对话失败:', error)
  }
}

// 清空对话消息
const clearConversationMessages = async (id: number) => {
  try {
    const response = await apiService.clearConversationMessages(id)
    
    if (response.code === 200) {
      // 清空本地消息
      const conversation = conversations.find(c => c.id === id)
      if (conversation) {
        conversation.messages = []
        conversation.message_count = 0
        conversation.preview = '对话已清空'
      }
    } else {
      console.error('清空对话消息失败:', response.message)
    }
  } catch (error) {
    console.error('清空对话消息失败:', error)
  }
}

// 组件挂载后，从后端加载对话历史并聚焦输入框
onMounted(async () => {
  await loadConversationsFromServer()
  
  // 无论是否有活动对话，都创建一个新的临时对话
  console.log("首次打开组件，创建新临时对话")
  await createNewConversation()
  
  focusInput()
  scrollToBottom()
})

// 从服务器加载对话历史
const loadConversationsFromServer = async () => {
  isLoadingConversations.value = true
  
  try {
    console.log("开始从服务器加载对话历史")
    const response = await apiService.getConversations()
    console.log("获取对话列表响应:", response)
    
    if (response.code === 200 && response.data) {
      // 转换API返回的对话格式为UI需要的格式
      const serverConversations = response.data.map(conv => {
        console.log("处理对话:", conv)
        return {
          id: conv.id,
          title: conv.title || '未命名对话',
          messages: conv.messages || [],
          lastUpdated: new Date(conv.updated_at || new Date()),
          preview: conv.last_message?.content || '空对话',
          message_count: conv.message_count || 0,
          last_message: conv.last_message
        }
      })
      
      console.log("转换后的对话列表:", serverConversations)
      
      // 清空并添加新的对话
      conversations.splice(0, conversations.length, ...serverConversations)
      
      console.log("对话列表更新完成，当前对话数量:", conversations.length)
      
      // 不设置任何活动对话，等待后面创建新对话
      activeConversationId.value = null
      console.log("加载完成，活动对话ID设为null，准备创建新对话")
    } else {
      console.error('加载对话失败:', response.message, response)
      // 设置活动对话ID为null，等待后面创建新对话
      activeConversationId.value = null
    }
  } catch (error) {
    console.error('加载对话出错:', error)
    // 设置活动对话ID为null，等待后面创建新对话
    activeConversationId.value = null
  } finally {
    isLoadingConversations.value = false
    console.log("对话加载完成，当前活动对话ID:", activeConversationId.value, "对话列表:", conversations)
  }
}

// 创建默认对话
const createNewDefaultConversation = async (userMessage?: string) => {
  try {
    console.log("开始创建默认对话")
    
    // 确定对话标题 - 如果提供了用户消息，使用它作为标题
    const title = userMessage ? 
      (userMessage.length > 50 ? userMessage.substring(0, 50) + '...' : userMessage) : 
      '新对话'
      
    console.log("创建默认对话，标题:", title)
    
    const response = await apiService.createConversation(title)
    console.log("创建对话API响应:", response)
    
    if (response.code === 200 && response.data && response.data.id) {
      const newConversation = {
        id: response.data.id,
        title: response.data.title || title,
        messages: [],
        lastUpdated: new Date(),
        preview: '开始一个新的对话',
        message_count: 0,
        last_message: undefined
      }
      
      console.log("创建新对话成功:", newConversation)
      conversations.push(newConversation)
      
      // 设置为活动对话
      activeConversationId.value = response.data.id
      console.log("设置活动对话ID:", activeConversationId.value)
      
      return newConversation
    } else {
      console.error('创建默认对话失败:', response.message, response)
      return null
    }
  } catch (error) {
    console.error('创建默认对话出现异常:', error)
    return null
  }
}

// Toggle conversation expansion
const toggleConversationExpand = async (id: number) => {
  if (expandedConversations.value.has(id)) {
    expandedConversations.value.delete(id)
  } else {
    expandedConversations.value.add(id)
    
    // 查找当前对话
    const conversation = conversations.find(c => c.id === id)
    if (conversation && (!conversation.messages || conversation.messages.length === 0) && conversation.message_count > 0) {
      // 需要加载对话历史
      loadingHistoryConversations.value.add(id)
      await loadConversationDetail(id)
      loadingHistoryConversations.value.delete(id)
    }
  }
}

// Check if a conversation is expanded
const isConversationExpanded = (id: number) => {
  return expandedConversations.value.has(id)
}

// Check if a conversation history is loading
const isHistoryLoading = (id: number) => {
  return loadingHistoryConversations.value.has(id)
}

// Get user questions from a conversation
const getUserQuestions = (conversation: Conversation) => {
  if (!conversation.messages || conversation.messages.length === 0) return []
  
  return conversation.messages
    .filter(message => message.role === 'user')
    .map((message, index) => ({
      content: message.content,
      timestamp: message.timestamp,
      index: index // 保存消息在对话中的位置，用于后续定位
    }))
}

// 跳转到特定问题
const jumpToQuestion = (conversationId: number, questionIndex: number) => {
  // 如果不是当前对话，先切换到该对话
  if (activeConversationId.value !== conversationId) {
    switchConversation(conversationId).then(() => {
      scrollToQuestion(questionIndex)
    })
  } else {
    scrollToQuestion(questionIndex)
  }
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
</script>

<template>
  <div class="app-container">
    <!-- 聊天主区域 -->
    <div class="chat-container" :class="{ 'center-layout': isCenterLayout }">
      <!-- 居中布局内容包装器 -->
      <div v-if="isCenterLayout" class="center-content">
        <!-- 欢迎信息 -->
        <div class="welcome-container">
          <div class="welcome-card">
            <h2>{{ greeting }}，{{ userDisplayName }}，欢迎使用AI助手</h2>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="chat-input-container" :class="{ 'centered-input': isCenterLayout }">
          <div class="input-wrapper">
            <textarea 
              v-model="userInput" 
              @keydown.enter="handleKeyDown"
              placeholder="请输入问题..."
              rows="3"
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
            <textarea 
              v-model="userInput" 
              @keydown.enter="handleKeyDown"
              placeholder="请输入问题..."
              rows="3"
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
        </div>
      </template>
    </div>
    
    <!-- 右侧功能区 -->
    <div class="sidebar-right">
      <div class="sidebar-header">
        <button class="new-chat-button" @click="createNewConversation">
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
            <div class="conversation-content" @click="switchConversation(conversation.id)">
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
                @click.stop="deleteConversation(conversation.id)"
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
              @click.stop="jumpToQuestion(conversation.id, question.index)"
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
  background-color: #f8fafc;
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
  background: linear-gradient(90deg, #4f74e3 0%, #5e60ce 100%);
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
  background-color: #f1f3f4;
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
  color: #94a3b8;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.list-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
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
  background-color: #f1f5f9;
}

.conversation-item.active {
  background-color: #e2e8f0;
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
}

.conversation-preview {
  font-size: 0.875rem;
  color: #64748b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-date {
  font-size: 0.75rem;
  color: #94a3b8;
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
  color: #64748b;
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
  color: #334155;
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
  color: #64748b;
  font-size: 0.875rem;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(79, 116, 227, 0.2);
  border-top-color: #4f74e3;
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
  color: #64748b;
  font-size: 0.875rem;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
  overflow: hidden;
  margin-right: 300px; /* 为右侧边栏留出空间 */
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

.welcome-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  margin-bottom: 3rem;
}

.welcome-card {
  text-align: center;
  padding: 2rem;
  background-color: transparent;
  border-radius: 0.75rem;
  max-width: 80%;
  animation: fade-in 0.5s ease-out;
  box-shadow: none;
}

.welcome-card h2 {
  margin-bottom: 0;
  color: #334155;
  font-size: 2rem;
}

.welcome-card p {
  color: #64748b;
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
  color: #666;
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
  color: #999;
  margin-top: 5px;
  text-align: right;
}

/* 加载动画修改 */
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
  background-color: #bbb;
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
  align-items: flex-end;
  border: none;
  border-radius: 0.75rem;
  overflow: hidden;
  background-color: #f1f3f4;
  padding: 0.75rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  min-height: 60px;
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

/* 响应式布局 */
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

/* 新增样式用于整体内容的垂直居中 */
.chat-container.center-layout .center-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  padding: 0 1rem;
  margin-top: -25vh; /* 进一步向上移动整体内容 */
}

/* 调整居中布局时的输入框容器 */
.chat-container.center-layout .chat-input-container {
  position: relative;
  margin-top: 0;
  width: 100%;
}

/* 添加聊天消息样式 */
.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  width: 100%;
  background-color: #f5f5f5;
}

.expand-btn {
  background: transparent;
  border: none;
  color: #64748b;
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
  color: #334155;
}

.conversation-history {
  width: 100%;
  padding: 0.5rem;
  margin-top: 0.5rem;
  background-color: #edf2f7;
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
  background-color: #ffffff;
  border-left: 3px solid #4f74e3;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.history-question:hover {
  background-color: #f8fafc;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.history-question:last-child {
  margin-bottom: 0;
}

.question-content {
  font-size: 14px;
  color: #334155;
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
  color: #94a3b8;
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
  color: #64748b;
  font-size: 0.875rem;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 6px;
  margin: 0.5rem 0;
}

.history-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(79, 116, 227, 0.2);
  border-top-color: #4f74e3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.history-empty {
  text-align: center;
  padding: 1rem;
  color: #64748b;
  font-size: 0.875rem;
  background-color: #ffffff;
  border-radius: 6px;
  border-left: 3px solid #cbd5e1;
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
</style>
