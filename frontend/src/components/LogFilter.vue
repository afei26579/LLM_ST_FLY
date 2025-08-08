<template>
  <div class="log-filter">
    <div class="filter-row">
      <div class="filter-item">
        <label>日志级别：</label>
        <select v-model="filters.level" @change="onFilterChange">
          <option value="">全部</option>
          <option value="DEBUG">调试</option>
          <option value="INFO">信息</option>
          <option value="WARNING">警告</option>
          <option value="ERROR">错误</option>
          <option value="CRITICAL">严重</option>
        </select>
      </div>
      
      <div class="filter-item">
        <label>时间范围：</label>
        <input 
          type="datetime-local" 
          v-model="filters.start_time" 
          @change="onFilterChange"
          placeholder="开始时间"
        />
        <span class="time-separator">至</span>
        <input 
          type="datetime-local" 
          v-model="filters.end_time" 
          @change="onFilterChange"
          placeholder="结束时间"
        />
      </div>
    </div>
    
    <div class="filter-row">
      <div class="filter-item" v-if="showUserFilter">
        <label>用户：</label>
        <input 
          type="text" 
          v-model="filters.user" 
          @input="onFilterChange"
          placeholder="用户名或ID"
        />
      </div>
      
      <div class="filter-item" v-if="showModuleFilter">
        <label>模块：</label>
        <input 
          type="text" 
          v-model="filters.module" 
          @input="onFilterChange"
          placeholder="模块名称"
        />
      </div>
      
      <div class="filter-item" v-if="showActionFilter">
        <label>操作类型：</label>
        <select v-model="filters.action" @change="onFilterChange">
          <option value="">全部</option>
          <option value="CREATE">创建</option>
          <option value="UPDATE">更新</option>
          <option value="DELETE">删除</option>
          <option value="VIEW">查看</option>
          <option value="LOGIN">登录</option>
          <option value="LOGOUT">登出</option>
        </select>
      </div>
      
      <div class="filter-item" v-if="showMethodFilter">
        <label>请求方法：</label>
        <select v-model="filters.method" @change="onFilterChange">
          <option value="">全部</option>
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
          <option value="PATCH">PATCH</option>
        </select>
      </div>
    </div>
    
    <div class="filter-row">
      <div class="filter-item search-item">
        <label>关键词搜索：</label>
        <input 
          type="text" 
          v-model="filters.search" 
          @input="onFilterChange"
          placeholder="搜索日志内容..."
          class="search-input"
        />
      </div>
      
      <div class="filter-actions">
        <button @click="resetFilters" class="btn-reset">重置</button>
        <button @click="exportLogs" class="btn-export">导出</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'

interface LogFilters {
  level: string
  start_time: string
  end_time: string
  user: string
  module: string
  action: string
  method: string
  search: string
}

interface Props {
  showUserFilter?: boolean
  showModuleFilter?: boolean
  showActionFilter?: boolean
  showMethodFilter?: boolean
  initialFilters?: Partial<LogFilters>
}

const props = withDefaults(defineProps<Props>(), {
  showUserFilter: true,
  showModuleFilter: true,
  showActionFilter: true,
  showMethodFilter: true,
  initialFilters: () => ({})
})

const emit = defineEmits<{
  filterChange: [filters: LogFilters]
  export: [filters: LogFilters]
}>()

const filters = reactive<LogFilters>({
  level: '',
  start_time: '',
  end_time: '',
  user: '',
  module: '',
  action: '',
  method: '',
  search: '',
  ...props.initialFilters
})

const onFilterChange = () => {
  emit('filterChange', { ...filters })
}

const resetFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key as keyof LogFilters] = ''
  })
  emit('filterChange', { ...filters })
}

const exportLogs = () => {
  emit('export', { ...filters })
}

// 监听初始过滤器变化
watch(() => props.initialFilters, (newFilters) => {
  Object.assign(filters, newFilters)
}, { deep: true })
</script>

<style scoped>
.log-filter {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 200px;
}

.filter-item label {
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  min-width: 80px;
}

.filter-item input,
.filter-item select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-width: 120px;
}

.filter-item input:focus,
.filter-item select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.time-separator {
  margin: 0 8px;
  color: #666;
}

.search-item {
  flex: 1;
  min-width: 300px;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.filter-actions {
  display: flex;
  gap: 10px;
  margin-left: auto;
}

.btn-reset,
.btn-export {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-reset {
  background-color: #6c757d;
  color: white;
}

.btn-reset:hover {
  background-color: #5a6268;
}

.btn-export {
  background-color: #28a745;
  color: white;
}

.btn-export:hover {
  background-color: #218838;
}

@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-item {
    min-width: auto;
  }
  
  .filter-actions {
    margin-left: 0;
    justify-content: center;
  }
}
</style>