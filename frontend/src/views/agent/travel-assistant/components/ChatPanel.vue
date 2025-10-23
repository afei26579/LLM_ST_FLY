<template>
  <div class="chat-panel">
    <!-- 头部 -->
    <div class="chat-header">
      <h3>🧳 旅游助手</h3>
      <div class="header-actions">
        <button @click="togglePreferences" class="btn-icon" title="旅行设置">
          ⚙️
        </button>
        <button @click="emit('clear-chat')" class="btn-icon" title="清空对话">
          🗑️
        </button>
      </div>
    </div>

    <!-- 旅行设置面板 -->
    <div v-if="showPreferences" class="preferences-panel">
      <div class="preferences-header">
        <h4>🛠️ 旅行设置</h4>
        <button @click="showPreferences = false" class="close-btn">×</button>
      </div>
      <div class="pref-grid">
        <div class="pref-item">
          <label>起点</label>
          <input 
            v-model="localPreferences.origin" 
            type="text" 
            placeholder="出发地点"
          />
        </div>
        <div class="pref-item">
          <label>终点</label>
          <input 
            v-model="localPreferences.destination" 
            type="text" 
            placeholder="目的地"
          />
        </div>
        <div class="pref-item">
          <label>出发时间</label>
          <input 
            v-model="localPreferences.departureTime" 
            type="date"
          />
        </div>
        <div class="pref-item">
          <label>时长</label>
          <input 
            v-model="localPreferences.duration" 
            type="text" 
            placeholder="如: 3天"
          />
        </div>
        <div class="pref-item">
          <label>人数</label>
          <input 
            v-model="localPreferences.peopleCount" 
            type="text" 
            placeholder="如: 2大人1小孩"
          />
        </div>
        <div class="pref-item">
          <label>出行方式</label>
          <select v-model="localPreferences.transportation">
            <option value="">请选择</option>
            <option value="自驾">自驾</option>
            <option value="公共交通">公共交通</option>
            <option value="混合">混合</option>
          </select>
        </div>
        <div class="pref-item">
          <label>预算</label>
          <input 
            v-model="localPreferences.budget" 
            type="text" 
            placeholder="如: 5000元"
          />
        </div>
        <div class="pref-item full-width">
          <label>备注</label>
          <textarea 
            v-model="localPreferences.notes" 
            placeholder="其他要求或备注..."
            rows="2"
          ></textarea>
        </div>
      </div>
      <div class="preferences-actions">
        <button @click="applyPreferences" class="apply-btn">
          ✨ 应用设置
        </button>
      </div>
    </div>

    <!-- 消息列表 -->
    <div ref="messagesContainer" class="messages-container">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="welcome">
          <h2>👋 欢迎使用旅游助手</h2>
          <p>我可以帮您：</p>
          <ul>
            <li>🗺️ 搜索景点、美食、酒店</li>
            <li>🚗 规划路线和交通</li>
            <li>☀️ 查询天气信息</li>
            <li>📅 制定详细的行程计划</li>
          </ul>
          <div class="quick-suggestions">
            <p>快速开始：</p>
            <button 
              v-for="suggestion in suggestions" 
              :key="suggestion"
              @click="emit('send-suggestion', suggestion)"
              class="suggestion-btn"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
      </div>

      <div v-for="message in messages" :key="message.id" class="message" :class="message.role">
        <div class="message-avatar">
          <span v-if="message.role === 'user'">👤</span>
          <span v-else-if="message.role === 'assistant'">🤖</span>
          <span v-else>ℹ️</span>
        </div>
        <div class="message-content">
          <div class="message-text" v-html="formatMessage(message.content)"></div>
          <div v-if="message.toolCalls && message.toolCalls.length > 0" class="tool-calls">
            <span class="tool-badge">🔧 使用了工具</span>
          </div>
          <div v-if="message.isStreaming" class="streaming-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>

      <div v-if="isLoading && !isStreaming" class="message assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="loading-dots">
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
          v-model="inputText"
          @keydown.enter.prevent="handleSend"
          placeholder="输入您的旅行需求..."
          rows="3"
          :disabled="isLoading"
        ></textarea>
        <div class="input-buttons">
          <button 
            @click="handleSend" 
            :disabled="!inputText.trim() || isLoading"
            class="send-btn"
            title="发送消息"
          >
            <span v-if="isLoading">⏳</span>
            <span v-else>↑</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'

// Props
interface Props {
  messages: Array<{
    id: string
    role: 'user' | 'assistant' | 'system'
    content: string
    timestamp: Date
    toolCalls?: any[]
    isStreaming?: boolean
  }>
  isLoading: boolean
  userPreferences?: {
    origin?: string
    destination?: string
    departureTime?: string
    duration?: string
    peopleCount?: string
    transportation?: string
    budget?: string
    notes?: string
    travelStyle?: string
  }
}

const props = withDefaults(defineProps<Props>(), {
  messages: () => [],
  isLoading: false,
  userPreferences: () => ({})
})

// Emits
const emit = defineEmits<{
  'send-message': [content: string, useStream: boolean]
  'send-suggestion': [suggestion: string]
  'update-preferences': [preferences: any]
  'toggle-preferences': []
  'clear-chat': []
}>()

// 状态
const inputText = ref('')
const showPreferences = ref(false)
const localPreferences = ref({ ...props.userPreferences })
const messagesContainer = ref<HTMLElement | null>(null)

// 快速建议
const suggestions = [
  '我想去北京旅游3天',
  '帮我推荐上海的美食',
  '查询杭州的天气',
  '规划一个成都周末游'
]

// 计算属性
const isStreaming = computed(() => {
  return props.messages.some(m => m.isStreaming)
})

// 方法
const handleSend = () => {
  if (!inputText.value.trim() || props.isLoading) return
  
  // 默认使用流式输出
  emit('send-message', inputText.value, true)
  inputText.value = ''
}

const togglePreferences = () => {
  showPreferences.value = !showPreferences.value
}

const applyPreferences = () => {
  // 更新偏好设置
  emit('update-preferences', { ...localPreferences.value })
  
  // 生成提示词
  const prompt = generatePromptFromPreferences()
  if (prompt) {
    inputText.value = prompt
  }
  
  // 关闭设置面板
  showPreferences.value = false
}

const generatePromptFromPreferences = (): string => {
  const prefs = localPreferences.value
  const parts: string[] = []
  
  if (prefs.origin && prefs.destination) {
    parts.push(`我计划从${prefs.origin}到${prefs.destination}旅游`)
  } else if (prefs.destination) {
    parts.push(`我想去${prefs.destination}旅游`)
  }
  
  if (prefs.departureTime) {
    parts.push(`出发时间是${prefs.departureTime}`)
  }
  
  if (prefs.duration) {
    parts.push(`时长${prefs.duration}`)
  }
  
  if (prefs.peopleCount) {
    parts.push(`出行人数${prefs.peopleCount}`)
  }
  
  if (prefs.transportation) {
    parts.push(`出行方式${prefs.transportation}`)
  }
  
  if (prefs.budget) {
    parts.push(`预算${prefs.budget}`)
  }
  
  if (prefs.notes) {
    parts.push(`特殊要求：${prefs.notes}`)
  }
  
  return parts.length > 0 ? parts.join('，') + '。请帮我规划行程。' : ''
}

const formatMessage = (content: string) => {
  // 简单的markdown转换
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}

const formatTime = (date: Date) => {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动到底部
watch(() => props.messages, scrollToBottom, { deep: true })

// 监听偏好设置切换
watch(() => props.userPreferences, (newPrefs) => {
  localPreferences.value = { ...newPrefs }
}, { deep: true })

// 暴露方法供父组件调用
defineExpose({
  togglePreferences
})
</script>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--card-background);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--button-primary);
  color: var(--button-primaryText);
}

.chat-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 16px;
  color: var(--button-primaryText);
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.05);
}

.preferences-panel {
  padding: 16px 20px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.preferences-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.preferences-header h4 {
  margin: 0;
  font-size: 16px;
  color: var(--color-text);
  font-weight: 600;
}

.preferences-header .close-btn {
  background: none;
  border: none;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
  color: var(--color-textSecondary);
  padding: 0;
  width: 28px;
  height: 28px;
  transition: all 0.2s;
}

.preferences-header .close-btn:hover {
  color: var(--color-text);
  transform: rotate(90deg);
}

.pref-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.pref-item {
  display: flex;
  flex-direction: column;
}

.pref-item.full-width {
  grid-column: 1 / -1;
}

.pref-item label {
  margin-bottom: 6px;
  font-size: 13px;
  color: var(--color-textSecondary);
  font-weight: 500;
}

.pref-item input,
.pref-item select,
.pref-item textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
  background: var(--color-background);
  color: var(--color-text);
  transition: all 0.2s;
}

.pref-item input:focus,
.pref-item select:focus,
.pref-item textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb, 94, 155, 255), 0.1);
}

.pref-item textarea {
  resize: vertical;
  font-family: inherit;
}

.preferences-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.apply-btn {
  padding: 10px 24px;
  background: var(--button-success);
  color: var(--button-successText);
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.apply-btn:hover {
  background: var(--button-successHover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-success-rgb, 34, 197, 94), 0.3);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--color-background);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.welcome {
  text-align: center;
  max-width: 500px;
}

.welcome h2 {
  color: var(--color-text);
  margin-bottom: 16px;
}

.welcome ul {
  text-align: left;
  margin: 20px 0;
  color: var(--color-textSecondary);
}

.quick-suggestions {
  margin-top: 24px;
}

.quick-suggestions p {
  margin-bottom: 12px;
  color: var(--color-textSecondary);
}

.suggestion-btn {
  display: inline-block;
  margin: 4px;
  padding: 8px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text);
  transition: all 0.2s;
}

.suggestion-btn:hover {
  background: var(--button-primary);
  color: var(--button-primaryText);
  border-color: var(--button-primary);
  transform: translateY(-2px);
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
}

.message.user .message-avatar {
  background: var(--button-primary);
}

.message.assistant .message-avatar {
  background: var(--button-secondary);
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  background: var(--color-surface);
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.message.user .message-text {
  background: var(--button-primary);
  color: var(--button-primaryText);
  border-color: transparent;
}

.tool-calls {
  margin-top: 8px;
}

.tool-badge {
  display: inline-block;
  padding: 4px 8px;
  background: #ffeaa7;
  border-radius: 4px;
  font-size: 11px;
  color: #d63031;
}

.streaming-indicator {
  margin-top: 8px;
  display: flex;
  gap: 4px;
}

.streaming-indicator .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #667eea;
  animation: pulse 1.4s infinite;
}

.streaming-indicator .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.streaming-indicator .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

.message-time {
  margin-top: 4px;
  font-size: 11px;
  color: var(--color-textSecondary);
  opacity: 0.7;
}

.loading-dots {
  display: flex;
  gap: 6px;
  padding: 12px 16px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: bounce 1.4s infinite;
}

.loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.input-area {
  padding: 16px 20px;
  background: var(--card-background);
  border-top: 1px solid var(--color-border);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.input-wrapper textarea {
  flex: 1;
  padding: 12px 16px;
  padding-right: 50px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  background: var(--color-background);
  color: var(--color-text);
  transition: all 0.2s;
}

.input-wrapper textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb, 94, 155, 255), 0.1);
}

.input-wrapper textarea::placeholder {
  color: var(--color-textSecondary);
  opacity: 0.6;
}

.input-buttons {
  position: absolute;
  right: 8px;
  bottom: 8px;
  display: flex;
  gap: 6px;
}

.send-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  background: var(--button-primary);
  color: var(--button-primaryText);
  font-weight: 600;
}

.send-btn:hover:not(:disabled) {
  background: var(--button-primaryHover);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(var(--color-primary-rgb, 94, 155, 255), 0.3);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>

