<template>
  <div class="knowledge-base-list">
    <div class="list-header">
      <h3>📚 知识库列表</h3>
      <button @click="$emit('switch-view')" class="btn-switch-view">
        切换到助手
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
          :class="['kb-item', { active: selectedId === kb.id, 'has-open-dropdown': activeDropdownId === kb.id }]"
          @click="selectKnowledgeBase(kb)"
        >
          <div class="kb-header">
            <div class="kb-title-section">
              <h4 class="kb-name">{{ kb.name }}</h4>
              <div class="kb-stats">
                <span class="stat-item">
                  <span class="stat-icon">📄</span>
                  {{ kb.document_count || 0 }}
                </span>
                <span class="stat-item">
                  <span class="stat-icon">✂️</span>
                  {{ kb.chunk_count || 0 }}
                </span>
              </div>
            </div>
            
            <!-- 三个点下拉菜单 -->
            <div class="dropdown-container">
              <button 
                class="action-btn more-btn" 
                @click.stop="toggleDropdown(kb.id, $event)"
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
                v-if="activeDropdownId === kb.id" 
                class="dropdown-menu"
                :style="dropdownPosition"
                @click.stop
              >
                <div class="dropdown-item" @click="handleViewDocuments(kb)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14,2 14,8 20,8"></polyline>
                  </svg>
                  <span>查看文档</span>
                </div>
                <div class="dropdown-item" @click="handleUploadDocument(kb)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17,8 12,3 7,8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                  </svg>
                  <span>上传文档</span>
                </div>
                <div class="dropdown-item" @click="handleEdit(kb)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                  </svg>
                  <span>编辑</span>
                </div>
                <div class="dropdown-divider"></div>
                <div class="dropdown-item danger" @click="handleDelete(kb)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m3 6 3 0"></path>
                    <path d="m21 6-3 0"></path>
                    <path d="m10 11 0 6"></path>
                    <path d="m14 11 0 6"></path>
                    <path d="m18 6-1 14-10 0-1-14"></path>
                    <path d="m8 6 0-2c0-1 1-2 2-2l4 0c1 0 2 1 2 2l0 2"></path>
                  </svg>
                  <span>删除</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

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
  'switch-view': []
}>()

const searchQuery = ref('')
const activeDropdownId = ref<number | null>(null)
const dropdownPosition = ref<{ top?: string; left?: string; right?: string; bottom?: string }>({})

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

// 下拉菜单处理
const toggleDropdown = (kbId: number, event?: Event) => {
  if (activeDropdownId.value === kbId) {
    activeDropdownId.value = null
    dropdownPosition.value = {}
    return
  }
  
  activeDropdownId.value = kbId
  
  // 计算下拉菜单位置
  if (event) {
    const target = event.currentTarget as HTMLElement
    const rect = target.getBoundingClientRect()
    const menuWidth = 160 // 下拉菜单宽度
    const menuHeight = 180 // 预估下拉菜单高度
    const padding = 8 // 间距
    
    // 计算水平位置
    let left: number | undefined
    let right: number | undefined
    
    // 检查右侧是否有足够空间
    if (rect.left + menuWidth > window.innerWidth) {
      // 右侧空间不足，菜单向左展开，右边缘对齐按钮左边缘
      right = window.innerWidth - rect.left - padding
    } else {
      // 右侧空间充足，菜单左边缘对齐按钮左边缘
      left = rect.left
    }
    
    // 计算垂直位置
    let top: number | undefined
    let bottom: number | undefined
    
    if (rect.bottom + menuHeight > window.innerHeight) {
      // 下方空间不足，菜单向上展开，底部对齐按钮顶部
      bottom = window.innerHeight - rect.top + padding
    } else {
      // 下方空间充足，菜单顶部在按钮下方
      top = rect.bottom + padding
    }
    
    dropdownPosition.value = {
      top: top !== undefined ? `${top}px` : undefined,
      bottom: bottom !== undefined ? `${bottom}px` : undefined,
      left: left !== undefined ? `${left}px` : undefined,
      right: right !== undefined ? `${right}px` : undefined
    }
  }
}

const handleViewDocuments = (kb: KnowledgeBase) => {
  emit('view-documents', kb)
  activeDropdownId.value = null
  dropdownPosition.value = {}
}

const handleUploadDocument = (kb: KnowledgeBase) => {
  emit('upload-document', kb)
  activeDropdownId.value = null
  dropdownPosition.value = {}
}

const handleEdit = (kb: KnowledgeBase) => {
  emit('edit', kb)
  activeDropdownId.value = null
  dropdownPosition.value = {}
}

const handleDelete = (kb: KnowledgeBase) => {
  emit('delete', kb)
  activeDropdownId.value = null
  dropdownPosition.value = {}
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.dropdown-container')) {
    activeDropdownId.value = null
    dropdownPosition.value = {}
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
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

.kb-items {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.kb-item {
  position: relative;
  padding: 12px 14px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 1;
}

.kb-item:hover {
  transform: translateX(4px);
  box-shadow: var(--card-shadow);
  border-color: var(--button-primary);
  z-index: 2;
}

/* 当下拉菜单打开时，禁用 hover 的 transform 效果，防止位置跳动 */
.kb-item.has-open-dropdown {
  transform: none !important;
  box-shadow: var(--card-shadow);
  border-color: var(--button-primary);
  z-index: 10;
}

.kb-item.active {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
  z-index: 2;
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.kb-title-section {
  flex: 1;
  min-width: 0;
}

.kb-name {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kb-stats {
  display: flex;
  gap: 12px;
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

/* 下拉菜单容器 */
.dropdown-container {
  position: relative;
  flex-shrink: 0;
  z-index: 100000;
}

.action-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--color-text-secondary);
}

.action-btn:hover {
  background: var(--color-surface);
  border-color: var(--color-border);
  color: var(--color-text);
}

.more-btn:hover {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
  color: var(--button-primary);
}

.dropdown-menu {
  position: fixed;
  z-index: 99999;
  min-width: 160px;
  max-height: 300px;
  overflow-y: auto;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: 
    0 10px 30px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.05);
  padding: 4px 0;
  transform-origin: top left;
  animation: slideIn 0.15s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text);
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: var(--color-surface);
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
  background: var(--color-border);
  margin: 4px 0;
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

