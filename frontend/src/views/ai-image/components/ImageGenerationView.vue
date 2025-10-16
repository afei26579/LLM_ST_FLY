<template>
  <div class="image-generation-view">
    <div class="page-header">
      <button class="back-btn" @click="$emit('goBack')">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m12 19-7-7 7-7"></path>
          <path d="M19 12H5"></path>
        </svg>
        返回
      </button>
      <h1 class="page-title">AI 图像生成</h1>
      <button class="gallery-btn" @click="showGallery = true">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
        </svg>
        我的相册
      </button>
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
              <span v-else">✨ 生成图像</span>
            </button>
          </div>
        </div>
          
        <!-- 结果展示区域 -->
        <div class="result-panel">
          <!-- 占位符模式 - 铺满整个面板 -->
          <div v-if="placeholderImage" class="placeholder-wrapper">
            <div class="placeholder-container" :class="getPlaceholderClass(placeholderImage.aspectRatio)">
              <div class="placeholder-skeleton">
                <div class="skeleton-shimmer"></div>
                <div class="placeholder-content">
                  <div class="loading-spinner"></div>
                  <p class="loading-text">AI 创作中...</p>
                  <p class="loading-subtext">这可能需要几秒钟</p>
                </div>
              </div>
            </div>
            <div class="placeholder-info">
              <p class="image-prompt">{{ placeholderImage.prompt }}</p>
              <div class="image-meta">
                <span class="placeholder-meta">{{ getSizeLabel(placeholderImage.size) }}</span>
                <span class="generating-text">生成中...</span>
              </div>
            </div>
          </div>
          
          <!-- 图片展示模式 -->
          <div v-else-if="generatedImages.length > 0" class="result-section">
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
    
    <!-- 我的相册模态框 -->
    <div v-if="showGallery" class="gallery-modal" @click="showGallery = false">
      <div class="gallery-modal-content" @click.stop>
        <div class="gallery-header">
          <h2>我的相册</h2>
          <button class="close-btn" @click="showGallery = false">×</button>
        </div>
        
        <!-- 相册分类tab -->
        <div class="gallery-tabs">
          <button 
            class="gallery-tab-btn"
            :class="{ active: galleryTab === 'text_to_image' }"
            @click="switchGalleryTab('text_to_image')"
          >
            <span class="tab-icon">🎨</span>
            <span>文生图</span>
          </button>
          <button 
            class="gallery-tab-btn"
            :class="{ active: galleryTab === 'image_edit' }"
            @click="switchGalleryTab('image_edit')"
          >
            <span class="tab-icon">✏️</span>
            <span>图像编辑</span>
          </button>
        </div>
        
        <div class="gallery-body">
          <div v-if="loadingHistory" class="loading-state">
            <div class="loading-spinner-large"></div>
            <p>加载中...</p>
          </div>
          
          <div v-else-if="historyImages.length > 0" class="gallery-grid">
            <div 
              v-for="image in historyImages" 
              :key="image.id" 
              class="gallery-item"
            >
              <div class="gallery-image-container">
                <img :src="image.saved_url || image.original_url" :alt="image.orig_prompt" />
                <div class="gallery-image-overlay">
                  <div class="overlay-actions">
                    <!-- 文生图：显示画同款 + 下载 -->
                    <template v-if="image.image_source === 'text_to_image'">
                      <button class="gallery-action-btn create-similar-btn" @click.stop="createSimilarImage(image)" title="画同款">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M12 19l7-7 3 3-7 7-3-3z"></path>
                          <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path>
                          <path d="M2 2l7.586 7.586"></path>
                          <circle cx="11" cy="11" r="2"></circle>
                        </svg>
                      </button>
                      <button class="gallery-action-btn download-btn" @click.stop="downloadImage(image)" title="下载图片">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                          <polyline points="7 10 12 15 17 10"></polyline>
                          <line x1="12" y1="15" x2="12" y2="3"></line>
                        </svg>
                      </button>
                    </template>
                    
                    <!-- 图像编辑：只显示下载 -->
                    <template v-else>
                      <button class="gallery-action-btn download-btn single-btn" @click.stop="downloadImage(image)" title="下载图片">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                          <polyline points="7 10 12 15 17 10"></polyline>
                          <line x1="12" y1="15" x2="12" y2="3"></line>
                        </svg>
                      </button>
                    </template>
                  </div>
                </div>
              </div>
              <div class="gallery-item-info">
                <div class="gallery-meta">
                  <span class="gallery-size">{{ formatFileSize(image.size) }}</span>
                  <span class="gallery-date">{{ formatShortTime(image.created_at) }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-gallery">
            <div class="empty-icon">📷</div>
            <p>还没有生成过图片</p>
            <small>开始创作您的第一张AI图像吧</small>
          </div>
          
          <!-- 分页 -->
          <div v-if="historyPagination.total_pages > 1" class="gallery-pagination">
            <button 
              class="page-btn" 
              :disabled="!historyPagination.has_previous"
              @click="loadHistoryPage(historyPagination.page - 1)"
            >
              上一页
            </button>
            <span class="page-info">{{ historyPagination.page }} / {{ historyPagination.total_pages }}</span>
            <button 
              class="page-btn" 
              :disabled="!historyPagination.has_next"
              @click="loadHistoryPage(historyPagination.page + 1)"
            >
              下一页
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
import { apiService } from '@/services/api'
import type { ImageGenerationRequest, ImagePresets } from '@/services/api'
import MyGallery from '@/components/MyGallery.vue'

// Define emits
const emit = defineEmits(['goBack'])

const toast = useToast()

// 响应式数据
const generating = ref(false)
const showAdvanced = ref(false)
const showSizeDropdown = ref(false)
const showTooltip = ref('')
const generatedImages = ref<any[]>([])
const selectedImage = ref<any>(null)
const placeholderImage = ref<any>(null)  // 占位符图像

// 我的相册相关
const showGallery = ref(false)
const historyImages = ref<any[]>([])
const loadingHistory = ref(false)
const galleryTab = ref<'text_to_image' | 'image_edit'>('text_to_image')  // 相册tab
const historyPagination = ref({
  page: 1,
  page_size: 20,
  total: 0,
  total_pages: 0,
  has_next: false,
  has_previous: false
})

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
  
  // 创建占位符
  placeholderImage.value = {
    isPlaceholder: true,
    aspectRatio: getAspectRatioFromSize(formData.size),
    prompt: formData.prompt,
    size: formData.size
  }
  
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
        // 清除占位符
        placeholderImage.value = null
        // 处理图片URL，确保是完整路径
        const processedImages = result.images.map((img: any) => ({
          ...img,
          saved_url: ensureAbsoluteUrl(img.saved_url),
          original_url: ensureAbsoluteUrl(img.original_url)
        }))
        // 添加生成的图片
        generatedImages.value.unshift(...processedImages)
        toast.success(`成功生成 ${result.images.length} 张图片！`)
        
        console.log('图片生成成功，URL:', processedImages[0]?.saved_url)
      } else {
        toast.warning('图片生成成功，但没有返回图片数据')
        placeholderImage.value = null
      }
    } else {
      throw new Error(response.message || '生成失败')
    }
  } catch (error: any) {
    console.error('图片生成失败:', error)
    const errorMsg = error.message || '生成图片时发生错误'
    toast.error(errorMsg)
    // 清除占位符
    placeholderImage.value = null
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

const formatShortTime = (timeStr: string) => {
  if (!timeStr) return '未知'
  try {
    const date = new Date(timeStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (days === 0) return '今天'
    if (days === 1) return '昨天'
    if (days < 7) return `${days}天前`
    if (days < 30) return `${Math.floor(days / 7)}周前`
    if (days < 365) return `${Math.floor(days / 30)}月前`
    return date.toLocaleDateString('zh-CN')
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

// 从尺寸获取宽高比
const getAspectRatioFromSize = (size: string) => {
  const sizeOption = presets.value.sizes.find(s => s.value === size)
  return sizeOption?.aspect_ratio || '1:1'
}

// 获取占位符的类名（根据宽高比）
const getPlaceholderClass = (aspectRatio: string) => {
  switch (aspectRatio) {
    case '1:1':
      return 'placeholder-square'
    case '16:9':
      return 'placeholder-landscape'
    case '9:16':
      return 'placeholder-portrait'
    case '4:3':
      return 'placeholder-landscape-43'
    case '3:4':
      return 'placeholder-portrait-34'
    default:
      return 'placeholder-square'
  }
}

// 点击外部关闭下拉框
const handleClickOutside = (event: Event) => {
  const target = event.target as HTMLElement
  if (!target.closest('.size-selector')) {
    showSizeDropdown.value = false
  }
}

// 确保URL是完整的绝对路径
const ensureAbsoluteUrl = (url: string): string => {
  if (!url) return ''
  
  // 如果已经是完整URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  
  // 如果是相对路径，拼接base URL
  const baseUrl = 'http://localhost:8000'
  return url.startsWith('/') ? `${baseUrl}${url}` : `${baseUrl}/${url}`
}

// 切换相册tab
const switchGalleryTab = (tab: 'text_to_image' | 'image_edit') => {
  galleryTab.value = tab
  loadImageHistory(1)  // 重新加载第一页
}

// 加载图片历史（根据当前tab过滤）
const loadImageHistory = async (page: number = 1) => {
  loadingHistory.value = true
  try {
    const response = await apiService.getImageHistory(page, 20)
    
    if (response.code === 200) {
      // 处理图片URL，确保是完整路径
      let images = response.data.list.map((img: any) => ({
        ...img,
        saved_url: ensureAbsoluteUrl(img.saved_url),
        original_url: ensureAbsoluteUrl(img.original_url)
      }))
      
      // 根据当前tab过滤图片
      images = images.filter((img: any) => img.image_source === galleryTab.value)
      
      historyImages.value = images
      historyPagination.value = {
        page: response.data.page,
        page_size: response.data.page_size,
        total: images.length,  // 使用过滤后的数量
        total_pages: Math.ceil(images.length / response.data.page_size),
        has_next: response.data.has_next,
        has_previous: response.data.has_previous
      }
      
      console.log(`图片历史加载成功（${galleryTab.value}），共`, images.length, '张图片')
      console.log('第一张图片URL:', images[0]?.saved_url)
    }
  } catch (error) {
    console.error('加载图片历史失败:', error)
    toast.error('加载图片历史失败')
  } finally {
    loadingHistory.value = false
  }
}

const loadHistoryPage = (page: number) => {
  loadImageHistory(page)
}

// 画同款 - 基于历史图片参数重新生成
const createSimilarImage = (image: any) => {
  console.log('画同款 - 图片参数:', image)
  
  // 关闭相册模态框
  showGallery.value = false
  
  // 填充正向提示词
  formData.prompt = image.orig_prompt || image.actual_prompt || ''
  
  // 填充反向提示词
  if (image.negative_prompt) {
    formData.negative_prompt = image.negative_prompt
  }
  
  // 填充图像尺寸
  if (image.task_size) {
    formData.size = image.task_size
  }
  
  // 填充基础设置
  if (image.prompt_extend !== undefined) {
    formData.prompt_extend = image.prompt_extend
  }
  if (image.watermark !== undefined) {
    formData.watermark = image.watermark
  }
  
  // 填充高级设置参数
  let hasAdvancedParams = false
  
  if (image.style) {
    formData.style = image.style
    hasAdvancedParams = true
  }
  
  if (image.shot_type) {
    formData.shot_type = image.shot_type
    hasAdvancedParams = true
  }
  
  if (image.angle) {
    formData.angle = image.angle
    hasAdvancedParams = true
  }
  
  if (image.shooting_technique) {
    formData.shooting_technique = image.shooting_technique
    hasAdvancedParams = true
  }
  
  if (image.lighting) {
    formData.lighting = image.lighting
    hasAdvancedParams = true
  }
  
  // 如果有高级参数，自动展开高级设置
  if (hasAdvancedParams) {
    showAdvanced.value = true
  }
  
  // 显示成功提示
  toast.success('✨ 参数已填充，开始画同款吧！', {
    timeout: 3000
  })
  
  // 滚动到页面顶部
  setTimeout(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }, 100)
  
  console.log('画同款参数已填充:', {
    prompt: formData.prompt,
    negative_prompt: formData.negative_prompt,
    size: formData.size,
    style: formData.style,
    shot_type: formData.shot_type,
    angle: formData.angle,
    shooting_technique: formData.shooting_technique,
    lighting: formData.lighting,
    prompt_extend: formData.prompt_extend,
    watermark: formData.watermark
  })
}

// 从 localStorage 加载画同款参数
const loadSimilarImageParams = () => {
  const paramsStr = localStorage.getItem('similarImageParams')
  if (paramsStr) {
    try {
      const params = JSON.parse(paramsStr)
      
      // 填充所有参数
      if (params.prompt) formData.prompt = params.prompt
      if (params.negative_prompt) formData.negative_prompt = params.negative_prompt
      if (params.size) formData.size = params.size
      if (params.prompt_extend !== undefined) formData.prompt_extend = params.prompt_extend
      if (params.watermark !== undefined) formData.watermark = params.watermark
      if (params.style) formData.style = params.style
      if (params.shot_type) formData.shot_type = params.shot_type
      if (params.angle) formData.angle = params.angle
      if (params.shooting_technique) formData.shooting_technique = params.shooting_technique
      if (params.lighting) formData.lighting = params.lighting
      
      // 如果有高级参数，展开高级设置
      if (params.style || params.shot_type || params.angle || params.shooting_technique || params.lighting) {
        showAdvanced.value = true
      }
      
      // 清除 localStorage 中的参数，避免下次进入时自动填充
      localStorage.removeItem('similarImageParams')
      
      console.log('画同款参数已加载:', params)
      
      // 滚动到页面顶部
      setTimeout(() => {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }, 100)
    } catch (error) {
      console.error('解析画同款参数失败:', error)
      localStorage.removeItem('similarImageParams')
    }
  }
}

// 生命周期
onMounted(() => {
  loadPresets()
  document.addEventListener('click', handleClickOutside)
  
  // 检查并加载画同款参数
  loadSimilarImageParams()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 监听相册显示状态，打开时加载历史
import { watch } from 'vue'
watch(showGallery, (newValue) => {
  if (newValue) {
    loadImageHistory()
  }
})
</script>

<style scoped>
.image-generation-view {
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
  position: relative;
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
  color: var(--color-text);
}

.gallery-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.25rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(94, 155, 255, 0.3);
}

.gallery-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(94, 155, 255, 0.4);
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
  box-shadow: 0 0 0 3px rgba(94, 155, 255, 0.1);
}

.prompt-textarea.negative {
  border-color: rgba(239, 68, 68, 0.3);
}

.prompt-textarea.negative:focus {
  border-color: var(--color-error);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
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
  background-color: rgba(94, 155, 255, 0.05);
  border: 1px solid rgba(94, 155, 255, 0.1);
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
  background-color: rgba(94, 155, 255, 0.1);
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
  box-shadow: 0 0 0 3px rgba(94, 155, 255, 0.1);
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
  background: var(--card-background, #ffffff) !important;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 10px;
  box-shadow: var(--card-shadow, 0 4px 6px -1px rgba(0, 0, 0, 0.1));
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 4px;
  opacity: 1;
}

/* 确保在不同主题下下拉框都有正确的背景 */
:global(.theme-dark) .size-dropdown {
  background: #1e293b !important;
}

:global(.theme-future) .size-dropdown {
  background: linear-gradient(135deg, #1e1b3a 0%, #2d1b4e 50%, #1b2942 100%) !important;
}

:global(.theme-light) .size-dropdown {
  background: #ffffff !important;
}

.size-option {
  padding: 0.75rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid var(--color-border, #e5e7eb);
  background-color: transparent;
}

.size-option:last-child {
  border-bottom: none;
}

.size-option:hover {
  background-color: var(--color-surface, rgba(59, 130, 246, 0.05)) !important;
}

.size-option.selected {
  background-color: var(--color-primary-alpha, rgba(59, 130, 246, 0.1)) !important;
  color: var(--color-primary, #3b82f6) !important;
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
  background-color: rgba(94, 155, 255, 0.1);
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
  color: white;
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
  box-shadow: 0 10px 20px rgba(94, 155, 255, 0.3);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.generate-btn.generating {
  opacity: 0.6;
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

/* 占位符包装器 - 铺满整个结果面板 */
.placeholder-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1.5rem;
  padding: 2rem;
}

/* 占位符容器 - 居中并根据宽高比自适应 */
.placeholder-container {
  width: 100%;
  max-width: 800px;
  max-height: calc(100% - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 占位符不同宽高比 */
.placeholder-container.placeholder-square {
  aspect-ratio: 1 / 1;
}

.placeholder-container.placeholder-landscape {
  aspect-ratio: 16 / 9;
}

.placeholder-container.placeholder-portrait {
  aspect-ratio: 9 / 16;
  max-width: 450px;
}

.placeholder-container.placeholder-landscape-43 {
  aspect-ratio: 4 / 3;
}

.placeholder-container.placeholder-portrait-34 {
  aspect-ratio: 3 / 4;
  max-width: 500px;
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

/* 闪烁动画 */
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
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
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

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
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

.placeholder-info {
  max-width: 800px;
  width: 100%;
  text-align: center;
}

.placeholder-info .image-prompt {
  font-size: 1rem;
  color: var(--color-text);
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.placeholder-info .image-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  font-size: 0.9rem;
}

.placeholder-meta {
  color: var(--color-primary);
  font-weight: 600;
}

.generating-text {
  color: var(--color-primary);
  font-weight: 600;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
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
  background: var(--color-error);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s;
}

.clear-btn:hover {
  opacity: 0.8;
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
  color: white;
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

/* 我的相册模态框样式 */
.gallery-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 2rem;
  animation: fadeIn 0.2s ease;
}

.gallery-modal-content {
  background: var(--card-background);
  border: 1px solid var(--card-border);
  border-radius: 20px;
  width: 90%;
  max-width: 1200px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.gallery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--color-border);
}

.gallery-header h2 {
  margin: 0;
  color: var(--color-text);
  font-size: 1.8rem;
  font-weight: 600;
}

.gallery-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  min-height: 400px;
}

/* 相册网格布局 */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.gallery-item {
  background: var(--color-surface);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.gallery-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(94, 155, 255, 0.2);
  border-color: var(--color-primary);
}

.gallery-image-container {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  background: var(--color-background);
}

.gallery-image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.gallery-item:hover .gallery-image-container img {
  transform: scale(1.08);
}

.gallery-image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  backdrop-filter: blur(8px);
}

.gallery-item:hover .gallery-image-overlay {
  opacity: 1;
}

.overlay-actions {
  display: flex;
  gap: 1rem;
  padding: 1rem;
}

.gallery-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--card-background);
  color: var(--color-text);
  border: 2px solid var(--color-border);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.gallery-action-btn:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 16px rgba(94, 155, 255, 0.4);
}

.gallery-action-btn:active {
  transform: scale(1.05);
}

.gallery-action-btn.create-similar-btn {
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  border: none;
  box-shadow: 0 2px 12px rgba(94, 155, 255, 0.4);
}

.gallery-action-btn.create-similar-btn:hover {
  background: linear-gradient(135deg, var(--color-primary-dark), var(--color-accent));
  box-shadow: 0 4px 20px rgba(94, 155, 255, 0.6);
}

.gallery-action-btn.download-btn {
  background: var(--card-background);
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
}

.gallery-action-btn.download-btn:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.gallery-action-btn svg {
  flex-shrink: 0;
  stroke-width: 2.5;
}

.gallery-item-info {
  padding: 0.75rem 1rem;
  background: var(--card-background);
  border-top: 1px solid var(--color-border);
}

.gallery-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: var(--color-textSecondary);
}

.gallery-size {
  font-weight: 500;
  color: var(--color-text);
}

.gallery-date {
  color: var(--color-primary);
  font-weight: 500;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 1rem;
  color: var(--color-text);
}

.loading-spinner-large {
  width: 60px;
  height: 60px;
  border: 4px solid var(--color-border);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* 空状态 */
.empty-gallery {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 1rem;
  color: var(--color-textSecondary);
  text-align: center;
}

.empty-gallery .empty-icon {
  font-size: 4rem;
  opacity: 0.6;
}

.empty-gallery p {
  font-size: 1.1rem;
  color: var(--color-text);
  margin: 0;
}

.empty-gallery small {
  font-size: 0.9rem;
  color: var(--color-textSecondary);
}

/* 分页 */
.gallery-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--color-border);
}

.page-btn {
  padding: 0.5rem 1.25rem;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.page-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: none;
}

.page-info {
  font-size: 0.9rem;
  color: var(--color-text);
  font-weight: 500;
  min-width: 80px;
  text-align: center;
}

/* 相册滚动条样式 */
.gallery-body::-webkit-scrollbar {
  width: 8px;
}

.gallery-body::-webkit-scrollbar-track {
  background: var(--color-background);
  border-radius: 4px;
}

.gallery-body::-webkit-scrollbar-thumb {
  background: var(--color-primary-alpha);
  border-radius: 4px;
}

.gallery-body::-webkit-scrollbar-thumb:hover {
  background: var(--color-primary);
}

.gallery-body {
  scrollbar-width: thin;
  scrollbar-color: var(--color-primary-alpha) var(--color-background);
}

/* 相册分类tab */
.gallery-tabs {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 2rem 0;
  border-bottom: 1px solid var(--color-border);
}

.gallery-tab-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  color: var(--color-textSecondary);
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.gallery-tab-btn:hover {
  color: var(--color-primary);
  background: var(--color-primary-alpha);
}

.gallery-tab-btn.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.gallery-tab-btn .tab-icon {
  font-size: 1.2rem;
}

/* 单按钮样式（图像编辑只有下载） */
.gallery-action-btn.single-btn {
  margin: 0 auto;  /* 居中显示 */
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
  .image-generation-view {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.8rem;
  }
  
  .gallery-btn {
    padding: 0.4rem 1rem;
    font-size: 0.9rem;
  }
  
  .gallery-btn svg {
    width: 16px;
    height: 16px;
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
  
  /* 占位符响应式 */
  .placeholder-wrapper {
    padding: 1rem;
  }
  
  .placeholder-container {
    max-width: 100%;
  }
  
  .placeholder-container.placeholder-portrait,
  .placeholder-container.placeholder-portrait-34 {
    max-width: 350px;
  }
  
  .loading-spinner {
    width: 36px;
    height: 36px;
  }
  
  .loading-text {
    font-size: 0.9rem;
  }
  
  .loading-subtext {
    font-size: 0.8rem;
  }
  
  /* 相册模态框响应式 */
  .gallery-modal {
    padding: 1rem;
  }
  
  .gallery-modal-content {
    width: 95%;
    max-height: 90vh;
  }
  
  .gallery-header {
    padding: 1rem 1.5rem;
  }
  
  .gallery-header h2 {
    font-size: 1.4rem;
  }
  
  .gallery-body {
    padding: 1.5rem;
  }
  
  .gallery-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 1rem;
  }
  
  .gallery-action-btn {
    width: 44px;
    height: 44px;
  }
  
  .gallery-action-btn svg {
    width: 20px;
    height: 20px;
  }
  
  .overlay-actions {
    gap: 0.75rem;
    padding: 0.75rem;
  }
  
  .gallery-pagination {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .page-btn {
    width: 100%;
  }
}
</style>
