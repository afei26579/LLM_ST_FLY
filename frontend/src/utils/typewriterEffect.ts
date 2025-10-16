/**
 * 打字机效果工具类
 * 实现逐字符显示的动画效果
 */

export interface TypewriterOptions {
  /**
   * 每个字符的显示延迟（毫秒）
   * @default 30
   */
  delay?: number
  
  /**
   * 每次处理的字符数
   * @default 1
   */
  charsPerStep?: number
  
  /**
   * 内容更新回调
   */
  onUpdate: (content: string) => void
  
  /**
   * 完成回调
   */
  onComplete?: () => void
}

export class TypewriterEffect {
  private queue: string[] = []
  private isTyping: boolean = false
  private currentContent: string = ''
  private options: Required<Omit<TypewriterOptions, 'onComplete'>> & { onComplete?: () => void }
  private animationFrame: number | null = null
  private lastUpdateTime: number = 0

  constructor(options: TypewriterOptions) {
    this.options = {
      delay: options.delay ?? 30,
      charsPerStep: options.charsPerStep ?? 1,
      onUpdate: options.onUpdate,
      onComplete: options.onComplete
    }
  }

  /**
   * 添加文本到队列
   */
  addText(text: string) {
    if (!text) return
    
    // 将文本拆分成字符数组并添加到队列
    const chars = Array.from(text) // 使用 Array.from 正确处理 emoji 和中文
    this.queue.push(...chars)
    
    // 如果当前没有在打字，开始打字
    if (!this.isTyping) {
      this.startTyping()
    }
  }

  /**
   * 开始打字动画
   */
  private startTyping() {
    if (this.isTyping) return
    
    this.isTyping = true
    this.lastUpdateTime = performance.now()
    this.typeNextChars()
  }

  /**
   * 打印下一批字符
   */
  private typeNextChars = () => {
    const now = performance.now()
    const elapsed = now - this.lastUpdateTime

    // 检查是否到了下一次更新的时间
    if (elapsed >= this.options.delay) {
      // 从队列中取出字符
      const charsToType = this.queue.splice(0, this.options.charsPerStep)
      
      if (charsToType.length > 0) {
        // 添加到当前内容
        this.currentContent += charsToType.join('')
        
        // 触发更新回调
        this.options.onUpdate(this.currentContent)
        
        this.lastUpdateTime = now
      }
      
      // 如果队列还有内容，继续打字
      if (this.queue.length > 0) {
        this.animationFrame = requestAnimationFrame(this.typeNextChars)
      } else {
        // 打字完成
        this.isTyping = false
        this.options.onComplete?.()
      }
    } else {
      // 还没到更新时间，继续等待
      this.animationFrame = requestAnimationFrame(this.typeNextChars)
    }
  }

  /**
   * 立即显示所有剩余内容（跳过动画）
   */
  skipAnimation() {
    if (this.queue.length > 0) {
      // 取出所有剩余字符
      const remainingChars = this.queue.splice(0, this.queue.length)
      this.currentContent += remainingChars.join('')
      
      // 触发更新回调
      this.options.onUpdate(this.currentContent)
    }
    
    // 停止动画
    if (this.animationFrame !== null) {
      cancelAnimationFrame(this.animationFrame)
      this.animationFrame = null
    }
    
    this.isTyping = false
    this.options.onComplete?.()
  }

  /**
   * 清空当前内容和队列
   */
  clear() {
    this.queue = []
    this.currentContent = ''
    this.isTyping = false
    
    if (this.animationFrame !== null) {
      cancelAnimationFrame(this.animationFrame)
      this.animationFrame = null
    }
  }

  /**
   * 获取当前内容（仅已显示的部分）
   */
  getCurrentContent(): string {
    return this.currentContent
  }

  /**
   * 获取总内容（已显示 + 队列中等待显示的）
   */
  getTotalContent(): string {
    return this.currentContent + this.queue.join('')
  }

  /**
   * 检查是否正在打字
   */
  isCurrentlyTyping(): boolean {
    return this.isTyping || this.queue.length > 0
  }

  /**
   * 销毁实例
   */
  destroy() {
    this.clear()
  }
}

/**
 * 创建打字机效果实例的工厂函数
 */
export function createTypewriter(options: TypewriterOptions): TypewriterEffect {
  return new TypewriterEffect(options)
}

