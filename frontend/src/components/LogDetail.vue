<template>
  <div class="log-detail-modal" v-if="visible" @click="closeModal">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>日志详情</h3>
        <button @click="closeModal" class="close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <label>日志ID：</label>
              <span>{{ log.id }}</span>
            </div>
            <div class="detail-item" v-if="log.level">
              <label>日志级别：</label>
              <span :class="`level-badge level-${log.level?.toLowerCase()}`">
                {{ getLevelText(log.level) }}
              </span>
            </div>
            <div class="detail-item">
              <label>时间：</label>
              <span class="timestamp">{{ formatDateTime(log.timestamp) }}</span>
            </div>
            <div class="detail-item" v-if="log.user || log.user_id">
              <label>用户：</label>
              <span>{{ log.user?.username || `ID: ${log.user_id}` }}</span>
            </div>
            <div class="detail-item" v-if="log.module">
              <label>模块：</label>
              <span>{{ log.module }}</span>
            </div>
            <div class="detail-item" v-if="log.action">
              <label>操作：</label>
              <span>{{ log.action }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section" v-if="log.path || log.method || log.status_code">
          <h4>请求信息</h4>
          <div class="detail-grid">
            <div class="detail-item" v-if="log.method">
              <label>请求方法：</label>
              <span class="method-badge">{{ log.method }}</span>
            </div>
            <div class="detail-item" v-if="log.path">
              <label>请求路径：</label>
              <span class="path-text">{{ log.path }}</span>
            </div>
            <div class="detail-item" v-if="log.status_code">
              <label>状态码：</label>
              <span :class="`status-code status-${getStatusClass(log.status_code)}`">
                {{ log.status_code }}
              </span>
            </div>
            <div class="detail-item" v-if="log.response_time">
              <label>响应时间：</label>
              <span>{{ log.response_time }}ms</span>
            </div>
            <div class="detail-item" v-if="log.ip_address">
              <label>IP地址：</label>
              <span>{{ log.ip_address }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>日志内容</h4>
          <div class="message-content">
            <pre>{{ log.message }}</pre>
          </div>
        </div>
        
        <div class="detail-section" v-if="log.user_agent">
          <h4>用户代理</h4>
          <div class="user-agent-content">
            <pre>{{ log.user_agent }}</pre>
          </div>
        </div>
        
        <div class="detail-section" v-if="log.extra_data">
          <h4>额外数据</h4>
          <div class="extra-data-content">
            <pre>{{ formatExtraData(log.extra_data) }}</pre>
          </div>
        </div>
        
        <div class="detail-section" v-if="log.stack_trace">
          <h4>堆栈跟踪</h4>
          <div class="stack-trace-content">
            <pre>{{ log.stack_trace }}</pre>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="copyToClipboard" class="btn-copy">复制详情</button>
        <button @click="closeModal" class="btn-close">关闭</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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
  response_time?: number
  ip_address?: string
  user_agent?: string
  extra_data?: any
  stack_trace?: string
  [key: string]: any
}

interface Props {
  visible: boolean
  log: LogData
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const closeModal = () => {
  emit('close')
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
  return new Date(timestamp).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: 'short'
  })
}

const formatExtraData = (data: any) => {
  if (typeof data === 'string') {
    try {
      return JSON.stringify(JSON.parse(data), null, 2)
    } catch {
      return data
    }
  }
  return JSON.stringify(data, null, 2)
}

const copyToClipboard = async () => {
  const content = generateLogText()
  try {
    await navigator.clipboard.writeText(content)
    alert('日志详情已复制到剪贴板')
  } catch (err) {
    console.error('复制失败:', err)
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = content
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    alert('日志详情已复制到剪贴板')
  }
}

const generateLogText = () => {
  const lines = []
  lines.push('=== 日志详情 ===')
  lines.push(`ID: ${props.log.id}`)
  if (props.log.level) lines.push(`级别: ${getLevelText(props.log.level)}`)
  lines.push(`时间: ${formatDateTime(props.log.timestamp)}`)
  if (props.log.user || props.log.user_id) {
    lines.push(`用户: ${props.log.user?.username || `ID: ${props.log.user_id}`}`)
  }
  if (props.log.module) lines.push(`模块: ${props.log.module}`)
  if (props.log.action) lines.push(`操作: ${props.log.action}`)
  if (props.log.method) lines.push(`方法: ${props.log.method}`)
  if (props.log.path) lines.push(`路径: ${props.log.path}`)
  if (props.log.status_code) lines.push(`状态码: ${props.log.status_code}`)
  if (props.log.response_time) lines.push(`响应时间: ${props.log.response_time}ms`)
  if (props.log.ip_address) lines.push(`IP地址: ${props.log.ip_address}`)
  
  lines.push('')
  lines.push('=== 日志内容 ===')
  lines.push(props.log.message)
  
  if (props.log.user_agent) {
    lines.push('')
    lines.push('=== 用户代理 ===')
    lines.push(props.log.user_agent)
  }
  
  if (props.log.extra_data) {
    lines.push('')
    lines.push('=== 额外数据 ===')
    lines.push(formatExtraData(props.log.extra_data))
  }
  
  if (props.log.stack_trace) {
    lines.push('')
    lines.push('=== 堆栈跟踪 ===')
    lines.push(props.log.stack_trace)
  }
  
  return lines.join('\n')
}
</script>

<style scoped>
.log-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
  border-bottom: 2px solid #007bff;
  padding-bottom: 4px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-item label {
  font-weight: 500;
  color: #666;
  min-width: 80px;
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

.method-badge {
  padding: 2px 6px;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

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
  font-size: 14px;
}

.path-text {
  font-family: monospace;
  font-size: 13px;
  word-break: break-all;
}

.message-content,
.user-agent-content,
.extra-data-content,
.stack-trace-content {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.message-content pre,
.user-agent-content pre,
.extra-data-content pre,
.stack-trace-content pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-break: break-word;
}

.stack-trace-content {
  background-color: #fff5f5;
  border-color: #fed7d7;
}

.stack-trace-content pre {
  color: #c53030;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.btn-copy,
.btn-close {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-copy {
  background-color: #28a745;
  color: white;
}

.btn-copy:hover {
  background-color: #218838;
}

.btn-close {
  background-color: #6c757d;
  color: white;
}

.btn-close:hover {
  background-color: #5a6268;
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-footer {
    flex-direction: column;
  }
}
</style>
