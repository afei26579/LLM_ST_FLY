/**
 * 统一API客户端
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { StandardResponse, ResponseHelper, ErrorInfo } from './responseHelper'

/**
 * API客户端配置
 */
interface ApiClientConfig {
  baseURL?: string
  timeout?: number
  headers?: Record<string, string>
}

/**
 * 统一API客户端类
 */
export class ApiClient {
  private instance: AxiosInstance

  constructor(config: ApiClientConfig = {}) {
    const defaultConfig = {
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    }

    this.instance = axios.create({ ...defaultConfig, ...config })
    this.setupInterceptors()
  }

  /**
   * 设置请求和响应拦截器
   */
  private setupInterceptors(): void {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 自动添加认证token
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response) => {
        const data = response.data as StandardResponse

        // 检查是否是统一返回格式
        if (data && typeof data === 'object' && 'code' in data && 'message' in data) {
          // 验证响应格式
          const validation = ResponseHelper.validateResponseFormat(data)
          if (!validation.isValid) {
            console.warn('响应格式验证失败:', validation.errors)
          }

          // 如果业务状态码不是200，抛出错误
          if (data.code !== 200) {
            const errorInfo = ResponseHelper.getErrorInfo(data)
            const error = new Error(data.message)
            Object.assign(error, errorInfo)
            throw error
          }

          // 返回数据部分，同时保留完整的标准响应
          return {
            ...response,
            data: data.data,
            standardResponse: data
          }
        }

        // 兼容旧格式
        return response
      },
      (error) => {
        // 处理认证错误
        if (error.response?.status === 401) {
          this.handleAuthError()
        }

        // 如果响应包含统一格式的错误信息
        if (error.response?.data && typeof error.response.data === 'object' && 'code' in error.response.data) {
          const errorData = error.response.data as StandardResponse
          const errorInfo = ResponseHelper.getErrorInfo(errorData)
          const customError = new Error(errorData.message)
          Object.assign(customError, errorInfo)
          return Promise.reject(customError)
        }

        // 处理其他HTTP错误
        const errorInfo = ResponseHelper.handleApiError(error)
        const customError = new Error(errorInfo.message)
        Object.assign(customError, errorInfo)
        return Promise.reject(customError)
      }
    )
  }

  /**
   * 处理认证错误
   */
  private handleAuthError(): void {
    // 清除本地存储的认证信息
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('userInfo')

    // 跳转到登录页
    if (window.location.pathname !== '/login') {
      window.location.href = '/login'
    }
  }

  /**
   * GET请求
   */
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.get(url, config)
    return response.data
  }

  /**
   * POST请求
   */
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.post(url, data, config)
    return response.data
  }

  /**
   * PUT请求
   */
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.put(url, data, config)
    return response.data
  }

  /**
   * PATCH请求
   */
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.patch(url, data, config)
    return response.data
  }

  /**
   * DELETE请求
   */
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.instance.delete(url, config)
    return response.data
  }

  /**
   * 获取完整响应（包含标准响应格式信息）
   */
  async getFullResponse<T = any>(url: string, config?: AxiosRequestConfig): Promise<{
    data: T
    standardResponse: StandardResponse<T>
  }> {
    const response = await this.instance.get(url, config)
    return {
      data: response.data,
      standardResponse: (response as any).standardResponse
    }
  }

  /**
   * 下载文件
   */
  async downloadFile(url: string, filename: string, config?: AxiosRequestConfig): Promise<void> {
    const response = await this.instance.get(url, {
      ...config,
      responseType: 'blob'
    })

    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  }

  /**
   * 上传文件
   */
  async uploadFile<T = any>(
    url: string,
    file: File,
    fieldName: string = 'file',
    additionalData?: Record<string, any>,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData()
    formData.append(fieldName, file)

    if (additionalData) {
      Object.keys(additionalData).forEach(key => {
        formData.append(key, additionalData[key])
      })
    }

    const config: AxiosRequestConfig = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }

    if (onProgress) {
      config.onUploadProgress = (progressEvent) => {
        if (progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    }

    const response = await this.instance.post(url, formData, config)
    return response.data
  }

  /**
   * 获取原始axios实例（用于特殊需求）
   */
  getAxiosInstance(): AxiosInstance {
    return this.instance
  }
}

// 创建默认的API客户端实例
export const apiClient = new ApiClient({
  baseURL: `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1`
})

// 导出类型
export type { ApiClientConfig }