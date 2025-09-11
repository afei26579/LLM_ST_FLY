<template>
  <div class="ai-reading-view">
    <div class="page-header">
      <h1 class="page-title">AI 阅读</h1>
      <p class="page-description">智能文档阅读与理解功能</p>
    </div>
    
    <div class="content-container">
      <div class="demo-card">
        <div class="card-header">
          <h2>文档上传与解析</h2>
          <p>上传文档，AI智能解析内容</p>
        </div>
        
        <div class="demo-content">
          <div class="upload-section">
            <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleFileDrop">
              <input 
                ref="fileInput" 
                type="file" 
                accept=".pdf,.doc,.docx,.txt,.md" 
                @change="handleFileSelect" 
                style="display: none"
              >
              <div class="upload-icon">📄</div>
              <p v-if="!selectedFile">点击或拖拽文档到此处上传</p>
              <p v-else class="selected-file">已选择文件: {{ selectedFile.name }}</p>
              <small>支持 PDF, DOC, DOCX, TXT, MD 格式</small>
            </div>
          </div>
          
          <div class="document-preview" v-if="selectedFile">
            <h4>文档预览</h4>
            <div class="preview-content">
              <div class="document-info">
                <p><strong>文件名:</strong> {{ selectedFile.name }}</p>
                <p><strong>文件大小:</strong> {{ formatFileSize(selectedFile.size) }}</p>
                <p><strong>文件类型:</strong> {{ selectedFile.type || '未知' }}</p>
              </div>
              
              <div class="preview-text" v-if="documentContent">
                <h5>文档内容预览:</h5>
                <div class="content-text">{{ documentContent }}</div>
              </div>
              
              <button class="analyze-btn" @click="analyzeDocument" :disabled="analyzing">
                <span v-if="analyzing">分析中...</span>
                <span v-else>开始分析</span>
              </button>
            </div>
          </div>
          
          <div class="analysis-results" v-if="analysisResults">
            <h4>分析结果</h4>
            
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
              <div v-if="activeTab === 'summary'" class="summary-content">
                <h5>文档摘要</h5>
                <p>{{ analysisResults.summary }}</p>
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
              
              <div v-if="activeTab === 'sentiment'" class="sentiment-content">
                <h5>情感分析</h5>
                <div class="sentiment-result">
                  <div class="sentiment-score">
                    <span class="score-label">情感倾向:</span>
                    <span class="score-value" :class="analysisResults.sentiment.type">
                      {{ analysisResults.sentiment.label }}
                    </span>
                  </div>
                  <div class="confidence-score">
                    <span class="score-label">置信度:</span>
                    <span class="score-value">{{ analysisResults.sentiment.confidence }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="demo-card">
        <div class="card-header">
          <h2>智能问答</h2>
          <p>基于文档内容进行智能问答</p>
        </div>
        
        <div class="demo-content" v-if="selectedFile">
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
          <p>请先上传文档以启用智能问答功能</p>
        </div>
      </div>
      
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">📖</div>
          <h3>文档解析</h3>
          <p>智能解析各种格式的文档内容</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🔍</div>
          <h3>内容分析</h3>
          <p>深度分析文档结构和关键信息</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">💬</div>
          <h3>智能问答</h3>
          <p>基于文档内容的智能问答系统</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>数据提取</h3>
          <p>自动提取关键数据和信息</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const documentContent = ref('')
const analyzing = ref(false)
const analysisResults = ref<any>(null)
const activeTab = ref('summary')

const question = ref('')
const answering = ref(false)
const qaHistory = ref<Array<{question: string, answer: string}>>([])

const resultTabs = [
  { key: 'summary', label: '摘要' },
  { key: 'keywords', label: '关键词' },
  { key: 'entities', label: '实体' },
  { key: 'sentiment', label: '情感' }
]

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedFile.value = target.files[0]
    readFileContent(target.files[0])
  }
}

const handleFileDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedFile.value = event.dataTransfer.files[0]
    readFileContent(event.dataTransfer.files[0])
  }
}

const readFileContent = (file: File) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    // 模拟文档内容
    documentContent.value = `这是文档"${file.name}"的内容预览。在实际应用中，这里会显示解析后的文档内容。AI阅读系统可以处理各种格式的文档，包括PDF、Word文档、文本文件等，并提供智能分析和问答功能。`
  }
  reader.readAsText(file)
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const analyzeDocument = () => {
  analyzing.value = true
  
  setTimeout(() => {
    analysisResults.value = {
      summary: '这份文档主要讨论了人工智能在现代社会中的应用和发展趋势。文档详细介绍了AI技术的核心概念、应用场景以及未来发展方向，为读者提供了全面的AI知识概览。',
      keywords: ['人工智能', '机器学习', '深度学习', '自然语言处理', '计算机视觉', '数据分析'],
      entities: [
        { text: '人工智能', type: '技术概念' },
        { text: 'OpenAI', type: '组织机构' },
        { text: 'GPT', type: '技术产品' },
        { text: '2023年', type: '时间' }
      ],
      sentiment: {
        type: 'positive',
        label: '积极',
        confidence: 85
      }
    }
    analyzing.value = false
  }, 2000)
}

const askQuestion = () => {
  if (!question.value.trim()) return
  
  answering.value = true
  const currentQuestion = question.value
  
  setTimeout(() => {
    const answer = `基于文档内容，关于"${currentQuestion}"的回答是：这是一个很好的问题。根据文档分析，AI技术正在快速发展，并在各个领域展现出巨大的潜力。具体来说，文档中提到了相关的技术应用和发展趋势。`
    
    qaHistory.value.unshift({
      question: currentQuestion,
      answer: answer
    })
    
    question.value = ''
    answering.value = false
  }, 1500)
}
</script>

<style scoped>
.ai-reading-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
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
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background-color 0.2s;
}

.upload-area:hover {
  border-color: var(--color-primary);
  background-color: var(--color-primary-alpha);
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.document-preview {
  background: var(--input-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.document-info {
  margin-bottom: 1rem;
}

.document-info p {
  margin: 0.5rem 0;
  color: var(--color-text);
}

.preview-text {
  margin: 1rem 0;
}

.content-text {
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  max-height: 200px;
  overflow-y: auto;
  line-height: 1.6;
  color: var(--color-text);
}

.analyze-btn {
  background: linear-gradient(135deg, #5e9bff 0%, #a569ff 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(94, 155, 255, 0.3);
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.sentiment-result {
  display: flex;
  gap: 2rem;
}

.sentiment-score, .confidence-score {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-value.positive {
  color: #27ae60;
}

.score-value.negative {
  color: #e74c3c;
}

.score-value.neutral {
  color: #f39c12;
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

.no-document {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.feature-card {
  background: var(--card-background);
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: var(--color-text-secondary);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .ai-reading-view {
    padding: 1rem;
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
  
  .sentiment-result {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>