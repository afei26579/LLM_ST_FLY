<template>
  <div class="chat-sidebar">
    <div class="sidebar-header">
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
          <div 
            class="conversation-content" 
            @click="handleSwitchConversation(conversation.id)"
            :title="getConversationPreview(conversation)"
          >
            <div class="conversation-title">
              <!-- 置顶图标 -->
              <svg 
                v-if="conversation.is_pinned || conversation.isPinned" 
                class="pin-icon"
                xmlns="http://www.w3.org/2000/svg" 
                width="14" 
                height="14" 
                viewBox="0 0 24 24" 
                fill="currentColor"
              >
                <path d="M16 9V4h1c.55 0 1-.45 1-1s-.45-1-1-1H7c-.55 0-1 .45-1 1s.45 1 1 1h1v5c0 1.66-1.34 3-3 3v2h5.97v7l1 1 1-1v-7H19v-2c-1.66 0-3-1.34-3-3z"/>
              </svg>
              <span>{{ conversation.display_title || conversation.custom_title || conversation.title }}</span>
            </div>
           
            <div class="conversation-date">{{ formatDate(conversation.lastUpdated) }}</div>
          </div>
          <div class="conversation-actions">
            <!-- 展开按钮占位区域 - 始终保持高度一致 -->
            <div class="expand-btn-wrapper">
              <button 
                v-if="getQuestionCount(conversation) > 1"
                class="action-btn expand-btn" 
                @click="toggleConversationExpand(conversation.id)"
                :title="isConversationExpanded(conversation.id) ? '收起问题列表' : '展开问题列表'"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                     :class="{ 'expanded': isConversationExpanded(conversation.id) }">
                  <polyline points="6,9 12,15 18,9"></polyline>
                </svg>
              </button>
            </div>
            <!-- 三个点下拉菜单 -->
            <div class="dropdown-container">
              <button 
                class="action-btn more-btn" 
                @click="toggleDropdown(conversation.id, $event)"
                title="更多操作"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="1"></circle>
                  <circle cx="19" cy="12" r="1"></circle>
                  <circle cx="5" cy="12" r="1"></circle>
                </svg>
              </button>
              
              <!-- 下拉菜单 -->
              <div 
                v-if="activeDropdownId === conversation.id" 
                class="dropdown-menu"
                :style="{
                  top: dropdownPosition.top + 'px',
                  right: dropdownPosition.right + 'px'
                }"
                @click.stop
              >
                <div class="dropdown-item" @click="handlePinConversation(conversation.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="17" x2="12" y2="3"></line>
                    <path d="m5 7 14 0"></path>
                    <path d="m12 17.01.01 0"></path>
                  </svg>
                  <span>{{ conversation.isPinned ? '取消置顶' : '置顶' }}</span>
                </div>
                <div class="dropdown-item" @click="handleRenameConversation(conversation.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m18 2-4 20L10.5 17 3 9.5z"></path>
                    <path d="m9 15 5-5"></path>
                  </svg>
                  <span>重命名</span>
                </div>
                <div class="dropdown-item" @click="handleDownloadConversation(conversation.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7,10 12,15 17,10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                  <span>下载对话</span>
                </div>
                <div class="dropdown-divider"></div>
                <div class="dropdown-item danger" @click="handleDeleteConversation(conversation.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m3 6 3 0"></path>
                    <path d="m21 6-3 0"></path>
                    <path d="m10 11 0 6"></path>
                    <path d="m14 11 0 6"></path>
                    <path d="m18 6-1 14-10 0-1-14"></path>
                    <path d="m8 6 0-2c0-1 1-2 2-2l4 0c1 0 2 1 2 2l0 2"></path>
                  </svg>
                  <span>删除对话</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 展开的问题列表 -->
        <div 
          v-if="isConversationExpanded(conversation.id)" 
          class="questions-list"
        >
          <div class="questions-container">
            <div v-if="props.isHistoryLoading(conversation.id)" class="loading-questions">
              <div class="spinner-small"></div>
              <span>加载问题列表中...</span>
            </div>
            
            <div v-else>
              <div 
                v-for="(question, qIndex) in getUserQuestions(conversation.id)" 
                :key="`q-${qIndex}`"
                class="question-item"
                @click="handleJumpToQuestion(conversation.id, qIndex)"
              >
                <div class="question-text">{{ question }}</div>
              </div>
              
              <div v-if="getUserQuestions(conversation.id).length === 0" class="no-questions">
                暂无问题记录
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="filteredConversations.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <p>还没有对话历史</p>
        <p class="empty-hint">开始你的第一次对话吧！</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { formatDate } from '@/utils/dateUtils'

// Types are imported from composables
type Conversation = any // Will use the type from useConversations composable

// Props
interface Props {
  conversations: any[]
  activeConversationId: number | null
  isLoadingConversations: boolean
  isHistoryLoading: (id: number) => boolean
  filteredConversations: any[]
  isConversationExpanded: (id: number) => boolean
  getUserQuestions: (id: number) => string[]
}

const props = defineProps<Props>()

// Emits
interface Emits {
  (e: 'createNewConversation'): void
  (e: 'switchConversation', id: number): void
  (e: 'deleteConversation', id: number): void
  (e: 'toggleConversationExpand', id: number): void
  (e: 'jumpToQuestion', conversationId: number, questionIndex: number): void
  (e: 'pinConversation', id: number): void
  (e: 'renameConversation', id: number): void
  (e: 'downloadConversation', id: number): void
}

const emit = defineEmits<Emits>()

// State
const searchQuery = ref('')
const activeDropdownId = ref<number | null>(null)
const dropdownPosition = ref({ top: 0, right: 0 })

// Methods
const handleCreateNewConversation = () => {
  emit('createNewConversation')
}

const handleSwitchConversation = (id: number) => {
  emit('switchConversation', id)
}

const toggleConversationExpand = (id: number) => {
  emit('toggleConversationExpand', id)
}

const handleJumpToQuestion = (conversationId: number, questionIndex: number) => {
  emit('jumpToQuestion', conversationId, questionIndex)
}

// 下拉菜单相关方法
const toggleDropdown = (conversationId: number, event?: Event) => {
  if (activeDropdownId.value === conversationId) {
    activeDropdownId.value = null
    return
  }
  
  // 计算按钮位置
  if (event) {
    const target = event.currentTarget as HTMLElement
    const rect = target.getBoundingClientRect()
    const viewportWidth = window.innerWidth
    
    dropdownPosition.value = {
      top: rect.bottom + 4, // 按钮下方4px
      right: viewportWidth - rect.right // 从右边对齐
    }
  }
  
  activeDropdownId.value = conversationId
}

const handlePinConversation = (id: number) => {
  emit('pinConversation', id)
  activeDropdownId.value = null
}

const handleRenameConversation = (id: number) => {
  emit('renameConversation', id)
  activeDropdownId.value = null
}

const handleDownloadConversation = (id: number) => {
  emit('downloadConversation', id)
  activeDropdownId.value = null
}

// 重写删除方法，添加关闭下拉菜单逻辑
const handleDeleteConversation = (id: number) => {
  emit('deleteConversation', id)
  activeDropdownId.value = null
}

// Use functions from props
const isConversationExpanded = (id: number): boolean => {
  return props.isConversationExpanded(id)
}

const getUserQuestions = (conversationId: number): string[] => {
  return props.getUserQuestions(conversationId)
}

// 获取对话的预览文本（显示第一个用户问题）
const getConversationPreview = (conversation: any): string => {
  // 优先使用后端返回的第一个用户问题
  if (conversation.first_user_question) {
    return conversation.first_user_question
  }
  
  // 如果有消息数组，找到第一个用户问题
  if (conversation.messages && conversation.messages.length > 0) {
    const firstUserMessage = conversation.messages.find((msg: any) => msg.role === 'user')
    if (firstUserMessage) {
      // 截取前50个字符作为预览
      return firstUserMessage.content.length > 50 
        ? firstUserMessage.content.substring(0, 50) + '...'
        : firstUserMessage.content
    }
  }
  
  // 如果没有用户问题，使用原有的preview
  return conversation.preview || '空对话'
}

// 获取对话中用户问题的数量
const getQuestionCount = (conversation: any): number => {
  // 优先使用后端返回的用户问题数量
  if (conversation.user_question_count !== undefined) {
    return conversation.user_question_count
  }
  
  // 如果有消息数组，计算用户问题数量
  if (conversation.messages && conversation.messages.length > 0) {
    return conversation.messages.filter((msg: any) => msg.role === 'user').length
  }
  
  return 0
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.dropdown-container')) {
    activeDropdownId.value = null
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Expose search query for parent component
defineExpose({
  searchQuery
})
</script>

<style scoped>
.chat-sidebar {
  width: 320px;
  background: var(--sidebar-background, #f8f9fa);
  border-left: 1px solid var(--sidebar-border, #e9ecef);
  display: flex;
  flex-direction: column;
  height: 100%;
  order: 2;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid var(--sidebar-border, #e9ecef);
  background: var(--color-surface, white);
}

.new-chat-button {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: var(--button-primary, #007bff);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
  position: relative;
  overflow: hidden;
}

.new-chat-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.new-chat-button:hover {
  background: var(--button-primaryHover, #0056b3);
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px var(--color-primary, rgba(0, 245, 255, 0.3)),
    0 0 20px var(--color-primary, rgba(0, 245, 255, 0.2));
  animation: buttonPulse 1.5s ease-in-out infinite alternate;
}

.new-chat-button:hover::before {
  left: 100%;
}

@keyframes buttonPulse {
  0% {
    box-shadow: 
      0 8px 25px var(--color-primary, rgba(0, 245, 255, 0.3)),
      0 0 20px var(--color-primary, rgba(0, 245, 255, 0.2));
  }
  100% {
    box-shadow: 
      0 12px 35px var(--color-primary, rgba(0, 245, 255, 0.4)),
      0 0 30px var(--color-primary, rgba(0, 245, 255, 0.3));
  }
}

.search-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  padding-right: 2.5rem;
  border: 1px solid var(--color-border, #e9ecef);
  border-radius: 12px;
  outline: none;
  transition: border-color 0.3s ease;
  background: var(--color-background, white);
  color: var(--color-text, #1f2937);
}

.search-input:focus {
  border-color: var(--color-primary, #007bff);
}

.search-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-textSecondary, #6c757d);
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

/* 霓虹滚动条样式 */
.conversations-list::-webkit-scrollbar {
  width: 6px;
}

.conversations-list::-webkit-scrollbar-track {
  background: var(--color-surface, #f1f1f1);
  border-radius: 10px;
}

.conversations-list::-webkit-scrollbar-thumb {
  background: var(--color-primary, linear-gradient(180deg, #00f5ff, #9d4edd, #ff0080));
  border-radius: 10px;
  box-shadow: 0 0 8px var(--color-primary, rgba(0, 245, 255, 0.4));
  animation: sidebarScrollbarGlow 2.5s ease-in-out infinite alternate;
}

.conversations-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary, linear-gradient(180deg, #00d4ff, #8b3fd9, #e6006b));
  box-shadow: 0 0 12px var(--color-primary, rgba(0, 245, 255, 0.7));
}

@keyframes sidebarScrollbarGlow {
  0% {
    box-shadow: 0 0 8px var(--color-primary, rgba(0, 245, 255, 0.4));
  }
  100% {
    box-shadow: 0 0 16px var(--color-primary, rgba(255, 0, 128, 0.6));
  }
}

.list-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-textSecondary, #6c757d);
  margin: 0 0 1rem 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: var(--color-textSecondary, #6c757d);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f8f9fa;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.conversation-item {
  background: var(--card-background, white);
  border: 1px solid var(--card-border, #e9ecef);
  border-radius: 12px;
  margin-bottom: 0.5rem;
  overflow: visible; /* 改为visible，允许下拉菜单显示 */
  transition: all 0.3s ease;
}

.conversation-item:hover {
  box-shadow: var(--card-shadow, 0 4px 12px rgba(0, 0, 0, 0.1));
}

.conversation-item.active {
  border: 1px solid transparent;
  background-clip: padding-box;
  position: relative;
  animation: activeConversationGlow 2s ease-in-out infinite alternate;
}

.conversation-item.active::before {
  content: '';
  position: absolute;
  top: -1px;
  left: -1px;
  right: -1px;
  bottom: -1px;
  background: var(--color-border, linear-gradient(90deg, #00f5ff 0%, #9d4edd 50%, #ff0080 100%));
  border-radius: 13px;
  z-index: -1;
}

@keyframes activeConversationGlow {
  0% {
    box-shadow: 
      0 0 15px var(--color-primary, rgba(0, 245, 255, 0.3)),
      inset 0 0 15px var(--color-primary, rgba(0, 245, 255, 0.1));
  }
  100% {
    box-shadow: 
      0 0 25px var(--color-primary, rgba(0, 245, 255, 0.5)),
      inset 0 0 25px var(--color-primary, rgba(0, 245, 255, 0.15));
  }
}

.conversation-main {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.conversation-content {
  flex: 1;
  min-width: 0; /* 确保flex子元素可以正确收缩 */
  padding: 1rem;
  cursor: pointer;
}

.conversation-title {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 600;
  color: var(--color-text, #343a40);
  margin-bottom: 0.25rem;
  overflow: hidden;
}

.conversation-title span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pin-icon {
  color: var(--color-warning, #ffc107);
  flex-shrink: 0;
  filter: drop-shadow(0 0 4px rgba(255, 193, 7, 0.5));
  animation: pinGlow 2s ease-in-out infinite alternate;
}

@keyframes pinGlow {
  0% {
    filter: drop-shadow(0 0 4px rgba(255, 193, 7, 0.5));
  }
  100% {
    filter: drop-shadow(0 0 8px rgba(255, 193, 7, 0.8));
  }
}

.conversation-preview {
  color: var(--color-textSecondary, #6c757d);
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-date {
  color: var(--color-textTertiary, #adb5bd);
  font-size: 0.75rem;
}

.conversation-actions {
  display: flex;
  flex-direction: column;
  padding: 0.5rem;
  gap: 0.25rem;
  flex-shrink: 0; /* 防止按钮被压缩 */
  position: relative; /* 为下拉菜单提供定位基准 */
}

.expand-btn-wrapper {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0; /* 固定高度，即使没有展开按钮也占位 */
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  color: var(--color-text, #6c757d);
  opacity: 0.7;
}

.action-btn:hover {
  opacity: 1;
}

.expand-btn {
  color: var(--color-primary, #00f5ff);
}

.expand-btn:hover {
  background: var(--button-secondaryHover, rgba(0, 245, 255, 0.15));
  color: var(--color-primary, #00f5ff);
  transform: scale(1.15);
  box-shadow: 0 0 12px var(--color-primary, rgba(0, 245, 255, 0.4));
}

.expand-btn svg {
  transition: transform 0.3s ease;
  filter: drop-shadow(0 0 2px var(--color-primary, rgba(0, 245, 255, 0.5)));
}

.expand-btn svg.expanded {
  transform: rotate(180deg);
}

.delete-btn {
  color: #ff4757;
}

.delete-btn:hover {
  background: rgba(255, 71, 87, 0.15);
  color: #ff4757;
  transform: scale(1.15);
  box-shadow: 0 0 12px rgba(255, 71, 87, 0.4);
}

.delete-btn svg {
  filter: drop-shadow(0 0 2px rgba(255, 71, 87, 0.5));
}

/* 下拉菜单样式 */
.dropdown-container {
  position: relative;
}

.more-btn {
  color: var(--color-text, #6c757d);
}

.more-btn:hover {
  background: var(--button-secondaryHover, rgba(108, 117, 125, 0.15));
  color: var(--color-text, #495057);
}

.dropdown-menu {
  position: fixed;
  z-index: 9999;
  min-width: 160px;
  background: var(--color-background, #ffffff);
  border: 1px solid var(--color-border, #e9ecef);
  border-radius: 8px;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.05);
  padding: 4px 0;
  animation: slideIn 0.2s ease-out;
  backdrop-filter: blur(10px); /* 毛玻璃效果 */
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.875rem;
  color: var(--color-text, #495057);
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: var(--color-surface, #f8f9fa);
}

.dropdown-item.danger {
  color: #ff4757;
}

.dropdown-item.danger:hover {
  background: rgba(255, 71, 87, 0.1);
  color: #ff4757;
}

.dropdown-item svg {
  flex-shrink: 0;
}

.dropdown-divider {
  height: 1px;
  background: var(--color-border, #e9ecef);
  margin: 4px 0;
}

.questions-list {
  border-top: 1px solid var(--color-border, rgba(0, 245, 255, 0.2));
  background: var(--color-surface, rgba(0, 0, 0, 0.3));
  backdrop-filter: blur(10px);
}

.questions-container {
  padding: 1rem;
  max-height: 200px;
  overflow-y: auto;
}

/* 问题列表的滚动条样式 */
.questions-container::-webkit-scrollbar {
  width: 4px;
}

.questions-container::-webkit-scrollbar-track {
  background: var(--color-surface, #f1f1f1);
  border-radius: 10px;
}

.questions-container::-webkit-scrollbar-thumb {
  background: var(--color-accent, #ff0080);
  border-radius: 10px;
  box-shadow: 0 0 6px var(--color-accent, rgba(255, 0, 128, 0.5));
}

.questions-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-accent, #e6006b);
  box-shadow: 0 0 10px var(--color-accent, rgba(255, 0, 128, 0.8));
}

.loading-questions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--color-textSecondary, #6c757d);
  padding: 1rem;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-surface, #f8f9fa);
  border-top: 2px solid var(--color-primary, #00f5ff);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.question-item {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 0.5rem;
  border: 1px solid transparent;
  position: relative;
}

.question-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: linear-gradient(135deg, var(--color-primary, #00f5ff), var(--color-accent, #ff0080));
  border-radius: 0 2px 2px 0;
  transition: height 0.3s ease;
}

.question-item:hover {
  background: var(--button-secondaryHover, rgba(0, 245, 255, 0.08));
  border-color: var(--color-primary, rgba(0, 245, 255, 0.3));
  transform: translateX(4px);
  box-shadow: 0 2px 8px var(--color-primary, rgba(0, 245, 255, 0.15));
}

.question-item:hover::before {
  height: 70%;
}

.question-text {
  font-size: 0.875rem;
  color: var(--color-text, #495057);
  line-height: 1.5;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
}

.no-questions {
  text-align: center;
  color: var(--color-textSecondary, #6c757d);
  font-size: 0.875rem;
  padding: 1rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
  color: #6c757d;
}

.empty-state svg {
  color: #adb5bd;
  margin-bottom: 1rem;
}

.empty-state p {
  margin: 0.25rem 0;
}

.empty-hint {
  font-size: 0.875rem;
  opacity: 0.8;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .chat-sidebar {
    width: 100%;
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1000;
    height: 100vh;
  }
}

/* 主题样式已由CSS变量控制 */
</style>
