/**
 * 前端响应格式处理工具
 */

// 统一响应格式接口
export interface StandardResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
  request_id: string
}

// 分页数据接口
export interface PaginatedData<T = any> {
  list: T[]
  total: number
  page?: number
  page_size?: number
  total_pages?: number
  has_next?: boolean
  has_previous?: boolean
}

// 错误信息接口
export interface ErrorInfo {
  code: number
  message: string
  data?: any
  request_id?: string
}

/**
 * 响应格式处理工具类
 */
export class ResponseHelper {
  /**
   * 判断响应是否成功
   */
  static isSuccess(response: StandardResponse): boolean {
    return response.code === 200
  }

  /**
   * 提取响应数据
   */
  static getData<T>(response: StandardResponse<T>): T {
    return response.data
  }

  /**
   * 提取错误信息
   */
  static getErrorInfo(response: StandardResponse): ErrorInfo | null {
    if (response.code !== 200) {
      return {
        code: response.code,
        message: response.message,
        data: response.data,
        request_id: response.request_id
      }
    }
    return null
  }

  /**
   * 格式化错误消息
   */
  static formatErrorMessage(error: ErrorInfo): string {
    let message = `[${error.code}] ${error.message}`
    if (error.request_id) {
      message += ` (请求ID: ${error.request_id})`
    }
    return message
  }

  /**
   * 判断是否是分页数据
   */
  static isPaginatedData(data: any): data is PaginatedData {
    return data && typeof data === 'object' && 'list' in data && 'total' in data
  }

  /**
   * 提取分页数据列表
   */
  static getPaginatedList<T>(data: PaginatedData<T>): T[] {
    return data.list || []
  }

  /**
   * 获取分页信息
   */
  static getPaginationInfo(data: PaginatedData): {
    total: number
    page: number
    pageSize: number
    totalPages: number
    hasNext: boolean
    hasPrevious: boolean
  } {
    return {
      total: data.total || 0,
      page: data.page || 1,
      pageSize: data.page_size || 20,
      totalPages: data.total_pages || 0,
      hasNext: data.has_next || false,
      hasPrevious: data.has_previous || false
    }
  }

  /**
   * 处理API错误
   */
  static handleApiError(error: any): ErrorInfo {
    // 如果是自定义错误（包含code属性）
    if (error.code && error.message) {
      return {
        code: error.code,
        message: error.message,
        data: error.data,
        request_id: error.request_id
      }
    }

    // 如果是HTTP错误
    if (error.response) {
      const status = error.response.status
      const statusText = error.response.statusText
      
      return {
        code: status,
        message: `HTTP ${status}: ${statusText}`,
        data: error.response.data
      }
    }

    // 网络错误或其他错误
    return {
      code: 500,
      message: error.message || '未知错误',
      data: null
    }
  }

  /**
   * 创建成功提示消息
   */
  static createSuccessMessage(message: string, requestId?: string): string {
    let result = `✅ ${message}`
    if (requestId) {
      result += ` (请求ID: ${requestId})`
    }
    return result
  }

  /**
   * 创建错误提示消息
   */
  static createErrorMessage(error: ErrorInfo): string {
    return `❌ ${this.formatErrorMessage(error)}`
  }

  /**
   * 获取状态码对应的颜色类型
   */
  static getStatusColorType(code: number): 'success' | 'warning' | 'error' | 'info' {
    if (code === 200) return 'success'
    if (code >= 400 && code < 500) return 'warning'
    if (code >= 500) return 'error'
    return 'info'
  }

  /**
   * 格式化时间戳
   */
  static formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    } catch (error) {
      return timestamp
    }
  }

  /**
   * 验证响应格式是否正确
   */
  static validateResponseFormat(response: any): {
    isValid: boolean
    errors: string[]
  } {
    const errors: string[] = []

    if (!response || typeof response !== 'object') {
      errors.push('响应不是有效的对象')
      return { isValid: false, errors }
    }

    // 检查必需字段
    const requiredFields = ['code', 'message', 'data', 'timestamp', 'request_id']
    for (const field of requiredFields) {
      if (!(field in response)) {
        errors.push(`缺少必需字段: ${field}`)
      }
    }

    // 检查字段类型
    if ('code' in response && typeof response.code !== 'number') {
      errors.push('code字段必须是数字类型')
    }

    if ('message' in response && typeof response.message !== 'string') {
      errors.push('message字段必须是字符串类型')
    }

    if ('timestamp' in response && typeof response.timestamp !== 'string') {
      errors.push('timestamp字段必须是字符串类型')
    }

    if ('request_id' in response && typeof response.request_id !== 'string') {
      errors.push('request_id字段必须是字符串类型')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }
}

/**
 * 响应格式常量
 */
export const RESPONSE_CODES = {
  SUCCESS: 200,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
} as const

/**
 * 响应消息常量
 */
export const RESPONSE_MESSAGES = {
  SUCCESS: '操作成功',
  BAD_REQUEST: '请求参数错误',
  UNAUTHORIZED: '未授权访问',
  FORBIDDEN: '权限不足',
  NOT_FOUND: '资源不存在',
  INTERNAL_SERVER_ERROR: '服务器内部错误'
} as const