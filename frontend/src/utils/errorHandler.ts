/**
 * 前端错误处理工具
 */
import { ResponseHelper, ErrorInfo } from './responseHelper'

/**
 * 错误处理配置
 */
interface ErrorHandlerConfig {
  showMessage?: boolean
  logToConsole?: boolean
}

/**
 * 错误处理器类
 */
export class ErrorHandler {
  private static defaultConfig: ErrorHandlerConfig = {
    showMessage: true,
    logToConsole: true
  }

  /**
   * 处理API错误
   */
  static handleApiError(error: any, config: ErrorHandlerConfig = {}): void {
    const finalConfig = { ...this.defaultConfig, ...config }
    const errorInfo = ResponseHelper.handleApiError(error)

    // 控制台日志
    if (finalConfig.logToConsole) {
      console.error('API错误:', errorInfo)
    }

    // 显示消息提示
    if (finalConfig.showMessage) {
      this.showErrorMessage(errorInfo)
    }
  }

  /**
   * 显示错误消息
   */
  private static showErrorMessage(errorInfo: ErrorInfo): void {
    const message = ResponseHelper.formatErrorMessage(errorInfo)
    console.error(message)
    
    // 如果有Element Plus，使用ElMessage
    if (typeof window !== 'undefined' && (window as any).ElMessage) {
      (window as any).ElMessage({
        type: 'error',
        message,
        duration: 5000,
        showClose: true
      })
    }
  }

  /**
   * 显示成功消息
   */
  static showSuccess(message: string, requestId?: string): void {
    const successMessage = ResponseHelper.createSuccessMessage(message, requestId)
    console.log(successMessage)
    
    // 如果有Element Plus，使用ElMessage
    if (typeof window !== 'undefined' && (window as any).ElMessage) {
      (window as any).ElMessage({
        type: 'success',
        message: successMessage,
        duration: 3000,
        showClose: true
      })
    }
  }

  /**
   * 显示警告消息
   */
  static showWarning(message: string): void {
    console.warn(message)
    
    // 如果有Element Plus，使用ElMessage
    if (typeof window !== 'undefined' && (window as any).ElMessage) {
      (window as any).ElMessage({
        type: 'warning',
        message,
        duration: 4000,
        showClose: true
      })
    }
  }

  /**
   * 处理表单验证错误
   */
  static handleValidationError(error: any): Record<string, string[]> {
    const errorInfo = ResponseHelper.handleApiError(error)
    
    if (errorInfo.code === 400 && errorInfo.data && typeof errorInfo.data === 'object') {
      return errorInfo.data
    }

    return {}
  }
}

// 导出默认实例
export const errorHandler = ErrorHandler