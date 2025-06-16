<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, watch, computed } from 'vue'

const userInput = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputElement = ref<HTMLTextAreaElement | null>(null)
const searchQuery = ref('')
const activeConversationId = ref(1)

// 聊天消息
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

// 对话类型
interface Conversation {
  id: number
  title: string
  messages: ChatMessage[]
  lastUpdated: Date
  preview: string
}

// 历史对话列表
const conversations = reactive<Conversation[]>([
  {
    id: 1,
    title: '当前对话',
    messages: [
      {
        role: 'assistant',
        content: '你好！我是AI助手，有什么我可以帮助你的吗？',
        timestamp: new Date()
      }
    ],
    lastUpdated: new Date(),
    preview: '你好！我是AI助手，有什么我可以帮助你的吗？'
  }
])

// 添加一些模拟的历史对话
for (let i = 2; i <= 10; i++) {
  const date = new Date()
  date.setDate(date.getDate() - (i - 1))
  
  const title = [
    '关于机器学习的讨论',
    '如何提高编程效率',
    '人工智能的未来发展',
    '数据分析最佳实践',
    '云计算技术探讨',
    '网络安全防护措施',
    '区块链技术应用',
    '前端开发技巧分享',
    '后端架构设计'
  ][i % 9]
  
  const preview = [
    '机器学习是人工智能的一个分支...',
    '提高编程效率的关键是选择合适的工具...',
    '人工智能未来将会更加智能化...',
    '数据分析需要注重数据质量...',
    '云计算为企业提供了灵活的资源...',
    '网络安全需要多层次防护...',
    '区块链可以应用于多个领域...',
    '前端开发需要关注用户体验...',
    '后端架构的稳定性至关重要...'
  ][i % 9]
  
  conversations.push({
    id: i,
    title: `${title}`,
    messages: [
      {
        role: 'assistant',
        content: preview,
        timestamp: date
      }
    ],
    lastUpdated: date,
    preview: preview
  })
}

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

// 创建新对话
const createNewConversation = () => {
  // 生成新的对话ID
  const newId = Math.max(...conversations.map(c => c.id)) + 1
  
  // 创建新对话
  const newConversation = {
    id: newId,
    title: '新对话',
    messages: [
      {
        role: 'assistant' as const,
        content: '你好！我是AI助手，有什么我可以帮助你的吗？',
        timestamp: new Date()
      }
    ],
    lastUpdated: new Date(),
    preview: '你好！我是AI助手，有什么我可以帮助你的吗？'
  }
  
  // 添加到对话列表
  conversations.push(newConversation)
  
  // 切换到新对话
  switchConversation(newId)
}

// 切换对话
const switchConversation = (id: number) => {
  activeConversationId.value = id
  
  // 重置加载状态
  isLoading.value = false
  
  // 滚动到底部
  nextTick(() => {
    scrollToBottom()
    focusInput()
  })
}

// 发送消息
const sendMessage = async () => {
  const content = userInput.value.trim()
  if (!content || isLoading.value) return
  
  const timestamp = new Date()
  
  // 查找当前对话
  const conversation = conversations.find(c => c.id === activeConversationId.value)
  if (!conversation) return
  
  // 添加用户消息
  conversation.messages.push({
    role: 'user',
    content,
    timestamp
  })
  
  // 更新对话标题（使用用户的第一条消息）
  if (conversation.title === '新对话' || conversation.title === '当前对话') {
    // 截取前20个字符作为标题
    conversation.title = content.length > 20 ? content.substring(0, 20) + '...' : content
  }
  
  // 更新预览和最后更新时间
  conversation.preview = content
  conversation.lastUpdated = timestamp
  
  userInput.value = ''
  
  // 自动滚动到底部
  await nextTick()
  scrollToBottom()
  
  // 模拟AI回复
  isLoading.value = true
  setTimeout(() => {
    const responseContent = simulateAIResponse(content)
    const responseTimestamp = new Date()
    
    conversation.messages.push({
      role: 'assistant',
      content: responseContent,
      timestamp: responseTimestamp
    })
    
    // 更新预览和最后更新时间
    conversation.preview = responseContent
    conversation.lastUpdated = responseTimestamp
    
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
        
        <div 
          v-for="conversation in filteredConversations.slice(0, 15)" 
          :key="conversation.id" 
          class="conversation-item"
          :class="{ 'active': conversation.id === activeConversationId }"
          @click="switchConversation(conversation.id)"
        >
          <div class="conversation-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
          </div>
          <div class="conversation-content">
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-preview">{{ conversation.preview }}</div>
          </div>
          <div class="conversation-date">{{ formatDate(conversation.lastUpdated) }}</div>
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
  align-items: flex-start;
  padding: 0.75rem;
  border-radius: 6px;
  cursor: pointer;
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

.conversation-icon {
  margin-right: 0.75rem;
  color: #64748b;
  flex-shrink: 0;
}

.conversation-content {
  flex: 1;
  min-width: 0;
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
  margin-left: 0.5rem;
  flex-shrink: 0;
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
