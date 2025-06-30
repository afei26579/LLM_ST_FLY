<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, watch, computed } from 'vue'
import { apiService } from '../services/api'
import type { ChatMessage as ApiChatMessage } from '../services/api'
import { useAuthStore } from '../stores/auth'

const userInput = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputElement = ref<HTMLTextAreaElement | null>(null)
const searchQuery = ref('')
const activeConversationId = ref<number | null>(null)
const authStore = useAuthStore()

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
    // 检查当前对话是否为空对话，如果是空对话，不允许创建新对话
    if (activeConversationId.value !== null) {
      const activeConv = conversations.find(c => c.id === activeConversationId.value)
      if (activeConv && activeConv.messages.length === 0) {
        console.log("当前对话没有消息，不允许创建新对话")
        return null
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
          localConv.messages = conv.messages
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
          messages: Array.isArray(conv.messages) ? conv.messages : [],
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
      
      // 如果没有对话，创建一个默认对话
      if (conversations.length === 0) {
        console.log("没有对话，创建默认对话")
        const newConv = await createNewDefaultConversation()
        if (newConv) {
          console.log("成功创建默认对话:", newConv.id)
        } else {
          console.error("创建默认对话失败")
        }
      } else {
        // 设置第一个对话为活动对话
        activeConversationId.value = conversations[0].id
        console.log("设置第一个对话为活动对话:", activeConversationId.value)
        
        // 加载第一个对话详情
        await loadConversationDetail(activeConversationId.value)
      }
    } else {
      console.error('加载对话失败:', response.message, response)
    }
  } catch (error) {
    console.error('加载对话出错:', error)
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
</script>

<template>
  <div class="app-container">
    <!-- 聊天主区域 -->
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
            <div class="timestamp" v-if="message.timestamp">{{ formatDate(message.timestamp) }}</div>
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
          <div class="conversation-content" @click="switchConversation(conversation.id)">
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-preview">{{ conversation.preview }}</div>
            <div class="conversation-date">{{ formatDate(conversation.lastUpdated) }}</div>
          </div>
          <div class="conversation-actions">
            <button 
              class="action-btn" 
              title="清空对话"
              @click.stop="clearConversationMessages(conversation.id)"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="9" y1="9" x2="15" y2="15"></line>
                <line x1="15" y1="9" x2="9" y2="15"></line>
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
  border-left: 1px solid #e2e8f0;
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
  border-bottom: 1px solid #e2e8f0;
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
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: white;
}

.search-input:focus {
  outline: none;
  border-color: #4f74e3;
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
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-radius: 6px;
  transition: background-color 0.2s;
  margin-bottom: 0.5rem;
  position: relative;
}

.conversation-item:hover {
  background-color: #f1f5f9;
}

.conversation-item.active {
  background-color: #e2e8f0;
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

.timestamp {
  margin-left: auto;
  font-size: 0.75rem;
  font-weight: normal;
  opacity: 0.7;
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
}
</style>
