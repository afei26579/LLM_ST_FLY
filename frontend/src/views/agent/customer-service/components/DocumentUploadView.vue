<template>
  <div class="upload-view">
    <!-- 头部信息 -->
    <div class="upload-header">
      <div class="header-left">
        <button @click="$emit('back')" class="btn-back">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 19-7-7 7-7"/>
            <path d="M19 12H5"/>
          </svg>
          返回
        </button>
        <div class="kb-info">
          <div class="kb-icon">{{ getFormatIcon(knowledgeBase.format) }}</div>
          <div class="kb-details">
            <h2>{{ knowledgeBase.name }}</h2>
            <p class="kb-format">{{ getFormatLabel(knowledgeBase.format) }}</p>
          </div>
        </div>
      </div>
      <div class="header-right">
        <div class="progress-indicator">
          <span class="step" :class="{ active: currentStep >= 1, completed: currentStep > 1 }">
            <span class="step-number">1</span>
            <span class="step-label">上传文档</span>
          </span>
          <div class="step-divider"></div>
          <span class="step" :class="{ active: currentStep >= 2, completed: currentStep > 2 }">
            <span class="step-number">2</span>
            <span class="step-label">配置处理</span>
          </span>
          <div class="step-divider"></div>
          <span class="step" :class="{ active: currentStep >= 3 }">
            <span class="step-number">3</span>
            <span class="step-label">完成</span>
          </span>
        </div>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="upload-content">
      <!-- 步骤1：上传文档 -->
      <div v-if="currentStep === 1" class="upload-step">
        <div class="upload-zone" 
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
            <div class="upload-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14,2 14,8 20,8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10,9 9,9 8,9"/>
              </svg>
            </div>
            <h3>上传{{ getFormatLabel(knowledgeBase.format) }}文档</h3>
            <p>拖拽文件到此处，或点击选择文件</p>
            <div class="supported-formats">
              <span class="format-tag" v-for="format in getSupportedFormats()" :key="format">
                {{ format }}
              </span>
            </div>
          </div>

          <!-- 已上传文件列表 -->
          <div v-else class="uploaded-files">
            <div class="files-header">
              <h3>已上传文件 ({{ uploadedFiles.length }})</h3>
              <button @click="triggerFileInput" class="btn-add-more">
                ➕ 继续添加
              </button>
            </div>
            <div class="file-list">
              <div 
                v-for="(file, index) in uploadedFiles" 
                :key="index"
                class="file-item"
              >
                <div class="file-icon">{{ getFileIcon(file.type) }}</div>
                <div class="file-info">
                  <div class="file-name">{{ file.name }}</div>
                  <div class="file-meta">
                    {{ formatFileSize(file.size) }} • {{ file.type.toUpperCase() }}
                  </div>
                  <div class="file-status" :class="file.status">
                    <span v-if="file.status === 'uploading'">
                      <div class="spinner-tiny"></div>
                      上传中...
                    </span>
                    <span v-else-if="file.status === 'completed'">
                      ✅ 上传完成
                    </span>
                    <span v-else-if="file.status === 'error'">
                      ❌ 上传失败
                    </span>
                  </div>
                </div>
                <button @click="removeFile(index)" class="btn-remove" :disabled="file.status === 'uploading'">
                  ✕
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤1按钮 -->
        <div class="step-actions">
          <button 
            @click="nextStep" 
            :disabled="uploadedFiles.length === 0 || hasUploadingFiles"
            class="btn-next btn-primary"
          >
            下一步：配置处理
          </button>
        </div>
      </div>

      <!-- 步骤2：配置处理 -->
      <div v-if="currentStep === 2" class="config-step">
        <div class="config-grid">
          <!-- 文档切片配置 -->
          <div class="config-section">
            <h3 class="section-title">
              <span class="section-icon">✂️</span>
              文档切片
            </h3>
            <div class="config-group">
              <label class="config-label">切片策略</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input type="radio" v-model="processingConfig.chunkStrategy" value="auto" />
                  <span class="radio-label">
                    <strong>智能切片</strong>
                    <small>AI自动识别段落和语义边界</small>
                  </span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="processingConfig.chunkStrategy" value="fixed" />
                  <span class="radio-label">
                    <strong>固定长度</strong>
                    <small>按固定字符数切片</small>
                  </span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="processingConfig.chunkStrategy" value="semantic" />
                  <span class="radio-label">
                    <strong>语义切片</strong>
                    <small>按语义相关性切片</small>
                  </span>
                </label>
              </div>
            </div>

            <div v-if="processingConfig.chunkStrategy === 'fixed'" class="config-group">
              <label class="config-label">切片大小</label>
              <div class="input-with-unit">
                <input 
                  type="number" 
                  v-model.number="processingConfig.chunkSize"
                  min="100" 
                  max="2000"
                  class="form-input"
                />
                <span class="input-unit">字符</span>
              </div>
            </div>

            <div class="config-group">
              <label class="config-label">切片重叠</label>
              <div class="input-with-unit">
                <input 
                  type="number" 
                  v-model.number="processingConfig.chunkOverlap"
                  min="0" 
                  :max="Math.floor(processingConfig.chunkSize * 0.5)"
                  class="form-input"
                />
                <span class="input-unit">字符</span>
              </div>
              <p class="config-hint">重叠部分有助于保持上下文连贯性</p>
            </div>
          </div>

          <!-- 文档清洗配置 -->
          <div class="config-section">
            <h3 class="section-title">
              <span class="section-icon">🧹</span>
              文档清洗
            </h3>
            <div class="config-group">
              <label class="config-label">清洗策略</label>
              <div class="radio-group">
                <label class="radio-option">
                  <input type="radio" v-model="processingConfig.cleanStrategy" value="auto" />
                  <span class="radio-label">
                    <strong>智能清洗</strong>
                    <small>AI自动去除无用内容</small>
                  </span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="processingConfig.cleanStrategy" value="basic" />
                  <span class="radio-label">
                    <strong>基础清洗</strong>
                    <small>去除特殊字符和空行</small>
                  </span>
                </label>
                <label class="radio-option">
                  <input type="radio" v-model="processingConfig.cleanStrategy" value="none" />
                  <span class="radio-label">
                    <strong>不清洗</strong>
                    <small>保持原始内容</small>
                  </span>
                </label>
              </div>
            </div>

            <!-- 自定义清洗规则 -->
            <div v-if="processingConfig.cleanStrategy !== 'none'" class="config-group">
              <label class="config-label">自定义规则（可选）</label>
              <div class="custom-rules">
                <div v-for="(rule, index) in processingConfig.customRules" :key="index" class="rule-item">
                  <input 
                    v-model="rule.pattern" 
                    placeholder="正则表达式"
                    class="rule-input"
                  />
                  <input 
                    v-model="rule.replacement" 
                    placeholder="替换为"
                    class="rule-input"
                  />
                  <button @click="removeRule(index)" class="btn-remove-rule">✕</button>
                </div>
                <button @click="addRule" class="btn-add-rule">➕ 添加规则</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤2按钮 -->
        <div class="step-actions">
          <button @click="prevStep" class="btn-prev">上一步</button>
          <button @click="startProcessing" class="btn-next btn-primary" :disabled="isProcessing">
            <span v-if="!isProcessing">开始处理</span>
            <span v-else>
              <div class="spinner-small"></div>
              处理中...
            </span>
          </button>
        </div>
      </div>

      <!-- 步骤3：处理结果 -->
      <div v-if="currentStep === 3" class="result-step">
        <div class="result-content">
          <div class="success-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22,4 12,14.01 9,11.01"/>
            </svg>
          </div>
          <h2>处理完成！</h2>
          <p>文档已成功上传并处理完毕</p>
          
          <div class="result-stats">
            <div class="stat-item">
              <div class="stat-number">{{ uploadedFiles.length }}</div>
              <div class="stat-label">文档数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ processingResult.totalChunks }}</div>
              <div class="stat-label">切片数量</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ processingResult.totalTokens }}</div>
              <div class="stat-label">Token数量</div>
            </div>
          </div>
        </div>

        <!-- 步骤3按钮 -->
        <div class="step-actions">
          <button @click="$emit('complete')" class="btn-complete btn-primary">
            完成配置
          </button>
          <button @click="uploadMore" class="btn-secondary">
            继续上传
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'

interface Props {
  knowledgeBase: {
    id: number
    name: string
    format: string
    description?: string
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  back: []
  complete: []
}>()

const toast = useToast()

// 状态
const currentStep = ref(1)
const isDragOver = ref(false)
const isProcessing = ref(false)
const uploadedFiles = ref<any[]>([])
const fileInput = ref<HTMLInputElement>()

// 处理配置
const processingConfig = ref({
  chunkStrategy: 'auto',
  chunkSize: 500,
  chunkOverlap: 50,
  cleanStrategy: 'auto',
  customRules: [] as { pattern: string; replacement: string }[]
})

// 处理结果
const processingResult = ref({
  totalChunks: 0,
  totalTokens: 0
})

// 计算属性
const hasUploadingFiles = computed(() => {
  return uploadedFiles.value.some(file => file.status === 'uploading')
})

// 格式相关方法
const getFormatIcon = (format: string) => {
  const icons = {
    text: '📝',
    structured: '📊', 
    image: '🖼️'
  }
  return icons[format as keyof typeof icons] || '📄'
}

const getFormatLabel = (format: string) => {
  const labels = {
    text: '文本格式',
    structured: '结构化格式',
    image: '图片格式'
  }
  return labels[format as keyof typeof labels] || '未知格式'
}

const getSupportedFormats = () => {
  const formats = {
    text: ['PDF', 'DOCX', 'TXT', 'MD'],
    structured: ['CSV', 'JSON', 'XML', 'XLSX', 'HTML'],
    image: ['PNG', 'JPG', 'JPEG', 'GIF', 'WEBP']
  }
  return formats[props.knowledgeBase.format as keyof typeof formats] || []
}

const getAcceptTypes = () => {
  const accepts = {
    text: '.pdf,.docx,.txt,.md',
    structured: '.csv,.json,.xml,.xlsx,.html',
    image: '.png,.jpg,.jpeg,.gif,.webp'
  }
  return accepts[props.knowledgeBase.format as keyof typeof accepts] || '*'
}

const getFileIcon = (type: string) => {
  const ext = type.split('.').pop()?.toLowerCase() || ''
  const icons: Record<string, string> = {
    pdf: '📄', docx: '📝', txt: '📃', md: '📑',
    csv: '📊', json: '🔧', xml: '⚙️', xlsx: '📈', html: '🌐',
    png: '🖼️', jpg: '📷', jpeg: '📷', gif: '🎭', webp: '🖼️'
  }
  return icons[ext] || '📄'
}

// 文件处理方法
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    handleFiles(Array.from(target.files))
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = false
  
  if (event.dataTransfer?.files) {
    handleFiles(Array.from(event.dataTransfer.files))
  }
}

const handleFiles = (files: File[]) => {
  const supportedFormats = getSupportedFormats().map(f => f.toLowerCase())
  
  files.forEach(file => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (!ext || !supportedFormats.some(format => ext.includes(format.toLowerCase()))) {
      toast.error(`不支持的文件格式: ${file.name}`)
      return
    }

    const fileItem = {
      name: file.name,
      size: file.size,
      type: ext,
      file: file,
      status: 'uploading'
    }

    uploadedFiles.value.push(fileItem)
    
    // 模拟上传
    setTimeout(() => {
      fileItem.status = 'completed'
    }, 1000 + Math.random() * 2000)
  })
}

const removeFile = (index: number) => {
  uploadedFiles.value.splice(index, 1)
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 步骤控制
const nextStep = () => {
  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const startProcessing = async () => {
  isProcessing.value = true
  
  try {
    // 模拟处理过程
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // 模拟结果
    processingResult.value = {
      totalChunks: uploadedFiles.value.length * 15,
      totalTokens: uploadedFiles.value.length * 2500
    }
    
    currentStep.value = 3
    toast.success('文档处理完成!')
  } catch (error) {
    toast.error('处理失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

const uploadMore = () => {
  currentStep.value = 1
}

// 自定义规则管理
const addRule = () => {
  processingConfig.value.customRules.push({
    pattern: '',
    replacement: ''
  })
}

const removeRule = (index: number) => {
  processingConfig.value.customRules.splice(index, 1)
}
</script>

<style scoped>
.upload-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-background);
}

/* 头部 */
.upload-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  color: var(--color-text);
  transition: all 0.3s;
}

.btn-back:hover {
  border-color: var(--button-primary);
  color: var(--button-primary);
}

.kb-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kb-icon {
  font-size: 40px;
}

.kb-details h2 {
  margin: 0;
  font-size: 20px;
  color: var(--color-text);
}

.kb-format {
  margin: 4px 0 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

/* 进度指示器 */
.progress-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  opacity: 0.5;
  transition: all 0.3s;
}

.step.active {
  opacity: 1;
  color: var(--button-primary);
}

.step.completed {
  opacity: 1;
  color: var(--color-success);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-border);
  color: var(--color-text-secondary);
  font-weight: 600;
}

.step.active .step-number {
  background: var(--button-primary);
  color: white;
}

.step.completed .step-number {
  background: var(--color-success);
  color: white;
}

.step-label {
  font-size: 12px;
  font-weight: 500;
}

.step-divider {
  width: 40px;
  height: 2px;
  background: var(--color-border);
}

/* 内容区域 */
.upload-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* 上传区域 */
.upload-zone {
  border: 2px dashed var(--color-border);
  border-radius: 16px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: var(--color-surface);
}

.upload-zone:hover,
.upload-zone.drag-over {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  color: var(--color-text-secondary);
}

.upload-placeholder h3 {
  margin: 0;
  font-size: 20px;
  color: var(--color-text);
}

.upload-placeholder p {
  margin: 0;
  color: var(--color-text-secondary);
}

.supported-formats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

.format-tag {
  padding: 4px 12px;
  background: var(--color-primary-alpha);
  color: var(--button-primary);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

/* 文件列表 */
.uploaded-files {
  text-align: left;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.files-header h3 {
  margin: 0;
  color: var(--color-text);
}

.btn-add-more {
  padding: 8px 16px;
  background: var(--button-primary);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 12px;
}

.file-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
}

.file-name {
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 4px;
}

.file-meta {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.file-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.file-status.completed {
  color: var(--color-success);
}

.file-status.error {
  color: var(--color-error);
}

.btn-remove {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: transparent;
  border: 1px solid var(--color-border);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all 0.3s;
}

.btn-remove:hover:not(:disabled) {
  background: var(--color-error);
  border-color: var(--color-error);
  color: white;
}

.btn-remove:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 配置步骤 */
.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 32px;
}

.config-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 24px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
}

.section-icon {
  font-size: 24px;
}

.config-group {
  margin-bottom: 24px;
}

.config-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--color-text);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.radio-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.radio-option:hover {
  border-color: var(--button-primary);
  background: var(--color-primary-alpha);
}

.radio-option input[type="radio"] {
  margin-top: 2px;
}

.radio-label {
  flex: 1;
}

.radio-label strong {
  display: block;
  color: var(--color-text);
  margin-bottom: 4px;
}

.radio-label small {
  color: var(--color-text-secondary);
  font-size: 12px;
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 8px;
}

.input-unit {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.config-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--color-text-secondary);
}

/* 自定义规则 */
.custom-rules {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rule-item {
  display: flex;
  gap: 8px;
}

.rule-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 12px;
}

.btn-remove-rule {
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.btn-add-rule {
  align-self: flex-start;
  padding: 8px 12px;
  background: transparent;
  border: 1px dashed var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  color: var(--color-text-secondary);
}

/* 结果步骤 */
.result-content {
  text-align: center;
  padding: 40px;
}

.success-icon {
  color: var(--color-success);
  margin-bottom: 24px;
}

.result-content h2 {
  margin: 0 0 12px;
  color: var(--color-text);
}

.result-content p {
  margin: 0 0 32px;
  color: var(--color-text-secondary);
}

.result-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin-bottom: 32px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--button-primary);
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

/* 步骤按钮 */
.step-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.btn-prev,
.btn-next,
.btn-complete,
.btn-secondary {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  justify-content: center;
}

.btn-prev,
.btn-secondary {
  background: var(--color-background);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.btn-prev:hover,
.btn-secondary:hover {
  border-color: var(--button-primary);
  color: var(--button-primary);
}

.btn-next,
.btn-complete {
  background: var(--button-primary);
  border: 1px solid var(--button-primary);
  color: white;
}

.btn-next:hover:not(:disabled),
.btn-complete:hover:not(:disabled) {
  background: var(--button-primary);
  transform: translateY(-2px);
  box-shadow: var(--button-shadow);
}

.btn-next:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 加载动画 */
.spinner-tiny,
.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner-small {
  width: 20px;
  height: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 1200px) {
  .config-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }
}

@media (max-width: 768px) {
  .upload-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .progress-indicator {
    align-self: stretch;
    justify-content: center;
  }
  
  .result-stats {
    flex-direction: column;
    gap: 20px;
  }
}
</style>
