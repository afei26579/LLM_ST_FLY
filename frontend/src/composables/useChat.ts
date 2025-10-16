import { ref, computed, reactive } from 'vue'
import { apiService } from '../services/api'
import type { Conversation, ChatMessage } from './useConversations'
// 打字机效果已改为实时同步模式，暂时保留导入以备将来使用
// import { createTypewriter, type TypewriterEffect } from '@/utils/typewriterEffect'

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
      sortConversations?: () => void
    }
  ) => {
    // 清理输入内容：trim首尾空格，并将多个连续换行符压缩为一个空格
    let content = userInput.value.trim()
    // 将多个连续的换行符（\n\n+）替换为单个空格，单个换行符也替换为空格
    content = content.replace(/\n+/g, ' ')
    // 清理多余的空格
    content = content.replace(/\s+/g, ' ')
    
    if (!content || isLoading.value) return

    try {
      const timestamp = new Date()
      let conversation: Conversation | undefined
      
      // 检查是否需要创建新对话（activeConversationId为null的情况）
      if (activeConversationId.value === null) {
        console.log("开始新对话，需要创建对话")
        
        // 使用用户输入的消息作为对话标题
        const title = content.length > 50 ? content.substring(0, 50) + '...' : content
        console.log("使用消息作为对话标题:", title)
        
        // 创建新对话
        const response = await apiService.createConversation(title)
        console.log("创建对话响应:", response)
        
        if (response.code === 201 && response.data && response.data.id) {
          const newConversationId = response.data.id
          
          // 创建新的对话对象
          const newConversation: Conversation = {
            id: newConversationId,
            title: title,
            messages: [],
            lastUpdated: timestamp,
            preview: content,
            message_count: 0,
            conversationType: 'ai-chat',
            isTemporary: false
          }
          
          // 添加到对话列表
          conversations.push(newConversation)  // 先添加到列表
          
          // 重新排序，确保置顶对话在最上方，新对话在非置顶对话的最上方
          if (options?.sortConversations) {
            options.sortConversations()
            console.log("已重新排序对话列表，置顶对话优先")
          }
          
          // 设置为活动对话
          activeConversationId.value = newConversationId
          conversation = newConversation
          
          console.log("新对话创建成功:", newConversationId, "标题:", title)
        } else {
          console.error('创建新对话失败:', response.message)
          return
        }
      } else {
        // 查找现有对话
        conversation = conversations.find(c => c.id === activeConversationId.value)
        
        if (!conversation) {
          console.error('无法找到活动对话，ID:', activeConversationId.value)
          return
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
      }

      // 发送第一条消息时，切换布局
      if (conversation.messages.length === 0) {
        isCenterLayout.value = false
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

    // 创建AI消息占位符用于流式更新（使用 reactive 确保响应式）
    const aiMessage: any = reactive({
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      thinking_process: '',
      has_thinking: false,
      is_thinking: false
    })

    // 🔧 修复：立即添加AI消息占位符到对话中，确保流式输出能够实时显示
    conversation.messages.push(aiMessage)
    console.log('✅ [前端处理] AI消息占位符已预先添加到对话中，准备接收流式数据')
    
    // 立即触发一次更新，让页面显示占位符
    onConversationUpdate(conversation)

    try {
      // 准备发送到API的消息历史（排除刚添加的空AI消息）
      const apiMessages = conversation.messages
        .filter(msg => !(msg.role === 'assistant' && msg.content === ''))
        .map(msg => ({
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
            
            if (chunk.type === 'content') {
              // 实时同步显示内容，直接更新不使用延迟
              try {
                // 获取本次块的新内容（增量内容）
                const newContent = chunk.content || '';
                
                if (newContent) {
                  // 直接累加内容，实时同步后端响应速度
                  // aiMessage 是 reactive 对象，修改会自动触发响应式更新
                  aiMessage.content += newContent;
                  console.log('⚡ [实时流式] 新增内容:', newContent.length + ' 字符, 总长度:', aiMessage.content.length);
                  
                  // 通知父组件更新（reactive 会自动追踪变化）
                  onConversationUpdate(conversation);
                }
                
                // 如果有思考过程信息，也更新
                if (chunk.thinking_content && typeof chunk.thinking_content === 'string') {
                  aiMessage.thinking_process = chunk.thinking_content;
                  aiMessage.has_thinking = true;
                  // 思考过程需要立即更新
                  onConversationUpdate(conversation);
                }
                
                // 标记当前是否处于思考阶段
                if (chunk.is_thinking !== undefined) {
                  aiMessage.is_thinking = chunk.is_thinking;
                }
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
            } else if (chunk.type === 'final') {
              // 处理最终结果，更新时间戳
              try {
                // 更新用户消息的时间戳（如果有）
                if (chunk.userMessageTimestamp && conversation.messages.length >= 2) {
                  const userMessage = conversation.messages[conversation.messages.length - 2]
                  if (userMessage && userMessage.role === 'user') {
                    userMessage.timestamp = new Date(chunk.userMessageTimestamp)
                    console.log('⏰ [前端处理] 更新用户消息时间戳:', chunk.userMessageTimestamp)
                  }
                }
                
                // 更新AI消息的时间戳（如果有）
                if (chunk.aiMessageTimestamp) {
                  aiMessage.timestamp = new Date(chunk.aiMessageTimestamp)
                  console.log('⏰ [前端处理] 更新AI消息时间戳:', chunk.aiMessageTimestamp)
                }
                
                // 触发Vue的响应式更新
                onConversationUpdate(conversation);
              } catch (error) {
                console.warn('处理最终结果数据时出错:', error);
              }
            }
          }
        }
      )
      console.log("聊天API响应:", response)

      // 流式响应完成后，更新最终状态
      if (response.code === 200) {
        // 🔧 关键修复：确保使用完整内容
        const fullContent = response.data?.message || ''
        console.log('📦 [前端处理] 流式响应完成，完整内容长度:', fullContent.length + ' 字符')
        
        // 检查当前内容长度
        const currentContentLength = aiMessage.content.length
        console.log('📦 [前端处理] 当前已显示内容长度:', currentContentLength + ' 字符')
        
        if (fullContent && currentContentLength < fullContent.length) {
          // 如果当前内容少于完整内容，说明有内容缺失（可能流式传输中断）
          const missingContent = fullContent.substring(currentContentLength)
          console.log('⚠️ [前端处理] 发现缺失内容:', missingContent.length + ' 字符，立即补充')
          
          // 直接补充缺失内容
          aiMessage.content = fullContent
          onConversationUpdate(conversation)
        } else if (currentContentLength === 0 && fullContent) {
          // 如果完全没有内容（可能流式响应完全失败），直接使用完整内容
          console.log('📝 [前端处理] 无流式内容，使用API返回的完整内容')
          aiMessage.content = fullContent
          onConversationUpdate(conversation)
        } else {
          // 内容完整
          console.log('✅ [前端处理] 内容完整，流式输出成功')
        }
        
        // 如果有思考过程数据，更新相关字段
        if (response.data?.thinking_process) {
          aiMessage.thinking_process = response.data.thinking_process
          aiMessage.has_thinking = true
        }

        // 使用完整内容更新预览
        conversation.preview = fullContent || aiMessage.content
        conversation.lastUpdated = new Date()
        conversation.message_count = (conversation.message_count || 0) + 1

        // 如果是新对话，可能需要更新对话ID（如果后端创建了新对话）
        if (response.data?.conversation_id && response.data.conversation_id !== conversation.id) {
          console.log("更新对话ID:", conversation.id, "->", response.data.conversation_id)
          conversation.id = response.data.conversation_id
          activeConversationId.value = response.data.conversation_id
        }
        
        // 流式响应完成，立即结束 loading
        console.log('✅ [前端处理] 流式响应完成，结束 loading')
        isLoading.value = false
      } else {
        // 流式响应失败，更新消息内容为错误信息（AI消息已预先添加）
        aiMessage.content = `抱歉，我遇到了一些问题。${response.message || '请稍后再试。'}`
        conversation.message_count = (conversation.message_count || 0) + 1
        
        // 错误情况下立即结束 loading
        isLoading.value = false
      }
    } catch (error) {
      console.error('聊天API调用失败:', error)
      
      // 设置错误消息内容（AI消息已预先添加）
      aiMessage.content = '抱歉，我遇到了网络问题。请检查您的网络连接并稍后再试。'
      
      conversation.message_count = (conversation.message_count || 0) + 1
      
      // 错误情况下立即结束 loading
      isLoading.value = false
    } finally {
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

  // 跳过打字机动画（已废弃，保留以兼容）
  const skipTypingAnimation = () => {
    // 由于已改为实时同步显示，此函数不再需要
    console.log('ℹ️ [流式输出] 已采用实时同步模式，无需跳过动画')
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
    jumpToQuestion,
    skipTypingAnimation
  }
}