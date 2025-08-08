<template>
  <div class="log-table-container">
    <div class="table-header">
      <h3>{{ title }}</h3>
      <div class="table-actions">
        <button @click="refreshData" class="btn-refresh" :disabled="loading">
          <span v-if="loading">刷新中...</span>
          <span v-else>刷新</span>
        </button>
      </div>
    </div>
    
    <div class="table-wrapper">
      <table class="log-table">
        <thead>
          <tr>
            <th v-for="column in visibleColumns" :key="column.key" :class="column.class">
              <div class="th-content">
                <span>{{ column.label }}</span>
                <button 
                  v-if="column.sortable" 
                  @click="toggleSort(column.key)"
                  class="sort-btn"
                  :class="getSortClass(column.key)"
                >
                  ↕
                </button>
              </div>
            </th>
            <th class="actions-column">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading" class="loading-row">
            <td :colspan="visibleColumns.length + 1" class="loading-cell">
              <div class="loading-spinner">加载中...</div>
            </td>
          </tr>
          <tr v-else-if="logs.length === 0" class="empty-row">
            <td :colspan="visibleColumns.length + 1" class="empty-cell">
              暂无数据
            </td>
          </tr>
          <tr v-else v-for="log in logs" :key="log.id" class="log-row">
            <td v-for="column in visibleColumns" :key="column.key" :class="column.class">
              <div class="cell-content">
                <span v-if="column.key === 'level'" :class="`level-badge level-${log.level?.toLowerCase()}`">
                  {{ getLevelText(log.level) }}
                </span>
                <span v-else-if="column.key === 'timestamp'" class="timestamp">
                  {{ formatDateTime(log.timestamp) }}
                </span>
                <span v-else-if="column.key === 'user'" class="user-info">
                  {{ log.user?.username || log.user_id || '-' }}
                </span>
                <span v-else-if="column.key === 'status_code'" :class="`status-code status-${getStatusClass(log.status_code)}`">
                  {{ log.status_code }}
                </span>
                <span v-else-if="column.key === 'message'" class="message" :title="log.message">
                  {{ truncateText(log.message, 50) }}
                </span>
                <span v-else-if="column.key === 'path'" class="path" :title="log.path">
                  {{ truncateText(log.path, 30) }}
                </span>
                <span v-else>
                  {{ log[column.key] || '-' }}
                </span>
              </div>
            </td>
            <td class="actions-column">
              <button @click="viewDetail(log)" class="btn-detail">详情</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div class="pagination" v-if="totalPages > 1">
      <button 
        @click="changePage(currentPage - 1)" 
        :disabled="currentPage <= 1"
        class="page-btn"
      >
        上一页
      </button>
      
      <div class="page-numbers">
        <button 
          v-for="page in getPageNumbers()" 
          :key="page"
          @click="changePage(page)"
          :class="['page-btn', { active: page === currentPage }]"
        >
          {{ page }}
        </button>
      </div>
      
      <button 
        @click="changePage(currentPage + 1)" 
        :disabled="currentPage >= totalPages"
        class="page-btn"
      >
        下一页
      </button>
      
      <div class="page-info">
        共 {{ totalCount }} 条记录，第 {{ currentPage }} / {{ totalPages }} 页
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface LogData {
  id: number
  level?: string
  message: string
  timestamp: string
  user?: { username: string }
  user_id?: number
  module?: string
  action?: string
  path?: string
  method?: string
  status_code?: number
  ip_address?: string
  user_agent?: string
  [key: string]: any
}

interface TableColumn {
  key: string
  label: string
  sortable?: boolean
  class?: string
}

interface Props {
  title: string
  logs: LogData[]
  columns: TableColumn[]
  loading?: boolean
  currentPage: number
  totalPages: number
  totalCount: number
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<{
  refresh: []
  sort: [field: string, direction: 'asc' | 'desc']
  pageChange: [page: number]
  viewDetail: [log: LogData]
}>()

const sortField = ref<string>('')
const sortDirection = ref<'asc' | 'desc'>('desc')

const visibleColumns = computed(() => props.columns)

const refreshData = () => {
  emit('refresh')
}

const toggleSort = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'desc'
  }
  emit('sort', field, sortDirection.value)
}

const getSortClass = (field: string) => {
  if (sortField.value !== field) return ''
  return sortDirection.value === 'asc' ? 'sort-asc' : 'sort-desc'
}

const changePage = (page: number) => {
  if (page >= 1 && page <= props.totalPages) {
    emit('pageChange', page)
  }
}

const viewDetail = (log: LogData) => {
  emit('viewDetail', log)
}

const getLevelText = (level?: string) => {
  const levelMap: Record<string, string> = {
    'DEBUG': '调试',
    'INFO': '信息',
    'WARNING': '警告',
    'ERROR': '错误',
    'CRITICAL': '严重'
  }
  return levelMap[level || ''] || level || '-'
}

const getStatusClass = (statusCode?: number) => {
  if (!statusCode) return 'unknown'
  if (statusCode >= 200 && statusCode < 300) return 'success'
  if (statusCode >= 300 && statusCode < 400) return 'redirect'
  if (statusCode >= 400 && statusCode < 500) return 'client-error'
  if (statusCode >= 500) return 'server-error'
  return 'unknown'
}

const formatDateTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const truncateText = (text: string, maxLength: number) => {
  if (!text) return '-'
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const getPageNumbers = () => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, props.currentPage - Math.floor(maxVisible / 2))
  let end = Math.min(props.totalPages, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
}
</script>

<style scoped>
.log-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.table-header h3 {
  margin: 0;
  color: #333;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.btn-refresh {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-refresh:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-refresh:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.table-wrapper {
  overflow-x: auto;
}

.log-table {
  width: 100%;
  border-collapse: collapse;
}

.log-table th,
.log-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.log-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  color: #666;
  padding: 2px;
}

.sort-btn.sort-asc {
  color: #007bff;
  transform: rotate(180deg);
}

.sort-btn.sort-desc {
  color: #007bff;
}

.log-row:hover {
  background-color: #f8f9fa;
}

.cell-content {
  display: flex;
  align-items: center;
}

.level-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.level-debug { background-color: #e9ecef; color: #495057; }
.level-info { background-color: #d1ecf1; color: #0c5460; }
.level-warning { background-color: #fff3cd; color: #856404; }
.level-error { background-color: #f8d7da; color: #721c24; }
.level-critical { background-color: #f5c6cb; color: #721c24; }

.status-code {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-success { background-color: #d4edda; color: #155724; }
.status-redirect { background-color: #d1ecf1; color: #0c5460; }
.status-client-error { background-color: #fff3cd; color: #856404; }
.status-server-error { background-color: #f8d7da; color: #721c24; }
.status-unknown { background-color: #e9ecef; color: #495057; }

.timestamp {
  font-family: monospace;
  font-size: 13px;
}

.user-info {
  font-weight: 500;
}

.message,
.path {
  font-family: monospace;
  font-size: 13px;
}

.actions-column {
  width: 80px;
  text-align: center;
}

.btn-detail {
  padding: 4px 8px;
  background-color: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-detail:hover {
  background-color: #138496;
}

.loading-row,
.empty-row {
  text-align: center;
}

.loading-cell,
.empty-cell {
  padding: 40px;
  color: #666;
}

.loading-spinner {
  display: inline-block;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.page-numbers {
  display: flex;
  gap: 5px;
}

.page-btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background-color: white;
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #f8f9fa;
  border-color: #007bff;
}

.page-btn:disabled {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.page-btn.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.page-info {
  margin-left: 20px;
  color: #666;
  font-size: 14px;
}

@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 5px;
  }
  
  .page-info {
    margin-left: 0;
    width: 100%;
    text-align: center;
  }
}
</style>