<template>
  <div class="assistant-list">
    <div class="list-header">
      <h3>🤖 助手列表</h3>
      <button @click="$emit('switch-view')" class="btn-switch-view">
        切换到知识库
      </button>
    </div>

    <div class="search-box">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索助手..."
        class="search-input"
      />
    </div>

    <div class="list-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="filteredAssistants.length === 0" class="empty-state">
        <div class="empty-icon">🤖</div>
        <p>暂无助手</p>
        <button @click="$emit('create')" class="btn-create-first">
          创建第一个助手
        </button>
      </div>

      <div v-else class="assistant-items">
        <div
          v-for="assistant in filteredAssistants"
          :key="assistant.id"
          :class="['assistant-item', { active: selectedId === assistant.id, default: assistant.is_default }]"
          @click="selectAssistant(assistant)"
        >
          <div class="assistant-header">
            <div class="assistant-avatar">{{ assistant.avatar || '🤖' }}</div>
            <div class="assistant-info">
              <div class="assistant-name-row">
                <h4 class="assistant-name">{{ assistant.name }}</h4>
                <span v-if="assistant.is_default" class="default-badge">默认</span>
              </div>
              <p v-if="assistant.description" class="assistant-description">
                {{ assistant.description }}
              </p>
            </div>
          </div>

          <div class="assistant-meta">
            <span class="meta-item">
              <span class="meta-icon">🧠</span>
              {{ assistant.model }}
            </span>
            <span class="meta-item">
              <span class="meta-icon">📚</span>
              {{ assistant.knowledge_bases_info?.length || 0 }} 知识库
            </span>
          </div>

          <div class="assistant-stats">
            <div class="stat-col">
              <div class="stat-value">{{ assistant.total_conversations || 0 }}</div>
              <div class="stat-label">对话</div>
            </div>
            <div class="stat-col">
              <div class="stat-value">{{ assistant.total_messages || 0 }}</div>
              <div class="stat-label">消息</div>
            </div>
            <div class="stat-col">
              <div class="stat-value">
                {{ assistant.avg_satisfaction ? assistant.avg_satisfaction.toFixed(1) : '-' }}
              </div>
              <div class="stat-label">满意度</div>
            </div>
          </div>

          <div class="assistant-actions">
            <button
              @click.stop="$emit('use', assistant)"
              class="btn-action btn-use"
              title="使用此助手"
            >
              💬 使用
            </button>
            <button
              @click.stop="$emit('edit', assistant)"
              class="btn-action"
              title="编辑"
            >
              ✏️
            </button>
            <button
              @click.stop="$emit('test', assistant)"
              class="btn-action"
              title="测试"
            >
              🧪
            </button>
            <button
              @click.stop="$emit('delete', assistant)"
              class="btn-action btn-danger"
              title="删除"
            >
              🗑️
            </button>
          </div>

          <div v-if="!assistant.is_active" class="inactive-overlay">
            <span>已禁用</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Assistant {
  id: number
  name: string
  description: string
  avatar: string
  model: string
  is_default: boolean
  is_active: boolean
  total_conversations: number
  total_messages: number
  avg_satisfaction?: number
  knowledge_bases_info?: Array<{ id: number; name: string }>
}

interface Props {
  assistants: Assistant[]
  loading?: boolean
  selectedId?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  selectedId: undefined
})

const emit = defineEmits<{
  create: []
  edit: [assistant: Assistant]
  delete: [assistant: Assistant]
  select: [assistant: Assistant]
  use: [assistant: Assistant]
  test: [assistant: Assistant]
  'switch-view': []
}>()

const searchQuery = ref('')

const filteredAssistants = computed(() => {
  if (!searchQuery.value) return props.assistants
  
  const query = searchQuery.value.toLowerCase()
  return props.assistants.filter(assistant =>
    assistant.name.toLowerCase().includes(query) ||
    assistant.description?.toLowerCase().includes(query)
  )
})

const selectAssistant = (assistant: Assistant) => {
  emit('select', assistant)
}
</script>

<style scoped>
.assistant-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  border-radius: 12px;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.list-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.btn-switch-view {
  padding: 8px 16px;
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-switch-view:hover {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
  color: var(--button-primary);
  transform: translateY(-2px);
}

.search-box {
  padding: 12px 20px;
  border-bottom: 1px solid var(--color-border);
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--input-border);
  border-radius: 8px;
  background: var(--input-background);
  color: var(--color-text);
  font-size: 14px;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: var(--button-primary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  color: var(--color-text-secondary);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top-color: var(--button-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.btn-create-first {
  margin-top: 16px;
  padding: 10px 20px;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-create-first:hover {
  box-shadow: var(--button-shadow);
}

.assistant-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assistant-item {
  position: relative;
  padding: 16px;
  background: var(--color-background);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.assistant-item:hover {
  transform: translateX(4px);
  box-shadow: var(--card-shadow);
  border-color: var(--button-primary);
}

.assistant-item.active {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
}

.assistant-item.default {
  border-color: var(--button-secondary);
  border-width: 2px;
}

.assistant-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.assistant-avatar {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  background: var(--color-primary-alpha);
  border-radius: 12px;
  flex-shrink: 0;
}

.assistant-info {
  flex: 1;
  min-width: 0;
}

.assistant-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.assistant-name {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.default-badge {
  padding: 2px 8px;
  background: var(--button-secondary);
  color: var(--button-secondaryText);
  border-radius: 10px;
  font-size: 10px;
  font-weight: 600;
}

.assistant-description {
  margin: 0;
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.assistant-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-icon {
  font-size: 14px;
}

.assistant-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 12px;
  background: var(--color-surface);
  border-radius: 8px;
  margin-bottom: 12px;
}

.stat-col {
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: var(--button-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.assistant-actions {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 6px;
}

.btn-use {
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  font-weight: 500;
}

.btn-use:hover {
  background: var(--button-primary);
  opacity: 0.9;
}

.inactive-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: white;
  font-weight: 500;
}

/* 滚动条样式 */
.list-content::-webkit-scrollbar {
  width: 6px;
}

.list-content::-webkit-scrollbar-track {
  background: var(--color-background);
  border-radius: 3px;
}

.list-content::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 3px;
}

.list-content::-webkit-scrollbar-thumb:hover {
  background: var(--button-primary);
}
</style>

