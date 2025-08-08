<template>
  <div class="user-logs-view">
    <div class="page-header">
      <h2>用户操作日志</h2>
      <p class="page-description">查看和管理用户操作记录</p>
    </div>
    
    <LogFilter
      :show-user-filter="true"
      :show-module-filter="true"
      :show-action-filter="true"
      :show-method-filter="false"
      @filter-change="handleFilterChange"
      @export="handleExport"
    />
    
    <LogTable
      title="用户操作日志"
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

interface UserLog {
  id: number
  user: { username: string }
  user_id: number
  action: string
  module: string
  description: string
  timestamp: string
  ip_address: string
  user_agent: string
  extra_data?: any
}

const logs = ref<UserLog[]>([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const filters = ref({})
const sortField = ref('')
const sortDirection = ref<'asc' | 'desc'>('desc')

const showDetail = ref(false)
const selectedLog = ref<UserLog>({} as UserLog)

const columns = [
  { key: 'timestamp', label: '时间', sortable: true, class: 'timestamp-column' },
  { key: 'user', label: '用户', sortable: true },
  { key: 'action', label: '操作', sortable: true },
  { key: 'module', label: '模块', sortable: true },
  { key: 'message', label: '描述', class: 'message-column' },
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
    
    const response = await logService.getUserLogs(params)
    logs.value = response.results
    totalCount.value = response.count
    totalPages.value = Math.ceil(response.count / 20)
  } catch (error) {
    console.error('加载用户日志失败:', error)
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

const handleViewDetail = (log: UserLog) => {
  selectedLog.value = { ...log, message: log.description }
  showDetail.value = true
}

const handleExport = async (exportFilters: any) => {
  try {
    await logService.exportUserLogs(exportFilters)
  } catch (error) {
    console.error('导出用户日志失败:', error)
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.user-logs-view {
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

.message-column {
  min-width: 200px;
}
</style>