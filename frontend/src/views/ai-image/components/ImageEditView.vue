<template>
  <div class="image-edit-view">
    <div class="page-header">
      <button class="back-btn" @click="$emit('goBack')">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m12 19-7-7 7-7"></path>
          <path d="M19 12H5"></path>
        </svg>
        返回
      </button>
      <h1 class="page-title">AI 图像编辑</h1>
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
      <!-- 功能选项卡 -->
      <div class="edit-tabs">
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
      <div class="edit-content">
        <!-- 1. 修改背景 -->
        <div v-if="activeTab === 'background'" class="edit-section">
    
          
          <div class="edit-panel">
            <div class="upload-panel">
              <div class="upload-area" @click="triggerUpload('background')">
                <input 
                  ref="backgroundInput" 
                  type="file" 
                  accept="image/*" 
                  @change="handleImageSelect('background', $event)" 
                  style="display: none"
                >
                <div v-if="!backgroundImage" class="upload-placeholder">
                  <div class="upload-icon">🖼️</div>
                  <p>点击上传原图</p>
                  <small>支持 JPG, PNG, GIF, WebP</small>
                </div>
                <div v-else class="uploaded-preview">
                  <img :src="backgroundImagePreview" alt="原图" />
                  <button class="remove-btn" @click.stop="clearImage('background')">×</button>
                </div>
              </div>
              
              <div class="prompt-input">
                <label>新背景描述：</label>
                <textarea 
                  v-model="backgroundPrompt" 
                  placeholder="描述您想要的新背景，例如：夕阳下的海滩、雪山、现代城市夜景..."
                  rows="3"
                ></textarea>
                <button 
                  class="edit-btn" 
                  @click="changeBackground" 
                  :disabled="!backgroundImage || !backgroundPrompt.trim() || processing"
                >
                  <span v-if="processing">处理中...</span>
                  <span v-else>🌆 更换背景</span>
                </button>
              </div>
            </div>
            
            <div class="result-panel">
              <!-- 处理中的占位动画 -->
              <div v-if="processing" class="placeholder-wrapper">
                <div class="placeholder-container">
                  <div class="placeholder-skeleton">
                    <div class="skeleton-shimmer"></div>
                    <div class="placeholder-content">
                      <div class="loading-spinner"></div>
                      <p class="loading-text">AI 处理中...</p>
                      <p class="loading-subtext">正在更换背景</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 编辑结果 -->
              <div v-else-if="editResult" class="result-display">
                <h3>编辑结果</h3>
                <img :src="editResult" alt="编辑结果" />
                <button class="download-result-btn" @click="downloadResult">下载图片</button>
              </div>
              
              <!-- 空状态 -->
              <div v-else class="empty-result">
                <div class="empty-icon">🎨</div>
                <p>编辑结果将在这里显示</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 2. 修改风格 -->
        <div v-if="activeTab === 'style'" class="edit-section">
          
          <div class="edit-panel">
            <div class="upload-panel">
              <div class="upload-area" @click="triggerUpload('style')">
                <input 
                  ref="styleInput" 
                  type="file" 
                  accept="image/*" 
                  @change="handleImageSelect('style', $event)" 
                  style="display: none"
                >
                <div v-if="!styleImage" class="upload-placeholder">
                  <div class="upload-icon">🖼️</div>
                  <p>上传人物原图</p>
                  <small>支持 JPG, PNG, GIF, WebP</small>
                </div>
                <div v-else class="uploaded-preview">
                  <img :src="styleImagePreview" alt="原图" />
                  <button class="remove-btn" @click.stop="clearImage('style')">×</button>
                </div>
              </div>
              
              <div class="style-selector">
                <label>选择风格：</label>
                <select v-model="selectedStyle" class="style-select">
                  <option :value="null" disabled>请选择风格</option>
                  <option 
                    v-for="style in styleOptions" 
                    :key="style.value"
                    :value="style.value"
                  >
                    {{ style.label }}
                  </option>
                </select>
                <button 
                  class="edit-btn" 
                  @click="changeStyle" 
                  :disabled="!styleImage || selectedStyle === null || processing"
                >
                  <span v-if="processing">转换中...</span>
                  <span v-else>🎭 转换风格</span>
                </button>
              </div>
            </div>
            
            <div class="result-panel">
              <!-- 处理中的占位动画 -->
              <div v-if="processing" class="placeholder-wrapper">
                <div class="placeholder-container">
                  <div class="placeholder-skeleton">
                    <div class="skeleton-shimmer"></div>
                    <div class="placeholder-content">
                      <div class="loading-spinner"></div>
                      <p class="loading-text">AI 处理中...</p>
                      <p class="loading-subtext">正在转换风格</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 编辑结果 -->
              <div v-else-if="editResult" class="result-display">
                <h3>编辑结果</h3>
                <img :src="editResult" alt="编辑结果" />
                <button class="download-result-btn" @click="downloadResult">下载图片</button>
              </div>
              
              <!-- 空状态 -->
              <div v-else class="empty-result">
                <div class="empty-icon">🎨</div>
                <p>编辑结果将在这里显示</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 3. 描述修改 -->
        <div v-if="activeTab === 'prompt'" class="edit-section">
          
          <div class="edit-panel">
            <div class="upload-panel">
              <div class="upload-area" @click="triggerUpload('prompt')">
                <input 
                  ref="promptInput" 
                  type="file" 
                  accept="image/*" 
                  @change="handleImageSelect('prompt', $event)" 
                  style="display: none"
                >
                <div v-if="!promptImage" class="upload-placeholder">
                  <div class="upload-icon">🖼️</div>
                  <p>点击上传原图</p>
                  <small>支持 JPG, PNG, GIF, WebP</small>
                </div>
                <div v-else class="uploaded-preview">
                  <img :src="promptImagePreview" alt="原图" />
                  <button class="remove-btn" @click.stop="clearImage('prompt')">×</button>
                </div>
              </div>
              
              <div class="prompt-input">
                <label>修改描述：</label>
                <textarea 
                  v-model="editPrompt" 
                  placeholder="描述您想要的修改，例如：将人物表情改为微笑、添加一只小猫、改变天气为雨天..."
                  rows="4"
                ></textarea>
                <button 
                  class="edit-btn" 
                  @click="editByPrompt" 
                  :disabled="!promptImage || !editPrompt.trim() || processing"
                >
                  <span v-if="processing">处理中...</span>
                  <span v-else>📝 应用修改</span>
                </button>
              </div>
            </div>
            
            <div class="result-panel">
              <!-- 处理中的占位动画 -->
              <div v-if="processing" class="placeholder-wrapper">
                <div class="placeholder-container">
                  <div class="placeholder-skeleton">
                    <div class="skeleton-shimmer"></div>
                    <div class="placeholder-content">
                      <div class="loading-spinner"></div>
                      <p class="loading-text">AI 处理中...</p>
                      <p class="loading-subtext">正在应用修改</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 编辑结果 -->
              <div v-else-if="editResult" class="result-display">
                <h3>编辑结果</h3>
                <img :src="editResult" alt="编辑结果" />
                <button class="download-result-btn" @click="downloadResult">下载图片</button>
              </div>
              
              <!-- 空状态 -->
              <div v-else class="empty-result">
                <div class="empty-icon">🎨</div>
                <p>编辑结果将在这里显示</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 4. 多图融合 -->
        <div v-if="activeTab === 'merge'" class="edit-section">
          
          <div class="edit-panel merge-panel">
            <div class="upload-panel">
              <div class="multi-upload-section">
                <div class="upload-slots">
                  <div 
                    v-for="(slot, index) in mergeSlots" 
                    :key="index" 
                    class="upload-slot"
                    @click="triggerUpload(`merge-${index}`)"
                  >
                    <input 
                      :ref="el => mergeInputs[index] = el as HTMLInputElement" 
                      type="file" 
                      accept="image/*" 
                      @change="handleMergeImageSelect(index, $event)" 
                      style="display: none"
                    >
                    <div v-if="!slot.image" class="slot-placeholder">
                      <div class="slot-icon">{{ slot.icon }}</div>
                      <p>{{ slot.label }}</p>
                      <small>点击上传</small>
                    </div>
                    <div v-else class="slot-preview">
                      <img :src="slot.preview" :alt="slot.label" />
                      <button class="remove-btn" @click.stop="removeMergeImage(index)">×</button>
                      <div class="slot-tag">{{ slot.label }}</div>
                    </div>
                  </div>
                </div>
                
                <div class="merge-prompt-input">
                  <label>融合描述：</label>
                  <textarea 
                    v-model="mergePrompt" 
                    placeholder="描述如何融合这些图片，例如：图1中的女生穿着图2中的黑色裙子按图3的姿势坐下..."
                    rows="4"
                  ></textarea>
                  <button 
                    class="edit-btn" 
                    @click="mergeImages" 
                    :disabled="!canMerge || processing"
                  >
                    <span v-if="processing">融合中...</span>
                    <span v-else>🎨 开始融合</span>
                  </button>
                </div>
              </div>
            </div>
            
            <div class="result-panel">
              <!-- 处理中的占位动画 -->
              <div v-if="processing" class="placeholder-wrapper">
                <div class="placeholder-container">
                  <div class="placeholder-skeleton">
                    <div class="skeleton-shimmer"></div>
                    <div class="placeholder-content">
                      <div class="loading-spinner"></div>
                      <p class="loading-text">AI 融合中...</p>
                      <p class="loading-subtext">这可能需要一分钟</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 融合结果 -->
              <div v-else-if="editResult" class="result-display">
                <h3>融合结果</h3>
                <img :src="editResult" alt="融合结果" />
                <button class="download-result-btn" @click="downloadResult">下载图片</button>
              </div>
              
              <!-- 空状态 -->
              <div v-else class="empty-result">
                <div class="empty-icon">✨</div>
                <p>融合结果将在这里显示</p>
                <small>上传2-3张图片即可开始融合</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 我的相册组件 -->
    <MyGallery 
      :showGallery="showGallery" 
      @close="showGallery = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'
import MyGallery from '@/components/MyGallery.vue'

// 定义 emits
const emit = defineEmits(['goBack'])

const toast = useToast()

// 当前激活的标签
const activeTab = ref<'background' | 'style' | 'prompt' | 'merge'>('background')

// 标签配置
const tabs: Array<{ key: 'background' | 'style' | 'prompt' | 'merge', icon: string, label: string }> = [
  { key: 'background', icon: '🌆', label: '修改背景' },
  { key: 'style', icon: '🎭', label: '修改风格' },
  { key: 'prompt', icon: '📝', label: '描述修改' },
  { key: 'merge', icon: '🎨', label: '多图融合' }
]

// 风格选项（基于 wanx-style-repaint-v1 模型的预置风格）
const styleOptions = [
  { value: 0, label: '复古漫画', icon: '📚' },
  { value: 1, label: '3D童话', icon: '🧚' },
  { value: 2, label: '二次元', icon: '🎌' },
  { value: 3, label: '小清新', icon: '🌸' },
  { value: 4, label: '未来科技', icon: '🤖' },
  { value: 5, label: '国画古风', icon: '🎨' },
  { value: 6, label: '将军百战', icon: '⚔️' },
  { value: 7, label: '炫彩卡通', icon: '🎪' },
  { value: 8, label: '清雅国风', icon: '🏮' },
  { value: 9, label: '喜迎新年', icon: '🎊' },
  { value: 14, label: '国风工笔', icon: '🖌️' },
  { value: 15, label: '恭贺新禧', icon: '🧧' },
  { value: 30, label: '童话世界', icon: '🏰' },
  { value: 31, label: '黏土世界', icon: '🧱' },
  { value: 32, label: '像素世界', icon: '🎮' },
  { value: 33, label: '冒险世界', icon: '🗺️' },
  { value: 34, label: '日漫世界', icon: '🌸' },
  { value: 35, label: '3D世界', icon: '🎲' },
  { value: 36, label: '二次元世界', icon: '🎭' },
  { value: 37, label: '手绘世界', icon: '✏️' },
  { value: 38, label: '蜡笔世界', icon: '🖍️' },
  { value: 39, label: '冰箱贴世界', icon: '🧲' },
  { value: 40, label: '吧嗒世界', icon: '🎪' }
]

// 修改背景相关
const backgroundInput = ref<HTMLInputElement>()
const backgroundImage = ref<File | null>(null)
const backgroundImagePreview = ref<string>('')
const backgroundPrompt = ref('')

// 修改风格相关
const styleInput = ref<HTMLInputElement>()
const styleImage = ref<File | null>(null)
const styleImagePreview = ref<string>('')
const selectedStyle = ref<number | null>(null)

// 描述修改相关
const promptInput = ref<HTMLInputElement>()
const promptImage = ref<File | null>(null)
const promptImagePreview = ref<string>('')
const editPrompt = ref('')

// 多图融合相关
const mergeInputs = ref<HTMLInputElement[]>([])
const mergeSlots = ref([
  { label: '图片1', icon: '1️⃣', image: null as File | null, preview: '' },
  { label: '图片2', icon: '2️⃣', image: null as File | null, preview: '' },
  { label: '图片3', icon: '3️⃣', image: null as File | null, preview: '' }
])
const mergePrompt = ref('')

// 通用状态
const processing = ref(false)
const editResult = ref<string>('')

// 我的相册
const showGallery = ref(false)

// 计算属性
const hasAnyMergeImage = computed(() => {
  return mergeSlots.value.some(slot => slot.image !== null)
})

const canMerge = computed(() => {
  const imageCount = mergeSlots.value.filter(slot => slot.image !== null).length
  return imageCount >= 2 && mergePrompt.value.trim().length > 0
})

// 方法
const switchTab = (tab: 'background' | 'style' | 'prompt' | 'merge') => {
  activeTab.value = tab
  // 清空编辑结果
  editResult.value = ''
}

// 组件挂载时检查是否需要激活特定tab
onMounted(() => {
  const tabToActivate = localStorage.getItem('editTabToActivate')
  if (tabToActivate) {
    activeTab.value = tabToActivate as 'background' | 'style' | 'prompt' | 'merge'
    localStorage.removeItem('editTabToActivate')
  }
})

const triggerUpload = (type: string) => {
  if (type === 'background') {
    backgroundInput.value?.click()
  } else if (type === 'style') {
    styleInput.value?.click()
  } else if (type === 'prompt') {
    promptInput.value?.click()
  } else if (type.startsWith('merge-')) {
    const index = parseInt(type.split('-')[1])
    mergeInputs.value[index]?.click()
  }
}

const handleImageSelect = (type: 'background' | 'style' | 'prompt', event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    
    if (type === 'background') {
      backgroundImage.value = file
      createImagePreview(file, (url) => { backgroundImagePreview.value = url })
    } else if (type === 'style') {
      styleImage.value = file
      createImagePreview(file, (url) => { styleImagePreview.value = url })
    } else if (type === 'prompt') {
      promptImage.value = file
      createImagePreview(file, (url) => { promptImagePreview.value = url })
    }
    
    // 清空之前的结果
    editResult.value = ''
  }
}

const handleMergeImageSelect = (index: number, event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    mergeSlots.value[index].image = file
    createImagePreview(file, (url) => { mergeSlots.value[index].preview = url })
    
    // 清空之前的结果
    editResult.value = ''
  }
}

const createImagePreview = (file: File, callback: (url: string) => void) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    callback(e.target?.result as string)
  }
  reader.readAsDataURL(file)
}

const clearImage = (type: 'background' | 'style' | 'prompt') => {
  if (type === 'background') {
    backgroundImage.value = null
    backgroundImagePreview.value = ''
    backgroundPrompt.value = ''
  } else if (type === 'style') {
    styleImage.value = null
    styleImagePreview.value = ''
    selectedStyle.value = null
  } else if (type === 'prompt') {
    promptImage.value = null
    promptImagePreview.value = ''
    editPrompt.value = ''
  }
  editResult.value = ''
}

const removeMergeImage = (index: number) => {
  mergeSlots.value[index].image = null
  mergeSlots.value[index].preview = ''
  editResult.value = ''
}

// 修改背景
const changeBackground = async () => {
  if (!backgroundImage.value || !backgroundPrompt.value.trim()) {
    toast.error('请上传图片并输入背景描述')
    return
  }
  
  processing.value = true
  editResult.value = ''
  
  try {
    // 将图片转为base64
    const base64Image = await fileToBase64(backgroundImage.value)
    
    const requestData = {
      image_url: base64Image,
      prompt: backgroundPrompt.value
    }
    
    const response = await (apiService as any).instance.post('/ai-image/background-edit/', requestData, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 60000  // 60秒超时
    })
    
    if (response.data.code === 200) {
      editResult.value = response.data.data.edited_image_url
      toast.success('背景更换完成！')
    } else {
      throw new Error(response.data.message || '背景更换失败')
    }
  } catch (error: any) {
    console.error('背景更换失败:', error)
    toast.error(error.message || '背景更换失败，请稍后重试')
  } finally {
    processing.value = false
  }
}

// 修改风格
const changeStyle = async () => {
  if (!styleImage.value || selectedStyle.value === null) {
    toast.error('请上传图片并选择风格')
    return
  }
  
  processing.value = true
  editResult.value = ''
  
  try {
    // 将图片转为base64
    const base64Image = await fileToBase64(styleImage.value)
    
    const requestData = {
      image_url: base64Image,
      style_index: selectedStyle.value
    }
    
    const response = await (apiService as any).instance.post('/ai-image/style-repaint/', requestData, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 120000  // 120秒超时（异步任务需要更长时间）
    })
    
    if (response.data.code === 200) {
      editResult.value = response.data.data.edited_image_url
      toast.success('风格转换完成！')
    } else {
      throw new Error(response.data.message || '风格转换失败')
    }
  } catch (error: any) {
    console.error('风格转换失败:', error)
    toast.error(error.message || '风格转换失败，请稍后重试')
  } finally {
    processing.value = false
  }
}

// 描述修改
const editByPrompt = async () => {
  if (!promptImage.value || !editPrompt.value.trim()) {
    toast.error('请上传图片并输入修改描述')
    return
  }
  
  processing.value = true
  editResult.value = ''
  
  try {
    // 将图片转为base64
    const base64Image = await fileToBase64(promptImage.value)
    
    const requestData = {
      image_url: base64Image,
      prompt: editPrompt.value
    }
    
    const response = await (apiService as any).instance.post('/ai-image/prompt-edit/', requestData, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 60000  // 60秒超时
    })
    
    if (response.data.code === 200) {
      editResult.value = response.data.data.edited_image_url
      toast.success('图片修改完成！')
    } else {
      throw new Error(response.data.message || '图片修改失败')
    }
  } catch (error: any) {
    console.error('图片修改失败:', error)
    toast.error(error.message || '图片修改失败，请稍后重试')
  } finally {
    processing.value = false
  }
}

// 多图融合
const mergeImages = async () => {
  if (!canMerge.value) {
    toast.error('请至少上传2张图片并输入融合描述')
    return
  }
  
  processing.value = true
  editResult.value = ''
  
  try {
    // 使用 qwen-image-edit 模型的多图编辑功能
    // 构建 messages 格式
    const content: any[] = []
    
    // 添加所有上传的图片（转为base64或URL）
    for (let i = 0; i < mergeSlots.value.length; i++) {
      const slot = mergeSlots.value[i]
      if (slot.image) {
        // 将图片转为base64
        const base64 = await fileToBase64(slot.image)
        content.push({ image: base64 })
      }
    }
    
    // 添加融合描述
    content.push({ text: mergePrompt.value })
    
    const requestData = {
      messages: [
        {
          role: 'user',
          content: content
        }
      ]
    }
    
    const response = await (apiService as any).instance.post('/ai-image/merge/', requestData, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 60000  // 60秒超时
    })
    
    if (response.data.code === 200) {
      editResult.value = response.data.data.merged_image_url
      toast.success('图片融合完成！')
    } else {
      throw new Error(response.data.message || '图片融合失败')
    }
  } catch (error: any) {
    console.error('图片融合失败:', error)
    toast.error(error.message || '图片融合失败，请稍后重试')
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

// 下载结果
const downloadResult = async () => {
  if (!editResult.value) return
  
  try {
    const response = await fetch(editResult.value)
    const blob = await response.blob()
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.style.display = 'none'
    link.href = url
    link.download = `edited-${Date.now()}.png`
    
    document.body.appendChild(link)
    link.click()
    
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)
    
    toast.success('图片下载成功！')
  } catch (error) {
    console.error('下载失败:', error)
    toast.error('下载失败，请稍后重试')
  }
}
</script>

<style scoped>
.image-edit-view {
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

/* 标签页 */
.edit-tabs {
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

/* 编辑内容区 */
.edit-content {
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

.edit-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.merge-panel {
  grid-template-columns: 1.2fr 1fr;
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

/* 输入区域 */
.prompt-input,
.style-selector,
.merge-prompt-input {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.prompt-input label,
.style-selector label,
.merge-prompt-input label {
  font-weight: 600;
  font-size: 1rem;
  color: var(--color-text);
}

textarea {
  width: 100%;
  padding: 1rem;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.95rem;
  line-height: 1.6;
  resize: vertical;
  transition: border-color 0.2s;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(94, 155, 255, 0.1);
}

/* 风格下拉选择框 */
.style-select {
  width: 100%;
  padding: 1rem;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 1rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  padding-right: 2.5rem;
}

.style-select:hover {
  border-color: var(--color-primary);
  background: var(--color-surface);  /* 保持原背景色 */
}

.style-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(94, 155, 255, 0.1);
  background: var(--color-surface);  /* 保持原背景色 */
}

.style-select option {
  background: var(--card-background);  /* 选项背景使用主题色 */
  color: var(--color-text);
  padding: 0.75rem;
  font-size: 1rem;
}

/* 多图融合 */
.multi-upload-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.upload-slots {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.upload-slot {
  border: 2px dashed var(--color-border);
  border-radius: 12px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--color-surface);
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-slot:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-alpha);
}

.slot-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.slot-icon {
  font-size: 2.5rem;
}

.slot-placeholder p {
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.slot-placeholder small {
  color: var(--color-textSecondary);
  font-size: 0.85rem;
}

.slot-preview {
  position: relative;
  width: 100%;
}

.slot-preview img {
  width: 100%;
  height: auto;
  max-height: 180px;
  object-fit: cover;
  border-radius: 8px;
}

.slot-tag {
  position: absolute;
  top: 8px;
  left: 8px;
  background: var(--color-primary);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* 操作按钮 */
.edit-btn {
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

.edit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(94, 155, 255, 0.4);
}

.edit-btn:disabled {
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

.result-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
  width: 100%;
}

.result-display h3 {
  margin: 0;
  color: var(--color-text);
  font-size: 1.5rem;
}

.result-display img {
  width: 100%;
  max-width: 500px;
  height: auto;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
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
}

.download-result-btn:hover {
  background: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(94, 155, 255, 0.3);
}

.empty-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: var(--color-textSecondary);
  text-align: center;
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

.empty-result small {
  font-size: 0.9rem;
  color: var(--color-textSecondary);
}

/* 占位动画样式 - 与 ImageGenerationView 保持一致 */
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

@keyframes spin {
  to { transform: rotate(360deg); }
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

/* 响应式设计 */
@media (max-width: 1024px) {
  .edit-panel {
    grid-template-columns: 1fr;
  }
  
  .merge-panel {
    grid-template-columns: 1fr;
  }
  
  .edit-tabs {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .image-edit-view {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .edit-tabs {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .tab-btn {
    padding: 1rem;
  }
  
  .tab-icon {
    font-size: 2rem;
  }
  
  .edit-content {
    padding: 1.5rem;
  }
  
  .upload-slots {
    grid-template-columns: 1fr;
  }
  
  .upload-area {
    min-height: 250px;
  }
  
  .placeholder-container {
    max-width: 400px;
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
}
</style>

