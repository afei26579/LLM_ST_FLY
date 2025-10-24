<template>
  <div class="cs-manage-view">
    <!-- 头部 -->
    <div class="cs-header">
      <div class="header-left">
        <div class="cs-icon">🤖</div>
        <div class="header-info">
          <h2>智能客服管理中心</h2>
          <p class="subtitle">配置知识库和自定义客服助手</p>
        </div>
      </div>
      <div class="header-right">
        <button @click="handleCreateKBClick" class="btn-action">
          <span>📚</span> 新建知识库
        </button>
        <button @click="handleCreateAssistantClick" class="btn-action btn-primary">
          <span>🤖</span> 新建助手
        </button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧内容区域 -->
      <div class="left-section">
        <!-- 空状态 - 没有助手 -->
        <EmptyAssistantView
          v-if="leftView === 'empty'"
          :has-knowledge-base="knowledgeBases.length > 0"
          @create-kb="handleCreateKBClick"
          @create-assistant="handleCreateAssistantClick"
        />

        <!-- 创建知识库表单 -->
        <CreateKnowledgeBaseForm
          v-else-if="leftView === 'create-kb'"
          @submit="handleCreateKB"
          @cancel="handleCancelCreate"
        />

        <!-- 创建助手表单 -->
        <CreateAssistantForm
          v-else-if="leftView === 'create-assistant'"
          :available-knowledge-bases="knowledgeBases.filter(kb => kb.status === 'ready')"
          @submit="handleCreateAssistant"
          @cancel="handleCancelCreate"
          @create-kb="handleCreateKBClick"
        />

        <!-- 对话测试区 -->
        <div class="chat-section" v-else-if="leftView === 'chat'">
        <div class="chat-header">
          <div class="current-assistant-info" v-if="currentAssistant">
            <span class="assistant-avatar-small">{{ currentAssistant.avatar }}</span>
            <span class="assistant-name-small">{{ currentAssistant.name }}</span>
            
          </div>
          <div v-else class="no-assistant">
            <span>请先选择或创建助手</span>
          </div>
          <button @click="newSession" class="btn-new-session">
            <span>➕</span> 新会话
          </button>
        </div>

        <!-- 消息区域 -->
        <div class="messages-container" ref="messagesContainer">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-icon">{{ currentAssistant?.avatar || '👋' }}</div>
            <h3>{{ currentAssistant?.greeting_message || greeting }}</h3>
            <div class="quick-questions">
              <div class="quick-title">快速开始：</div>
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

          <!-- 消息列表 -->
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message', message.role]"
          >
            <div class="message-avatar">
              <span v-if="message.role === 'user'">👤</span>
              <span v-else>{{ currentAssistant?.avatar || '🤖' }}</span>
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
            <div class="message-avatar">{{ currentAssistant?.avatar || '🤖' }}</div>
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
              :disabled="isLoading || !currentAssistant"
            ></textarea>
            <button
              @click="sendMessage"
              :disabled="isLoading || !userInput.trim() || !currentAssistant"
              class="btn-send"
            >
              <span v-if="!isLoading">发送 📤</span>
              <span v-else>发送中...</span>
            </button>
          </div>
        </div>
        </div>
      </div>

      <!-- 右侧：列表切换面板 -->
      <div class="manage-panel">
        <div class="panel-content">
          <!-- 助手列表 -->
          <AssistantList
            v-if="rightPanelView === 'assistants'"
            :assistants="assistants"
            :loading="assistantsLoading"
            :selectedId="currentAssistant?.id"
            @create="handleCreateAssistantClick"
            @edit="handleEditAssistant"
            @delete="handleDeleteAssistant"
            @select="handleSelectAssistant"
            @use="handleUseAssistant"
            @test="handleTestAssistant"
            @switch-view="rightPanelView = 'knowledge'"
          />
          
          <!-- 知识库列表 -->
          <KnowledgeBaseList
            v-else-if="rightPanelView === 'knowledge'"
            :knowledge-bases="knowledgeBases"
            :loading="kbLoading"
            :selectedId="selectedKBId"
            @create="handleCreateKBClick"
            @edit="handleEditKB"
            @delete="handleDeleteKB"
            @select="handleSelectKB"
            @view-documents="handleViewDocuments"
            @upload-document="handleUploadDocument"
            @switch-view="rightPanelView = 'assistants'"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'
import AssistantList from './components/AssistantList.vue'
import KnowledgeBaseList from './components/KnowledgeBaseList.vue'
import EmptyAssistantView from './components/EmptyAssistantView.vue'
import CreateKnowledgeBaseForm from './components/CreateKnowledgeBaseForm.vue'
import CreateAssistantForm from './components/CreateAssistantForm.vue'

const toast = useToast()

// 左侧视图状态：empty | create-kb | create-assistant | chat
type LeftViewType = 'empty' | 'create-kb' | 'create-assistant' | 'chat'
const leftView = ref<LeftViewType>('empty')

// 右侧面板视图状态：assistants | knowledge
const rightPanelView = ref<'assistants' | 'knowledge'>('assistants')

// 聊天相关状态
const messages = ref<any[]>([])
const userInput = ref('')
const isLoading = ref(false)
const currentSessionId = ref('')
const greeting = ref('您好！我是智能客服助手')

// 数据
const assistants = ref<any[]>([])
const knowledgeBases = ref<any[]>([])
const currentAssistant = ref<any>(null)
const selectedKBId = ref<number>()

// 加载状态
const assistantsLoading = ref(false)
const kbLoading = ref(false)

// 删除状态
const deleteTarget = ref<any>(null)
const deleteType = ref<'kb' | 'assistant'>('kb')

// 快捷问题 - 动态生成
const quickQuestions = ref<string[]>([])

// 加载推荐问题
const loadRecommendedQuestions = async () => {
  console.log('=== 加载推荐问题 ===')
  console.log('当前助手:', currentAssistant.value)
  console.log('关联知识库信息:', currentAssistant.value?.knowledge_bases_info)
  
  if (!currentAssistant.value || !currentAssistant.value.knowledge_bases_info?.length) {
    // 没有关联知识库时的默认问题
    console.log('❌ 没有关联知识库，使用默认问题')
    quickQuestions.value = [
      '你好，请问你能帮我什么？',
      '你有哪些功能？',
      '如何使用你的服务？'
    ]
    return
  }

  try {
    // 从助手关联的知识库中获取推荐问题
    const kbIds = currentAssistant.value.knowledge_bases_info.map((kb: any) => kb.id)
    console.log('📚 知识库IDs:', kbIds)
    
    const response = await apiService.post('/agent/customer-service/recommended-questions/', {
      knowledge_base_ids: kbIds,
      limit: 4
    })
    
    console.log('API 响应:', response.data)

    if (response.data?.code === 200 && response.data.data?.length > 0) {
      quickQuestions.value = response.data.data
      console.log('✅ 加载推荐问题成功:', quickQuestions.value)
    } else {
      // 后端没有返回问题时的备选方案
      console.log('⚠️ 后端未返回推荐问题，使用备选方案')
      quickQuestions.value = [
        '介绍一下主要功能',
        '有什么使用技巧？',
        '常见问题有哪些？',
        '如何快速上手？'
      ]
    }
  } catch (error) {
    console.error('❌ 加载推荐问题失败:', error)
    // 失败时使用通用问题
    quickQuestions.value = [
      '你能做什么？',
      '有哪些功能？',
      '如何开始使用？',
      '常见问题'
    ]
  }
}

const messagesContainer = ref<HTMLElement>()

// 监听助手列表变化，自动切换视图
watch(() => assistants.value.length, (newLength) => {
  if (newLength === 0 && leftView.value === 'chat') {
    leftView.value = 'empty'
  } else if (newLength > 0 && leftView.value === 'empty') {
    leftView.value = 'chat'
  }
})

// 初始化
onMounted(async () => {
  await loadAssistants()
  await loadKnowledgeBases()
  
  // 设置初始视图
  if (assistants.value.length > 0) {
    leftView.value = 'chat'
    // 加载当前助手的推荐问题
    if (currentAssistant.value) {
      await loadRecommendedQuestions()
    }
  } else {
    leftView.value = 'empty'
  }
})

// 加载助手列表
const loadAssistants = async () => {
  assistantsLoading.value = true
  try {
    const response = await apiService.get('/agent/customer-service/assistants/')
    if (response.data?.code === 200) {
      assistants.value = response.data.data || []
      // 自动选择默认助手
      const defaultAssistant = assistants.value.find(a => a.is_default)
      if (defaultAssistant) {
        currentAssistant.value = defaultAssistant
      } else if (assistants.value.length > 0) {
        currentAssistant.value = assistants.value[0]
      }
    }
  } catch (error) {
    console.error('加载助手失败:', error)
    toast.error('加载助手列表失败')
  } finally {
    assistantsLoading.value = false
  }
}

// 加载知识库列表
const loadKnowledgeBases = async () => {
  kbLoading.value = true
  try {
    const response = await apiService.get('/agent/customer-service/knowledge-bases/')
    if (response.data?.code === 200) {
      knowledgeBases.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载知识库失败:', error)
    toast.error('加载知识库列表失败')
  } finally {
    kbLoading.value = false
  }
}

// 点击创建知识库
const handleCreateKBClick = () => {
  leftView.value = 'create-kb'
}

// 点击创建助手
const handleCreateAssistantClick = () => {
  leftView.value = 'create-assistant'
}

// 取消创建
const handleCancelCreate = () => {
  if (assistants.value.length > 0) {
    leftView.value = 'chat'
  } else {
    leftView.value = 'empty'
  }
}

// 创建知识库
const handleCreateKB = async (data: any) => {
  try {
    const response = await apiService.post('/agent/customer-service/knowledge-bases/', data)
    if (response.data?.code === 201) {
      toast.success('知识库创建成功')
      await loadKnowledgeBases()
      // 返回到原视图
      handleCancelCreate()
    } else {
      toast.error(response.data?.message || '创建失败')
    }
  } catch (error: any) {
    console.error('创建知识库失败:', error)
    toast.error(error.response?.data?.message || '创建失败')
  }
}

// 创建助手
const handleCreateAssistant = async (data: any) => {
  try {
    const response = await apiService.post('/agent/customer-service/assistants/', data)
    if (response.data?.code === 201) {
      toast.success('助手创建成功')
      await loadAssistants()
      // 创建成功后切换到聊天视图
      leftView.value = 'chat'
    } else {
      toast.error(response.data?.message || '创建失败')
    }
  } catch (error: any) {
    console.error('创建助手失败:', error)
    toast.error(error.response?.data?.message || '创建失败')
  }
}

// 选择助手
const handleSelectAssistant = (assistant: any) => {
  currentAssistant.value = assistant
  loadRecommendedQuestions()
}

// 使用助手
const handleUseAssistant = (assistant: any) => {
  currentAssistant.value = assistant
  newSession()
  loadRecommendedQuestions()
  toast.success(`已切换到助手: ${assistant.name}`)
}

// 编辑助手
const handleEditAssistant = (assistant: any) => {
  toast.info('编辑功能开发中...')
  // TODO: 打开编辑弹窗
}

// 删除助手
const handleDeleteAssistant = (assistant: any) => {
  // 直接确认删除
  if (confirm(`确定要删除助手"${assistant.name}"吗？`)) {
    confirmDeleteAssistant(assistant)
  }
}

// 确认删除助手
const confirmDeleteAssistant = async (assistant: any) => {
  try {
    const response = await apiService.delete(`/agent/customer-service/assistants/${assistant.id}/`)
    if (response.data?.code === 200) {
      toast.success('助手已删除')
      await loadAssistants()
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || '删除失败')
  }
}

// 测试助手
const handleTestAssistant = (assistant: any) => {
  currentAssistant.value = assistant
  newSession()
  loadRecommendedQuestions()
  toast.info(`测试模式: ${assistant.name}`)
}

// 选择知识库
const handleSelectKB = (kb: any) => {
  selectedKBId.value = kb.id
}

// 编辑知识库
const handleEditKB = (kb: any) => {
  toast.info('编辑功能开发中...')
  // TODO: 打开编辑弹窗
}

// 删除知识库
const handleDeleteKB = (kb: any) => {
  // 直接确认删除
  if (confirm(`确定要删除知识库"${kb.name}"吗？\n将同时删除所有文档和向量数据。`)) {
    confirmDeleteKB(kb)
  }
}

// 确认删除知识库
const confirmDeleteKB = async (kb: any) => {
  try {
    const response = await apiService.delete(`/agent/customer-service/knowledge-bases/${kb.id}/`)
    if (response.data?.code === 200) {
      toast.success('知识库已删除')
      await loadKnowledgeBases()
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || '删除失败')
  }
}

// 查看文档
const handleViewDocuments = (kb: any) => {
  toast.info('文档管理功能开发中...')
  // TODO: 打开文档管理弹窗
}

// 上传文档
const handleUploadDocument = (kb: any) => {
  toast.info('文档上传功能开发中...')
  // TODO: 打开上传弹窗
}

// 切换助手
const switchAssistant = () => {
  toast.info('请在右侧选择助手')
}

// 新会话
const newSession = () => {
  currentSessionId.value = ''
  messages.value = []
  userInput.value = ''
}

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value || !currentAssistant.value) return

  const messageText = userInput.value.trim()
  userInput.value = ''

  // 添加用户消息
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
      session_id: currentSessionId.value,
      assistant_id: currentAssistant.value.id
    })

    if (response.data?.code === 200) {
      const data = response.data.data

      currentSessionId.value = data.session_id

      messages.value.push({
        role: 'assistant',
        content: data.response,
        intent: data.intent,
        confidence: data.confidence,
        created_at: new Date().toISOString()
      })

      scrollToBottom()
    }
  } catch (error: any) {
    toast.error(error.response?.data?.message || '发送失败')
  } finally {
    isLoading.value = false
  }
}

// 发送快捷问题
const sendQuickQuestion = (question: string) => {
  userInput.value = question
  sendMessage()
}

// 滚动到底部
const scrollToBottom = () => {
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }, 100)
}

// 格式化消息
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

// 获取意图文本
const getIntentText = (intent: string) => {
  const intentMap: Record<string, string> = {
    retrieval: '知识检索',
    reject: '非业务问题'
  }
  return intentMap[intent] || intent
}
</script>

<style scoped>
.cs-manage-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--color-background);
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
  gap: 12px;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-action.btn-primary {
  background: var(--button-primary);
  color: var(--button-primaryText);
  border-color: var(--button-primary);
}

.btn-action:hover {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.main-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 0;
  overflow: hidden;
}

/* 左侧内容区域 */
.left-section {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  overflow: hidden;
}

/* 左侧聊天区域 */
.chat-section {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  margin: 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.current-assistant-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.assistant-avatar-small {
  font-size: 24px;
}

.assistant-name-small {
  font-weight: 600;
  color: var(--color-text);
}

.btn-switch {
  padding: 6px 12px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-switch:hover {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
}

.no-assistant {
  color: var(--color-text-secondary);
  font-style: italic;
}

.btn-new-session {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-new-session:hover {
  box-shadow: var(--button-shadow);
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
  background: var(--input-background);
  color: var(--color-text);
  transition: border-color 0.3s;
}

.input-wrapper textarea:focus {
  outline: none;
  border-color: var(--button-primary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.input-wrapper textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

/* 右侧管理面板 */
.manage-panel {
  display: flex;
  flex-direction: column;
  background: var(--color-background);
}

.panel-content {
  flex: 1;
  overflow: hidden;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr 350px;
  }
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .manage-panel {
    display: none;
  }
  
  /* 移动端可以添加底部标签栏或抽屉 */
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: var(--color-surface);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: var(--button-primary);
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr 350px;
  }
}
</style>

