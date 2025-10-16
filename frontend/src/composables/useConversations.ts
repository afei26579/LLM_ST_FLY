import { ref, reactive, computed } from 'vue'
import { apiService } from '../services/api'
import type { ChatMessage as ApiChatMessage } from '../services/api'

// 聊天消息类型
export interface ChatMessage extends ApiChatMessage {
  timestamp?: Date
  type?: 'text' | 'image' | 'file' | 'system'
}

// 对话类型
export interface Conversation {
  id: number
  title: string
  custom_title?: string  // 自定义标题
  display_title?: string  // 显示标题（优先显示custom_title）
  messages: ChatMessage[]
  lastUpdated: Date
  preview: string
  message_count: number
  user_question_count?: number
  first_user_question?: string
  last_message?: ChatMessage
  isTemporary?: boolean
  conversationType?: 'default' | 'ai-chat'
  
  // 置顶功能
  is_pinned?: boolean
  pinned_at?: string
  isPinned?: boolean  // 兼容前端命名
  created_at?: string
  updated_at?: string
}

// 返回类型定义
export interface UseConversationsReturn {
  // 状态
  conversations: Conversation[]
  isLoadingConversations: boolean
  expandedConversations: Set<number>
  loadingHistoryConversations: Set<number>
  
  // 方法
  getFilteredConversations: (searchQuery: string) => Conversation[]
  createNewConversation: (conversationType?: 'default' | 'ai-chat') => Promise<Conversation | null>
  loadConversationDetail: (conversationId: number) => Promise<void>
  loadConversationsFromServer: () => Promise<void>
  deleteConversation: (id: number) => Promise<boolean>
  clearConversationMessages: (id: number) => Promise<boolean>
  toggleConversationExpand: (id: number) => Promise<void>
  isConversationExpanded: (id: number) => boolean
  isHistoryLoading: (id: number) => boolean
  getUserQuestions: (conversation: Conversation) => Array<{content: string, timestamp?: Date, index: number}>
  pinConversation: (id: number) => Promise<boolean>
  sortConversations: () => void
  
  // 缓存管理方法
  saveTempConversationToCache: (conversation: Conversation) => void
  loadTempConversationFromCache: () => Conversation | null
  removeTempConversationFromCache: () => void
}

/**
 * 对话管理组合式函数
 */
export function useConversations(): UseConversationsReturn {
  // 状态
  const conversations = reactive<Conversation[]>([])
  const isLoadingConversations = ref(false)
  const expandedConversations = ref<Set<number>>(new Set())
  const loadingHistoryConversations = ref<Set<number>>(new Set())

  // 临时对话缓存键名
  const TEMP_CONVERSATION_KEY = 'temp_conversation'

  /**
   * 保存临时对话到缓存
   */
  const saveTempConversationToCache = (conversation: Conversation) => {
    try {
      localStorage.setItem(TEMP_CONVERSATION_KEY, JSON.stringify({
        ...conversation,
        lastUpdated: conversation.lastUpdated.toISOString()
      }))
      console.log('临时对话已保存到缓存:', conversation.id)
    } catch (error) {
      console.error('保存临时对话到缓存失败:', error)
    }
  }

  /**
   * 从缓存加载临时对话
   */
  const loadTempConversationFromCache = (): Conversation | null => {
    try {
      const cached = localStorage.getItem(TEMP_CONVERSATION_KEY)
      if (!cached) return null

      const data = JSON.parse(cached)
      const conversation: Conversation = {
        ...data,
        lastUpdated: new Date(data.lastUpdated)
      }
      console.log('从缓存加载临时对话:', conversation.id)
      return conversation
    } catch (error) {
      console.error('从缓存加载临时对话失败:', error)
      return null
    }
  }

  /**
   * 删除缓存中的临时对话
   */
  const removeTempConversationFromCache = () => {
    try {
      localStorage.removeItem(TEMP_CONVERSATION_KEY)
      console.log('已删除缓存中的临时对话')
    } catch (error) {
      console.error('删除缓存中的临时对话失败:', error)
    }
  }

  // 计算属性
  const getFilteredConversations = (searchQuery: string, conversationType?: 'default' | 'ai-chat') => {
    // 如果没有搜索词且没有指定对话类型，返回所有对话（保持后端返回的置顶排序）
    if (!searchQuery.trim() && !conversationType) {
      return conversations.slice()  // 移除排序，保持后端返回的顺序
    }
    
    const query = searchQuery.toLowerCase()
    return conversations
      .filter(conversation => {
        // 如果指定了对话类型，先过滤类型
        if (conversationType && conversation.conversationType !== conversationType) {
          return false
        }
        
        // 搜索标题
        if (conversation.title.toLowerCase().includes(query)) return true
        
        // 搜索消息内容
        return conversation.messages.some(message => 
          message.content.toLowerCase().includes(query)
        )
      })
      .sort((a, b) => {
        // 搜索结果也按置顶优先排序
        const aPinned = a.is_pinned || a.isPinned || false
        const bPinned = b.is_pinned || b.isPinned || false
        
        if (aPinned && !bPinned) return -1
        if (!aPinned && bPinned) return 1
        
        // 都置顶时，按置顶时间降序
        if (aPinned && bPinned) {
          const timeA = new Date(a.pinned_at || 0).getTime()
          const timeB = new Date(b.pinned_at || 0).getTime()
          return timeB - timeA
        }
        
        // 都不置顶时，按更新时间降序
        const updateA = new Date(a.updated_at || a.lastUpdated || 0).getTime()
        const updateB = new Date(b.updated_at || b.lastUpdated || 0).getTime()
        return updateB - updateA
      })
  }

  /**
   * 创建新对话
   * 首先检查缓存中是否有临时对话，如果有则使用缓存的，否则创建新的
   */
  const createNewConversation = async (conversationType: 'default' | 'ai-chat' = 'default'): Promise<Conversation | null> => {
    try {
      console.log(`开始创建新对话（${conversationType}）`)
      
      // 首先检查缓存中是否有临时对话
      const cachedTempConversation = loadTempConversationFromCache()
      if (cachedTempConversation) {
        console.log("发现缓存中的临时对话，使用缓存的对话:", cachedTempConversation.id)
        
        // 检查是否已经在对话列表中
        const existingConv = conversations.find(c => c.id === cachedTempConversation.id)
        if (!existingConv) {
          conversations.push(cachedTempConversation)
        }
        
        return cachedTempConversation
      }
      
      // 生成临时ID（负数，避免与后端ID冲突）
      const tempId = -Date.now()
      
      // 创建新对话（仅前端）
      const newConversation: Conversation = {
        id: tempId,
        title: conversationType === 'ai-chat' ? '新AI对话' : '新对话',
        messages: [],
        lastUpdated: new Date(),
        preview: conversationType === 'ai-chat' ? '开始一个新的AI对话' : '开始一个新的对话',
        message_count: 0,
        last_message: undefined,
        isTemporary: true,
        conversationType: conversationType
      }
      
      console.log("创建新的临时对话:", newConversation)
      
      // 添加到对话列表
      conversations.push(newConversation)
      
      // 保存到缓存
      saveTempConversationToCache(newConversation)
      
      return newConversation
    } catch (error) {
      console.error('创建对话出现异常:', error)
      return null
    }
  }

  // 加载对话详情
  const loadConversationDetail = async (conversationId: number) => {
    try {
      if (!conversationId) {
        console.error("无效的对话ID:", conversationId)
        return
      }
      
      console.log("开始加载对话详情:", conversationId)
      const response = await apiService.getConversation(conversationId)
      console.log("获取对话详情响应:", response)
      
      if (response.code === 200 && response.data) {
        const conv = response.data
        
        // 查找并更新本地对话
        const localConv = conversations.find(c => c.id === conv.id)
        if (localConv) {
          // 确保messages是数组
          if (Array.isArray(conv.messages)) {
            localConv.messages = conv.messages.map(msg => ({
              ...msg,
              // 后端返回的是created_at，需要映射到timestamp
              timestamp: msg.created_at ? new Date(msg.created_at) : (msg.timestamp ? new Date(msg.timestamp) : new Date())
            }))
          } else {
            localConv.messages = []
            console.warn("返回的messages不是数组:", conv.messages)
          }
          
          localConv.title = conv.title || '未命名对话'
          localConv.custom_title = conv.custom_title  // 更新自定义标题
          localConv.display_title = conv.display_title  // 更新显示标题
          localConv.message_count = conv.message_count || 0
          
          // 更新预览为第一个用户问题
          const firstUserMessage = localConv.messages.find(msg => msg.role === 'user')
          if (firstUserMessage) {
            localConv.preview = firstUserMessage.content.length > 50 
              ? firstUserMessage.content.substring(0, 50) + '...'
              : firstUserMessage.content
          }
          
          console.log("更新本地对话成功:", conv.id, "消息数量:", localConv.messages.length)
        } else {
          console.error("找不到对应的本地对话:", conv.id, "当前对话列表:", conversations)
          
          // 如果找不到对话，添加到本地列表
          const messages = Array.isArray(conv.messages) ? conv.messages.map(msg => ({
            ...msg,
            // 后端返回的是created_at，需要映射到timestamp
            timestamp: msg.created_at ? new Date(msg.created_at) : (msg.timestamp ? new Date(msg.timestamp) : new Date())
          })) : []
          
          // 获取第一个用户问题作为预览
          const firstUserMessage = messages.find(msg => msg.role === 'user')
          const preview = firstUserMessage 
            ? (firstUserMessage.content.length > 50 
                ? firstUserMessage.content.substring(0, 50) + '...'
                : firstUserMessage.content)
            : (conv.last_message?.content || '空对话')
          
          const newConv = {
            id: conv.id,
            title: conv.title || '未命名对话',
            messages: messages,
            lastUpdated: new Date(conv.updated_at || new Date()),
            preview: preview,
            message_count: conv.message_count || 0,
            last_message: conv.last_message
          }
          
          conversations.push(newConv)
          console.log("添加新对话到本地列表:", newConv)
        }
      } else {
        console.error('加载对话详情失败:', response.message, response)
      }
    } catch (error) {
      console.error('加载对话详情失败:', error)
    }
  }

  // 从服务器加载对话历史
  const loadConversationsFromServer = async (conversationType?: 'default' | 'ai-chat') => {
    isLoadingConversations.value = true
    
    try {
      console.log(`开始从服务器加载${conversationType ? conversationType : '所有'}对话历史`)
      const response = await apiService.getConversations(conversationType)
      console.log("获取对话列表响应:", response)
      
      if (response.code === 200 && response.data) {
        // 根据后端标准化响应格式获取数据
        const conversationsData = response.data.list || [];
        console.log('获取到的对话数据:', conversationsData);
        console.log('总数:', response.data?.total);
        
        // 转换API返回的对话格式为UI需要的格式
        const serverConversations = conversationsData.map((conv: any) => {
          console.log("处理对话:", conv)
          
          // 优先使用后端返回的第一个用户问题作为预览
          let preview = '空对话'
          if (conv.first_user_question) {
            preview = conv.first_user_question
          } else if (conv.messages && Array.isArray(conv.messages) && conv.messages.length > 0) {
            // 如果有消息数组，尝试从中获取第一个用户问题
            const firstUserMessage = conv.messages.find((msg: any) => msg.role === 'user')
            if (firstUserMessage) {
              preview = firstUserMessage.content.length > 50 
                ? firstUserMessage.content.substring(0, 50) + '...'
                : firstUserMessage.content
            } else {
              preview = conv.last_message_preview || conv.last_message?.content || '空对话'
            }
          } else {
            // 使用后端返回的预览字段
            preview = conv.last_message_preview || conv.last_message?.content || '空对话'
          }
          
          return {
            id: conv.id,
            title: conv.title || '未命名对话',
            custom_title: conv.custom_title,  // 自定义标题
            display_title: conv.display_title,  // 显示标题（后端已计算好优先级）
            messages: conv.messages || [],
            lastUpdated: new Date(conv.updated_at || new Date()),
            preview: preview,
            message_count: conv.message_count || 0,
            user_question_count: conv.user_question_count || 0,
            first_user_question: conv.first_user_question || '',
            last_message: conv.last_message,
            conversationType: conv.conversation_type || 'default',
            // 置顶相关字段
            is_pinned: conv.is_pinned || false,
            isPinned: conv.is_pinned || false,
            pinned_at: conv.pinned_at,
            created_at: conv.created_at,
            updated_at: conv.updated_at
          }
        })
        
        console.log("转换后的对话列表:", serverConversations)
        
        // 清空并添加新的对话
        // 注意：后端已经返回了正确的排序（置顶优先），所以这里不需要再次排序
        conversations.splice(0, conversations.length, ...serverConversations)
        
        console.log("对话列表更新完成，当前对话数量:", conversations.length)
      } else {
        console.error('加载对话失败:', response.message, response)
      }
    } catch (error) {
      console.error('加载对话出错:', error)
    } finally {
      isLoadingConversations.value = false
      console.log("对话加载完成，对话列表:", conversations)
    }
  }

  // 删除对话
  const deleteConversation = async (id: number) => {
    try {
      const response = await apiService.deleteConversation(id)
      
      if (response.code === 200) {
        // 从本地列表中删除
        const index = conversations.findIndex(c => c.id === id)
        if (index !== -1) {
          conversations.splice(index, 1)
        }
        return true
      } else {
        console.error('删除对话失败:', response.message)
        return false
      }
    } catch (error) {
      console.error('删除对话失败:', error)
      return false
    }
  }

  // 清空对话消息
  const clearConversationMessages = async (id: number) => {
    try {
      const response = await apiService.clearConversationMessages(id)
      
      if (response.code === 200) {
        // 清空本地消息
        const conversation = conversations.find(c => c.id === id)
        if (conversation) {
          conversation.messages = []
          conversation.message_count = 0
          conversation.preview = '对话已清空'
        }
        return true
      } else {
        console.error('清空对话消息失败:', response.message)
        return false
      }
    } catch (error) {
      console.error('清空对话消息失败:', error)
      return false
    }
  }

  // 切换对话展开状态
  const toggleConversationExpand = async (id: number) => {
    if (expandedConversations.value.has(id)) {
      expandedConversations.value.delete(id)
    } else {
      expandedConversations.value.add(id)
      
      // 查找当前对话
      const conversation = conversations.find(c => c.id === id)
      if (conversation && (!conversation.messages || conversation.messages.length === 0) && conversation.message_count > 0) {
        // 需要加载对话历史
        loadingHistoryConversations.value.add(id)
        await loadConversationDetail(id)
        loadingHistoryConversations.value.delete(id)
      }
    }
  }

  // 检查对话是否展开
  const isConversationExpanded = (id: number) => {
    return expandedConversations.value.has(id)
  }

  // 检查对话历史是否正在加载
  const isHistoryLoading = (id: number) => {
    return loadingHistoryConversations.value.has(id)
  }

  // 获取用户问题列表
  const getUserQuestions = (conversation: Conversation) => {
    if (!conversation.messages || conversation.messages.length === 0) return []
    
    return conversation.messages
      .filter(message => message.role === 'user')
      .map((message, index) => ({
        content: message.content,
        timestamp: message.timestamp,
        index: index // 保存消息在对话中的位置，用于后续定位
      }))
  }

  /**
   * 对话列表排序（置顶优先）
   */
  const sortConversations = () => {
    // 创建排序后的新数组
    const sorted = [...conversations].sort((a, b) => {
      // 1. 置顶对话优先
      const aPinned = a.is_pinned || a.isPinned || false
      const bPinned = b.is_pinned || b.isPinned || false
      
      if (aPinned && !bPinned) return -1
      if (!aPinned && bPinned) return 1
      
      // 2. 都置顶时，按置顶时间降序
      if (aPinned && bPinned) {
        const timeA = new Date(a.pinned_at || 0).getTime()
        const timeB = new Date(b.pinned_at || 0).getTime()
        return timeB - timeA
      }
      
      // 3. 都不置顶时，按更新时间降序
      const updateA = new Date(a.updated_at || a.lastUpdated || 0).getTime()
      const updateB = new Date(b.updated_at || b.lastUpdated || 0).getTime()
      return updateB - updateA
    })
    
    // 使用 splice 替换数组内容以触发响应式更新
    conversations.splice(0, conversations.length, ...sorted)
  }

  /**
   * 置顶/取消置顶对话
   */
  const pinConversation = async (id: number): Promise<boolean> => {
    try {
      const response = await apiService.pinConversation(id)
      
      if (response.code === 200 || response.code === 201) {
        // 更新本地状态
        const conversation = conversations.find(c => c.id === id)
        if (conversation && response.data) {
          conversation.is_pinned = response.data.is_pinned
          conversation.isPinned = response.data.is_pinned
          conversation.pinned_at = response.data.pinned_at
          
          // 重新排序对话列表
          sortConversations()
        }
        
        console.log('置顶操作成功:', response.message)
        return true
      } else {
        console.error('置顶操作失败:', response.message)
        return false
      }
    } catch (error) {
      console.error('置顶对话失败:', error)
      return false
    }
  }

  return {
    // 状态
    conversations,
    isLoadingConversations,
    expandedConversations,
    loadingHistoryConversations,
    
    // 方法
    getFilteredConversations,
    createNewConversation,
    loadConversationDetail,
    loadConversationsFromServer,
    deleteConversation,
    clearConversationMessages,
    toggleConversationExpand,
    isConversationExpanded,
    isHistoryLoading,
    getUserQuestions,
    pinConversation,
    sortConversations,
    
    // 缓存管理方法
    saveTempConversationToCache,
    loadTempConversationFromCache,
    removeTempConversationFromCache
  }
}