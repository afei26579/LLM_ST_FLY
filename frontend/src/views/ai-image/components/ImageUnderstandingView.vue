<template>
  <div class="image-understanding-view">
    <div class="page-header">
      <button class="back-btn" @click="$emit('goBack')">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m12 19-7-7 7-7"></path>
          <path d="M19 12H5"></path>
        </svg>
        返回
      </button>
      <h1 class="page-title">AI 图像理解</h1>
    </div>
    
    <div class="content-container">
      <!-- 功能选项卡 -->
      <div class="understanding-tabs">
        <button 
          v-for="tab in tabs" 
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="switchTab(tab.key)"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>
      
      <!-- 功能内容区 -->
      <div class="understanding-content">
        <!-- 1. 图像描述 -->
        <div v-if="activeTab === 'description'" class="understanding-section">
          
          <div class="understanding-panel">
            <div class="upload-panel">
              <div class="upload-area" @click="triggerUpload('description')">
                <input 
                  ref="descriptionInput" 
                  type="file" 
                  accept="image/*" 
                  @change="handleImageSelect('description', $event)" 
                  style="display: none"
                >
                <div v-if="!descriptionImage" class="upload-placeholder">
                  <div class="upload-icon">🖼️</div>
                  <p>点击上传图片</p>
                  <small>支持 JPG, PNG, GIF, WebP</small>
                </div>
                <div v-else class="uploaded-preview">
                  <img :src="descriptionImagePreview" alt="上传图片" />
                  <button class="remove-btn" @click.stop="clearImage('description')">×</button>
                </div>
              </div>
              
              <button 
                class="analyze-btn" 
                @click="analyzeDescription" 
                :disabled="!descriptionImage || processing"
              >
                <span v-if="processing">分析中...</span>
                <span v-else>🔍 开始分析</span>
              </button>
            </div>
            
            <div class="result-panel">
              <!-- 处理中动画 -->
              <div v-if="processing" class="processing-state">
                <div class="loading-spinner"></div>
                <p>AI 分析中...</p>
              </div>
              
              <!-- 分析结果 -->
              <div v-else-if="analysisResult" class="result-display">
                <h3>分析结果</h3>
                <div class="result-content">
                  <div class="result-section">
                   
                    <div class="formatted-description" v-html="formatDescription(analysisResult.description)"></div>
                  </div>
                  
                  <div v-if="analysisResult.tags && analysisResult.tags.length > 0" class="result-section">
                    <h4>🏷️ 分类标签</h4>
                    <div class="tags-container">
                      <span v-for="tag in analysisResult.tags" :key="tag" class="tag">{{ tag }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 空状态 -->
              <div v-else class="empty-result">
                <div class="empty-icon">🔍</div>
                <p>分析结果将在这里显示</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 2. 题目解答 -->
        <div v-if="activeTab === 'question'" class="understanding-section">
          <div class="section-header">
            <h2>📚 题目解答</h2>
          </div>
          
          <div class="understanding-panel">
            <div class="upload-panel">
              <div class="upload-area" @click="triggerUpload('question')">
                <input 
                  ref="questionInput" 
                  type="file" 
                  accept="image/*" 
                  @change="handleImageSelect('question', $event)" 
                  style="display: none"
                >
                <div v-if="!questionImage" class="upload-placeholder">
                  <div class="upload-icon">📖</div>
                  <p>上传题目图片</p>
                  <small>支持数学、物理、化学等理科题目</small>
                </div>
                <div v-else class="uploaded-preview">
                  <img :src="questionImagePreview" alt="题目图片" />
                  <button class="remove-btn" @click.stop="clearImage('question')">×</button>
                </div>
              </div>
              
              <button 
                class="analyze-btn" 
                @click="solveQuestion" 
                :disabled="!questionImage || processing"
              >
                <span v-if="processing">解答中...</span>
                <span v-else>📚 开始解答</span>
              </button>
            </div>
            
            <div class="result-panel">
              <!-- 处理中动画 -->
              <div v-if="processing" class="processing-state">
                <div class="loading-spinner"></div>
                <p>AI 解答中...</p>
              </div>
              
              <!-- 解答结果 -->
              <div v-else-if="analysisResult" class="result-display">
               
                <div class="result-content answer-content">
                  <div class="formatted-description" v-html="formatDescription(analysisResult.answer)"></div>
                </div>
              </div>
              
              <!-- 空状态 -->
              <div v-else class="empty-result">
                <div class="empty-icon">📚</div>
                <p>解答结果将在这里显示</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 3. OCR识别 -->
        <div v-if="activeTab === 'ocr'" class="understanding-section">
          <div class="section-header">
            <h2>📄 文字识别</h2>
          </div>
          
          <div class="understanding-panel">
            <div class="upload-panel">
              <div class="upload-area" @click="triggerUpload('ocr')">
                <input 
                  ref="ocrInput" 
                  type="file" 
                  accept="image/*" 
                  @change="handleImageSelect('ocr', $event)" 
                  style="display: none"
                >
                <div v-if="!ocrImage" class="upload-placeholder">
                  <div class="upload-icon">📄</div>
                  <p>上传包含文字的图片</p>
                  <small>支持票据、证件、表单、文档等</small>
                </div>
                <div v-else class="uploaded-preview">
                  <img :src="ocrImagePreview" alt="OCR图片" />
                  <button class="remove-btn" @click.stop="clearImage('ocr')">×</button>
                </div>
              </div>
              
              <button 
                class="analyze-btn" 
                @click="recognizeText" 
                :disabled="!ocrImage || processing"
              >
                <span v-if="processing">识别中...</span>
                <span v-else>📄 开始识别</span>
              </button>
            </div>
            
            <div class="result-panel">
              <!-- 处理中动画 -->
              <div v-if="processing" class="processing-state">
                <div class="loading-spinner"></div>
                <p>AI 识别中...</p>
              </div>
              
              <!-- OCR结果 -->
              <div v-else-if="analysisResult" class="result-display">
                <h3>识别结果</h3>
                <div class="result-content ocr-content">
                  <div v-if="analysisResult.structured_data" class="structured-data">
                    <h4>📋 结构化信息</h4>
                    <div class="data-grid">
                      <div 
                        v-for="(value, key) in analysisResult.structured_data" 
                        :key="key"
                        class="data-item"
                      >
                        <span class="data-label">{{ key }}:</span>
                        <span class="data-value">{{ value }}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="analysisResult.extracted_text" class="text-result">
                    <h4>📝 识别文本</h4>
                    <div class="ocr-text formatted-description" v-html="formatDescription(analysisResult.extracted_text)"></div>
                    <button class="copy-btn" @click="copyText(analysisResult.extracted_text)">
                      📋 复制文本
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- 空状态 -->
              <div v-else class="empty-result">
                <div class="empty-icon">📄</div>
                <p>识别结果将在这里显示</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 4. 物体定位 -->
        <div v-if="activeTab === 'detection'" class="understanding-section">
            
          <div class="understanding-panel">
            <div class="upload-panel">
              <div class="upload-area" @click="triggerUpload('detection')">
                <input 
                  ref="detectionInput" 
                  type="file" 
                  accept="image/*" 
                  @change="handleImageSelect('detection', $event)" 
                  style="display: none"
                >
                <div v-if="!detectionImage" class="upload-placeholder">
                  <div class="upload-icon">🎯</div>
                  <p>上传图片进行物体定位</p>
                  <small>AI将识别图像中的所有物体</small>
                </div>
                <div v-else class="uploaded-preview">
                  <img :src="detectionImagePreview" alt="物体定位图片" />
                  <button class="remove-btn" @click.stop="clearImage('detection')">×</button>
                </div>
              </div>
              
              <div class="prompt-input-area">
                <label for="detection-prompt" class="prompt-label">描述要定位的物体：</label>
                <textarea 
                  id="detection-prompt"
                  v-model="detectionPrompt"
                  class="prompt-textarea"
                  placeholder="请描述您想要定位的物体，例如：人、汽车、猫咪、红色的苹果等..."
                  rows="3"
                ></textarea>
                <small class="prompt-hint">💡 提示：描述越具体，定位越准确</small>
              </div>
              
              <button 
                class="analyze-btn" 
                @click="detectObjects" 
                :disabled="!detectionImage || processing || !detectionPrompt.trim()"
              >
                <span v-if="processing">定位中...</span>
                <span v-else>🎯 开始定位</span>
              </button>
            </div>
            
            <div class="result-panel">
              <!-- 处理中的占位动画 - 参照ImageEditView -->
              <div v-if="processing" class="placeholder-wrapper">
                <div class="placeholder-container">
                  <div class="placeholder-skeleton">
                    <div class="skeleton-shimmer"></div>
                    <div class="placeholder-content">
                      <div class="loading-spinner"></div>
                      <p class="loading-text">AI 定位中...</p>
                      <p class="loading-subtext">正在标注物体位置</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 定位结果 - 主要显示标注后的图片 -->
              <div v-else-if="analysisResult" class="result-display">
                
                <!-- 如果有标注图像，显示标注后的图片 -->
                <div v-if="analysisResult.annotatedImageUrl" class="annotated-result">
                  <img :src="analysisResult.annotatedImageUrl" alt="物体标注结果" class="result-image" />
                  <button class="download-result-btn" @click="downloadAnnotatedImage(analysisResult.annotatedImageUrl)">
                    📥 下载标注图像
                  </button>
                </div>
                
                <!-- 如果没有标注图像，显示文字描述 -->
                <div v-else class="no-image-result">
                  <div class="no-image-icon">ℹ️</div>
                  <h4>AI 反馈</h4>
                  <div class="formatted-description" v-html="formatDescription(analysisResult.description)"></div>
                </div>
              </div>
              
              <!-- 空状态 -->
              <div v-else class="empty-result">
                <div class="empty-icon">🎯</div>
                <p>定位结果将在这里显示</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'

// 定义 emits
const emit = defineEmits(['goBack'])

const toast = useToast()

// 当前激活的标签
const activeTab = ref<'description' | 'question' | 'ocr' | 'detection'>('description')

// 标签配置
const tabs: Array<{ key: 'description' | 'question' | 'ocr' | 'detection', icon: string, label: string }> = [
  { key: 'description', icon: '🔍', label: '图像描述' },
  { key: 'question', icon: '📚', label: '题目解答' },
  { key: 'ocr', icon: '📄', label: 'OCR识别' },
  { key: 'detection', icon: '🎯', label: '物体定位' }
]

// 图像描述相关
const descriptionInput = ref<HTMLInputElement>()
const descriptionImage = ref<File | null>(null)
const descriptionImagePreview = ref<string>('')

// 题目解答相关
const questionInput = ref<HTMLInputElement>()
const questionImage = ref<File | null>(null)
const questionImagePreview = ref<string>('')

// OCR识别相关
const ocrInput = ref<HTMLInputElement>()
const ocrImage = ref<File | null>(null)
const ocrImagePreview = ref<string>('')

// 物体定位相关
const detectionInput = ref<HTMLInputElement>()
const detectionImage = ref<File | null>(null)
const detectionImagePreview = ref<string>('')
const detectionPrompt = ref<string>('')

// 通用状态
const processing = ref(false)
const analysisResult = ref<any>(null)

// 方法
const switchTab = (tab: 'description' | 'question' | 'ocr' | 'detection') => {
  activeTab.value = tab
  analysisResult.value = null
  // 清空当前tab的输入内容
  if (tab === 'detection') {
    detectionPrompt.value = ''
  }
}

const triggerUpload = (type: string) => {
  if (type === 'description') {
    descriptionInput.value?.click()
  } else if (type === 'question') {
    questionInput.value?.click()
  } else if (type === 'ocr') {
    ocrInput.value?.click()
  } else if (type === 'detection') {
    detectionInput.value?.click()
  }
}

const handleImageSelect = (type: 'description' | 'question' | 'ocr' | 'detection', event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    
    if (type === 'description') {
      descriptionImage.value = file
      createImagePreview(file, (url) => { descriptionImagePreview.value = url })
    } else if (type === 'question') {
      questionImage.value = file
      createImagePreview(file, (url) => { questionImagePreview.value = url })
    } else if (type === 'ocr') {
      ocrImage.value = file
      createImagePreview(file, (url) => { ocrImagePreview.value = url })
    } else if (type === 'detection') {
      detectionImage.value = file
      createImagePreview(file, (url) => { detectionImagePreview.value = url })
    }
    
    analysisResult.value = null
  }
}

const createImagePreview = (file: File, callback: (url: string) => void) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    callback(e.target?.result as string)
  }
  reader.readAsDataURL(file)
}

const clearImage = (type: 'description' | 'question' | 'ocr' | 'detection') => {
  if (type === 'description') {
    descriptionImage.value = null
    descriptionImagePreview.value = ''
  } else if (type === 'question') {
    questionImage.value = null
    questionImagePreview.value = ''
  } else if (type === 'ocr') {
    ocrImage.value = null
    ocrImagePreview.value = ''
  } else if (type === 'detection') {
    detectionImage.value = null
    detectionImagePreview.value = ''
    detectionPrompt.value = ''
  }
  analysisResult.value = null
}

// 生命周期钩子 - 处理外部激活的tab
onMounted(() => {
  // 检查是否有要激活的特定tab
  const tabToActivate = localStorage.getItem('understandingTabToActivate')
  if (tabToActivate && ['description', 'question', 'ocr', 'detection'].includes(tabToActivate)) {
    activeTab.value = tabToActivate as 'description' | 'question' | 'ocr' | 'detection'
    // 清除localStorage中的设置
    localStorage.removeItem('understandingTabToActivate')
  }
})

// 图像描述分析
const analyzeDescription = async () => {
  if (!descriptionImage.value) {
    toast.error('请先上传图片')
    return
  }
  
  processing.value = true
  analysisResult.value = null
  
  try {
    // 使用FormData发送文件（与后端multipart/form-data格式匹配）
    const formData = new FormData()
    formData.append('image', descriptionImage.value)
    
    console.log('发送图像理解请求:', {
      fileName: descriptionImage.value.name,
      fileSize: descriptionImage.value.size,
      fileType: descriptionImage.value.type
    })
    
    const response = await (apiService as any).instance.post('/ai-image/understand/', formData, {
      timeout: 30000,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    console.log('图像理解响应:', response.data)
    console.log('完整响应结构:', JSON.stringify(response.data, null, 2))
    
    if (response.data.code === 200) {
      // 调试日志：检查后端返回的数据类型
      console.log('后端返回的data对象:', response.data.data)
      console.log('后端返回的description类型:', typeof response.data.data.description)
      console.log('后端返回的description内容:', response.data.data.description)
      console.log('description的JSON结构:', JSON.stringify(response.data.data.description, null, 2))
      
      // 适配后端返回格式，先尝试提取正确的描述文本
      let description = response.data.data.description
      
      // 如果description是对象，尝试提取文本内容
      if (typeof description === 'object' && description !== null) {
        if (description.text) {
          description = description.text
        } else if (description.content) {
          description = description.content
        } else if (Array.isArray(description)) {
          description = description.map(item => {
            if (typeof item === 'string') return item
            if (item && item.text) return item.text
            if (item && item.content) return item.content
            return String(item)
          }).join(' ')
        }
      }
      
      analysisResult.value = {
        description: description,
        confidence: response.data.data.confidence,
        tags: [] // 如果需要标签，后端需要相应返回
      }
      toast.success('图像分析完成！')
    } else {
      throw new Error(response.data.message || '图像分析失败')
    }
  } catch (error: any) {
    console.error('图像分析失败:', error)
    toast.error(error.message || '图像分析失败，请稍后重试')
  } finally {
    processing.value = false
  }
}

// 题目解答
const solveQuestion = async () => {
  if (!questionImage.value) {
    toast.error('请先上传题目图片')
    return
  }
  
  processing.value = true
  analysisResult.value = null
  
  try {
    // 使用FormData发送文件
    const formData = new FormData()
    formData.append('image', questionImage.value)
    formData.append('analyze_type', 'question')
    
    const response = await (apiService as any).instance.post('/ai-image/understand/', formData, {
      timeout: 40000,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.code === 200) {
      // 调试日志：检查题目解答返回的数据类型
      console.log('题目解答返回的description类型:', typeof response.data.data.description)
      console.log('题目解答返回的description内容:', response.data.data.description)
      console.log('题目解答description的JSON结构:', JSON.stringify(response.data.data.description, null, 2))
      
      // 提取正确的描述文本
      let description = response.data.data.description
      
      // 如果description是对象，尝试提取文本内容
      if (typeof description === 'object' && description !== null) {
        if (description.text) {
          description = description.text
        } else if (description.content) {
          description = description.content
        } else if (Array.isArray(description)) {
          description = description.map(item => {
            if (typeof item === 'string') return item
            if (item && item.text) return item.text
            if (item && item.content) return item.content
            return String(item)
          }).join(' ')
        }
      }
      
      analysisResult.value = {
        description: description,
        confidence: response.data.data.confidence,
        answer: description
      }
      toast.success('题目解答完成！')
    } else {
      throw new Error(response.data.message || '题目解答失败')
    }
  } catch (error: any) {
    console.error('题目解答失败:', error)
    toast.error(error.message || '题目解答失败，请稍后重试')
  } finally {
    processing.value = false
  }
}

// OCR识别
const recognizeText = async () => {
  if (!ocrImage.value) {
    toast.error('请先上传图片')
    return
  }
  
  processing.value = true
  analysisResult.value = null
  
  try {
    // 使用FormData发送文件
    const formData = new FormData()
    formData.append('image', ocrImage.value)
    formData.append('analyze_type', 'ocr')
    
    const response = await (apiService as any).instance.post('/ai-image/understand/', formData, {
      timeout: 60000,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.code === 200) {
      // 调试日志：检查OCR返回的数据类型
      console.log('OCR返回的description类型:', typeof response.data.data.description)
      console.log('OCR返回的description内容:', response.data.data.description)
      console.log('OCR description的JSON结构:', JSON.stringify(response.data.data.description, null, 2))
      
      // 提取正确的描述文本
      let description = response.data.data.description
      
      // 如果description是对象，尝试提取文本内容
      if (typeof description === 'object' && description !== null) {
        if (description.text) {
          description = description.text
        } else if (description.content) {
          description = description.content
        } else if (Array.isArray(description)) {
          description = description.map(item => {
            if (typeof item === 'string') return item
            if (item && item.text) return item.text
            if (item && item.content) return item.content
            return String(item)
          }).join(' ')
        }
      }
      
      analysisResult.value = {
        description: description,
        confidence: response.data.data.confidence,
        extracted_text: description,
        structured_data: null // OCR结构化数据，如果后端支持
      }
      toast.success('文字识别完成！')
    } else {
      throw new Error(response.data.message || '文字识别失败')
    }
  } catch (error: any) {
    console.error('文字识别失败:', error)
    toast.error(error.message || '文字识别失败，请稍后重试')
  } finally {
    processing.value = false
  }
}

// 物体定位
const detectObjects = async () => {
  if (!detectionImage.value) {
    toast.error('请先上传图片')
    return
  }
  
  if (!detectionPrompt.value.trim()) {
    toast.error('请描述要定位的物体')
    return
  }
  
  processing.value = true
  analysisResult.value = null
  
  try {
    // 使用专门的物体检测接口
    const formData = new FormData()
    formData.append('image', detectionImage.value)
    formData.append('detection_prompt', detectionPrompt.value.trim())
    
    console.log('发送物体检测请求:', {
      fileName: detectionImage.value.name,
      fileSize: detectionImage.value.size,
      fileType: detectionImage.value.type,
      detectionPrompt: detectionPrompt.value.trim()
    })
    
    const response = await (apiService as any).instance.post('/ai-image/detect/', formData, {
      timeout: 60000,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.code === 200) {
      // 调试日志：检查物体定位返回的数据类型
      console.log('物体定位返回的description类型:', typeof response.data.data.description)
      console.log('物体定位返回的description内容:', response.data.data.description)
      console.log('用户查找的物体:', detectionPrompt.value.trim())
      console.log('物体定位description的JSON结构:', JSON.stringify(response.data.data.description, null, 2))
      
      // 提取正确的描述文本
      let description = response.data.data.description
      
      // 如果description是对象，尝试提取文本内容
      if (typeof description === 'object' && description !== null) {
        if (description.text) {
          description = description.text
        } else if (description.content) {
          description = description.content
        } else if (Array.isArray(description)) {
          description = description.map(item => {
            if (typeof item === 'string') return item
            if (item && item.text) return item.text
            if (item && item.content) return item.content
            return String(item)
          }).join(' ')
        }
      }
      
      // 后端现在直接返回coordinates，无需前端解析
      let coordinates = response.data.data.coordinates || []
      
      // 简化：只关注标注后的图片和描述
      let annotatedUrl = response.data.data.annotated_image_url
      
      // 如果URL是相对路径，转换为完整URL
      if (annotatedUrl && annotatedUrl.startsWith('/')) {
        annotatedUrl = `http://localhost:8000${annotatedUrl}`
      }
      
      console.log('标注图片URL:', annotatedUrl)
      
      analysisResult.value = {
        annotatedImageUrl: annotatedUrl,  // 标注后的图片URL（完整路径）
        description: response.data.data.description,  // AI返回的描述
        confidence: response.data.data.confidence,
        prompt: detectionPrompt.value.trim()
      }
      
      // 根据是否有标注图像显示不同的成功信息
      if (analysisResult.value.annotatedImageUrl) {
        toast.success(`🎯 物体定位完成！已生成标注图像`)
      } else {
        toast.success(`🔍 物体定位完成，请查看描述结果`)
      }
    } else {
      throw new Error(response.data.message || '物体定位失败')
    }
  } catch (error: any) {
    console.error('物体定位失败:', error)
    toast.error(error.message || '物体定位失败，请稍后重试')
  } finally {
    processing.value = false
  }
}

// 将文件转为base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const result = e.target?.result as string
      resolve(result)
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

// 格式化图像描述（处理Markdown格式和换行符）
const formatDescription = (description: any) => {
  // 调试信息：记录传入参数的类型和内容
  console.log('formatDescription 接收到的参数类型:', typeof description)
  console.log('formatDescription 接收到的参数内容:', description)
  
  // 安全检查：确保输入是字符串类型
  if (!description) return ''
  
  let formatted = ''
  
  // 处理不同类型的输入数据
  if (typeof description === 'string') {
    formatted = description
  } else if (typeof description === 'object') {
    // 如果是对象，尝试提取文本内容
    if (description.text) {
      formatted = description.text
    } else if (description.content) {
      formatted = description.content
    } else if (description.message) {
      formatted = description.message
    } else if (Array.isArray(description)) {
      // 如果是数组，尝试提取文本
      formatted = description.map(item => {
        if (typeof item === 'string') return item
        if (item && item.text) return item.text
        if (item && item.content) return item.content
        return String(item)
      }).join('\n')
    } else {
      // 如果是其他对象，尝试JSON序列化然后提取可读内容
      try {
        const jsonStr = JSON.stringify(description, null, 2)
        console.log('对象JSON结构:', jsonStr)
        formatted = jsonStr
      } catch (e) {
        formatted = String(description)
      }
    }
  } else {
    formatted = String(description)
  }
  
  // 如果转换后还是空字符串，直接返回
  if (!formatted || formatted === 'undefined' || formatted === 'null' || formatted === '[object Object]') return ''
  
  try {
    // 处理标题格式 ### -> <h3>
    formatted = formatted.replace(/###\s*([^\n]+)/g, '<h3 class="desc-title">$1</h3>')
    formatted = formatted.replace(/##\s*([^\n]+)/g, '<h4 class="desc-subtitle">$1</h4>')
    formatted = formatted.replace(/#\s*([^\n]+)/g, '<h5 class="desc-heading">$1</h5>')
    
    // 处理加粗文本 **text** -> <strong>text</strong>
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    
    // 处理双换行为段落分隔
    formatted = formatted.replace(/\n\n+/g, '</p><p>')
    
    // 处理单换行为<br>
    formatted = formatted.replace(/\n/g, '<br>')
    
    // 包装在段落标签中
    formatted = `<p>${formatted}</p>`
    
    // 清理空段落
    formatted = formatted.replace(/<p><\/p>/g, '')
    formatted = formatted.replace(/<p><br><\/p>/g, '')
    
    return formatted
  } catch (error) {
    console.error('格式化描述时出错:', error, '原始数据:', description)
    return `<p>${String(description)}</p>`
  }
}

// 格式化答案（支持换行）
const formatAnswer = (answer: any) => {
  if (!answer) return ''
  
  // 确保输入是字符串类型
  const answerStr = String(answer)
  if (!answerStr || answerStr === 'undefined' || answerStr === 'null') return ''
  
  try {
    return answerStr.replace(/\n/g, '<br>')
  } catch (error) {
    console.error('格式化答案时出错:', error, '原始数据:', answer)
    return String(answer)
  }
}

// 复制文本
const copyText = async (text: any) => {
  try {
    // 提取正确的文本内容
    let textStr = ''
    
    if (typeof text === 'string') {
      textStr = text
    } else if (typeof text === 'object' && text !== null) {
      if (text.text) {
        textStr = text.text
      } else if (text.content) {
        textStr = text.content
      } else if (Array.isArray(text)) {
        textStr = text.map(item => {
          if (typeof item === 'string') return item
          if (item && item.text) return item.text
          if (item && item.content) return item.content
          return String(item)
        }).join(' ')
      } else {
        textStr = JSON.stringify(text, null, 2)
      }
    } else {
      textStr = String(text || '')
    }
    
    if (!textStr || textStr === '[object Object]') {
      toast.error('没有可复制的内容')
      return
    }
    
    await navigator.clipboard.writeText(textStr)
    toast.success('文本已复制到剪贴板！')
  } catch (error) {
    // 降级方案
    let textStr = ''
    
    if (typeof text === 'string') {
      textStr = text
    } else if (typeof text === 'object' && text !== null) {
      if (text.text) {
        textStr = text.text
      } else if (text.content) {
        textStr = text.content
      } else {
        textStr = JSON.stringify(text, null, 2)
      }
    } else {
      textStr = String(text || '')
    }
    
    if (!textStr || textStr === '[object Object]') {
      toast.error('没有可复制的内容')
      return
    }
    
    const textArea = document.createElement('textarea')
    textArea.value = textStr
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      toast.success('文本已复制到剪贴板！')
    } catch (err) {
      toast.error('复制失败')
    }
    document.body.removeChild(textArea)
  }
}

// 下载标注图像
const downloadAnnotatedImage = async (imageUrl: string) => {
  try {
    const response = await fetch(imageUrl)
    const blob = await response.blob()
    
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `annotated_${Date.now()}.jpg`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    toast.success('标注图像下载成功！')
  } catch (error) {
    console.error('下载标注图像失败:', error)
    toast.error('下载失败，请稍后重试')
  }
}
</script>

<style scoped>
.image-understanding-view {
  min-height: 100vh;
  background: var(--color-background);
  color: var(--color-text);
  padding: 2rem;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  max-width: 1400px;
  margin: 0 auto 2rem;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: var(--color-primary-alpha);
  border-color: var(--color-primary);
}

.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0;
  flex: 1;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 标签页 */
.understanding-tabs {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.tab-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  background: var(--card-background);
  border: 2px solid var(--card-border);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--card-shadow);
}

.tab-btn:hover {
  transform: translateY(-4px);
  border-color: var(--color-primary);
  box-shadow: 0 8px 20px rgba(94, 155, 255, 0.2);
}

.tab-btn.active {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  border-color: transparent;
  box-shadow: 0 8px 25px rgba(94, 155, 255, 0.3);
}

.tab-icon {
  font-size: 2.5rem;
}

.tab-btn.active .tab-icon {
  transform: scale(1.1);
}

.tab-label {
  font-size: 1rem;
  font-weight: 600;
}

/* 内容区 */
.understanding-content {
  background: var(--card-background);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: var(--card-shadow);
}

.section-header {
  text-align: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text);
}

.understanding-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.upload-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 上传区域 */
.upload-area {
  border: 2px dashed var(--color-border);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--color-surface);
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-alpha);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-icon {
  font-size: 4rem;
  opacity: 0.6;
}

.upload-placeholder p {
  font-size: 1.1rem;
  color: var(--color-text);
  margin: 0;
}

.upload-placeholder small {
  color: var(--color-textSecondary);
}

.uploaded-preview {
  position: relative;
  width: 100%;
  max-width: 400px;
}

.uploaded-preview img {
  width: 100%;
  height: auto;
  max-height: 300px;
  object-fit: contain;
  border-radius: 12px;
}

.remove-btn {
  position: absolute;
  top: -12px;
  right: -12px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-error);
  color: white;
  border: 2px solid var(--card-background);
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.remove-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

/* 提示词输入区域 */
.prompt-input-area {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.prompt-label {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.prompt-textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
  color: var(--color-text);
  font-family: inherit;
  font-size: 0.95rem;
  line-height: 1.5;
  resize: vertical;
  min-height: 80px;
  transition: all 0.3s ease;
}

.prompt-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(94, 155, 255, 0.1);
  background: var(--card-background);
}

.prompt-textarea::placeholder {
  color: var(--color-textSecondary);
  opacity: 0.8;
}

.prompt-hint {
  color: var(--color-textSecondary);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

/* 按钮 */
.analyze-btn {
  width: 100%;
  padding: 1rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(94, 155, 255, 0.3);
}

.analyze-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(94, 155, 255, 0.4);
}

.analyze-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 结果面板 */
.result-panel {
  background: var(--color-surface);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.processing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.result-display {
  width: 100%;
  max-height: 600px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.result-display h3 {
  margin: 0;
  color: var(--color-text);
  font-size: 1.5rem;
  text-align: center;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.result-section h4 {
  margin: 0 0 1rem 0;
  color: var(--color-primary);
  font-size: 1.1rem;
}

.result-section p {
  line-height: 1.8;
  color: var(--color-text);
  margin: 0;
}

/* 标签容器 */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  padding: 0.4rem 1rem;
  background: var(--color-primary-alpha);
  color: var(--color-primary);
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 格式化描述内容 */
.formatted-description {
  line-height: 1.8;
  color: var(--color-text);
}

.formatted-description p {
  margin: 0 0 1rem 0;
  line-height: 1.8;
}

.formatted-description p:last-child {
  margin-bottom: 0;
}

.formatted-description .desc-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-primary);
  margin: 1.5rem 0 0.8rem 0;
  border-bottom: 2px solid var(--color-primary-alpha);
  padding-bottom: 0.5rem;
}

.formatted-description .desc-title:first-child {
  margin-top: 0;
}

.formatted-description .desc-subtitle {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-accent);
  margin: 1.2rem 0 0.6rem 0;
}

.formatted-description .desc-heading {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 1rem 0 0.5rem 0;
}

.formatted-description strong {
  color: var(--color-primary);
  font-weight: 600;
}

/* 答案内容 */
.answer-content {
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.5rem;
  line-height: 1.8;
}

/* OCR内容 */
.ocr-content {
  gap: 1.5rem;
}

/* 占位动画样式 - 与ImageEditView保持一致 */
.placeholder-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.placeholder-container {
  width: 100%;
  max-width: 500px;
  aspect-ratio: 1 / 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-skeleton {
  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(94, 155, 255, 0.08) 0%,
    rgba(165, 105, 255, 0.08) 50%,
    rgba(94, 155, 255, 0.08) 100%
  );
  border: 3px dashed var(--color-primary);
  background-size: 200% 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(94, 155, 255, 0.15);
}

/* 流光动画 */
.skeleton-shimmer {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.2) 50%,
    transparent 100%
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.placeholder-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  color: var(--color-text);
}

.loading-text {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.loading-subtext {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-textSecondary);
}

/* 标注结果显示 */
.annotated-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
}

.result-image {
  width: 100%;
  max-width: 500px;
  height: auto;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  border: 2px solid var(--color-primary-alpha);
}

.download-result-btn {
  padding: 0.75rem 2rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(94, 155, 255, 0.3);
}

.download-result-btn:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(94, 155, 255, 0.4);
}

/* 无图像结果时的显示 */
.no-image-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
  width: 100%;
}

.no-image-icon {
  font-size: 3rem;
  opacity: 0.6;
}

.no-image-result h4 {
  margin: 0;
  color: var(--color-primary);
  font-size: 1.2rem;
}

.no-image-result .formatted-description {
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.5rem;
  width: 100%;
  max-width: 500px;
}

.description-section h4 {
  margin: 0 0 1rem 0;
  color: var(--color-primary);
  font-size: 1.1rem;
}

.structured-data h4,
.text-result h4 {
  margin: 0 0 1rem 0;
  color: var(--color-primary);
  font-size: 1.1rem;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.data-item {
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem;
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.data-label {
  font-weight: 600;
  color: var(--color-textSecondary);
  flex-shrink: 0;
}

.data-value {
  color: var(--color-text);
  flex: 1;
}

.ocr-text {
  padding: 1rem;
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text);
  line-height: 1.6;
  word-wrap: break-word;
  margin: 0 0 1rem 0;
}

.ocr-text.formatted-description {
  font-family: monospace;
  white-space: pre-wrap;
}

.ocr-text.formatted-description p {
  font-family: monospace;
  white-space: pre-wrap;
}

.copy-btn {
  padding: 0.5rem 1rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-btn:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
}

.empty-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: var(--color-textSecondary);
}

.empty-icon {
  font-size: 4rem;
  opacity: 0.5;
}

.empty-result p {
  font-size: 1.1rem;
  color: var(--color-text);
  margin: 0;
}

/* 滚动条 */
.result-display::-webkit-scrollbar {
  width: 6px;
}

.result-display::-webkit-scrollbar-track {
  background: var(--color-background);
  border-radius: 3px;
}

.result-display::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 3px;
}

.result-display::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

/* 响应式 */
@media (max-width: 1024px) {
  .understanding-panel {
    grid-template-columns: 1fr;
  }
  
  .understanding-tabs {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .image-understanding-view {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .understanding-content {
    padding: 1.5rem;
  }
  
  .understanding-tabs {
    grid-template-columns: 1fr;
  }
  
  .data-grid {
    grid-template-columns: 1fr;
  }
}
</style>

