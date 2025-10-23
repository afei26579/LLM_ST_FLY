/**
 * 旅游助手聊天 Hook
 * 管理聊天状态、消息、用户偏好和行程数据
 */

import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

// 消息类型
interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  toolCalls?: any[]
  isStreaming?: boolean
}

// 用户偏好类型
interface UserPreferences {
  origin?: string // 起点
  destination?: string // 终点
  departureTime?: string // 出发时间
  duration?: string // 时长
  peopleCount?: string // 人数
  transportation?: string // 出行方式
  budget?: string // 预算
  notes?: string // 备注
  travelStyle?: string // 旅行风格（保留兼容）
}

// 行程数据类型
interface ItineraryData {
  destination?: string
  days?: number
  activities?: Array<{
    day: number
    time: string
    title: string
    description: string
    location?: string
    poi?: any
  }>
}

export function useTravelChat() {
  // 状态
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const currentCity = ref('')
  const threadId = ref(`travel_${Date.now()}`)
  const userPreferences = ref<UserPreferences>({})
  const itineraryData = ref<ItineraryData>({})

  // 计算属性
  const hasMessages = computed(() => messages.value.length > 0)
  const lastMessage = computed(() => messages.value[messages.value.length - 1])

  /**
   * 发送消息
   */
  const sendMessage = async (content: string, useStream = false) => {
    if (!content.trim()) return

    // 添加用户消息
    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }
    messages.value.push(userMessage)

    isLoading.value = true

    try {
      const token = localStorage.getItem('token')
      
      if (useStream) {
        await sendMessageStream(content, token)
      } else {
        await sendMessageNormal(content, token)
      }
    } catch (error: any) {
      console.error('发送消息失败:', error)
      
      // 添加错误消息
      const errorMessage: Message = {
        id: `msg_${Date.now()}`,
        role: 'system',
        content: `发送失败: ${error.message || '未知错误'}`,
        timestamp: new Date()
      }
      messages.value.push(errorMessage)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 普通模式发送消息
   */
  const sendMessageNormal = async (content: string, token: string | null) => {
    const response = await axios.post(
      `${API_BASE_URL}/agent/travel-assistant/chat/`,
      {
        message: content,
        thread_id: threadId.value,
        user_preferences: userPreferences.value,
        current_city: currentCity.value,
        stream: false
      },
      {
        headers: {
          Authorization: token ? `Bearer ${token}` : '',
          'Content-Type': 'application/json'
        }
      }
    )

    if (response.data.code === 200 && response.data.data) {
      const data = response.data.data

      // 添加AI响应
      const assistantMessage: Message = {
        id: `msg_${Date.now()}`,
        role: 'assistant',
        content: data.message || '',
        timestamp: new Date(),
        toolCalls: data.tool_calls || []
      }
      messages.value.push(assistantMessage)

      // 更新当前城市
      if (data.current_city) {
        currentCity.value = data.current_city
      }

      // 更新行程数据
      if (data.itinerary && data.itinerary.length > 0) {
        itineraryData.value = {
          destination: data.current_city,
          activities: data.itinerary
        }
      }
    } else {
      throw new Error(response.data.message || '请求失败')
    }
  }

  /**
   * 流式模式发送消息
   */
  const sendMessageStream = async (content: string, token: string | null) => {
    // 创建AI消息占位符
    const assistantMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    }
    messages.value.push(assistantMessage)

    const response = await fetch(`${API_BASE_URL}/agent/travel-assistant/chat/`, {
      method: 'POST',
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: content,
        thread_id: threadId.value,
        user_preferences: userPreferences.value,
        current_city: currentCity.value,
        stream: true
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('无法获取响应流')
    }

    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6).trim()

          if (data === '[DONE]') {
            assistantMessage.isStreaming = false
            break
          }

          try {
            const parsed = JSON.parse(data)

            if (parsed.type === 'message') {
              assistantMessage.content += parsed.content
            } else if (parsed.type === 'tool') {
              // 工具调用提示
              assistantMessage.content += '\n[正在调用工具...]'
            } else if (parsed.type === 'error') {
              throw new Error(parsed.content)
            }
          } catch (e) {
            console.warn('解析SSE数据失败:', e)
          }
        }
      }
    }

    assistantMessage.isStreaming = false
  }

  /**
   * 更新用户偏好
   */
  const updatePreferences = (prefs: Partial<UserPreferences>) => {
    userPreferences.value = { ...userPreferences.value, ...prefs }
  }

  /**
   * 设置当前城市
   */
  const setCurrentCity = (city: string) => {
    currentCity.value = city
  }

  /**
   * 清空聊天记录
   */
  const clearMessages = () => {
    messages.value = []
    threadId.value = `travel_${Date.now()}`
    currentCity.value = ''
    itineraryData.value = {}
  }

  /**
   * 加载对话历史
   */
  const loadHistory = async (historyThreadId: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(
        `${API_BASE_URL}/agent/travel-assistant/history/`,
        {
          params: { thread_id: historyThreadId },
          headers: {
            Authorization: token ? `Bearer ${token}` : ''
          }
        }
      )

      if (response.data.code === 200 && response.data.data) {
        const historyMessages = response.data.data.messages || []
        messages.value = historyMessages.map((msg: any, index: number) => ({
          id: `msg_${Date.now()}_${index}`,
          role: msg.role,
          content: msg.content,
          timestamp: new Date()
        }))
        threadId.value = historyThreadId
      }
    } catch (error) {
      console.error('加载历史失败:', error)
    }
  }

  /**
   * 导出行程
   */
  const exportItinerary = () => {
    if (!itineraryData.value.activities || itineraryData.value.activities.length === 0) {
      return
    }

    let text = `# ${itineraryData.value.destination || '旅游'}行程规划\n\n`
    
    const groupedByDay = itineraryData.value.activities.reduce((acc, activity) => {
      if (!acc[activity.day]) {
        acc[activity.day] = []
      }
      acc[activity.day].push(activity)
      return acc
    }, {} as Record<number, any[]>)

    Object.entries(groupedByDay).forEach(([day, activities]) => {
      text += `## 第${day}天\n\n`
      activities.forEach(activity => {
        text += `### ${activity.time} - ${activity.title}\n`
        text += `${activity.description}\n`
        if (activity.location) {
          text += `📍 ${activity.location}\n`
        }
        text += '\n'
      })
    })

    const blob = new Blob([text], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${itineraryData.value.destination || '旅游'}_行程.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  return {
    // 状态
    messages,
    isLoading,
    currentCity,
    threadId,
    userPreferences,
    itineraryData,

    // 计算属性
    hasMessages,
    lastMessage,

    // 方法
    sendMessage,
    updatePreferences,
    setCurrentCity,
    clearMessages,
    loadHistory,
    exportItinerary
  }
}

