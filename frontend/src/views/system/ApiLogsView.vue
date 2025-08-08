<template>
  <div class="api-logs-view">
    <div class="page-header">
      <h2>API访问日志</h2>
      <p class="page-description">查看和分析API接口访问记录</p>
    </div>
    
    <LogFilter
      :show-user-filter="true"
      :show-module-filter="false"
      :show-action-filter="false"
      :show-method-filter="true"
      @filter-change="handleFilterChange"
      @export="handleExport"
    />
    
    <LogTable
      title="API访问日志"
      :logs="logs"
      :columns="columns"
      :loading="loading"
      :current-page="currentPage"
      :total-pages="totalPages"
      :total-count="totalCount"
      @refresh="loadLogs"
      @sort="handleSort"
      @page-change="handlePageChange"
      @view-detail="handleViewDetail"
    />
    
    <LogDetail
      :visible="showDetail"
      :log="selectedLog"
      @close="showDetail = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import LogFilter from '@/components/LogFilter.vue'
import LogTable from '@/components/LogTable.vue'
import LogDetail from '@/components/LogDetail.vue'
import { logService } from '@/services/logService'

interface ApiLog {
  id: number
  user?: { username: string }
  user_id?: number
  method: string
  path: string
  status_code: number
  response_time: number
  timestamp: string
  ip_address: string
  user_agent: string
  request_data?: any
  response_data?: any
}

const logs = ref<ApiLog[]>([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const filters = ref({})
const sortField = ref('')
const sortDirection = ref<'asc' | 'desc'>('desc')

const showDetail = ref(false)
const selectedLog = ref<ApiLog>({} as ApiLog)

const columns = [
  { key: 'timestamp', label: '时间', sortable: true, class: 'timestamp-column' },
  { key: 'method', label: '方法', sortable: true, class: 'method-column' },
  { key: 'path', label: '路径', class: 'path-column' },
  { key: 'status_code', label: '状态码', sortable: true, class: 'status-column' },
  { key: 'response_time', label: '响应时间(ms)', sortable: true, class: 'time-column' },
  { key: 'user', label: '用户' },
  { key: 'ip_address', label: 'IP地址' }
]

const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      ...filters.value,
      ordering: sortField.value ? `${sortDirection.value === 'desc' ? '-' : ''}${sortField.value}` : '-timestamp'
    }
    
    const response = await logService.getApiLogs(params)
    logs.value = response.results.map(log => ({
      ...log,
      message: `${log.method} ${log.path} - ${log.status_code}`
    }))
    totalCount.value = response.count
    totalPages.value = Math.ceil(response.count / 20)
  } catch (error) {
    console.error('加载API日志失败:', error)
  } finally {
    loading.value = false
  }
}

const handleFilterChange = (newFilters: any) => {
  filters.value = newFilters
  currentPage.value = 1
  loadLogs()
}

const handleSort = (field: string, direction: 'asc' | 'desc') => {
  sortField.value = field
  sortDirection.value = direction
  loadLogs()
}

const handlePageChange = (page: number) => {
  currentPage.value = page
  loadLogs()
}

const handleViewDetail = (log: ApiLog) => {
  selectedLog.value = log
  showDetail.value = true
}

const handleExport = async (exportFilters: any) => {
  try {
    await logService.exportApiLogs(exportFilters)
  } catch (error) {
    console.error('导出API日志失败:', error)
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.api-logs-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 24px;
}

.page-description {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.timestamp-column {
  width: 180px;
}

.method-column {
  width: 80px;
}

.path-column {
  min-width: 200px;
}

.status-column {
  width: 100px;
}

.time-column {
  width: 120px;
}
</style>