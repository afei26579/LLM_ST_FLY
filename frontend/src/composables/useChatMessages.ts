import { ref, reactive } from 'vue'
import { apiService } from '../services/api'
import type { ChatMessage as ApiChatMessage } from '../services/api'
import type { ChatMessage } from './useConversations'

// 消息发送状态
export type MessageStatus = 'sending' | 'sent' | 'error' | 'generating'

// 消息输入类型
export interface MessageInput {
  content: string
  conversationId: number
  type?: 'text' | 'image' | 'file'
  fileUrl?: string
  fileName?: string
}

// 返回类型定义
export interface UseChatMessagesReturn {
  // 状态
  messages: ChatMessage[]
  isLoading: boolean
  isGenerating: boolean
  messageStatus: Map<number, MessageStatus>
  
  // 方法
  sendMessage: (input: MessageInput) => Promise<ChatMessage | null>
  updateMessage: (messageId: number, content: string) => void
  deleteMessage: (messageId: number) => Promise<boolean>
  clearMessages: () => void
  loadMessagesByConversation: (conversationId: number) => Promise<void>
  generateMessageId: () => number
}

/**
 * 聊天消息管理组合式函数
 */
export function useChatMessages(): UseChatMessagesReturn {
  // 状态
  const messages = reactive<ChatMessage[]>([])
  const isLoading = ref(false)
  const isGenerating = ref(false)
  const messageStatus = reactive<Map<number, MessageStatus>>(new Map())
  
  // 生成临时消息ID（负数，避免与后端ID冲突）
  const generateMessageId = (): number => {
    return -Date.now()
  }
  
  /**
   * 发送消息
   */
  const sendMessage = async (input: MessageInput): Promise<ChatMessage | null> => {
    try {
      // 创建临时消息
      const tempMessageId = generateMessageId()
      const newMessage: ChatMessage = {
        id: tempMessageId,
        conversation_id: input.conversationId,
        role: 'user',
        content: input.content,
        timestamp: new Date(),
        type: input.type || 'text',
        file_url: input.fileUrl,
        file_name: input.fileName
      }
      
      // 添加到消息列表
      messages.push(newMessage)
      
      // 设置消息状态为发送中
      messageStatus.set(tempMessageId, 'sending')
      
      // 发送到服务器
      const response = await apiService.sendMessage(input)
      
      if (response.code === 200 && response.data) {
        // 查找临时消息并更新
        const index = messages.findIndex(m => m.id === tempMessageId)
        if (index !== -1) {
          messages[index] = {
            ...messages[index],
            id: response.data.id,
            timestamp: new Date(response.data.timestamp || new Date())
          }
          
          // 更新消息状态为已发送
          messageStatus.set(response.data.id, 'sent')
          messageStatus.delete(tempMessageId)
          
          return messages[index]
        }
      } else {
        console.error('发送消息失败:', response.message)
        messageStatus.set(tempMessageId, 'error')
      }
    } catch (error) {
      console.error('发送消息出错:', error)
    }
    
    return null
  }
  
  /**
   * 更新消息内容
   */
  const updateMessage = (messageId: number, content: string): void => {
    const message = messages.find(m => m.id === messageId)
    if (message) {
      message.content = content
    }
  }
  
  /**
   * 删除消息
   */
  const deleteMessage = async (messageId: number): Promise<boolean> => {
    try {
      const response = await apiService.deleteMessage(messageId)
      
      if (response.code === 200) {
        // 从本地列表中删除
        const index = messages.findIndex(m => m.id === messageId)
        if (index !== -1) {
          messages.splice(index, 1)
        }
        
        // 移除消息状态
        messageStatus.delete(messageId)
        
        return true
      } else {
        console.error('删除消息失败:', response.message)
        return false
      }
    } catch (error) {
      console.error('删除消息出错:', error)
      return false
    }
  }
  
  /**
   * 清空消息列表
   */
  const clearMessages = (): void => {
    messages.splice(0, messages.length)
    messageStatus.clear()
  }
  
  /**
   * 加载指定对话的消息
   */
  const loadMessagesByConversation = async (conversationId: number): Promise<void> => {
    if (!conversationId) {
      console.error('无效的对话ID')
      return
    }
    
    isLoading.value = true
    
    try {
      const response = await apiService.getMessagesByConversation(conversationId)
      
      if (response.code === 200 && response.data) {
        // 清空当前消息
        clearMessages()
        
        // 添加新消息（转换时间格式）
        const loadedMessages: ChatMessage[] = response.data.list.map((msg: ApiChatMessage) => ({
          ...msg,
          timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
        }))
        
        messages.push(...loadedMessages)
      } else {
        console.error('加载消息失败:', response.message)
      }
    } catch (error) {
      console.error('加载消息出错:', error)
    } finally {
      isLoading.value = false
    }
  }
  
  return {
    // 状态
    messages,
    isLoading,
    isGenerating,
    messageStatus,
    
    // 方法
    sendMessage,
    updateMessage,
    deleteMessage,
    clearMessages,
    loadMessagesByConversation,
    generateMessageId
  }
}