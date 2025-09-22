import { ref, computed } from 'vue'
import { apiService } from '../services/api'
import type { Conversation, ChatMessage } from './useConversations'

/**
 * 聊天功能组合式函数
 */
export function useChat(removeTempConversationFromCache?: () => void) {
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
          
          // 删除缓存中的临时对话
          if (removeTempConversationFromCache) {
            removeTempConversationFromCache()
          }
          
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
    onConversationUpdate: (conversation: Conversation) => void,
    options?: {
      deepThinking?: boolean
      webSearch?: boolean
    }
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

    // 创建AI消息占位符用于流式更新（不立即添加到对话中）
    const aiMessage: any = {
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      thinking_process: '',
      has_thinking: false,
      is_thinking: false
    }

    // AI消息将在收到第一个内容块时添加到对话中
    let aiMessageAdded = false

    try {
      // 准备发送到API的消息历史
      const apiMessages = conversation.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      console.log("发送聊天请求:", {
        messages: apiMessages,
        conversation_id: conversation.id,
        deep_thinking: options?.deepThinking || false,
        web_search: options?.webSearch || false
      })

      // 调用聊天API（包含对话ID和功能选项）
      const response = await apiService.chatCompletion(
        apiMessages, 
        conversation.id, 
        {
          deepThinking: options?.deepThinking || false,
          webSearch: options?.webSearch || false,
          onChunk: (chunk) => {
            console.log('🎯 [前端处理] 收到流式数据块:', chunk);
            
            // 在收到第一个内容块时添加AI消息到对话中（只在content类型时添加）
            if (!aiMessageAdded && chunk.type === 'content') {
              conversation.messages.push(aiMessage);
              aiMessageAdded = true;
              console.log('✅ [前端处理] AI消息已添加到对话中');
            }
            
            if (chunk.type === 'content') {
              // 统一的流式内容处理 - 逐字符累积
              try {
                // 使用服务器推送的完整内容
                aiMessage.content = chunk.full_content || chunk.fullContent || '';
                
                // 如果有思考过程信息，也更新
                if (chunk.thinking_content && typeof chunk.thinking_content === 'string') {
                  aiMessage.thinking_process = chunk.thinking_content;
                  aiMessage.has_thinking = true;
                }
                
                // 标记当前是否处于思考阶段
                if (chunk.is_thinking !== undefined) {
                  aiMessage.is_thinking = chunk.is_thinking;
                }
                
                console.log('💬 [前端处理] 更新内容:', aiMessage.content.length + ' 字符');
              } catch (error) {
                console.warn('处理流式内容数据时出错:', error);
              }
            } else if (chunk.type === 'thinking') {
              // 单独处理思考过程数据（不添加消息）
              try {
                if (chunk.full_thinking) {
                  aiMessage.thinking_process = chunk.full_thinking;
                  aiMessage.has_thinking = true;
                  aiMessage.is_thinking = true;
                }
                console.log('🤔 [前端处理] 更新思考过程:', aiMessage.thinking_process.length + ' 字符');
              } catch (error) {
                console.warn('处理思考过程数据时出错:', error);
              }
            }
          }
        }
      )
      console.log("聊天API响应:", response)

      // 流式响应完成后，确保AI消息已添加并更新最终状态
      if (response.code === 200) {
        // 如果由于某种原因AI消息还没有添加（比如流式数据为空），现在添加
        if (!aiMessageAdded) {
          conversation.messages.push(aiMessage);
          aiMessageAdded = true;
          console.log('⚠️ [前端处理] 补充添加AI消息（流式响应为空）');
        }
        
        // 确保使用流式响应中收集的内容，而不是API返回的完整内容
        if (!aiMessage.content && response.data?.message) {
          // 如果流式响应没有收集到内容，使用API返回的内容作为备用
          aiMessage.content = response.data.message
          console.log('📝 [前端处理] 使用API返回的备用内容');
        }
        
        // 如果有思考过程数据，更新相关字段
        if (response.data?.thinking_process) {
          aiMessage.thinking_process = response.data.thinking_process
          aiMessage.has_thinking = true
        }

        // 更新预览和最后更新时间
        conversation.preview = aiMessage.content
        conversation.lastUpdated = new Date()
        conversation.message_count = (conversation.message_count || 0) + 1

        // 如果是新对话，可能需要更新对话ID（如果后端创建了新对话）
        if (response.data?.conversation_id && response.data.conversation_id !== conversation.id) {
          console.log("更新对话ID:", conversation.id, "->", response.data.conversation_id)
          conversation.id = response.data.conversation_id
          activeConversationId.value = response.data.conversation_id
        }
      } else {
        // 如果AI消息还没有添加到对话中，现在添加
        if (!aiMessageAdded) {
          conversation.messages.push(aiMessage);
          aiMessageAdded = true;
          console.log('❌ [前端处理] 错误情况下添加AI消息');
        }
        
        // 流式响应失败，更新消息内容为错误信息
        aiMessage.content = `抱歉，我遇到了一些问题。${response.message || '请稍后再试。'}`
        conversation.message_count = (conversation.message_count || 0) + 1
      }
    } catch (error) {
      console.error('聊天API调用失败:', error)
      
      // 如果AI消息还没有添加到对话中，现在添加
      if (!aiMessageAdded) {
        aiMessage.content = '抱歉，我遇到了网络问题。请检查您的网络连接并稍后再试。'
        conversation.messages.push(aiMessage)
        aiMessageAdded = true
      } else {
        // 如果已经添加了，更新内容
        aiMessage.content = '抱歉，我遇到了网络问题。请检查您的网络连接并稍后再试。'
      }
      
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
      
      // 检查是否为临时对话
      const conversation = conversations.find(c => c.id === id)
      
      if (conversation?.isTemporary) {
        // 临时对话不需要从服务器加载详情，直接跳转
        console.log("切换到临时对话，无需访问服务器:", id)
      } else {
        // 正式对话需要加载详情
        console.log("切换到正式对话，加载详情:", id)
        await loadConversationDetail(id)
      }
      
      // 检查对话是否有消息，决定布局
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