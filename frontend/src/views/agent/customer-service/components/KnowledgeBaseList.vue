<template>
  <div class="knowledge-base-list">
    <div class="list-header">
      <h3>📚 知识库列表</h3>
      <button @click="$emit('create')" class="btn-create">
        <span>➕</span> 新建
      </button>
    </div>

    <div class="search-box">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索知识库..."
        class="search-input"
      />
    </div>

    <div class="list-content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="filteredKnowledgeBases.length === 0" class="empty-state">
        <div class="empty-icon">📚</div>
        <p>暂无知识库</p>
        <button @click="$emit('create')" class="btn-create-first">
          创建第一个知识库
        </button>
      </div>

      <div v-else class="kb-items">
        <div
          v-for="kb in filteredKnowledgeBases"
          :key="kb.id"
          :class="['kb-item', { active: selectedId === kb.id }]"
          @click="selectKnowledgeBase(kb)"
        >
          <div class="kb-header">
            <h4 class="kb-name">{{ kb.name }}</h4>
            <span :class="['kb-status', kb.status]">
              {{ getStatusText(kb.status) }}
            </span>
          </div>
          
          <p v-if="kb.description" class="kb-description">
            {{ kb.description }}
          </p>
          
          <div class="kb-stats">
            <span class="stat-item">
              <span class="stat-icon">📄</span>
              {{ kb.document_count || 0 }} 文档
            </span>
            <span class="stat-item">
              <span class="stat-icon">✂️</span>
              {{ kb.chunk_count || 0 }} 切片
            </span>
          </div>

          <div class="kb-actions">
            <button
              @click.stop="$emit('view-documents', kb)"
              class="btn-action"
              title="查看文档"
            >
              📄
            </button>
            <button
              @click.stop="$emit('upload-document', kb)"
              class="btn-action"
              title="上传文档"
            >
              ⬆️
            </button>
            <button
              @click.stop="$emit('edit', kb)"
              class="btn-action"
              title="编辑"
            >
              ✏️
            </button>
            <button
              @click.stop="$emit('delete', kb)"
              class="btn-action btn-danger"
              title="删除"
            >
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface KnowledgeBase {
  id: number
  name: string
  description: string
  status: string
  document_count: number
  chunk_count: number
  total_tokens: number
  created_at: string
}

interface Props {
  knowledgeBases: KnowledgeBase[]
  loading?: boolean
  selectedId?: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  selectedId: undefined
})

const emit = defineEmits<{
  create: []
  edit: [kb: KnowledgeBase]
  delete: [kb: KnowledgeBase]
  select: [kb: KnowledgeBase]
  'view-documents': [kb: KnowledgeBase]
  'upload-document': [kb: KnowledgeBase]
}>()

const searchQuery = ref('')

const filteredKnowledgeBases = computed(() => {
  if (!searchQuery.value) return props.knowledgeBases
  
  const query = searchQuery.value.toLowerCase()
  return props.knowledgeBases.filter(kb =>
    kb.name.toLowerCase().includes(query) ||
    kb.description?.toLowerCase().includes(query)
  )
})

const selectKnowledgeBase = (kb: KnowledgeBase) => {
  emit('select', kb)
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    creating: '创建中',
    processing: '处理中',
    ready: '就绪',
    error: '错误'
  }
  return statusMap[status] || status
}
</script>

<style scoped>
.knowledge-base-list {
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

.kb-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.kb-item {
  padding: 16px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.kb-item:hover {
  transform: translateX(4px);
  box-shadow: var(--card-shadow);
  border-color: var(--button-primary);
}

.kb-item.active {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.kb-name {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
}

.kb-status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.kb-status.ready {
  background: var(--color-success, #28a745);
  color: white;
}

.kb-status.processing {
  background: var(--color-warning, #ffc107);
  color: var(--color-text, #333);
}

.kb-status.error {
  background: var(--color-error, #dc3545);
  color: white;
}

.kb-description {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.kb-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-icon {
  font-size: 14px;
}

.kb-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.btn-action {
  flex: 1;
  padding: 6px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.btn-action:hover {
  background: var(--button-primary);
  transform: scale(1.05);
}

.btn-action.btn-danger:hover {
  background: var(--color-error, #dc3545);
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

