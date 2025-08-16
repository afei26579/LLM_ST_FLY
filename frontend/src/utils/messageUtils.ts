/**
 * 消息处理工具函数
 */

/**
 * 简单格式化消息（支持换行）
 */
export const formatMessage = (text: string): string => {
  return text.replace(/\n/g, '<br>')
}

/**
 * 截取文本预览
 */
export const truncateText = (text: string, maxLength: number = 50): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

/**
 * 清理HTML标签
 */
export const stripHtml = (html: string): string => {
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

/**
 * 高亮搜索关键词
 */
export const highlightKeywords = (text: string, keywords: string): string => {
  if (!keywords.trim()) return text
  
  const regex = new RegExp(`(${keywords.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

/**
 * 自动调整输入框高度
 */
export const autoResizeTextarea = (element: HTMLTextAreaElement) => {
  element.style.height = 'auto'
  element.style.height = `${element.scrollHeight}px`
}

/**
 * 滚动到底部
 */
export const scrollToBottom = (container: HTMLElement) => {
  container.scrollTop = container.scrollHeight
}

/**
 * 聚焦输入框
 */
export const focusInput = (element: HTMLElement | null) => {
  element?.focus()
}