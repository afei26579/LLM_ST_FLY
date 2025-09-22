<template>
  <div class="ai-image-view">
    <div class="page-header">
      <h1 class="page-title">AI 图像生成</h1>
    
    </div>
    
    <div class="content-container">
      <!-- 图像生成主界面 -->
      <div class="generation-section">
        <div class="input-panel">
          <div class="prompt-section">
            <div class="prompt-group">
              <label for="prompt" class="input-label">
                <span class="label-text">正向提示词</span>
                <span class="required">*</span>
              </label>
              
              <!-- 提示词结构说明 -->
              <div class="prompt-structure">
                <span class="structure-text">提示词 = </span>
                <span class="structure-item" @mouseenter="showTooltip = 'subject'" @mouseleave="showTooltip = ''">主体</span>
                <span class="structure-text"> + </span>
                <span class="structure-item" @mouseenter="showTooltip = 'scene'" @mouseleave="showTooltip = ''">场景</span>
                <span class="structure-text"> + </span>
                <span class="structure-item" @mouseenter="showTooltip = 'style'" @mouseleave="showTooltip = ''">风格</span>
                <span class="structure-text"> + </span>
                <span class="structure-item" @mouseenter="showTooltip = 'camera'" @mouseleave="showTooltip = ''">镜头语言</span>
                <span class="structure-text"> + </span>
                <span class="structure-item" @mouseenter="showTooltip = 'atmosphere'" @mouseleave="showTooltip = ''">氛围词</span>
                <span class="structure-text"> + </span>
                <span class="structure-item" @mouseenter="showTooltip = 'details'" @mouseleave="showTooltip = ''">细节修饰</span>
                
                <!-- 悬停提示框 -->
                <div v-if="showTooltip" class="tooltip" :class="`tooltip-${showTooltip}`">
                  <div v-if="showTooltip === 'subject'" class="tooltip-content">
                    <h4>主体描述</h4>
                    <p>确定主体清晰地描述图像中的主体，包括其特征、动作等。例如，"一个可爱的10岁中国小女孩，穿着红色衣服"。</p>
        </div>
        
                  <div v-if="showTooltip === 'scene'" class="tooltip-content">
                    <h4>场景描述</h4>
                    <p>场景描述是对主体所处环境特征细节的描述，可通过形容词或短句列举。</p>
                  </div>
                  
                  <div v-if="showTooltip === 'style'" class="tooltip-content">
                    <h4>定义风格</h4>
                    <p>定义风格是明确地描述图像所应具有的特定艺术风格、表现手法或视觉特征。例如，"水彩风格"、"漫画风格"常见风格化详见下方高级设置。</p>
                  </div>
                  
                  <div v-if="showTooltip === 'camera'" class="tooltip-content">
                    <h4>镜头语言</h4>
                    <p>镜头语言包含景别、视角等，常见镜头语言详见提示词词典。</p>
                  </div>
                  
                  <div v-if="showTooltip === 'atmosphere'" class="tooltip-content">
                    <h4>氛围词</h4>
                    <p>氛围词是对预期画面氛围的描述，例如"梦幻"、"孤独"、"宏伟"，常见氛围词详见下方高级设置。</p>
                  </div>
                  
                  <div v-if="showTooltip === 'details'" class="tooltip-content">
                    <h4>细节修饰</h4>
                    <p>细节修饰是对画面进一步的精细化和优化，以增强图像的细节表现力、丰富度和美感。例如"光源的位置"、"道具搭配"、"环境细节"，"高分辨率"等。</p>
                  </div>
                </div>
              </div>
            <textarea 
                id="prompt"
                v-model="formData.prompt" 
                placeholder="请详细描述您想要生成的图片内容，例如：一只可爱的小猫坐在阳光明媚的花园里，周围有五彩斑斓的花朵..."
                rows="4"
                maxlength="2000"
                class="prompt-textarea"
            ></textarea>
              <div class="char-count">{{ formData.prompt.length }}/2000</div>
          </div>
          
            <div class="prompt-group">
              <label for="negativePrompt" class="input-label">
                <span class="label-text">反向提示词</span>
                <span class="optional">（可选）</span>
              </label>
              <textarea 
                id="negativePrompt"
                v-model="formData.negative_prompt" 
                placeholder="描述不希望在图片中出现的内容，例如：模糊、低质量、多余的手指、噪点..."
                rows="2"
                maxlength="1000"
                class="prompt-textarea negative"
              ></textarea>
              <div class="char-count">{{ formData.negative_prompt.length }}/1000</div>
            </div>
          </div>

          <!-- 基础设置 -->
          <div class="basic-settings">
            <div class="settings-row">
              <div class="setting-group size-group">
                <label class="input-label">
                  图像尺寸
                  <div class="aspect-ratio-icon inline-icon" :class="getAspectRatioClass(formData.size)"></div>
                </label>
                <div class="size-selector">
                  <div class="selected-size" @click="showSizeDropdown = !showSizeDropdown">
                    <div class="size-option-content">
                      <span class="size-text">{{ getSizeLabel(formData.size) }}</span>
                    </div>
                    <span class="dropdown-arrow" :class="{ 'rotated': showSizeDropdown }">▼</span>
                  </div>
                  <div v-show="showSizeDropdown" class="size-dropdown">
                    <div 
                      v-for="size in presets.sizes" 
                      :key="size.value" 
                      :value="size.value"
                      class="size-option"
                      :class="{ 'selected': formData.size === size.value }"
                      @click="selectSize(size.value)"
                    >
                      <div class="size-details">
                        <span class="size-label">{{ size.label }}</span>
                        <div class="aspect-ratio-icon" :class="getAspectRatioClass(size.value)"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
            </div>

            <div class="settings-row">
            <div class="setting-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="formData.prompt_extend" />
                  <span class="checkmark"></span>
                  启用智能改写
                 
                </label>
              </div>
              
              <div class="setting-group">
                <label class="checkbox-label">
                  <input type="checkbox" v-model="formData.watermark" />
                  <span class="checkmark"></span>
                  添加水印
                  
                </label>
              </div>
            </div>
          </div>

          <!-- 高级参数设置 -->
          <div class="advanced-settings">
            <div class="settings-header" @click="showAdvanced = !showAdvanced">
              <span>高级设置</span>
              <span class="toggle-icon" :class="{ 'rotated': showAdvanced }">▼</span>
            </div>
            
            <div v-show="showAdvanced" class="advanced-content">
              <div class="settings-grid">
                <div class="setting-group">
                  <label class="input-label">风格</label>
                  <select v-model="formData.style" class="select-input">
                    <option v-for="style in presets.styles" :key="style.value" :value="style.value">
                      {{ style.label }}
                    </option>
              </select>
            </div>
            
            <div class="setting-group">
                  <label class="input-label">景别</label>
                  <select v-model="formData.shot_type" class="select-input">
                    <option v-for="shot in presets.shot_types" :key="shot.value" :value="shot.value">
                      {{ shot.label }}
                    </option>
              </select>
            </div>
                
                <div class="setting-group">
                  <label class="input-label">视角</label>
                  <select v-model="formData.angle" class="select-input">
                    <option v-for="angle in presets.angles" :key="angle.value" :value="angle.value">
                      {{ angle.label }}
                    </option>
                  </select>
          </div>
          
                <div class="setting-group">
                  <label class="input-label">拍摄技法</label>
                  <select v-model="formData.shooting_technique" class="select-input">
                    <option v-for="technique in presets.shooting_techniques" :key="technique.value" :value="technique.value">
                      {{ technique.label }}
                    </option>
                  </select>
                </div>
                
                <div class="setting-group">
                  <label class="input-label">光线效果</label>
                  <select v-model="formData.lighting" class="select-input">
                    <option v-for="light in presets.lighting" :key="light.value" :value="light.value">
                      {{ light.label }}
                    </option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- 生成按钮 -->
          <div class="action-section">
            <button 
              class="generate-btn" 
              @click="generateImage" 
              :disabled="!canGenerate || generating"
              :class="{ 'generating': generating }"
            >
              <span v-if="generating" class="loading-text">
                <span class="spinner"></span>
                生成中...
              </span>
              <span v-else>✨ 生成图像</span>
            </button>
          </div>
          </div>
          
        <!-- 结果展示区域 -->
        <div class="result-panel">
          <div v-if="generatedImages.length > 0" class="result-section">
            <div class="result-header">
            <h3>生成结果</h3>
              <div class="result-info">
                <span>{{ generatedImages.length }}张图片</span>
                <button @click="clearResults" class="clear-btn">清空</button>
              </div>
            </div>
            
            <div class="image-gallery">
              <div 
                v-for="(image, index) in generatedImages" 
                :key="index" 
                class="image-item"
                @click="openImageModal(image)"
              >
                <div class="image-container">
                  <img :src="image.saved_url || image.original_url" :alt="image.orig_prompt" loading="lazy" />
                <div class="image-overlay">
                    <div class="image-actions">
                      <button class="action-btn download" @click.stop="downloadImage(image)" title="下载">
                        📥
                      </button>
                      <button class="action-btn view" @click.stop="openImageModal(image)" title="查看大图">
                        🔍
                  </button>
                </div>
              </div>
            </div>
                <div class="image-info">
                  <p class="image-prompt">{{ image.orig_prompt || formData.prompt }}</p>
                  <div class="image-meta">
                    <span class="file-size">{{ formatFileSize(image.size) }}</span>
                    <span class="download-time">{{ formatTime(image.download_time) }}</span>
          </div>
        </div>
      </div>
        </div>
        </div>
        
          <!-- 空状态 -->
          <div v-else class="empty-state">
            <div class="empty-icon">🎨</div>
            <h3>开始创作您的第一张AI图像</h3>
            <p>在左侧输入您的创意描述，选择合适的参数，然后点击生成按钮</p>
        </div>
      </div>
    </div>
    
      <!-- 图像预览模态框 -->
      <div v-if="selectedImage" class="image-modal" @click="closeImageModal">
      <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>图像详情</h3>
        <button class="close-btn" @click="closeImageModal">×</button>
      </div>
          <div class="modal-body">
            <img :src="selectedImage.saved_url || selectedImage.original_url" :alt="selectedImage.orig_prompt" />
            <div class="image-details">
              <div class="detail-item">
                <label>原始提示词：</label>
                <p>{{ selectedImage.orig_prompt }}</p>
              </div>
              <div class="detail-item" v-if="selectedImage.actual_prompt">
                <label>增强提示词：</label>
                <p>{{ selectedImage.actual_prompt }}</p>
              </div>
              <div class="detail-item">
                <label>文件大小：</label>
                <p>{{ formatFileSize(selectedImage.size) }}</p>
              </div>
              <div class="detail-item">
                <label>生成时间：</label>
                <p>{{ formatTime(selectedImage.download_time) }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="downloadImage(selectedImage)" class="download-btn-modal">
              下载图片
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '../../services/api'
import type { ImageGenerationRequest, ImagePresets } from '../../services/api'

const toast = useToast()

// 响应式数据
const generating = ref(false)
const showAdvanced = ref(false)
const showSizeDropdown = ref(false)
const showTooltip = ref('')
const generatedImages = ref<any[]>([])
const selectedImage = ref<any>(null)

// 表单数据
const formData = reactive({
  prompt: '',
  negative_prompt: '',
  size: '1328*1328',
  prompt_extend: true,
  watermark: true,
  style: '',
  shot_type: '',
  angle: '',
  shooting_technique: '',
  lighting: ''
})

// 预设参数
const presets = ref<ImagePresets>({
  sizes: [],
  styles: [],
  shot_types: [],
  angles: [],
  shooting_techniques: [],
  lighting: []
})

// 计算属性
const canGenerate = computed(() => {
  return formData.prompt.trim().length > 0 && !generating.value
})

// 方法
const loadPresets = async () => {
  try {
    const response = await apiService.getImagePresets()
    
    if (response.code === 200) {
      presets.value = response.data
    } else {
      throw new Error(response.message)
    }
  } catch (error) {
    console.error('加载预设参数失败:', error)
    // 使用默认预设
    presets.value = {
      sizes: [
        { value: '1328*1328', label: '1:1 (1328x1328)', aspect_ratio: '1:1' },
        { value: '1664*928', label: '16:9 (1664x928)', aspect_ratio: '16:9' },
        { value: '928*1664', label: '9:16 (928x1664)', aspect_ratio: '9:16' },
        { value: '1472*1140', label: '4:3 (1472x1140)', aspect_ratio: '4:3' },
        { value: '1140*1472', label: '3:4 (1140x1472)', aspect_ratio: '3:4' }
      ],
      styles: [
        { value: '', label: '默认' },
        { value: '3d_cartoon', label: '3D卡通' },
        { value: 'wasteland', label: '废土风' },
        { value: 'pointillism', label: '点彩画' },
        { value: 'surreal', label: '超现实' },
        { value: 'watercolor', label: '水彩' },
        { value: 'clay', label: '粘土' },
        { value: 'realistic', label: '写实' },
        { value: 'ceramic', label: '陶瓷' },
        { value: '3d', label: '3D' },
        { value: 'ink_wash', label: '水墨' },
        { value: 'origami', label: '折纸' },
        { value: 'meticulous', label: '工笔' },
        { value: 'chinese_style', label: '国风水墨' }
      ],
      shot_types: [
        { value: '', label: '默认' },
        { value: 'long_shot', label: '远景' },
        { value: 'full_shot', label: '全景' },
        { value: 'medium_shot', label: '中景' },
        { value: 'close_up', label: '近景' },
        { value: 'extreme_close_up', label: '特写' }
      ],
      angles: [
        { value: '', label: '默认' },
        { value: 'eye_level', label: '平视' },
        { value: 'high_angle', label: '俯视' },
        { value: 'low_angle', label: '仰视' },
        { value: 'aerial', label: '航拍' }
      ],
      shooting_techniques: [
        { value: '', label: '默认' },
        { value: 'macro', label: '微距' },
        { value: 'ultra_wide', label: '超广角' },
        { value: 'telephoto', label: '长焦' },
        { value: 'fisheye', label: '鱼眼' }
      ],
      lighting: [
        { value: '', label: '默认' },
        { value: 'natural', label: '自然光' },
        { value: 'backlight', label: '逆光' },
        { value: 'neon', label: '霓虹灯' },
        { value: 'ambient', label: '氛围光' }
      ]
    }
  }
}

const generateImage = async () => {
  if (!canGenerate.value) return
  
  generating.value = true
  
  try {
    const requestData: ImageGenerationRequest = {
      prompt: formData.prompt,
      negative_prompt: formData.negative_prompt || undefined,
      size: formData.size,
      n: 1,
      prompt_extend: formData.prompt_extend,
      watermark: formData.watermark,
      style: formData.style || undefined,
      shot_type: formData.shot_type || undefined,
      angle: formData.angle || undefined,
      shooting_technique: formData.shooting_technique || undefined,
      lighting: formData.lighting || undefined
    }
    
    const response = await apiService.generateImage(requestData)
    
    if (response.code === 200) {
      const result = response.data
      if (result.images && result.images.length > 0) {
        generatedImages.value.unshift(...result.images)
        toast.success(`成功生成 ${result.images.length} 张图片！`)
      } else {
        toast.warning('图片生成成功，但没有返回图片数据')
      }
    } else {
      throw new Error(response.message || '生成失败')
    }
  } catch (error: any) {
    console.error('图片生成失败:', error)
    const errorMsg = error.message || '生成图片时发生错误'
    toast.error(errorMsg)
  } finally {
    generating.value = false
  }
}

const downloadImage = async (image: any) => {
  try {
    const imageUrl = image.saved_url || image.original_url
    const response = await fetch(imageUrl)
    const blob = await response.blob()
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.style.display = 'none'
    link.href = url
    link.download = image.filename || `ai-image-${Date.now()}.png`
    
    document.body.appendChild(link)
    link.click()
    
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)
    
    toast.success('图片下载成功！')
  } catch (error) {
    console.error('下载图片失败:', error)
    toast.error('下载图片失败，请稍后重试')
  }
}

const openImageModal = (image: any) => {
  selectedImage.value = image
}

const closeImageModal = () => {
  selectedImage.value = null
}

const clearResults = () => {
  generatedImages.value = []
  toast.info('已清空生成结果')
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '未知'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return '未知'
  try {
    const date = new Date(timeStr)
    return date.toLocaleString()
  } catch {
    return timeStr
  }
}

// 尺寸选择相关方法
const selectSize = (size: string) => {
  formData.size = size
  showSizeDropdown.value = false
}

const getSizeLabel = (size: string) => {
  const sizeOption = presets.value.sizes.find(s => s.value === size)
  return sizeOption?.label || size
}

const getAspectRatioClass = (size: string) => {
  const sizeOption = presets.value.sizes.find(s => s.value === size)
  const ratio = sizeOption?.aspect_ratio || ''
  
  switch (ratio) {
    case '1:1':
      return 'ratio-square'
    case '16:9':
      return 'ratio-landscape'
    case '9:16':
      return 'ratio-portrait'
    case '4:3':
      return 'ratio-landscape-43'
    case '3:4':
      return 'ratio-portrait-34'
    default:
      return 'ratio-square'
  }
}

// 点击外部关闭下拉框
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.size-selector')) {
    showSizeDropdown.value = false
  }
}

// 生命周期
onMounted(() => {
  loadPresets()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.ai-image-view {
  min-height: 100vh;
  background-color: var(--color-background);
  color: var(--color-text);
  padding: 2rem;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--color-text);
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.page-description {
  font-size: 1.2rem;
  color: var(--color-textSecondary);
  margin-bottom: 0;
}

.content-container {
  max-width: 1400px;
  margin: 0 auto;
}

.generation-section {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 2rem;
  background-color: var(--card-background);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: var(--card-shadow);
}

.input-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.prompt-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.prompt-group {
  position: relative;
}

.input-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-text);
}

/* 标签内的内联比例图标 */
.input-label .inline-icon {
  display: inline-block;
  margin-left: 0.5rem;
  vertical-align: middle;
}

/* 内联图标尺寸调整 */
.inline-icon.aspect-ratio-icon {
  width: 24px;
  height: 16px;
}

.inline-icon.ratio-square {
  width: 16px;
  height: 16px;
}

.inline-icon.ratio-landscape {
  width: 24px;
  height: 14px;
}

.inline-icon.ratio-portrait {
  width: 14px;
  height: 24px;
}

.inline-icon.ratio-landscape-43 {
  width: 21px;
  height: 16px;
}

.inline-icon.ratio-portrait-34 {
  width: 16px;
  height: 21px;
}

.label-text {
  font-size: 0.9rem;
}

.required {
  color: var(--color-error);
  font-size: 0.8rem;
}

.optional {
  color: var(--color-textSecondary);
  font-size: 0.8rem;
}

.prompt-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--color-border);
  border-radius: 10px;
  font-size: 0.9rem;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.2s;
  background-color: var(--color-background);
  color: var(--color-text);
}

.prompt-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.prompt-textarea.negative {
  border-color: rgba(var(--color-error-rgb), 0.3);
}

.prompt-textarea.negative:focus {
  border-color: var(--color-error);
  box-shadow: 0 0 0 3px rgba(var(--color-error-rgb), 0.1);
}

.char-count {
  position: absolute;
  bottom: 0.5rem;
  right: 0.75rem;
  font-size: 0.75rem;
  color: var(--color-textSecondary);
  background-color: var(--color-background);
  padding: 0 0.25rem;
}

/* 提示词结构说明样式 */
.prompt-structure {
  position: relative;
  margin-bottom: 0.75rem;
  padding: 0.75rem;
  background-color: rgba(var(--color-primary-rgb), 0.05);
  border: 1px solid rgba(var(--color-primary-rgb), 0.1);
  border-radius: 8px;
  font-size: 0.85rem;
  line-height: 1.5;
}

.structure-text {
  color: var(--color-textSecondary);
  font-weight: 500;
}

.structure-item {
  color: var(--color-primary);
  font-weight: 600;
  cursor: help;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.structure-item:hover {
  background-color: rgba(var(--color-primary-rgb), 0.1);
  transform: translateY(-1px);
}

/* 悬停提示框样式 */
.tooltip {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 1000;
  margin-top: 0.5rem;
  background-color: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  overflow: hidden;
  animation: fadeIn 0.2s ease;
}

.tooltip-content {
  padding: 1rem;
}

.tooltip-content h4 {
  margin: 0 0 0.5rem 0;
  color: var(--color-primary);
  font-size: 0.9rem;
  font-weight: 600;
}

.tooltip-content p {
  margin: 0;
  color: var(--color-text);
  font-size: 0.8rem;
  line-height: 1.4;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.basic-settings {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.settings-row {
  display: flex;
  gap: 1rem;
}

.setting-group {
  flex: 1;
}

/* 图像尺寸设置 */
.size-group {
  flex: 1;
}

.select-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--color-border);
  border-radius: 10px;
  font-size: 0.9rem;
  background-color: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
  transition: border-color 0.2s;
}

.select-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.1);
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--color-text);
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}

.checkbox-label small {
  display: block;
  color: var(--color-textSecondary);
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

/* 自定义尺寸选择器样式 */
.size-selector {
  position: relative;
  width: 100%;
}

.selected-size {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid var(--color-border);
  border-radius: 10px;
  background-color: var(--color-background);
  color: var(--color-text);
  cursor: pointer;
  transition: border-color 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-size:hover {
  border-color: var(--color-primary);
}

.size-option-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.dropdown-arrow {
  transition: transform 0.2s;
  color: var(--color-textSecondary);
  font-size: 0.8rem;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.size-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  box-shadow: var(--card-shadow);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 4px;
}

.size-option {
  padding: 0.75rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid var(--color-border);
}

.size-option:last-child {
  border-bottom: none;
}

.size-option:hover {
  background-color: var(--color-surface);
}

.size-option.selected {
  background-color: rgba(var(--color-primary-rgb), 0.1);
  color: var(--color-primary);
}

.size-details {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.size-label {
  font-weight: 500;
  font-size: 0.9rem;
  flex: 1;
  text-align: left;
}

/* 下拉框中的比例图标对齐 */
.size-option .aspect-ratio-icon {
  flex-shrink: 0;
  margin-left: 0.75rem;
}

/* 比例示意图样式 */
.aspect-ratio-icon {
  width: 32px;
  height: 20px;
  border: 2px solid var(--color-primary);
  border-radius: 3px;
  position: relative;
  background-color: rgba(var(--color-primary-rgb), 0.1);
  flex-shrink: 0;
}

/* 1:1 正方形 */
.ratio-square {
  width: 20px;
  height: 20px;
}

/* 16:9 横向长方形 */
.ratio-landscape {
  width: 32px;
  height: 18px;
}

/* 9:16 竖向长方形 */
.ratio-portrait {
  width: 18px;
  height: 32px;
}

/* 4:3 横向 */
.ratio-landscape-43 {
  width: 28px;
  height: 21px;
}

/* 3:4 竖向 */
.ratio-portrait-34 {
  width: 21px;
  height: 28px;
}

.advanced-settings {
  border-top: 1px solid var(--color-border);
  padding-top: 1rem;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 0.5rem 0;
  font-weight: 600;
  color: var(--color-text);
}

.toggle-icon {
  transition: transform 0.2s;
}

.toggle-icon.rotated {
  transform: rotate(180deg);
}

.advanced-content {
  margin-top: 1rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.action-section {
  margin-top: 1rem;
}

.generate-btn {
  width: 100%;
  padding: 1rem;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  border-radius: 15px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.generate-btn:hover:not(:disabled) {
  background: var(--button-primaryHover);
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(var(--color-primary-rgb), 0.3);
}

.generate-btn:disabled {
  background: var(--button-primaryDisabled);
  color: var(--button-disabledText);
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.generate-btn.generating {
  background: var(--button-primaryDisabled);
  color: var(--button-disabledText);
}

.loading-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.result-panel {
  display: flex;
  flex-direction: column;
  min-height: 600px;
}

.result-section {
  flex: 1;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.result-header h3 {
  margin: 0;
  color: var(--color-text);
  font-size: 1.5rem;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
  color: var(--color-textSecondary);
}

.clear-btn {
  padding: 0.5rem 1rem;
  background: var(--button-error);
  color: var(--button-errorText);
  border: none;
  border-radius: 8px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s;
}

.clear-btn:hover {
  background: var(--button-errorHover);
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.image-item {
  background-color: var(--card-background);
  border: 1px solid var(--card-border);
  border-radius: 15px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.image-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.image-container {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.image-item:hover .image-container img {
  transform: scale(1.05);
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.image-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  width: 40px;
  height: 40px;
  background: rgba(255,255,255,0.9);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: transform 0.2s, background 0.2s;
}

.action-btn:hover {
  transform: scale(1.1);
  background: white;
}

.image-info {
  padding: 1rem;
}

.image-prompt {
  font-size: 0.85rem;
  color: var(--color-text);
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.image-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-textSecondary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  text-align: center;
  color: var(--color-textSecondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.empty-state p {
  max-width: 300px;
  line-height: 1.6;
  color: var(--color-textSecondary);
}

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal-content {
  background-color: var(--card-background);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  max-width: 800px;
  max-height: 90vh;
  overflow: auto;
  display: flex;
  flex-direction: column;
  box-shadow: var(--card-shadow);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h3 {
  margin: 0;
  color: var(--color-text);
}

.close-btn {
  width: 32px;
  height: 32px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--color-textSecondary);
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: var(--color-background);
}

.modal-body {
  padding: 1.5rem;
}

.modal-body img {
  width: 100%;
  height: auto;
  border-radius: 10px;
  margin-bottom: 1.5rem;
}

.image-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-item label {
  font-weight: 600;
  color: var(--color-text);
  display: block;
  margin-bottom: 0.25rem;
}

.detail-item p {
  margin: 0;
  color: var(--color-textSecondary);
  line-height: 1.5;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
}

.download-btn-modal {
  padding: 0.75rem 1.5rem;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, background-color 0.2s;
}

.download-btn-modal:hover {
  background: var(--button-primaryHover);
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .generation-section {
    grid-template-columns: 1fr;
    gap: 2rem;
  }
  
  .input-panel {
    order: 1;
  }
  
  .result-panel {
    order: 2;
    min-height: 400px;
  }
}

@media (max-width: 768px) {
  .ai-image-view {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .generation-section {
    padding: 1.5rem;
  }
  
  .settings-row {
    flex-direction: column;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  /* 移动端图像尺寸设置 */
  .size-group {
    flex: 1;
    min-width: auto;
  }
  
  .image-gallery {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem;
  }
  
  .image-modal {
    padding: 1rem;
  }
}
</style>