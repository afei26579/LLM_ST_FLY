import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 统一响应格式接口
interface StandardResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
  request_id: string
}

// 分页数据接口
interface PaginatedData<T = any> {
  list: T[]
  total: number
  page?: number
  page_size?: number
  total_pages?: number
  has_next?: boolean
  has_previous?: boolean
}

interface LogResponse {
  count: number
  next: string | null
  previous: string | null
  results: any[]
}

interface LogParams {
  page?: number
  level?: string
  start_time?: string
  end_time?: string
  user?: string
  module?: string
  action?: string
  method?: string
  search?: string
  ordering?: string
  page_size?: number
}

class LogService {
  private api = axios.create({
    baseURL: `${API_BASE_URL}/api/v1/logs/`,
    headers: {
      'Content-Type': 'application/json',
    },
  })

  constructor() {
    // 添加请求拦截器，自动添加认证token
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // 添加响应拦截器，处理统一返回格式
    this.api.interceptors.response.use(
      (response) => {
        const data = response.data as StandardResponse
        
        // 检查是否是统一返回格式
        if (data && typeof data === 'object' && 'code' in data && 'message' in data) {
          // 如果业务状态码不是200，抛出错误
          if (data.code !== 200) {
            const error = new Error(data.message)
            ;(error as any).code = data.code
            ;(error as any).data = data.data
            ;(error as any).request_id = data.request_id
            throw error
          }
          // 返回数据部分，同时保留完整的标准响应
          return { ...response, data: data.data, standardResponse: data }
        }
        
        // 兼容旧格式
        return response
      },
      (error) => {
        if (error.response?.status === 401) {
          // Token过期，重定向到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          window.location.href = '/login'
        }
        
        // 如果响应包含统一格式的错误信息
        if (error.response?.data && typeof error.response.data === 'object' && 'code' in error.response.data) {
          const errorData = error.response.data as StandardResponse
          const customError = new Error(errorData.message)
          ;(customError as any).code = errorData.code
          ;(customError as any).data = errorData.data
          ;(customError as any).request_id = errorData.request_id
          return Promise.reject(customError)
        }
        
        return Promise.reject(error)
      }
    )
  }

  // 获取系统日志
  async getSystemLogs(params: LogParams = {}): Promise<LogResponse> {
    const response = await this.api.get('system/', { params })
    return response.data
  }

  // 获取用户操作日志
  async getUserLogs(params: LogParams = {}): Promise<LogResponse> {
    const response = await this.api.get('user-actions/', { params })
    return response.data
  }

  // 获取API访问日志
  async getApiLogs(params: LogParams = {}): Promise<LogResponse> {
    const response = await this.api.get('api-access/', { params })
    return response.data
  }

  // 获取错误日志
  async getErrorLogs(params: LogParams = {}): Promise<LogResponse> {
    const response = await this.api.get('errors/', { params })
    return response.data
  }

  // 获取日志详情
  async getLogDetail(logType: string, id: number): Promise<any> {
    const response = await this.api.get(`${logType}/${id}/`)
    return response.data
  }

  // 导出系统日志
  async exportSystemLogs(params: LogParams = {}): Promise<void> {
    const response = await this.api.get('system/export/', {
      params,
      responseType: 'blob'
    })
    this.downloadFile(response.data, 'system_logs.csv')
  }

  // 导出用户操作日志
  async exportUserLogs(params: LogParams = {}): Promise<void> {
    const response = await this.api.get('user-actions/export/', {
      params,
      responseType: 'blob'
    })
    this.downloadFile(response.data, 'user_logs.csv')
  }

  // 导出API访问日志
  async exportApiLogs(params: LogParams = {}): Promise<void> {
    const response = await this.api.get('api-access/export/', {
      params,
      responseType: 'blob'
    })
    this.downloadFile(response.data, 'api_logs.csv')
  }

  // 导出错误日志
  async exportErrorLogs(params: LogParams = {}): Promise<void> {
    const response = await this.api.get('errors/export/', {
      params,
      responseType: 'blob'
    })
    this.downloadFile(response.data, 'error_logs.csv')
  }

  // 获取日志统计信息
  async getLogStats(params: { 
    start_time?: string
    end_time?: string
    log_type?: string
  } = {}): Promise<any> {
    const response = await this.api.get('stats/', { params })
    return response.data
  }

  // 清理过期日志
  async cleanupLogs(params: {
    log_type: string
    days: number
  }): Promise<any> {
    const response = await this.api.post('cleanup/', params)
    return response.data
  }

  // 下载文件辅助方法
  private downloadFile(data: Blob, filename: string): void {
    const url = window.URL.createObjectURL(data)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  // 格式化日志级别
  static formatLogLevel(level: string): string {
    const levelMap: Record<string, string> = {
      'DEBUG': '调试',
      'INFO': '信息',
      'WARNING': '警告',
      'ERROR': '错误',
      'CRITICAL': '严重'
    }
    return levelMap[level] || level
  }

  // 格式化操作类型
  static formatActionType(action: string): string {
    const actionMap: Record<string, string> = {
      'CREATE': '创建',
      'UPDATE': '更新',
      'DELETE': '删除',
      'VIEW': '查看',
      'LOGIN': '登录',
      'LOGOUT': '登出',
      'EXPORT': '导出',
      'IMPORT': '导入'
    }
    return actionMap[action] || action
  }

  // 格式化HTTP方法
  static formatHttpMethod(method: string): string {
    return method.toUpperCase()
  }

  // 格式化状态码
  static formatStatusCode(statusCode: number): { text: string; class: string } {
    if (statusCode >= 200 && statusCode < 300) {
      return { text: `${statusCode} 成功`, class: 'success' }
    } else if (statusCode >= 300 && statusCode < 400) {
      return { text: `${statusCode} 重定向`, class: 'redirect' }
    } else if (statusCode >= 400 && statusCode < 500) {
      return { text: `${statusCode} 客户端错误`, class: 'client-error' }
    } else if (statusCode >= 500) {
      return { text: `${statusCode} 服务器错误`, class: 'server-error' }
    }
    return { text: `${statusCode}`, class: 'unknown' }
  }

  // 格式化响应时间
  static formatResponseTime(time: number): string {
    if (time < 1000) {
      return `${time}ms`
    } else if (time < 60000) {
      return `${(time / 1000).toFixed(2)}s`
    } else {
      return `${(time / 60000).toFixed(2)}min`
    }
  }

  // 格式化文件大小
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 格式化时间差
  static formatTimeDiff(timestamp: string): string {
    const now = new Date()
    const time = new Date(timestamp)
    const diff = now.getTime() - time.getTime()
    
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)
    
    if (days > 0) return `${days}天前`
    if (hours > 0) return `${hours}小时前`
    if (minutes > 0) return `${minutes}分钟前`
    return `${seconds}秒前`
  }
}

export const logService = new LogService()
export default LogService