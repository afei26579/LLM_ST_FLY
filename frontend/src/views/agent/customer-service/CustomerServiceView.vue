<template>
  <div class="customer-service-container">
    <!-- 头部 -->
    <div class="cs-header">
      <div class="header-left">
        <div class="cs-icon">🤖</div>
        <div class="header-info">
          <h2>智能客服助手</h2>
          <p class="subtitle">专业、高效、24小时在线服务</p>
        </div>
      </div>
      <div class="header-right">
        <button v-if="currentSessionId" @click="showSessionsList = !showSessionsList" class="btn-sessions">
          <span>📋</span> 历史会话
        </button>
        <button @click="newSession" class="btn-new">
          <span>➕</span> 新会话
        </button>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="cs-main">
      <!-- 侧边栏 - 会话列表 -->
      <div v-if="showSessionsList" class="sessions-sidebar">
        <div class="sidebar-header">
          <h3>历史会话</h3>
          <button @click="loadSessions" class="btn-refresh">🔄</button>
        </div>
        <div class="sessions-list">
          <div
            v-for="session in sessions"
            :key="session.id"
            :class="['session-item', { active: session.session_id === currentSessionId }]"
            @click="switchSession(session)"
          >
            <div class="session-title">{{ session.title }}</div>
            <div class="session-meta">
              <span class="session-status" :class="session.status">
                {{ getStatusText(session.status) }}
              </span>
              <span class="session-time">{{ formatTime(session.updated_at) }}</span>
            </div>
          </div>
          <div v-if="sessions.length === 0" class="empty-sessions">
            暂无历史会话
          </div>
        </div>
      </div>

      <!-- 聊天区域 -->
      <div class="chat-area">
        <!-- 转人工提示 -->
        <div v-if="needHuman" class="human-transfer-banner">
          ⚠️ 正在为您转接人工客服，请稍候...
        </div>

        <!-- 消息列表 -->
        <div class="messages-container" ref="messagesContainer">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-icon">👋</div>
            <h3>{{ greeting }}</h3>
            <div class="quick-questions">
              <div class="quick-title">常见问题：</div>
              <button
                v-for="(q, index) in quickQuestions"
                :key="index"
                @click="sendQuickQuestion(q)"
                class="quick-btn"
              >
                {{ q }}
              </button>
            </div>
          </div>

          <!-- 消息 -->
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message', message.role]"
          >
            <div class="message-avatar">
              <span v-if="message.role === 'user'">👤</span>
              <span v-else-if="message.role === 'assistant'">🤖</span>
              <span v-else>ℹ️</span>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(message.content)"></div>
              <div v-if="message.intent && message.role === 'assistant'" class="message-meta">
                <span class="intent-tag">{{ getIntentText(message.intent) }}</span>
                <span v-if="message.confidence" class="confidence">
                  置信度: {{ (message.confidence * 100).toFixed(0) }}%
                </span>
              </div>
              <div class="message-time">{{ formatTime(message.created_at) }}</div>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="isLoading" class="message assistant loading">
            <div class="message-avatar">🤖</div>
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
        <div class="input-area">
          <div class="input-wrapper">
            <textarea
              v-model="userInput"
              @keydown.enter.exact.prevent="sendMessage"
              @keydown.shift.enter.exact="userInput += '\n'"
              placeholder="请描述您的问题... (Enter发送，Shift+Enter换行)"
              rows="2"
              :disabled="isLoading"
            ></textarea>
            <button
              @click="sendMessage"
              :disabled="isLoading || !userInput.trim()"
              class="btn-send"
            >
              <span v-if="!isLoading">发送 📤</span>
              <span v-else>发送中...</span>
            </button>
          </div>
          
          <!-- 满意度评价 -->
          <div v-if="showSatisfactionPrompt && !needHuman" class="satisfaction-prompt">
            <span>此次服务是否满意？</span>
            <div class="satisfaction-stars">
              <button
                v-for="star in 5"
                :key="star"
                @click="submitSatisfaction(star)"
                class="star-btn"
              >
                {{ star <= hoveredStar || star <= selectedStar ? '⭐' : '☆' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧信息栏 -->
      <div v-if="showInfoPanel" class="info-panel">
        <div class="panel-header">
          <h3>统计信息</h3>
        </div>
        <div class="stats-content">
          <div class="stat-item">
            <div class="stat-label">总会话数</div>
            <div class="stat-value">{{ stats.total_sessions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">已解决</div>
            <div class="stat-value">{{ stats.resolved_sessions || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">平均满意度</div>
            <div class="stat-value">
              {{ stats.avg_satisfaction_score ? stats.avg_satisfaction_score.toFixed(1) : '-' }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'

const toast = useToast()

// 状态
const messages = ref<any[]>([])
const userInput = ref('')
const isLoading = ref(false)
const currentSessionId = ref('')
const needHuman = ref(false)
const greeting = ref('您好！我是智能客服助手，有什么可以帮您的吗？')

// UI 状态
const showSessionsList = ref(false)
const showInfoPanel = ref(true)
const showSatisfactionPrompt = ref(false)
const selectedStar = ref(0)
const hoveredStar = ref(0)

// 数据
const sessions = ref<any[]>([])
const stats = ref<any>({})

// 快捷问题
const quickQuestions = [
  '如何查询我的订单？',
  '退换货流程是什么？',
  '产品保修政策',
  '如何联系人工客服？'
]

const messagesContainer = ref<HTMLElement>()

// 初始化
onMounted(async () => {
  await loadGreeting()
  await loadSessions()
  await loadStats()
})

// 加载欢迎语
const loadGreeting = async () => {
  try {
    const response = await apiService.get('/agent/customer-service/greeting/')
    if (response.data?.success) {
      greeting.value = response.data.data.greeting
    }
  } catch (error) {
    console.error('加载欢迎语失败:', error)
  }
}

// 加载会话列表
const loadSessions = async () => {
  try {
    const response = await apiService.get('/agent/customer-service/sessions/')
    if (response.data?.success) {
      sessions.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载会话失败:', error)
  }
}

// 加载统计信息
const loadStats = async () => {
  try {
    const response = await apiService.get('/agent/customer-service/stats/')
    if (response.data?.success) {
      stats.value = response.data.data || {}
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 切换会话
const switchSession = async (session: any) => {
  currentSessionId.value = session.session_id
  needHuman.value = session.status === 'transferred'
  
  // 加载会话消息
  try {
    const response = await apiService.get(`/agent/customer-service/sessions/${session.id}/`)
    if (response.data?.success) {
      messages.value = response.data.data.messages || []
      scrollToBottom()
    }
  } catch (error) {
    toast.error('加载会话消息失败')
  }
}

// 新会话
const newSession = () => {
  currentSessionId.value = ''
  messages.value = []
  userInput.value = ''
  needHuman.value = false
  showSatisfactionPrompt.value = false
  selectedStar.value = 0
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const messageText = userInput.value.trim()
  userInput.value = ''

  // 添加用户消息到界面
  messages.value.push({
    role: 'user',
    content: messageText,
    created_at: new Date().toISOString()
  })

  scrollToBottom()
  isLoading.value = true

  try {
    const response = await apiService.post('/agent/customer-service/chat/', {
      message: messageText,
      session_id: currentSessionId.value
    })

    if (response.data?.success) {
      const data = response.data.data

      // 更新会话ID
      currentSessionId.value = data.session_id

      // 添加AI回复
      messages.value.push({
        role: 'assistant',
        content: data.response,
        intent: data.intent,
        confidence: data.confidence,
        created_at: new Date().toISOString()
      })

      // 检查是否需要转人工
      if (data.need_human) {
        needHuman.value = true
      }

      // 如果会话有多轮对话，显示满意度提示
      if (messages.value.length >= 4) {
        showSatisfactionPrompt.value = true
      }

      scrollToBottom()
      await loadSessions()
    } else {
      toast.error(response.data?.message || '发送失败')
    }
  } catch (error: any) {
    console.error('发送消息失败:', error)
    toast.error(error.response?.data?.message || '发送失败，请重试')
  } finally {
    isLoading.value = false
  }
}

// 发送快捷问题
const sendQuickQuestion = (question: string) => {
  userInput.value = question
  sendMessage()
}

// 提交满意度
const submitSatisfaction = async (score: number) => {
  selectedStar.value = score

  try {
    const response = await apiService.post('/agent/customer-service/feedback/', {
      session_id: currentSessionId.value,
      score: score
    })

    if (response.data?.success) {
      toast.success('感谢您的反馈！')
      showSatisfactionPrompt.value = false
      await loadStats()
    }
  } catch (error) {
    toast.error('提交反馈失败')
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 格式化消息（支持换行）
const formatMessage = (content: string) => {
  return content.replace(/\n/g, '<br>')
}

// 格式化时间
const formatTime = (timeStr: string) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`

  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    active: '进行中',
    resolved: '已解决',
    transferred: '已转人工',
    closed: '已关闭'
  }
  return statusMap[status] || status
}

// 获取意图文本
const getIntentText = (intent: string) => {
  const intentMap: Record<string, string> = {
    order_query: '订单查询',
    product_consult: '产品咨询',
    technical_issue: '技术支持',
    complaint: '投诉建议',
    general: '通用咨询'
  }
  return intentMap[intent] || intent
}
</script>

<style scoped>
.customer-service-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--color-background);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
}

.cs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: var(--color-surface);
  box-shadow: var(--card-shadow);
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.cs-icon {
  font-size: 48px;
}

.header-info h2 {
  margin: 0;
  font-size: 24px;
  color: var(--header-text);
}

.subtitle {
  margin: 5px 0 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.header-right {
  display: flex;
  gap: 10px;
}

.btn-sessions,
.btn-new {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-sessions {
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-new {
  background: var(--button-primary);
  color: var(--button-primaryText);
}

.btn-sessions:hover,
.btn-new:hover {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.cs-main {
  display: flex;
  flex: 1;
  overflow: hidden;
  gap: 0;
}

.sessions-sidebar {
  width: 280px;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid var(--color-border);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--color-text);
}

.btn-refresh {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 5px;
  color: var(--color-text);
  transition: color 0.2s;
}

.btn-refresh:hover {
  color: var(--button-primary);
}

.sessions-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.session-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--color-background);
  border: 1px solid var(--color-border);
}

.session-item:hover {
  background: var(--color-primary-alpha);
  transform: translateX(4px);
}

.session-item.active {
  background: var(--button-primary);
  color: var(--button-primaryText);
  border-color: var(--button-primary);
}

.session-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: inherit;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  opacity: 0.85;
}

.session-status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.session-status.active {
  background: var(--color-success, #28a745);
  color: white;
}

.session-status.resolved {
  background: var(--color-info, #17a2b8);
  color: white;
}

.session-status.transferred {
  background: var(--color-warning, #ffc107);
  color: var(--color-text, #333);
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  position: relative;
}

.human-transfer-banner {
  background: var(--color-warning);
  color: var(--color-warning-text, white);
  padding: 12px 20px;
  text-align: center;
  font-weight: 500;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--color-background);
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.welcome-message h3 {
  color: var(--color-text);
  margin-bottom: 30px;
}

.quick-questions {
  max-width: 500px;
  margin: 0 auto;
}

.quick-title {
  font-weight: 500;
  margin-bottom: 15px;
  color: var(--color-text-secondary);
}

.quick-btn {
  display: block;
  width: 100%;
  margin: 10px 0;
  padding: 12px 20px;
  border: 2px solid var(--button-primary);
  border-radius: 8px;
  background: var(--color-surface);
  color: var(--button-primary);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.quick-btn:hover {
  background: var(--button-primary);
  color: var(--button-primaryText);
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  font-size: 32px;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--color-surface);
  box-shadow: var(--card-shadow);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.message.user .message-content {
  background: var(--button-primary);
  color: var(--button-primaryText);
  border-color: var(--button-primary);
}

.message-text {
  line-height: 1.6;
  word-wrap: break-word;
}

.message-meta {
  display: flex;
  gap: 10px;
  margin-top: 8px;
  font-size: 12px;
}

.intent-tag {
  background: var(--color-primary-alpha);
  color: var(--button-primary);
  padding: 2px 8px;
  border-radius: 4px;
}

.confidence {
  color: var(--color-text-secondary);
}

.message-time {
  margin-top: 6px;
  font-size: 11px;
  color: var(--color-text-secondary);
  opacity: 0.8;
}

.message.user .message-time {
  color: var(--button-primaryText);
  opacity: 0.8;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--button-primary);
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
  30% { transform: translateY(-10px); opacity: 1; }
}

.input-area {
  padding: 20px;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-wrapper textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--input-border);
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  transition: border-color 0.3s;
  background: var(--input-background);
  color: var(--color-text);
}

.input-wrapper textarea:focus {
  outline: none;
  border-color: var(--button-primary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.btn-send {
  padding: 12px 24px;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.satisfaction-prompt {
  margin-top: 15px;
  padding: 15px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 15px;
  color: var(--color-text);
}

.satisfaction-stars {
  display: flex;
  gap: 8px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  transition: transform 0.2s;
}

.star-btn:hover {
  transform: scale(1.2);
}

.info-panel {
  width: 260px;
  background: var(--color-surface);
  border-left: 1px solid var(--color-border);
  padding: 20px;
}

.panel-header h3 {
  margin: 0 0 20px;
  font-size: 16px;
  color: var(--color-text);
}

.stat-item {
  padding: 15px;
  margin-bottom: 12px;
  background: var(--button-primary);
  border-radius: 12px;
  color: var(--button-primaryText);
}

.stat-label {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.empty-sessions {
  text-align: center;
  padding: 20px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .info-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  .sessions-sidebar {
    position: absolute;
    z-index: 10;
    height: 100%;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style>

