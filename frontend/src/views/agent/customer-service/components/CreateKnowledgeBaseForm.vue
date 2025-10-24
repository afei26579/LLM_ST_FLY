<template>
  <div class="create-kb-form">
    <div class="form-header">
      <div class="header-left">
        <button @click="$emit('cancel')" class="btn-back">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          返回
        </button>
        <h2>📚 创建知识库</h2>
      </div>
      <div class="header-right">
        <div class="steps-indicator">
          <div class="step-item" :class="{ active: currentStep === 1, completed: currentStep > 1 }">
            <div class="step-circle">1</div>
            <div class="step-label">基本信息</div>
          </div>
          <div class="step-line"></div>
          <div class="step-item" :class="{ active: currentStep === 2, completed: currentStep > 2 }">
            <div class="step-circle">2</div>
            <div class="step-label">上传文档</div>
          </div>
          <div class="step-line"></div>
          <div class="step-item" :class="{ active: currentStep === 3, completed: currentStep > 3 }">
            <div class="step-circle">3</div>
            <div class="step-label">文档切片</div>
          </div>
          <div class="step-line"></div>
          <div class="step-item" :class="{ active: currentStep === 4 }">
            <div class="step-circle">4</div>
            <div class="step-label">向量化</div>
          </div>
        </div>
      </div>
    </div>

    <div class="form-content">
      <!-- 步骤1：基本信息 -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="form-section">
          <h3>基本信息</h3>
          
          <div class="form-group">
            <label class="required">知识库名称</label>
            <input
              v-model="formData.name"
              type="text"
              placeholder="例如：产品使用手册"
              maxlength="50"
              class="form-input"
            />
            <span class="char-count">{{ formData.name.length }}/50</span>
          </div>

          <div class="form-group">
            <label class="required">知识库格式</label>
            <div class="format-options">
              <label 
                v-for="format in formatOptions" 
                :key="format.value"
                class="format-option"
                :class="{ active: formData.format === format.value }"
              >
                <input
                  type="radio"
                  :value="format.value"
                  v-model="formData.format"
                />
                <div class="option-content">
                  <div class="option-icon">{{ format.icon }}</div>
                  <div class="option-info">
                    <div class="option-title">{{ format.label }}</div>
                    <div class="option-formats">{{ format.formats.join('、') }}</div>
                  </div>
                </div>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label>描述</label>
            <textarea
              v-model="formData.description"
              placeholder="简要描述该知识库的用途和内容范围..."
              maxlength="200"
              rows="3"
              class="form-textarea"
            ></textarea>
            <span class="char-count">{{ formData.description.length }}/200</span>
          </div>
        </div>
      </div>

      <!-- 步骤2：上传文档 -->
      <div v-else-if="currentStep === 2" class="step-content">
        <p class="step-tip">✅ 知识库"{{ formData.name }}"已创建，现在可以上传文档</p>
        
        <!-- 上传区域 -->
        <div 
          class="upload-zone" 
          :class="{ 'drag-over': isDragOver, 'has-files': uploadedFiles.length > 0 }"
          @drop="handleDrop"
          @dragover.prevent="isDragOver = true"
          @dragleave="isDragOver = false"
          @click="triggerFileInput"
        >
          <input 
            ref="fileInput"
            type="file" 
            :accept="getAcceptTypes()"
            multiple
            @change="handleFileSelect"
            style="display: none"
          />
          
          <div v-if="uploadedFiles.length === 0" class="upload-placeholder">
            <div class="upload-icon">📁</div>
            <h3>上传{{ getCurrentFormatLabel() }}文档</h3>
            <p>拖拽文件到此处，或点击选择文件</p>
            <div class="supported-formats">
              <span class="format-tag" v-for="fmt in getCurrentFormats()" :key="fmt">
                {{ fmt }}
              </span>
            </div>
          </div>

          <!-- 已上传文件列表 -->
          <div v-else class="uploaded-files">
            <div class="files-header">
              <h4>已上传 {{ uploadedFiles.length }} 个文件</h4>
              <button @click.stop="triggerFileInput" class="btn-add-more">
                ➕ 继续添加
              </button>
            </div>
            <div class="file-list">
              <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
                <div class="file-icon">{{ getFileIcon(file.name) }}</div>
                <div class="file-info">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-size">{{ formatFileSize(file.size) }}</div>
                </div>
                <button @click.stop="removeFile(index)" class="btn-remove">✕</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分段策略 -->
        <div class="config-section">
          <h4>分段策略</h4>
          
          <div class="strategy-options">
            <label class="strategy-option" :class="{ active: chunkConfig.strategy === 'auto' }">
              <input type="radio" value="auto" v-model="chunkConfig.strategy" />
              <div class="strategy-content">
                <div class="strategy-icon">🤖</div>
                <div class="strategy-info">
                  <strong>智能分段</strong>
                  <small>AI自动识别文档结构和语义边界</small>
                </div>
              </div>
            </label>

            <label class="strategy-option" :class="{ active: chunkConfig.strategy === 'custom' }">
              <input type="radio" value="custom" v-model="chunkConfig.strategy" />
              <div class="strategy-content">
                <div class="strategy-icon">⚙️</div>
                <div class="strategy-info">
                  <strong>自定义分段</strong>
                  <small>自定义分段规则及处理规则</small>
                </div>
              </div>
            </label>
          </div>

          <!-- 自定义分段配置 -->
          <div v-if="chunkConfig.strategy === 'custom'" class="custom-config">
            <div class="config-row">
              <label>分段标识符</label>
              <CustomSelect 
                v-model="chunkConfig.separator"
                :options="separatorOptions"
              />
              <small class="config-hint">💡 建议：文档类使用"双换行"，对话类使用"换行符"</small>
            </div>

            <div class="config-row">
              <label>分段最大长度: {{ chunkConfig.maxLength }} 字符</label>
              <input 
                v-model.number="chunkConfig.maxLength" 
                type="range"
                min="200"
                max="1200"
                step="50"
                class="config-range"
              />
              <div class="range-labels">
                <span>200</span>
                <span>1200</span>
              </div>
            </div>

            <div class="config-row">
              <label>分段重叠度: {{ chunkConfig.overlap }}% (约 {{ Math.round(chunkConfig.maxLength * chunkConfig.overlap / 100) }} 字符)</label>
              <input 
                v-model.number="chunkConfig.overlap" 
                type="range"
                min="10"
                max="30"
                step="5"
                class="config-range"
              />
              <div class="range-labels">
                <span>10%</span>
                <span>30%</span>
              </div>
            </div>

            <div class="config-row">
              <label>文本预处理规则</label>
              <div class="checkbox-group">
                <label class="checkbox-item">
                  <input type="checkbox" v-model="chunkConfig.removeSpaces" />
                  <span>替换掉连续的空格、换行符和制表符</span>
                </label>
                <label class="checkbox-item">
                  <input type="checkbox" v-model="chunkConfig.removeUrls" />
                  <span>删除所有 URL 和电子邮箱地址</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 步骤3：切片预览 -->
      <div v-else-if="currentStep === 3" class="step-content">
        <p class="step-tip">✅ 文档切片完成，共生成 {{ chunks.length }} 个切片</p>
        
        <div class="chunks-preview">
          <div class="preview-header">
            <h4>切片预览</h4>
            <div class="preview-stats">
              <span>总切片: {{ chunks.length }}</span>
              <span>平均长度: {{ avgChunkLength }} 字符</span>
            </div>
          </div>
          
          <div class="chunks-list">
            <div v-for="(chunk, index) in chunks.slice(0, 10)" :key="index" class="chunk-item">
              <div class="chunk-header">
                <span class="chunk-index">#{{ index + 1 }}</span>
                <span class="chunk-length">{{ chunk.content.length }} 字符</span>
              </div>
              <div class="chunk-content">{{ chunk.content }}</div>
              <div class="chunk-meta">
                <span v-if="chunk.metadata.source">来源: {{ chunk.metadata.source }}</span>
                <span v-if="chunk.metadata.page">页码: {{ chunk.metadata.page }}</span>
              </div>
            </div>
          </div>
          
          <div v-if="chunks.length > 10" class="preview-more">
            还有 {{ chunks.length - 10 }} 个切片未显示...
          </div>
        </div>
      </div>

      <!-- 步骤4：向量化 -->
      <div v-else-if="currentStep === 4" class="step-content">
        <div class="processing-view">
          <div class="processing-status">
            <div class="spinner-large"></div>
            <h3>正在向量化...</h3>
            <p>{{ vectorizingProgress }}%</p>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: vectorizingProgress + '%' }"></div>
            </div>
            <div class="async-notice">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 16v-4M12 8h.01"></path>
              </svg>
              <span>向量化正在后台进行，您可以点击"完成"按钮离开</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="form-footer">
      <button v-if="currentStep === 1" @click="$emit('cancel')" class="btn-secondary">
        取消
      </button>
      <button v-if="currentStep > 1 && currentStep < 4" @click="prevStep" class="btn-secondary">
        上一步
      </button>
      <button
        v-if="currentStep === 1"
        @click="handleCreateKB"
        :disabled="!isValid || loading"
        class="btn-primary"
      >
        <span v-if="!loading">下一步</span>
        <span v-else>创建中...</span>
      </button>
      <button
        v-else-if="currentStep === 2"
        @click="handleChunkDocuments"
        :disabled="uploadedFiles.length === 0 || loading"
        class="btn-primary"
      >
        <span v-if="!loading">下一步</span>
        <span v-else>切片中...</span>
      </button>
      <button
        v-else-if="currentStep === 3"
        @click="handleVectorize"
        :disabled="loading"
        class="btn-primary"
      >
        <span v-if="!loading">下一步：向量化</span>
        <span v-else>提交中...</span>
      </button>
      <button
        v-else-if="currentStep === 4"
        @click="handleComplete"
        class="btn-primary"
      >
        完成
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import CustomSelect from '@/components/CustomSelect.vue'

interface ChunkConfig {
  strategy: string
  separator: string
  maxLength: number
  overlap: number
  removeSpaces: boolean
  removeUrls: boolean
}

const emit = defineEmits<{
  submit: [data: { 
    name: string
    description: string
    format: string
    files: File[]
    chunkConfig: ChunkConfig
  }]
  cancel: []
}>()

const loading = ref(false)
const currentStep = ref(1)
const isDragOver = ref(false)
const uploadedFiles = ref<File[]>([])
const fileInput = ref<HTMLInputElement>()
const chunks = ref<any[]>([])
const isVectorizing = ref(false)
const vectorizingProgress = ref(0)
const knowledgeBaseId = ref<number>()

const formData = ref({
  name: '',
  description: '',
  format: 'text'
})

const chunkConfig = ref({
  strategy: 'auto',
  separator: '\n',
  maxLength: 800,
  overlap: 15,  // 百分比（15%）
  removeSpaces: true,
  removeUrls: false
})

const avgChunkLength = computed(() => {
  if (chunks.value.length === 0) return 0
  const total = chunks.value.reduce((sum, chunk) => sum + chunk.content.length, 0)
  return Math.round(total / chunks.value.length)
})

// 分段标识符选项
const separatorOptions = [
  { value: '\n', label: '换行符 - 按行分段' },
  { value: '\n\n', label: '双换行 - 按段落分段' },
  { value: '。', label: '句号 - 按句子分段' },
  { value: ' ', label: '空格 - 按词分段' }
]

// 格式选项
const formatOptions = [
  {
    value: 'text',
    label: '文本格式',
    icon: '📝',
    description: '适用于纯文本文档、文章、手册等',
    formats: ['TXT', 'MD', 'PDF', 'DOCX']
  },
  {
    value: 'structured',
    label: '结构化格式',
    icon: '📊',
    description: '适用于表格、数据库、API文档等',
    formats: ['CSV', 'JSON', 'XML', 'XLSX', 'HTML']
  },
  {
    value: 'image',
    label: '图片格式',
    icon: '🖼️',
    description: '适用于图表、截图、设计稿等',
    formats: ['PNG', 'JPG', 'JPEG', 'GIF', 'WEBP']
  }
]

const isValid = computed(() => {
  return formData.value.name.trim().length > 0
})

// 格式相关方法
const getCurrentFormats = () => {
  return formatOptions.find(f => f.value === formData.value.format)?.formats || []
}

const getCurrentFormatLabel = () => {
  return formatOptions.find(f => f.value === formData.value.format)?.label || ''
}

const getAcceptTypes = () => {
  const accepts = {
    text: '.txt,.md,.pdf,.doc,.docx',
    structured: '.csv,.json,.xml,.xlsx,.xls,.html',
    image: '.png,.jpg,.jpeg,.gif,.webp'
  }
  return accepts[formData.value.format as keyof typeof accepts] || '*'
}

const getFileIcon = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase() || ''
  const icons: Record<string, string> = {
    txt: '📄', md: '📝', pdf: '📕', doc: '📘', docx: '📘',
    csv: '📊', json: '🔧', xml: '⚙️', xlsx: '📈', xls: '📈', html: '🌐',
    png: '🖼️', jpg: '📷', jpeg: '📷', gif: '🎭', webp: '🖼️'
  }
  return icons[ext] || '📄'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 文件处理
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    addFiles(Array.from(target.files))
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = false
  if (event.dataTransfer?.files) {
    addFiles(Array.from(event.dataTransfer.files))
  }
}

const addFiles = (files: File[]) => {
  const supportedExts = getCurrentFormats().map(f => f.toLowerCase())
  
  files.forEach(file => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext && supportedExts.some(supported => ext === supported.toLowerCase())) {
      uploadedFiles.value.push(file)
    }
  })
}

const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
}

// 步骤控制
const prevStep = () => {
  if (currentStep.value > 1 && currentStep.value < 4) {
    currentStep.value--
  }
}

// 步骤1：创建知识库
const handleCreateKB = async () => {
  if (!isValid.value || loading.value) return
  
  loading.value = true
  
  try {
    const { apiService } = await import('@/services/api')
    const response = await apiService.post('/agent/customer-service/knowledge-bases/', {
      name: formData.value.name.trim(),
      description: formData.value.description.trim(),
      format: formData.value.format
    })
    
    if (response.data?.code === 201 || response.data?.code === 200) {
      knowledgeBaseId.value = response.data.data.id
      currentStep.value = 2
    }
  } catch (error: any) {
    console.error('创建知识库失败:', error)
  } finally {
    loading.value = false
  }
}

// 步骤2：文档切片
const handleChunkDocuments = async () => {
  if (uploadedFiles.value.length === 0 || loading.value) return
  
  loading.value = true
  
  const { useToast } = await import('vue-toastification')
  const toast = useToast()
  
  try {
    const { apiService } = await import('@/services/api')
    const formData = new FormData()
    
    // 添加文件
    uploadedFiles.value.forEach(file => {
      formData.append('files', file)
    })
    
    // 添加配置
    formData.append('knowledge_base_id', knowledgeBaseId.value!.toString())
    formData.append('chunk_strategy', chunkConfig.value.strategy)
    formData.append('chunk_separator', chunkConfig.value.separator)
    formData.append('chunk_max_length', chunkConfig.value.maxLength.toString())
    
    // 将百分比转换为实际字符数
    const overlapChars = Math.round(chunkConfig.value.maxLength * chunkConfig.value.overlap / 100)
    formData.append('chunk_overlap', overlapChars.toString())
    
    formData.append('remove_spaces', chunkConfig.value.removeSpaces.toString())
    formData.append('remove_urls', chunkConfig.value.removeUrls.toString())
    
    const response = await apiService.post('/agent/customer-service/knowledge-bases/chunk-documents/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000  // 文档切片超时时间设置为60秒
    })
    
    console.log('切片响应:', response.data)
    
    if (response.data?.code === 200) {
      chunks.value = response.data.data.chunks || []
      console.log('切片数据:', chunks.value.length, '个切片')
      toast.success(`文档切片完成，共生成 ${chunks.value.length} 个切片`)
      currentStep.value = 3
      console.log('切换到步骤3，currentStep =', currentStep.value)
    } else {
      console.error('切片失败，返回码:', response.data?.code, '消息:', response.data?.message)
      toast.error(response.data?.message || '文档切片失败')
    }
  } catch (error: any) {
    console.error('文档切片失败:', error)
    console.error('错误详情:', error.response?.data)
    const errorMessage = error.response?.data?.message || error.message || '文档切片失败'
    toast.error(errorMessage)
  } finally {
    loading.value = false
  }
}

// 步骤3：向量化（异步处理，显示模拟进度，用户可随时离开）
const handleVectorize = async () => {
  if (loading.value) return
  
  loading.value = true
  
  const { useToast } = await import('vue-toastification')
  const toast = useToast()
  
  try {
    const { apiService } = await import('@/services/api')
    
    // 提交向量化任务到后台
    const response = await apiService.post('/agent/customer-service/knowledge-bases/vectorize/', {
      knowledge_base_id: knowledgeBaseId.value,
      chunks: chunks.value
    })
    
    console.log('向量化任务提交响应:', response.data)
    
    if (response.data?.code === 200) {
      // 跳转到步骤4，显示进度
      currentStep.value = 4
      isVectorizing.value = true
      vectorizingProgress.value = 0
      
      toast.success('向量化任务已提交，正在后台处理')
      console.log('向量化任务已提交，后台处理中')
      
      // 模拟进度更新（仅用于UI反馈，后台实际异步处理）
      const progressInterval = setInterval(() => {
        if (vectorizingProgress.value < 95) {
          vectorizingProgress.value += 5
        } else {
          clearInterval(progressInterval)
        }
      }, 1000)
      
      // 存储 interval ID 以便清理
      ;(window as any).__vectorizeProgressInterval = progressInterval
    } else {
      toast.error(response.data?.message || '提交向量化任务失败')
    }
  } catch (error: any) {
    console.error('提交向量化任务失败:', error)
    toast.error(error.message || '提交向量化任务失败')
  } finally {
    loading.value = false
  }
}

// 完成操作
const handleComplete = async () => {
  // 清理进度更新定时器
  const progressInterval = (window as any).__vectorizeProgressInterval
  if (progressInterval) {
    clearInterval(progressInterval)
    delete (window as any).__vectorizeProgressInterval
  }
  
  // 提示用户
  const { useToast } = await import('vue-toastification')
  const toast = useToast()
  toast.info('知识库创建已提交，向量化将在后台完成')
  
  // 触发取消事件，关闭表单
  emit('cancel')
}

// 组件卸载时清理定时器
onUnmounted(() => {
  const progressInterval = (window as any).__vectorizeProgressInterval
  if (progressInterval) {
    clearInterval(progressInterval)
    delete (window as any).__vectorizeProgressInterval
  }
})
</script>

<style scoped>
.create-kb-form {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-surface);
  margin: 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
}

.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right {
  flex-shrink: 0;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  color: var(--color-text);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-back:hover {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
  color: var(--button-primary);
}

.form-header h2 {
  margin: 0;
  font-size: 20px;
  color: var(--color-text);
}

.form-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.step-content {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.step-tip {
  padding: 12px 16px;
  background: var(--color-success-alpha, rgba(16, 185, 129, 0.1));
  border-left: 3px solid var(--color-success, #10b981);
  border-radius: 6px;
  color: var(--color-text);
  margin-bottom: 20px;
  font-size: 14px;
}

.upload-placeholder,
.complete-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.placeholder-icon,
.complete-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.upload-placeholder h3,
.complete-view h3 {
  margin: 0 0 8px;
  font-size: 20px;
  color: var(--color-text);
}

.upload-placeholder p,
.complete-view p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.form-section {
  margin-bottom: 20px;
}

.form-section h3 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
}

.form-group {
  margin-bottom: 16px;
  position: relative;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
}

.form-group label.required::after,
.form-section h3 .required {
  content: ' *';
  color: var(--color-error, #ef4444);
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  background: var(--input-background);
  border: 1px solid var(--input-border);
  border-radius: 6px;
  font-size: 14px;
  color: var(--color-text);
  font-family: inherit;
  transition: all 0.2s;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--button-primary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.char-count {
  position: absolute;
  bottom: -20px;
  right: 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}

/* 格式选择样式 */
.format-options {
  display: flex;
  gap: 12px;
}

.format-option {
  position: relative;
  flex: 1;
  display: block;
  cursor: pointer;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  padding: 12px 8px;
  background: var(--input-background);
  transition: all 0.3s;
}

.format-option:hover {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
}

.format-option.active {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.format-option input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.option-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
}

.option-icon {
  font-size: 32px;
  line-height: 1;
}

.option-info {
  width: 100%;
}

.option-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 4px;
}

.option-formats {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 400;
  line-height: 1.4;
}

.format-option.active .option-title {
  color: var(--button-primary);
}

.format-option.active .option-formats {
  color: var(--button-primary);
  font-weight: 500;
}

.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.btn-secondary,
.btn-primary {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: var(--color-background);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background: var(--color-primary-alpha);
  border-color: var(--button-primary);
  color: var(--button-primary);
}

.btn-primary {
  background: var(--button-primary);
  color: var(--button-primaryText);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 滚动条样式 */
.form-content::-webkit-scrollbar {
  width: 6px;
}

.form-content::-webkit-scrollbar-track {
  background: var(--color-surface);
}

.form-content::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 3px;
}

/* 步骤指示器 */
.steps-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background);
  border: 2px solid var(--color-border);
  color: var(--color-text-secondary);
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s;
}

.step-item.active .step-circle {
  background: var(--button-primary);
  border-color: var(--button-primary);
  color: white;
}

.step-item.completed .step-circle {
  background: var(--color-success, #10b981);
  border-color: var(--color-success, #10b981);
  color: white;
}

.step-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  font-weight: 500;
  white-space: nowrap;
}

.step-item.active .step-label {
  color: var(--button-primary);
  font-weight: 600;
}

.step-item.completed .step-label {
  color: var(--color-success, #10b981);
}

.step-line {
  width: 40px;
  height: 2px;
  background: var(--color-border);
  margin-bottom: 20px;
}

/* 上传区域 */
.upload-zone {
  border: 2px dashed var(--color-border);
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: var(--input-background);
}

.upload-zone:hover,
.upload-zone.drag-over {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
}

.upload-zone.has-files {
  cursor: default;
  text-align: left;
  padding: 20px;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 12px;
  color: var(--color-text-secondary);
}

.supported-formats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 12px;
}

.format-tag {
  padding: 4px 10px;
  background: var(--color-primary-alpha);
  color: var(--button-primary);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

/* 文件列表 */
.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.files-header h4 {
  margin: 0;
  font-size: 14px;
  color: var(--color-text);
}

.btn-add-more {
  padding: 6px 12px;
  background: var(--button-primary);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.btn-add-more:hover {
  transform: translateY(-1px);
  box-shadow: var(--button-shadow);
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.file-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.btn-remove {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--color-border);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  font-size: 14px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-remove:hover {
  background: var(--color-error, #ef4444);
  border-color: var(--color-error, #ef4444);
  color: white;
}

/* 配置区域 */
.config-section {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
}

.config-section h4 {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.strategy-options {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.strategy-option {
  flex: 1;
  position: relative;
  cursor: pointer;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
  background: var(--input-background);
  transition: all 0.3s;
}

.strategy-option:hover {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
}

.strategy-option.active {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
}

.strategy-option input[type="radio"] {
  position: absolute;
  opacity: 0;
}

.strategy-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.strategy-icon {
  font-size: 24px;
}

.strategy-info strong {
  display: block;
  font-size: 13px;
  color: var(--color-text);
  margin-bottom: 2px;
}

.strategy-info small {
  font-size: 11px;
  color: var(--color-text-secondary);
}

/* 自定义配置 */
.custom-config {
  padding: 16px;
  margin-top: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

.config-row {
  margin-bottom: 16px;
}

.config-row:last-child {
  margin-bottom: 0;
}

.config-row label {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}

.config-input {
  width: 100%;
  padding: 10px 14px;
  background: var(--input-background);
  border: 2px solid var(--color-border);
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-text);
  transition: all 0.3s;
}

.config-input:hover {
  border-color: var(--button-primary);
}

.config-input:focus {
  outline: none;
  border-color: var(--button-primary);
  box-shadow: 0 0 0 3px var(--input-focus-shadow);
}

.config-hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: var(--color-text-secondary);
  font-style: italic;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 12px;
  background: var(--input-background);
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 13px;
  color: var(--color-text);
  padding: 6px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.checkbox-item:hover {
  background: var(--color-background);
}

.checkbox-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--button-primary);
}

/* 滑块样式 */
.config-range {
  width: 100%;
  height: 6px;
  background: linear-gradient(to right, 
    var(--color-primary-alpha) 0%, 
    var(--color-border) 100%);
  border-radius: 3px;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
  position: relative;
}

.config-range::-webkit-slider-runnable-track {
  width: 100%;
  height: 6px;
  background: var(--color-primary-alpha);
  border-radius: 3px;
}

.config-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  background: var(--button-primary);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.config-range::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 0 4px var(--input-focus-shadow);
}

.config-range::-moz-range-track {
  width: 100%;
  height: 6px;
  background: var(--color-primary-alpha);
  border-radius: 3px;
}

.config-range::-moz-range-thumb {
  width: 20px;
  height: 20px;
  background: var(--button-primary);
  border-radius: 50%;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.config-range::-moz-range-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 0 4px var(--input-focus-shadow);
}

.range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

/* 切片预览 */
.chunks-preview {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.preview-header h4 {
  margin: 0;
  font-size: 14px;
  color: var(--color-text);
}

.preview-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.chunks-list {
  max-height: 400px;
  overflow-y: auto;
}

.chunk-item {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.chunk-index {
  color: var(--button-primary);
  font-weight: 600;
}

.chunk-length {
  color: var(--color-text-secondary);
}

.chunk-content {
  font-size: 13px;
  line-height: 1.6;
  color: var(--color-text);
  margin-bottom: 8px;
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chunk-meta {
  font-size: 11px;
  color: var(--color-text-secondary);
  display: flex;
  gap: 12px;
}

.preview-more {
  text-align: center;
  padding: 12px;
  color: var(--color-text-secondary);
  font-size: 12px;
}

/* 处理视图 */
.processing-view {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.processing-status {
  text-align: center;
  width: 100%;
  max-width: 400px;
}

.spinner-large {
  width: 64px;
  height: 64px;
  border: 4px solid var(--color-border);
  border-top-color: var(--button-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 24px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.processing-status h3 {
  margin: 0 0 8px;
  font-size: 20px;
  color: var(--color-text);
}

.processing-status p {
  margin: 0 0 16px;
  font-size: 24px;
  font-weight: 600;
  color: var(--button-primary);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--button-primary);
  transition: width 0.3s;
}

.final-stats {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-top: 24px;
}

.stat-box {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--button-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
}

/* 异步处理提示 */
.async-notice {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 24px;
  padding: 12px 16px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 8px;
  color: var(--color-text);
  font-size: 13px;
  max-width: 400px;
}

.async-notice svg {
  flex-shrink: 0;
  color: var(--button-primary);
}

.processing-status .async-notice {
  margin-top: 24px;
  background: rgba(59, 130, 246, 0.08);
}
</style>

