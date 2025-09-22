<template>
  <div class="agent-chat-view">
    <div class="page-header">
      <div class="agent-info" v-if="currentAgent">
        <div class="agent-avatar">
          <img v-if="currentAgent.avatar" :src="currentAgent.avatar" :alt="currentAgent.name" />
          <div v-else class="avatar-placeholder">{{ currentAgent.name.charAt(0) }}</div>
        </div>
        <div class="agent-details">
          <h1 class="agent-name">{{ currentAgent.name }}</h1>
          <p class="agent-description">{{ currentAgent.description }}</p>
        </div>
      </div>
    </div>
    
    <div class="chat-container">
      <!-- 对话历史侧边栏 -->
      <div class="conversation-sidebar" :class="{ 'collapsed': sidebarCollapsed }">
        <div class="sidebar-header">
          <h3>对话历史</h3>
          <button class="collapse-btn" @click="toggleSidebar">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"></polyline>
            </svg>
          </button>
        </div>
        
        <div class="conversation-list">
          <div class="new-chat-btn" @click="startNewConversation">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            新建对话
          </div>
          
          <div class="conversation-item" 
               v-for="conversation in conversations" 
               :key="conversation.id"
               :class="{ 'active': currentConversation?.id === conversation.id }"
               @click="loadConversation(conversation.id)">
            <div class="conversation-title">{{ conversation.title }}</div>
            <div class="conversation-meta">
              <span class="message-count">{{ conversation.message_count }}条消息</span>
              <span class="last-message">{{ formatTime(conversation.last_message_at) }}</span>
            </div>
            <button class="delete-btn" @click.stop="deleteConversation(conversation.id)">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="m19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 聊天主界面 -->
      <div class="chat-main">
        <div class="messages-container" ref="messagesContainer">
          <div v-if="!currentConversation" class="welcome-message">
            <div class="welcome-content">
              <div class="welcome-icon">🤖</div>
              <h2>{{ currentAgent?.greeting_message || '您好！我是您的智能助手' }}</h2>
              <p>请开始一个新对话，我会尽力帮助您解决问题。</p>
            </div>
          </div>
          
          <div v-else class="messages-list">
            <div v-for="message in messages" 
                 :key="message.id" 
                 class="message"
                 :class="{ 'user-message': message.type === 'user', 'assistant-message': message.type === 'assistant' }">
              <div class="message-content">
                <div class="message-text" v-html="formatMessage(message.content)"></div>
                <div class="message-meta">
                  <span class="message-time">{{ formatTime(message.created_at) }}</span>
                  <span v-if="message.tokens_used > 0" class="tokens-used">{{ message.tokens_used }} tokens</span>
                </div>
              </div>
            </div>
            
            <div v-if="isThinking" class="message assistant-message thinking">
              <div class="message-content">
                <div class="thinking-indicator">
                  <div class="dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span class="thinking-text">AI正在思考...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-container">
            <textarea 
              v-model="userInput"
              @keydown="handleKeyDown"
              placeholder="请输入您的问题..."
              rows="1"
              ref="messageInput"
              :disabled="isThinking"
            ></textarea>
            <button class="send-btn" 
                    @click="sendMessage" 
                    :disabled="!userInput.trim() || isThinking"
                    :class="{ 'sending': isThinking }">
              <svg v-if="!isThinking" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22,2 15,22 11,13 2,9 22,2"></polygon>
              </svg>
              <div v-else class="loading-spinner"></div>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div class="stats-modal" v-if="showStats">
      <div class="modal-overlay" @click="showStats = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>使用统计</h3>
          <button class="close-btn" @click="showStats = false">×</button>
        </div>
        <div class="stats-content" v-if="userStats">
          <div class="stat-item">
            <div class="stat-value">{{ userStats.total_conversations }}</div>
            <div class="stat-label">总对话数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userStats.total_messages }}</div>
            <div class="stat-label">总消息数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userStats.total_tokens_used }}</div>
            <div class="stat-label">消耗Tokens</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'
import type { Agent, AgentConversation, Message, UserAgentStats } from '@/services/api'

interface Props {
  agentType: string
}

const props = defineProps<Props>()
const route = useRoute()
const toast = useToast()

// 数据状态
const currentAgent = ref<Agent | null>(null)
const currentConversation = ref<AgentConversation | null>(null)
const conversations = ref<AgentConversation[]>([])
const messages = ref<Message[]>([])
const userStats = ref<UserAgentStats | null>(null)

// UI状态
const sidebarCollapsed = ref(false)
const userInput = ref('')
const isThinking = ref(false)
const showStats = ref(false)

// DOM引用
const messagesContainer = ref<HTMLElement>()
const messageInput = ref<HTMLTextAreaElement>()

// 功能函数声明（需要在调用之前声明）
// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}


// 加载智能体信息
const loadAgent = async () => {
  try {
    const response = await apiService.getAgents()
    if (response.code === 200) {
      const agent = response.data.find(a => a.type === props.agentType)
      if (agent) {
        currentAgent.value = agent
      }
    }
  } catch (error) {
    console.error('加载智能体失败:', error)
    toast.error('加载智能体失败')
  }
}

// 加载对话列表
const loadConversations = async () => {
  try {
    const response = await apiService.getAgentConversations({
      agent_type: props.agentType,
      limit: 20
    })
    if (response.code === 200) {
      conversations.value = response.data
    }
  } catch (error) {
    console.error('加载对话列表失败:', error)
  }
}

// 加载用户统计
const loadUserStats = async () => {
  try {
    const response = await apiService.getUserAgentStats()
    if (response.code === 200) {
      userStats.value = response.data
    }
  } catch (error) {
    console.error('加载用户统计失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadAgent()
  loadConversations()
  loadUserStats()
})

// 监听路由变化
watch(() => route.params, () => {
  if (route.name && typeof route.name === 'string') {
    loadAgent()
    loadConversations()
  }
}, { immediate: true })

// 开始新对话
const startNewConversation = () => {
  currentConversation.value = null
  messages.value = []
  scrollToBottom()
}

// 加载对话
const loadConversation = async (conversationId: string) => {
  try {
    const response = await apiService.getAgentConversationDetail(conversationId)
    if (response.code === 200) {
      currentConversation.value = response.data
      messages.value = response.data.messages || []
      scrollToBottom()
    }
  } catch (error) {
    console.error('加载对话失败:', error)
    toast.error('加载对话失败')
  }
}

// 删除对话
const deleteConversation = async (conversationId: string) => {
  if (!confirm('确定要删除这个对话吗？')) return
  
  try {
    const response = await apiService.deleteAgentConversation(conversationId)
    if (response.code === 200) {
      conversations.value = conversations.value.filter(c => c.id !== conversationId)
      if (currentConversation.value?.id === conversationId) {
        startNewConversation()
      }
      toast.success('对话已删除')
    } else {
      toast.error(response.message)
    }
  } catch (error) {
    console.error('删除对话失败:', error)
    toast.error('删除对话失败')
  }
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isThinking.value) return
  
  const messageText = userInput.value.trim()
  userInput.value = ''
  isThinking.value = true
  
  // 添加用户消息到界面
  const userMessage: Message = {
    id: Date.now().toString(),
    type: 'user',
    type_display: '用户消息',
    content: messageText,
    created_at: new Date().toISOString(),
    tokens_used: 0
  }
  messages.value.push(userMessage)
  scrollToBottom()
  
  try {
    const response = await apiService.agentChat({
      message: messageText,
      agent_type: props.agentType,
      conversation_id: currentConversation.value?.id
    })
    
    if (response.code === 200) {
      const data = response.data
      
      // 如果是新对话，更新当前对话信息
      if (data.is_new_conversation) {
        currentConversation.value = {
          id: data.conversation_id,
          title: `与${data.agent.name}的对话`,
          agent_name: data.agent.name,
          agent_type: data.agent.type,
          agent_avatar: data.agent.avatar,
          started_at: new Date().toISOString(),
          last_message_at: new Date().toISOString(),
          is_active: true,
          message_count: 2
        }
        
        // 刷新对话列表
        loadConversations()
      }
      
      // 添加AI回复
      const aiMessage: Message = {
        id: data.message_id,
        type: 'assistant',
        type_display: '助手回复',
        content: data.message,
        created_at: new Date().toISOString(),
        tokens_used: data.tokens_used
      }
      messages.value.push(aiMessage)
      
      // 更新统计
      loadUserStats()
      
    } else {
      toast.error(response.message || '发送失败')
      // 移除用户消息
      messages.value = messages.value.filter(m => m.id !== userMessage.id)
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    toast.error('发送消息失败')
    // 移除用户消息
    messages.value = messages.value.filter(m => m.id !== userMessage.id)
  } finally {
    isThinking.value = false
    scrollToBottom()
    // 聚焦输入框
    nextTick(() => {
      messageInput.value?.focus()
    })
  }
}

// 键盘事件处理
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

</script>

<style scoped>
.agent-chat-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-color);
}

.page-header {
  padding: 1rem 2rem;
  border-bottom: 1px solid var(--color-border);
  background: var(--card-background);
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.agent-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.agent-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #5e9bff 0%, #a569ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  font-weight: 600;
}

.agent-details h1 {
  margin: 0 0 0.5rem 0;
  color: var(--color-text);
  font-size: 1.5rem;
}

.agent-details p {
  margin: 0;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.chat-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.conversation-sidebar {
  width: 300px;
  background: var(--card-background);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

.conversation-sidebar.collapsed {
  margin-left: -300px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.sidebar-header h3 {
  margin: 0;
  color: var(--color-text);
  font-size: 1rem;
}

.collapse-btn {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.collapse-btn:hover {
  background: var(--color-border);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: var(--color-primary);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.9rem;
}

.new-chat-btn:hover {
  background: var(--color-primary-dark);
}

.conversation-item {
  padding: 0.75rem;
  margin-bottom: 0.25rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.conversation-item:hover {
  background: var(--color-border);
}

.conversation-item.active {
  background: var(--color-primary-alpha);
  border: 1px solid var(--color-primary);
}

.conversation-title {
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
  line-height: 1.3;
}

.conversation-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.delete-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
  padding: 0.25rem;
  border-radius: 4px;
}

.conversation-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: var(--color-danger);
  color: white;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.welcome-message {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.welcome-content {
  text-align: center;
  max-width: 400px;
}

.welcome-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.welcome-content h2 {
  color: var(--color-text);
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.welcome-content p {
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  max-width: 80%;
}

.user-message {
  align-self: flex-end;
}

.assistant-message {
  align-self: flex-start;
}

.message-content {
  background: var(--card-background);
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid var(--color-border);
  position: relative;
}

.user-message .message-content {
  background: var(--color-primary);
  color: white;
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  opacity: 0.7;
}

.thinking {
  animation: pulse 1.5s infinite;
}

.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dots {
  display: flex;
  gap: 0.25rem;
}

.dots span {
  width: 6px;
  height: 6px;
  background: var(--color-primary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.dots span:nth-child(1) { animation-delay: -0.32s; }
.dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.input-area {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--card-background);
}

.input-container {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.input-container textarea {
  flex: 1;
  max-height: 120px;
  min-height: 44px;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--input-background);
  color: var(--color-text);
  resize: none;
  font-family: inherit;
  line-height: 1.4;
}

.input-container textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.send-btn {
  width: 44px;
  height: 44px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.stats-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.modal-content {
  background: var(--card-background);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  width: 90%;
  max-width: 400px;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
  color: var(--color-text);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.stats-content {
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

@media (max-width: 768px) {
  .conversation-sidebar {
    position: absolute;
    z-index: 100;
    height: 100%;
  }
  
  .agent-info {
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }
  
  .message {
    max-width: 90%;
  }
}
</style>
