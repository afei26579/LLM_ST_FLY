/**
 * 诗词绘画业务逻辑 Hook
 */
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'
import type {
  PoetryPaintingWork,
  CreateWorkRequest,
  CreateWorkResponse,
  IterateWorkRequest,
  PoetryStyleType,
  PoetryFormatType,
  PaintingStyleType,
  PoetryPaintingConversation
} from '../types'

export function usePoetryPainting() {
  const toast = useToast()

  // 状态
  const userInput = ref('')
  const poetryStyle = ref<PoetryStyleType | ''>('')  // 默认为智能选择
  const poetryFormat = ref<PoetryFormatType | ''>('')  // 默认为智能选择
  const paintingStyle = ref<PaintingStyleType | ''>('')  // 默认为智能选择
  const imageSize = ref('1328*1328')
  const isGenerating = ref(false)
  const currentStep = ref('')
  const currentWork = ref<CreateWorkResponse['result'] | null>(null)
  const currentWorkId = ref<number | null>(null)
  const workList = ref<PoetryPaintingWork[]>([])
  const conversationId = ref<number | null>(null)
  const conversations = ref<PoetryPaintingConversation[]>([])

  // 计算属性
  const hasCurrentWork = computed(() => !!currentWork.value)
  const canIterate = computed(() => currentWorkId.value !== null)

  /**
   * 创作作品（流式）
   */
  const createWork = async (input?: string) => {
    const inputText = input || userInput.value
    if (!inputText.trim()) {
      toast.warning('请输入创作主题')
      return
    }

    isGenerating.value = true
    currentStep.value = 'intent_recognizing'

    // 初始化临时作品对象
    const tempWork = {
      poetry: {
        title: '',
        content: '',
        style: '',
        format: '',
        theme: '',
        analysis: undefined
      },
      painting: {
        url: '',
        local_path: '',
        prompt: '',
        style: '',
        description: ''
      },
      metadata: {
        iteration: 1,
        current_step: ''
      }
    }

    try {
      const requestData = {
        input: inputText,
        poetry_style: poetryStyle.value || undefined,  // 空值不传递，由后端AI决定
        poetry_format: poetryFormat.value || undefined,
        painting_style: paintingStyle.value || undefined,
        image_size: imageSize.value,
        conversation_id: conversationId.value || undefined
      }

      const token = localStorage.getItem('token')
      const response = await fetch(
        `http://localhost:8000/api/v1/agent/poetry-painting/create-work-stream/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': token ? `Bearer ${token}` : '',
            'Accept': 'text/event-stream'
          },
          body: JSON.stringify(requestData)
        }
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
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
            try {
              const jsonStr = line.slice(6).trim()
              if (!jsonStr) continue

              const data = JSON.parse(jsonStr)

              // 处理不同类型的数据
              if (data.type === 'conversation_id') {
                conversationId.value = data.conversation_id
              }
              else if (data.type === 'step') {
                currentStep.value = data.step
              }
              else if (data.type === 'intent') {
                tempWork.poetry.theme = data.theme
                tempWork.poetry.style = data.poetry_style
                tempWork.painting.style = data.painting_style
                currentStep.value = 'intent_recognized'
              }
              else if (data.type === 'poetry') {
                tempWork.poetry.title = data.title
                tempWork.poetry.content = data.content
                tempWork.poetry.style = data.style
                tempWork.poetry.format = data.format
                currentWork.value = { ...tempWork }
                currentStep.value = 'poetry_created'
              }
              else if (data.type === 'analysis') {
                tempWork.poetry.analysis = data.analysis
                tempWork.painting.description = data.imagery_description
                currentWork.value = { ...tempWork }
                currentStep.value = 'poetry_analyzed'
              }
              else if (data.type === 'painting') {
                // 处理图片URL，优先使用本地路径
                let imageUrl = data.url
                
                // 如果有本地路径，构建完整URL
                if (data.local_path) {
                  imageUrl = `http://localhost:8000/media/${data.local_path}`
                } else if (imageUrl && !imageUrl.startsWith('http')) {
                  // 如果没有本地路径，处理远程URL
                  imageUrl = `http://localhost:8000${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`
                }
                
                console.log('图片URL:', imageUrl, 'local_path:', data.local_path)
                
                tempWork.painting.url = imageUrl
                tempWork.painting.local_path = data.local_path
                tempWork.painting.prompt = data.prompt
                currentWork.value = { ...tempWork }
                currentStep.value = 'painting_generated'
              }
              else if (data.type === 'complete') {
                currentWorkId.value = data.work_id
                conversationId.value = data.conversation_id
                currentStep.value = 'completed'
                toast.success('创作完成！')
              }
              else if (data.type === 'error') {
                throw new Error(data.message)
              }
            } catch (parseError) {
              console.warn('解析SSE数据失败:', parseError)
            }
          }
        }
      }

      // 刷新作品列表
      await loadWorks()

      // 清空输入
      userInput.value = ''

    } catch (error: any) {
      console.error('创作失败:', error)
      toast.error(error.message || '创作失败，请重试')
      throw error
    } finally {
      isGenerating.value = false
    }
  }

  /**
   * 迭代优化作品
   */
  const iterateWork = async (feedback: string, type: 'poetry' | 'painting' | 'both' = 'both') => {
    if (!currentWorkId.value) {
      toast.warning('没有可优化的作品')
      return
    }

    if (!feedback.trim()) {
      toast.warning('请输入优化建议')
      return
    }

    isGenerating.value = true
    currentStep.value = 'iterating'

    try {
      const requestData: IterateWorkRequest = {
        feedback,
        type
      }

      const response = await apiService.instance.post<CreateWorkResponse>(
        `/agent/poetry-painting/${currentWorkId.value}/iterate/`,
        requestData,
        {
          timeout: 60000 // 迭代优化也需要较长时间
        }
      )

      // 更新当前作品
      currentWork.value = response.result
      currentWorkId.value = response.work_id

      toast.success('优化完成！')

      // 刷新作品列表
      await loadWorks()

      return response
    } catch (error: any) {
      console.error('优化失败:', error)
      toast.error(error.response?.data?.message || '优化失败，请重试')
      throw error
    } finally {
      isGenerating.value = false
      currentStep.value = 'completed'
    }
  }

  /**
   * 加载作品列表
   */
  const loadWorks = async () => {
    try {
      const response = await apiService.instance.get(
        '/agent/poetry-painting/works/'
      )

      console.log('作品列表响应:', response)
      
      // 处理标准响应格式
      if (response.data && response.data.data && Array.isArray(response.data.data)) {
        workList.value = response.data.data
      } else if (response.data && Array.isArray(response.data)) {
        workList.value = response.data
      } else {
        workList.value = []
      }
      
      console.log('作品列表:', workList.value)
    } catch (error) {
      console.error('加载作品列表失败:', error)
      workList.value = []
    }
  }

  /**
   * 加载对话列表
   */
  const loadConversations = async () => {
    try {
      const response = await apiService.instance.get(
        '/agent/poetry-painting/conversations/'
      )

      console.log('对话列表响应:', response)
      
      // 处理响应数据
      if (response.data && Array.isArray(response.data)) {
        conversations.value = response.data
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        conversations.value = response.data.data
      } else {
        conversations.value = []
      }
      
      console.log('对话列表:', conversations.value)
    } catch (error) {
      console.error('加载对话列表失败:', error)
      conversations.value = []
    }
  }

  /**
   * 选择作品
   */
  const selectWork = (work: PoetryPaintingWork) => {
    currentWorkId.value = work.id
    
    // 处理图片URL
    let imageUrl = work.painting_url_full || work.painting_url
    if (work.painting_local_path) {
      imageUrl = `http://localhost:8000/media/${work.painting_local_path}`
    }
    
    currentWork.value = {
      poetry: {
        title: work.poetry_title,
        content: work.poetry_content,
        style: work.poetry_style,
        format: work.poetry_format,
        theme: work.poetry_theme,
        analysis: work.poetry_analysis || undefined
      },
      painting: {
        url: imageUrl,
        local_path: work.painting_local_path,
        prompt: work.painting_prompt,
        style: work.painting_style,
        description: work.poetry_analysis?.imagery_description || ''
      },
      metadata: {
        iteration: work.iteration_count,
        current_step: 'completed'
      }
    }
    conversationId.value = work.conversation
  }

  /**
   * 评分作品
   */
  const rateWork = async (workId: number, rating: number) => {
    try {
      await apiService.instance.post(
        `/agent/poetry-painting/${workId}/rate/`,
        { rating }
      )

      toast.success('评分成功')

      // 更新作品列表中的评分
      const work = workList.value.find(w => w.id === workId)
      if (work) {
        work.user_rating = rating
      }
    } catch (error: any) {
      console.error('评分失败:', error)
      toast.error(error.response?.data?.message || '评分失败')
    }
  }

  /**
   * 下载图片
   */
  const downloadImage = (url: string, filename: string) => {
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.target = '_blank'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  /**
   * 新建对话
   */
  const newConversation = () => {
    conversationId.value = null
    currentWork.value = null
    currentWorkId.value = null
    userInput.value = ''
  }

  // 组件挂载时加载数据
  onMounted(() => {
    loadWorks()  // 只加载作品列表
  })

  return {
    // 状态
    userInput,
    poetryStyle,
    poetryFormat,
    paintingStyle,
    imageSize,
    isGenerating,
    currentStep,
    currentWork,
    currentWorkId,
    workList,
    conversationId,
    conversations,

    // 计算属性
    hasCurrentWork,
    canIterate,

    // 方法
    createWork,
    iterateWork,
    loadWorks,
    loadConversations,
    selectWork,
    rateWork,
    downloadImage,
    newConversation
  }
}

