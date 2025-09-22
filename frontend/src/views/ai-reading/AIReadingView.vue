<template>
  <div class="ai-reading-view">
    <div class="page-header">
      <h1 class="page-title">AI 阅读</h1>
      <p class="page-description">智能文档阅读与理解功能</p>
    </div>
    
    <div class="content-container">
      <!-- 左侧：智能问答和文档上传 -->
      <div class="left-panel">
        <!-- 智能问答区域（移到上面） -->
        <div class="demo-card">
          <div class="card-header">
            <h2>智能问答</h2>
            <p>基于文档内容进行智能问答</p>
          </div>
          
          <div class="demo-content" v-if="selectedFile && currentFileId">
            <div class="qa-section">
              <div class="question-input">
                <label for="question">提出问题:</label>
                <input 
                  id="question"
                  type="text" 
                  v-model="question" 
                  placeholder="请输入您想了解的问题..."
                  @keyup.enter="askQuestion"
                >
                <button class="ask-btn" @click="askQuestion" :disabled="!question.trim() || answering">
                  <span v-if="answering">思考中...</span>
                  <span v-else>提问</span>
                </button>
              </div>
              
              <div class="qa-history" v-if="qaHistory.length > 0">
                <h5>问答历史</h5>
                <div class="qa-list">
                  <div v-for="(qa, index) in qaHistory" :key="index" class="qa-item">
                    <div class="question-item">
                      <strong>Q:</strong> {{ qa.question }}
                    </div>
                    <div class="answer-item">
                      <strong>A:</strong> {{ qa.answer }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="no-document" v-else>
            <p>请先上传文档并完成分析以启用智能问答功能</p>
          </div>
        </div>

        <!-- 文档上传与分析（合并） -->
        <div class="demo-card">
          <div class="card-header">
            <h2>文档上传与分析</h2>
            <p>上传文档，AI智能解析内容</p>
          </div>
          
          <div class="demo-content">
            <div class="upload-section">
              <div class="upload-area" :class="{ disabled: analyzing }" @dragover.prevent @drop.prevent="handleFileDrop">
                <input 
                  ref="fileInput" 
                  type="file" 
                  accept=".txt,.docx,.pdf,.xlsx,.epub,.mobi,.md,.csv,.json,.bmp,.png,.jpg,.jpeg,.gif" 
                  @change="handleFileSelect" 
                  style="display: none"
                  :disabled="analyzing"
                >
                
                <!-- 上传触发区域 -->
                <div class="upload-trigger" @click="triggerFileInput" :class="{ disabled: analyzing }">
                  <div class="upload-icon">📄</div>
                  <p v-if="!selectedFile">点击或拖拽文档到此处上传</p>
                  <p v-else class="selected-file">已选择文件: {{ selectedFile.name }}</p>
                </div>
                
                <!-- 文件信息和分析按钮合并显示 -->
                <div v-if="selectedFile" class="file-info-compact">
                  <div class="file-details">
                    <span class="file-name">{{ selectedFile.name }}</span>
                    <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
                  </div>
                  <div v-if="fileSizeError" class="error-message">
                    {{ fileSizeError }}
                  </div>
                  <button class="analyze-btn-compact" @click="analyzeDocument" :disabled="analyzing || !!fileSizeError">
                    <span v-if="analyzing">分析中...</span>
                    <span v-else>开始分析</span>
                  </button>
                </div>
                
                <div class="file-format-info">
                  <p><strong>支持格式：</strong>TXT, DOCX, PDF, XLSX, EPUB, MOBI, MD, CSV, JSON, BMP, PNG, JPG/JPEG, GIF</p>
                  <p><strong>文件大小：</strong>图片格式文件上限 18MB，其他格式文件上限 100MB</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧：文档历史、推荐问题和详细分析 -->
      <div class="right-panel">
        <!-- 文档历史 -->
        <div class="demo-card" v-if="documentHistory.length > 0">
          <div class="card-header">
            <h2>文档历史</h2>
            <p>您最近分析过的文档</p>
          </div>
          
          <div class="demo-content">
            <div class="document-history">
              <div 
                v-for="doc in documentHistory" 
                :key="doc.id" 
                class="history-item"
                :class="{ active: currentFileId === doc.file_object_id }"
                @click="loadDocument(doc)"
              >
                <div class="doc-info">
                  <div class="doc-name">{{ doc.name }}</div>
                  <div class="doc-meta">
                    <span class="doc-size">{{ formatFileSize(doc.size) }}</span>
                    <span class="doc-date">{{ formatDate(doc.created_at) }}</span>
                  </div>
                  <div v-if="doc.summary" class="doc-summary">{{ doc.summary.substring(0, 100) }}...</div>
                </div>
                <div class="doc-status">
                  <span v-if="doc.has_analysis" class="analyzed">已分析</span>
                  <span v-else class="pending">待分析</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 推荐问题 -->
        <div class="demo-card">
          <div class="card-header">
            <h2>推荐问题</h2>
            <p>基于文档内容的常见问题</p>
          </div>
          
          <div class="demo-content">
            <div v-if="suggestedQuestions.length > 0" class="questions-section">
              <div class="question-list">
                <button 
                  v-for="(q, index) in suggestedQuestions" 
                  :key="index"
                  class="question-btn"
                  @click="selectSuggestedQuestion(q)"
                  :disabled="answering"
                >
                  {{ q }}
                </button>
              </div>
            </div>
            
            <div v-else class="no-questions">
              <p>请先上传并分析文档以查看推荐问题</p>
            </div>
          </div>
        </div>

        <!-- 详细分析结果（移到推荐问题下面） -->
        <div class="demo-card" v-if="analysisResults">
          <div class="card-header">
            <h2>详细分析</h2>
            <p>文档的深度分析结果</p>
          </div>
          
          <div class="demo-content">
            <div class="analysis-results">
              <div class="result-tabs">
                <button 
                  v-for="tab in resultTabs" 
                  :key="tab.key"
                  class="tab-btn"
                  :class="{ active: activeTab === tab.key }"
                  @click="activeTab = tab.key"
                >
                  {{ tab.label }}
                </button>
              </div>
              
              <div class="tab-content">
                <div v-if="activeTab === 'conclusion'" class="conclusion-content">
                  <h5>总结</h5>
                  <p>{{ documentSummary?.summary }}</p>
                </div>
                
                <div v-if="activeTab === 'summary'" class="summary-content">
                  <h5>核心要点</h5>
                  <ul class="key-points-list">
                    <li v-for="point in documentSummary?.keyPoints" :key="point">{{ point }}</li>
                  </ul>
                </div>
                
                <div v-if="activeTab === 'keywords'" class="keywords-content">
                  <h5>关键词提取</h5>
                  <div class="keyword-tags">
                    <span v-for="keyword in analysisResults.keywords" :key="keyword" class="keyword-tag">
                      {{ keyword }}
                    </span>
                  </div>
                </div>
                
                <div v-if="activeTab === 'entities'" class="entities-content">
                  <h5>实体识别</h5>
                  <div class="entity-list">
                    <div v-for="entity in analysisResults.entities" :key="entity.text" class="entity-item">
                      <span class="entity-text">{{ entity.text }}</span>
                      <span class="entity-type">{{ entity.type }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// API基础配置
const API_BASE_URL = 'http://localhost:8000'

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const documentContent = ref('')
const analyzing = ref(false)
const analysisResults = ref<any>(null)
const activeTab = ref('conclusion') // 默认显示总结标签
const currentFileId = ref<string>('')
const fileSizeError = ref<string>('')

const question = ref('')
const answering = ref(false)
const qaHistory = ref<Array<{question: string, answer: string}>>([])

const documentSummary = ref<any>(null)
const suggestedQuestions = ref<string[]>([])
const documentHistory = ref<any[]>([])
const currentDocumentId = ref<string>('')

// 标签页顺序调整：总结放在第一位
const resultTabs = [
  { key: 'conclusion', label: '总结' },
  { key: 'summary', label: '摘要' },
  { key: 'keywords', label: '关键词' },
  { key: 'entities', label: '实体' }
]

// 文件大小限制检查
const checkFileSize = (file: File): string => {
  const isImage = file.type.startsWith('image/')
  const maxSize = isImage ? 18 * 1024 * 1024 : 100 * 1024 * 1024 // 18MB for images, 100MB for others
  
  if (file.size > maxSize) {
    const limit = isImage ? '18MB' : '100MB'
    return `文件大小超出限制，${isImage ? '图片' : '文档'}文件最大支持 ${limit}`
  }
  
  return ''
}

const triggerFileInput = () => {
  if (!analyzing.value) {
    fileInput.value?.click()
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    fileSizeError.value = checkFileSize(target.files[0])
    readFileContent(target.files[0])
  }
}

const handleFileDrop = (event: DragEvent) => {
  if (analyzing.value) return
  
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedFile.value = event.dataTransfer.files[0]
    fileSizeError.value = checkFileSize(event.dataTransfer.files[0])
    readFileContent(event.dataTransfer.files[0])
  }
}

const readFileContent = (file: File) => {
  if (file.type.startsWith('text/') || file.name.endsWith('.md')) {
    const reader = new FileReader()
    reader.onload = (e) => {
      documentContent.value = (e.target?.result as string)?.substring(0, 500) + '...'
    }
    reader.readAsText(file)
  } else {
    documentContent.value = `文档"${file.name}"已准备就绪，点击分析按钮开始AI智能分析。`
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 上传文件到服务器
const uploadFile = async (file: File): Promise<string> => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await fetch(`${API_BASE_URL}/api/v1/ai-reading/upload/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authStore.token}`
    },
    body: formData
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || '文件上传失败')
  }
  
  const result = await response.json()
  
  // 输出file_object.id到控制台
  console.log('=== 文件上传结果 ===')
  console.log('文件名:', file.name)
  console.log('文件大小:', formatFileSize(file.size))
  console.log('文件类型:', file.type)
  console.log('后端返回的file_object.id:', result.file_id)
  console.log('文档ID:', result.document_id)
  console.log('是否为新文档:', result.is_new)
  console.log('消息:', result.message)
  console.log('==================')
  
  // 保存文档ID
  currentDocumentId.value = result.document_id
  
  return result.file_id
}

const analyzeDocument = async () => {
  if (!selectedFile.value || fileSizeError.value) return
  
  analyzing.value = true
  
  try {
    console.log('=== 开始文档分析 ===')
    console.log('准备分析的文件:', selectedFile.value.name)
    
    // 1. 上传文件
    const fileId = await uploadFile(selectedFile.value)
    currentFileId.value = fileId
    
    console.log('文件上传成功，开始分析...')
    console.log('使用的file_id:', fileId)
    
    // 2. 分析文档
    const response = await fetch(`${API_BASE_URL}/api/v1/ai-reading/complete-analysis/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ file_id: fileId })
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '文档分析失败')
    }
    
    const result = await response.json()
    analysisResults.value = result.analysis
    
    console.log('文档分析完成！')
    console.log('分析结果:', result.analysis)
    console.log('消息:', result.message)
    console.log('==================')
    
    // 设置文档总结数据
    documentSummary.value = {
      keyPoints: result.analysis.keyPoints || [
        '文档主要内容概述',
        '关键信息提取',
        '重要观点总结'
      ],
      summary: result.analysis.summary
    }
    
    // 推荐问题只显示5个
    const allQuestions = result.analysis.suggestedQuestions || [
      '这份文档的主要内容是什么？',
      '文档中提到的关键概念有哪些？',
      '作者的主要观点是什么？',
      '文档的核心结论是什么？',
      '有哪些重要的数据或统计信息？'
    ]
    
    // 只显示前5个问题
    suggestedQuestions.value = allQuestions.slice(0, 5)
    
    // 加载历史问答记录
    await loadQAHistory()
    
    // 刷新文档历史
    await loadDocumentHistory()
    
  } catch (error: any) {
    console.error('分析失败:', error)
    alert(`分析失败: ${error.message}`)
  } finally {
    analyzing.value = false
  }
}

const askQuestion = async () => {
  if (!question.value.trim() || !currentFileId.value) return
  
  answering.value = true
  const currentQuestion = question.value
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai-reading/ask/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        file_id: currentFileId.value,
        question: currentQuestion
      })
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.error || '问答失败')
    }
    
    const result = await response.json()
    
    qaHistory.value.unshift({
      question: currentQuestion,
      answer: result.answer
    })
    
    question.value = ''
    
  } catch (error: any) {
    console.error('问答失败:', error)
    alert(`问答失败: ${error.message}`)
  } finally {
    answering.value = false
  }
}

const selectSuggestedQuestion = (selectedQuestion: string) => {
  question.value = selectedQuestion
  askQuestion()
}

// 加载问答历史
const loadQAHistory = async () => {
  if (!currentFileId.value) return
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai-reading/qa-history/?file_id=${currentFileId.value}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      qaHistory.value = result.history.map((item: any) => ({
        question: item.question,
        answer: item.answer,
        timestamp: new Date(item.timestamp)
      }))
      
      console.log('问答历史加载完成:', qaHistory.value.length, '条记录')
    }
  } catch (error) {
    console.error('加载问答历史失败:', error)
  }
}

// 获取文档历史
const loadDocumentHistory = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/ai-reading/history/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (response.ok) {
      const result = await response.json()
      documentHistory.value = result.documents || []
      console.log('文档历史加载完成:', documentHistory.value.length, '个文档')
    }
  } catch (error) {
    console.error('加载文档历史失败:', error)
  }
}

// 加载选中的文档
const loadDocument = async (doc: any) => {
  try {
    console.log('=== 加载历史文档 ===')
    console.log('文档名称:', doc.name)
    console.log('文档ID:', doc.id)
    console.log('file_object_id:', doc.file_object_id)
    
    currentFileId.value = doc.file_object_id
    currentDocumentId.value = doc.id
    
    // 如果文档已经有分析结果，直接加载
    if (doc.has_analysis) {
      const response = await fetch(`${API_BASE_URL}/api/v1/ai-reading/documents/?document_id=${doc.id}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${authStore.token}`
        }
      })
      
      if (response.ok) {
        const result = await response.json()
        const docData = result.documents[0]
        
        if (docData.analysis) {
          analysisResults.value = docData.analysis
          
          // 设置文档总结数据
          documentSummary.value = {
            keyPoints: docData.analysis.keyPoints || [],
            summary: docData.analysis.summary
          }
          
          // 设置推荐问题
          const allQuestions = docData.analysis.suggestedQuestions || []
          suggestedQuestions.value = allQuestions.slice(0, 5)
          
          console.log('历史文档分析结果加载完成')
        }
        
        // 加载问答历史
        await loadQAHistory()
      }
    }
    
    console.log('==================')
    
  } catch (error) {
    console.error('加载文档失败:', error)
  }
}

// 格式化日期
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) {
    return '今天'
  } else if (diffDays === 2) {
    return '昨天'
  } else if (diffDays <= 7) {
    return `${diffDays - 1}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

// 页面加载时检查是否有已选择的文件
const initializeFromStorage = async () => {
  // 加载文档历史
  await loadDocumentHistory()
  console.log('AI阅读页面初始化完成')
}

// 组件挂载时初始化
import { onMounted } from 'vue'
onMounted(() => {
  initializeFromStorage()
})
</script>

<style scoped>
.ai-reading-view {
  padding: 1rem;
  max-width: 1400px;
  margin: 0;
  margin-left: 1rem;
}

.page-header {
  margin-bottom: 2rem;
  text-align: center;
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #5e9bff 0%, #a569ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.page-description {
  font-size: 1.1rem;
  color: var(--color-text-secondary);
}

.content-container {
  display: grid;
  grid-template-columns: 1fr 500px;
  gap: 1.5rem;
}

.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.demo-card {
  background: var(--card-background);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
}

.card-header {
  margin-bottom: 2rem;
}

.card-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.card-header p {
  color: var(--color-text-secondary);
}

.demo-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.upload-area {
  border: 2px dashed var(--color-border);
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  transition: border-color 0.2s, background-color 0.2s;
}

.upload-area.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.upload-trigger {
  cursor: pointer;
  padding: 1rem;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.upload-trigger:hover:not(.disabled) {
  background-color: var(--color-primary-alpha);
}

.upload-trigger.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.upload-area:hover:not(.disabled) {
  border-color: var(--color-primary);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.file-info-compact {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--input-background);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.file-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-name {
  font-weight: 500;
  color: var(--color-text);
  flex: 1;
  text-align: left;
}

.file-size {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.analyze-btn-compact {
  background: linear-gradient(135deg, #5e9bff 0%, #a569ff 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  align-self: center;
}

.analyze-btn-compact:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(94, 155, 255, 0.3);
}

.analyze-btn-compact:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.file-format-info {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--input-background);
  border-radius: 8px;
  text-align: left;
}

.file-format-info p {
  margin: 0.5rem 0;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.error-message {
  color: #e74c3c;
  font-weight: 500;
  text-align: center;
}

.key-points-list {
  list-style: none;
  padding: 0;
}

.key-points-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}

.key-points-list li:before {
  content: "•";
  color: var(--color-primary);
  font-weight: bold;
  margin-right: 0.5rem;
}

.conclusion-content p {
  line-height: 1.6;
  color: var(--color-text);
}

.analysis-results {
  background: var(--input-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.result-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--color-border);
}

.tab-btn {
  background: none;
  border: none;
  padding: 0.75rem 1rem;
  cursor: pointer;
  color: var(--color-text-secondary);
  border-bottom: 2px solid transparent;
  transition: color 0.2s, border-color 0.2s;
}

.tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  padding-top: 1rem;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-tag {
  background: var(--color-primary-alpha);
  color: var(--color-primary);
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.9rem;
}

.entity-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.entity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: var(--card-background);
  border-radius: 4px;
}

.entity-type {
  background: var(--color-secondary);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
}

.question-input {
  display: flex;
  gap: 1rem;
  align-items: end;
  margin-bottom: 1.5rem;
}

.question-input label {
  display: block;
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.question-input input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--input-background);
  color: var(--color-text);
}

.ask-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  white-space: nowrap;
}

.ask-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.qa-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.qa-item {
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
}

.question-item {
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.answer-item {
  color: var(--color-text);
  line-height: 1.6;
}

.no-document, .no-questions {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.questions-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.question-btn {
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  text-align: left;
  cursor: pointer;
  color: var(--color-text);
  transition: background-color 0.2s, border-color 0.2s;
}

.question-btn:hover:not(:disabled) {
  background-color: var(--color-primary-alpha);
  border-color: var(--color-primary);
}

.question-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 1200px) {
  .content-container {
    grid-template-columns: 1fr 450px;
  }
}

@media (max-width: 1024px) {
  .content-container {
    grid-template-columns: 1fr;
  }
  
  .right-panel {
    order: -1;
  }
  
  .ai-reading-view {
    margin-left: 0.5rem;
  }
}

/* 文档历史样式 */
.document-history {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s, transform 0.2s;
}

.history-item:hover {
  background-color: var(--color-primary-alpha);
  border-color: var(--color-primary);
  transform: translateY(-1px);
}

.history-item.active {
  background-color: var(--color-primary-alpha);
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(94, 155, 255, 0.2);
}

.doc-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.doc-name {
  font-weight: 500;
  color: var(--color-text);
  font-size: 0.95rem;
}

.doc-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

.doc-summary {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.4;
  margin-top: 0.25rem;
}

.doc-status {
  display: flex;
  align-items: center;
}

.analyzed {
  background: #27ae60;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.pending {
  background: #f39c12;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

@media (max-width: 768px) {
  .ai-reading-view {
    padding: 0.5rem;
    margin-left: 0;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .demo-card {
    padding: 1.5rem;
  }
  
  .question-input {
    flex-direction: column;
    align-items: stretch;
  }
  
  .history-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .doc-status {
    align-self: flex-end;
  }
}
</style>