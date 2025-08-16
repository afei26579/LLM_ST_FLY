import { ref, computed } from 'vue'
import { apiService } from '../services/api'
import type { Conversation, ChatMessage } from './useConversations'

/**
 * 聊天功能组合式函数
 */
export function useChat() {
  // 状态
  const userInput = ref('')
  const isLoading = ref(false)
  const activeConversationId = ref<number | null>(null)
  const isCenterLayout = ref(false)

  // 发送消息
  const sendMessage = async (
    conversations: Conversation[],
    onConversationUpdate: (conversation: Conversation) => void,
    options?: {
      deepThinking?: boolean
      webSearch?: boolean
    }
  ) => {
    const content = userInput.value.trim()
    if (!content || isLoading.value) return

    try {
      const timestamp = new Date()
      
      // 查找当前对话
      const conversation = conversations.find(c => c.id === activeConversationId.value)
      
      if (!conversation) {
        console.error('无法找到活动对话，ID:', activeConversationId.value)
        return
      }

      // 发送第一条消息时，切换布局
      if (conversation.messages.length === 0) {
        isCenterLayout.value = false
      }

      // 如果是临时对话，需要先创建真实对话
      if (conversation.isTemporary) {
        console.log("当前是临时对话，需要先创建真实对话")
        
        // 使用用户输入的消息作为对话标题
        const title = content.length > 50 ? content.substring(0, 50) + '...' : content
        console.log("使用消息作为对话标题:", title)
        
        // 创建真实对话，使用消息内容作为标题
        const response = await apiService.createConversation(title)
        console.log("创建对话响应:", response)
        if (response.code === 201 && response.data && response.data.id) {
          // 更新临时对话为真实对话
          const realId = response.data.id
          conversation.id = realId
          conversation.isTemporary = false
          
          // 更新对话标题
          conversation.title = title
          
          // 更新活动对话ID
          activeConversationId.value = realId
          
          console.log("临时对话已转换为真实对话:", realId, "标题:", title)
        } else {
          console.error('创建真实对话失败:', response.message)
          return
        }
      }

      // 发送消息到对话
      await sendMessageToConversation(conversation, content, timestamp, onConversationUpdate, options)
    } catch (err) {
      console.error("发送消息过程中出错:", err)
      isLoading.value = false
    }
  }

  // 向指定对话发送消息
  const sendMessageToConversation = async (
    conversation: Conversation,
    content: string,
    timestamp: Date,
    onConversationUpdate: (conversation: Conversation) => void
  ) => {
    // 确保消息数组已初始化
    if (!conversation.messages) {
      conversation.messages = []
    }

    // 添加用户消息到本地UI
    conversation.messages.push({
      role: 'user',
      content,
      timestamp
    })

    // 更新预览和最后更新时间
    conversation.preview = content
    conversation.lastUpdated = timestamp
    conversation.message_count = (conversation.message_count || 0) + 1

    userInput.value = ''

    // 通知父组件更新
    onConversationUpdate(conversation)

    // 调用实际的AI API
    isLoading.value = true

    try {
      // 准备发送到API的消息历史
      const apiMessages = conversation.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      console.log("发送聊天请求:", {
        messages: apiMessages,
        conversation_id: conversation.id
      })

      // 调用聊天API（包含对话ID）
      const response = await apiService.chatCompletion(apiMessages, conversation.id)
      console.log("聊天API响应:", response)

      if (response.code === 200 && response.data && response.data.content) {
        const responseContent = response.data.content
        const responseTimestamp = new Date()

        // 添加AI回复到本地UI
        conversation.messages.push({
          role: 'assistant',
          content: responseContent,
          timestamp: responseTimestamp
        })

        // 更新预览和最后更新时间
        conversation.preview = responseContent
        conversation.lastUpdated = responseTimestamp
        conversation.message_count = (conversation.message_count || 0) + 1

        // 如果是新对话，可能需要更新对话ID（如果后端创建了新对话）
        if (response.data.conversation_id && response.data.conversation_id !== conversation.id) {
          console.log("更新对话ID:", conversation.id, "->", response.data.conversation_id)
          conversation.id = response.data.conversation_id
          activeConversationId.value = response.data.conversation_id
        }
      } else {
        // API调用失败，显示错误消息
        conversation.messages.push({
          role: 'assistant',
          content: `抱歉，我遇到了一些问题。${response.message || '请稍后再试。'}`,
          timestamp: new Date()
        })
        conversation.message_count = (conversation.message_count || 0) + 1
      }
    } catch (error) {
      console.error('聊天API调用失败:', error)
      // 显示错误消息
      conversation.messages.push({
        role: 'assistant',
        content: '抱歉，我遇到了网络问题。请检查您的网络连接并稍后再试。',
        timestamp: new Date()
      })
      conversation.message_count = (conversation.message_count || 0) + 1
    } finally {
      isLoading.value = false
      
      // 通知父组件更新
      onConversationUpdate(conversation)
    }
  }

  // 处理键盘事件
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      // 这里需要在组件中调用sendMessage
    }
  }

  // 切换对话
  const switchConversation = async (
    id: number,
    conversations: Conversation[],
    loadConversationDetail: (id: number) => Promise<void>
  ) => {
    try {
      console.log("切换到对话:", id)
      
      if (!id) {
        console.error("无效的对话ID:", id)
        return
      }
      
      activeConversationId.value = id
      
      // 重置加载状态
      isLoading.value = false
      
      // 加载对话详情
      await loadConversationDetail(id)
      
      // 检查对话是否有消息，决定布局
      const conversation = conversations.find(c => c.id === id)
      isCenterLayout.value = conversation?.messages.length === 0
      
      console.log("对话切换完成:", id)
    } catch (error) {
      console.error("切换对话出错:", error)
    }
  }

  // 跳转到特定问题
  const jumpToQuestion = (
    conversationId: number,
    questionIndex: number,
    conversations: Conversation[],
    loadConversationDetail: (id: number) => Promise<void>,
    scrollToQuestion: (questionIndex: number) => void
  ) => {
    // 如果不是当前对话，先切换到该对话
    if (activeConversationId.value !== conversationId) {
      switchConversation(conversationId, conversations, loadConversationDetail).then(() => {
        scrollToQuestion(questionIndex)
      })
    } else {
      scrollToQuestion(questionIndex)
    }
  }

  return {
    // 状态
    userInput,
    isLoading,
    activeConversationId,
    isCenterLayout,
    
    // 方法
    sendMessage,
    handleKeyDown,
    switchConversation,
    jumpToQuestion
  }
}