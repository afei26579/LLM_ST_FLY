<template>
  <div class="chat-history">
    <div class="history-header">
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
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatDate } from '../../../utils/dateUtils'

interface Question {
  index: number
  content: string
  timestamp: string
}

interface Conversation {
  id: number
  title: string
  preview: string
  lastUpdated: string | Date
  message_count: number
  messages?: any[]
}

interface Props {
  conversations: Conversation[]
  isLoadingConversations: boolean
  activeConversationId: number | null
  searchQuery: string
  filteredConversations: Conversation[]
  isConversationExpanded: (id: number) => boolean
  isHistoryLoading: (id: number) => boolean
  getUserQuestions: (conversation: Conversation) => Question[]
}

interface Emits {
  (e: 'update:searchQuery', value: string): void
  (e: 'create-new-conversation'): void
  (e: 'switch-conversation', id: number): void
  (e: 'delete-conversation', id: number): void
  (e: 'toggle-conversation-expand', id: number): void
  (e: 'jump-to-question', conversationId: number, questionIndex: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const searchQuery = computed({
  get: () => props.searchQuery,
  set: (value: string) => emit('update:searchQuery', value)
})

// 方法
const handleCreateNewConversation = () => {
  emit('create-new-conversation')
}

const handleSwitchConversation = (id: number) => {
  emit('switch-conversation', id)
}

const handleDeleteConversation = (id: number) => {
  emit('delete-conversation', id)
}

const toggleConversationExpand = (id: number) => {
  emit('toggle-conversation-expand', id)
}

const handleJumpToQuestion = (conversationId: number, questionIndex: number) => {
  emit('jump-to-question', conversationId, questionIndex)
}

// 使用从props传入的函数
const { isConversationExpanded, isHistoryLoading, getUserQuestions } = props
</script>

<style scoped>
.chat-history {
  width: 300px;
  height: 100%;
  background-color: var(--color-background-soft, #f8fafc);
  border-left: none;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-header {
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

.no-results {
  padding: 2rem 0;
  text-align: center;
  color: var(--color-text-soft, #64748b);
  font-size: 0.875rem;
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

@media (max-width: 768px) {
  .chat-history {
    width: 100%;
    height: 100%;
    position: fixed;
    transform: translateX(100%);
    transition: transform 0.3s ease;
    z-index: 1000;
  }
  
  .chat-history.show {
    transform: translateX(0);
  }
}
</style>