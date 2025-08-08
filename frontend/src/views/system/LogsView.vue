<template>
  <div class="logs-view">
    <div class="page-header">
      <h2>日志管理</h2>
      <p class="page-description">系统日志统一管理和查看</p>
    </div>
    
    <!-- 日志统计卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon system">📊</div>
        <div class="stat-content">
          <h3>{{ stats.system_logs || 0 }}</h3>
          <p>系统日志</p>
        </div>
        <router-link to="/logs/system" class="stat-link">查看详情</router-link>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon user">👤</div>
        <div class="stat-content">
          <h3>{{ stats.user_logs || 0 }}</h3>
          <p>用户操作</p>
        </div>
        <router-link to="/logs/user" class="stat-link">查看详情</router-link>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon api">🔗</div>
        <div class="stat-content">
          <h3>{{ stats.api_logs || 0 }}</h3>
          <p>API访问</p>
        </div>
        <router-link to="/logs/api" class="stat-link">查看详情</router-link>
      </div>
      
      <div class="stat-card error">
        <div class="stat-icon error">⚠️</div>
        <div class="stat-content">
          <h3>{{ stats.error_logs || 0 }}</h3>
          <p>错误日志</p>
        </div>
        <router-link to="/logs/error" class="stat-link">查看详情</router-link>
      </div>
    </div>
    
    <!-- 快速导航 -->
    <div class="quick-nav">
      <h3>快速导航</h3>
      <div class="nav-grid">
        <router-link to="/logs/system" class="nav-item">
          <div class="nav-icon">🖥️</div>
          <div class="nav-content">
            <h4>系统日志</h4>
            <p>查看系统运行日志和调试信息</p>
          </div>
        </router-link>
        
        <router-link to="/logs/user" class="nav-item">
          <div class="nav-icon">👥</div>
          <div class="nav-content">
            <h4>用户操作日志</h4>
            <p>追踪用户操作记录和行为分析</p>
          </div>
        </router-link>
        
        <router-link to="/logs/api" class="nav-item">
          <div class="nav-icon">🌐</div>
          <div class="nav-content">
            <h4>API访问日志</h4>
            <p>监控API接口调用和性能分析</p>
          </div>
        </router-link>
        
        <router-link to="/logs/error" class="nav-item">
          <div class="nav-icon">🚨</div>
          <div class="nav-content">
            <h4>错误日志</h4>
            <p>查看系统错误和异常信息</p>
          </div>
        </router-link>
      </div>
    </div>
    
    <!-- 最近日志 -->
    <div class="recent-logs">
      <div class="section-header">
        <h3>最近日志</h3>
        <div class="section-actions">
          <button @click="loadRecentLogs" class="btn-refresh" :disabled="loading">
            刷新
          </button>
        </div>
      </div>
      
      <div class="logs-container">
        <div v-if="loading" class="loading">
          加载中...
        </div>
        <div v-else-if="recentLogs.length === 0" class="empty">
          暂无最近日志
        </div>
        <div v-else class="log-list">
          <div 
            v-for="log in recentLogs" 
            :key="`${log.type}-${log.id}`"
            class="log-item"
            :class="log.level?.toLowerCase()"
          >
            <div class="log-time">
              {{ formatTime(log.timestamp) }}
            </div>
            <div class="log-type">
              {{ getLogTypeText(log.type) }}
            </div>
            <div class="log-level" v-if="log.level">
              <span :class="`level-badge level-${log.level.toLowerCase()}`">
                {{ getLevelText(log.level) }}
              </span>
            </div>
            <div class="log-content">
              {{ log.message }}
            </div>
            <div class="log-actions">
              <button @click="viewLogDetail(log)" class="btn-detail">
                详情
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 日志详情弹窗 -->
    <LogDetail
      :visible="showDetail"
      :log="selectedLog"
      @close="showDetail = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import LogDetail from '@/components/LogDetail.vue'
import { logService } from '@/services/logService'

interface LogStats {
  system_logs: number
  user_logs: number
  api_logs: number
  error_logs: number
}

interface RecentLog {
  id: number
  type: string
  level?: string
  message: string
  timestamp: string
  [key: string]: any
}

const stats = ref<LogStats>({
  system_logs: 0,
  user_logs: 0,
  api_logs: 0,
  error_logs: 0
})

const recentLogs = ref<RecentLog[]>([])
const loading = ref(false)
const showDetail = ref(false)
const selectedLog = ref<RecentLog>({} as RecentLog)

const loadStats = async () => {
  try {
    const response = await logService.getLogStats()
    stats.value = response
  } catch (error) {
    console.error('加载日志统计失败:', error)
  }
}

const loadRecentLogs = async () => {
  loading.value = true
  try {
    // 获取各类型最近的日志
    const [systemLogs, userLogs, apiLogs, errorLogs] = await Promise.all([
      logService.getSystemLogs({ page: 1, page_size: 5 }),
      logService.getUserLogs({ page: 1, page_size: 5 }),
      logService.getApiLogs({ page: 1, page_size: 5 }),
      logService.getErrorLogs({ page: 1, page_size: 5 })
    ])
    
    // 合并并按时间排序
    const allLogs: RecentLog[] = [
      ...systemLogs.results.map(log => ({ ...log, type: 'system' })),
      ...userLogs.results.map(log => ({ ...log, type: 'user' })),
      ...apiLogs.results.map(log => ({ ...log, type: 'api' })),
      ...errorLogs.results.map(log => ({ ...log, type: 'error' }))
    ]
    
    recentLogs.value = allLogs
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 20)
      
  } catch (error) {
    console.error('加载最近日志失败:', error)
  } finally {
    loading.value = false
  }
}

const viewLogDetail = (log: RecentLog) => {
  selectedLog.value = log
  showDetail.value = true
}

const formatTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('zh-CN')
}

const getLogTypeText = (type: string) => {
  const typeMap: Record<string, string> = {
    'system': '系统',
    'user': '用户',
    'api': 'API',
    'error': '错误'
  }
  return typeMap[type] || type
}

const getLevelText = (level: string) => {
  const levelMap: Record<string, string> = {
    'DEBUG': '调试',
    'INFO': '信息',
    'WARNING': '警告',
    'ERROR': '错误',
    'CRITICAL': '严重'
  }
  return levelMap[level] || level
}

onMounted(() => {
  loadStats()
  loadRecentLogs()
})
</script>

<style scoped>
.logs-view {
  padding: 20px;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 28px;
}

.page-description {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card.error {
  border-left: 4px solid #dc3545;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.system { background-color: #e3f2fd; }
.stat-icon.user { background-color: #f3e5f5; }
.stat-icon.api { background-color: #e8f5e8; }
.stat-icon.error { background-color: #ffebee; }

.stat-content h3 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.stat-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.stat-link {
  position: absolute;
  top: 16px;
  right: 16px;
  color: #007bff;
  text-decoration: none;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.stat-link:hover {
  background-color: #f8f9fa;
}

.quick-nav {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 32px;
}

.quick-nav h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #eee;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
}

.nav-item:hover {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.nav-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.nav-content h4 {
  margin: 0 0 4px 0;
  color: #333;
  font-size: 16px;
}

.nav-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.recent-logs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
}

.section-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
}

.btn-refresh {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-refresh:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.logs-container {
  padding: 24px;
}

.loading,
.empty {
  text-align: center;
  padding: 40px;
  color: #666;
}

.log-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.log-item {
  display: grid;
  grid-template-columns: 140px 80px 80px 1fr auto;
  gap: 16px;
  align-items: center;
  padding: 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.log-item:hover {
  background-color: #f8f9fa;
}

.log-time {
  font-size: 12px;
  color: #666;
  font-family: monospace;
}

.log-type {
  font-size: 12px;
  color: #007bff;
  font-weight: 500;
}

.level-badge {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
}

.level-debug { background-color: #e9ecef; color: #495057; }
.level-info { background-color: #d1ecf1; color: #0c5460; }
.level-warning { background-color: #fff3cd; color: #856404; }
.level-error { background-color: #f8d7da; color: #721c24; }
.level-critical { background-color: #f5c6cb; color: #721c24; }

.log-content {
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .nav-grid {
    grid-template-columns: 1fr;
  }
  
  .log-item {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
}
</style>