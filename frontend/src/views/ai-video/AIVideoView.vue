<template>
  <div class="ai-video-view">
    <div class="page-header">
      <h1 class="page-title">AI 视频生成</h1>
      <p class="page-description">智能视频生成与处理功能</p>
    </div>
    
    <div class="content-container">
      <!-- 文生视频 -->
      <div class="demo-card">
        <div class="card-header">
          <h2>文生视频</h2>
          <p>通过文字描述生成精彩的AI视频</p>
        </div>
        
        <div class="demo-content">
          <div class="input-section">
            <label for="videoPrompt">视频描述：</label>
            <textarea 
              id="videoPrompt" 
              v-model="textToVideoForm.prompt" 
              placeholder="请描述您想要生成的视频内容，例如：一只可爱的小猫在花园里玩耍..."
              rows="4"
            ></textarea>
          </div>
          
          <div class="settings-section">
            <div class="setting-group">
              <label>生成模型：</label>
              <select v-model="textToVideoForm.model">
                <option value="wanx2.1-t2v-turbo">万相2.1 Turbo</option>
                <option value="wanx2.1-t2v">万相2.1</option>
              </select>
            </div>

            <div class="setting-group">
              <label>视频分辨率：</label>
              <select v-model="textToVideoForm.resolution">
                <option value="1280*720">720P (1280*720)</option>
                <option value="1920*1080">1080P (1920*1080)</option>
                <option value="720*1280">竖屏 (720*1280)</option>
                <option value="1080*1920">竖屏 (1080*1920)</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>视频时长：</label>
              <select v-model="textToVideoForm.duration">
                <option :value="1">1秒</option>
                <option :value="3">3秒</option>
                <option :value="5">5秒</option>
                <option :value="10">10秒</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>帧率：</label>
              <select v-model="textToVideoForm.fps">
                <option :value="24">24 FPS</option>
                <option :value="25">25 FPS</option>
                <option :value="30">30 FPS</option>
                <option :value="60">60 FPS</option>
              </select>
            </div>

            <div class="setting-group" v-if="stylePresets.length > 0">
              <label>风格预设：</label>
              <select v-model="textToVideoForm.style_preset">
                <option value="">默认风格</option>
                <option v-for="preset in stylePresets" :key="preset.id" :value="preset.id">
                  {{ preset.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- 风格预设展示 -->
          <div v-if="selectedStylePreset" class="style-preset-info">
            <h4>{{ selectedStylePreset.name }}</h4>
            <p>{{ selectedStylePreset.description }}</p>
            <div class="preset-keywords">
              <span class="keyword-tag" v-for="keyword in selectedStylePreset.style_keywords.split(', ')" :key="keyword">
                {{ keyword }}
              </span>
            </div>
          </div>
          
          <div class="action-section">
            <button class="generate-btn" @click="generateVideo" :disabled="t2vGenerating">
              <span v-if="t2vGenerating">生成中...</span>
              <span v-else>生成视频</span>
            </button>
          </div>
          
          <div class="result-section" v-if="t2vResult">
            <h3>生成结果</h3>
            <div class="video-player">
              <video v-if="t2vResult.result_url" controls class="video-element" preload="metadata">
                <source :src="t2vResult.result_url" type="video/mp4">
                您的浏览器不支持视频播放
              </video>
              <div v-else class="video-placeholder">
                🎬 视频生成完成，任务ID: {{ t2vResult.task_id }}
                <p v-if="t2vResult.status === 'processing'">正在处理中，请稍候...</p>
              </div>
              <div class="video-info" v-if="t2vResult.duration || t2vResult.file_size">
                <span v-if="t2vResult.duration">时长: {{ t2vResult.duration }}秒</span>
                <span v-if="t2vResult.file_size">大小: {{ formatFileSize(t2vResult.file_size) }}</span>
                <span v-if="t2vResult.resolution">分辨率: {{ t2vResult.resolution }}</span>
              </div>
              <div class="video-controls" v-if="t2vResult.result_url">
                <button class="download-btn" @click="downloadVideo(t2vResult.result_url)">下载视频</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图生视频 -->
      <div class="demo-card">
        <div class="card-header">
          <h2>图生视频</h2>
          <p>上传图片，生成动态视频</p>
        </div>
        
        <div class="demo-content">
          <div class="upload-section">
            <div class="upload-area" @click="triggerImageInput" @dragover.prevent @drop.prevent="handleImageDrop">
              <input 
                ref="imageInput" 
                type="file" 
                accept="image/*" 
                @change="handleImageSelect" 
                style="display: none"
              >
              <div class="upload-icon">🖼️</div>
              <p v-if="!selectedImage">点击或拖拽图片文件到此处上传</p>
              <p v-else class="selected-file">已选择: {{ selectedImage.name }}</p>
              <small>支持 JPG, PNG, WebP 格式，建议分辨率不超过2048x2048</small>
            </div>
          </div>

          <div v-if="imagePreview" class="image-preview">
            <img :src="imagePreview" alt="预览图片" />
          </div>

          <div class="input-section" v-if="selectedImage">
            <label for="imageVideoPrompt">动态描述（可选）：</label>
            <textarea 
              id="imageVideoPrompt" 
              v-model="imageToVideoForm.prompt" 
              placeholder="描述图片中的元素应该如何动起来..."
              rows="3"
            ></textarea>
          </div>
          
          <div class="settings-section" v-if="selectedImage">
            <div class="setting-group">
              <label>生成模型：</label>
              <select v-model="imageToVideoForm.model">
                <option value="wanx2.1-i2v">万相2.1 图生视频</option>
              </select>
            </div>

            <div class="setting-group">
              <label>视频分辨率：</label>
              <select v-model="imageToVideoForm.resolution">
                <option value="1280*720">720P (1280*720)</option>
                <option value="1920*1080">1080P (1920*1080)</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>视频时长：</label>
              <select v-model="imageToVideoForm.duration">
                <option :value="3">3秒</option>
                <option :value="5">5秒</option>
                <option :value="10">10秒</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>帧率：</label>
              <select v-model="imageToVideoForm.fps">
                <option :value="24">24 FPS</option>
                <option :value="25">25 FPS</option>
                <option :value="30">30 FPS</option>
              </select>
            </div>
          </div>
          
          <div class="action-section" v-if="selectedImage">
            <button class="generate-btn" @click="generateImageVideo" :disabled="i2vGenerating">
              <span v-if="i2vGenerating">生成中...</span>
              <span v-else>生成视频</span>
            </button>
          </div>

          <div class="result-section" v-if="i2vResult">
            <h3>生成结果</h3>
            <div class="video-player">
              <video v-if="i2vResult.result_url" controls class="video-element" preload="metadata">
                <source :src="i2vResult.result_url" type="video/mp4">
                您的浏览器不支持视频播放
              </video>
              <div v-else class="video-placeholder">
                🎬 视频生成完成，任务ID: {{ i2vResult.task_id }}
                <p v-if="i2vResult.status === 'processing'">正在处理中，请稍候...</p>
              </div>
              <div class="video-info" v-if="i2vResult.duration || i2vResult.file_size">
                <span v-if="i2vResult.duration">时长: {{ i2vResult.duration }}秒</span>
                <span v-if="i2vResult.file_size">大小: {{ formatFileSize(i2vResult.file_size) }}</span>
                <span v-if="i2vResult.resolution">分辨率: {{ i2vResult.resolution }}</span>
              </div>
              <div class="video-controls" v-if="i2vResult.result_url">
                <button class="download-btn" @click="downloadVideo(i2vResult.result_url)">下载视频</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 使用统计 -->
      <div class="demo-card" v-if="userStats">
        <div class="card-header">
          <h2>使用统计</h2>
          <p>您的视频生成使用情况</p>
        </div>
        
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ userStats.total_tasks }}</div>
            <div class="stat-label">总任务数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userStats.completed_tasks }}</div>
            <div class="stat-label">完成任务</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ Math.round(userStats.total_duration / 60) }}</div>
            <div class="stat-label">总时长(分钟)</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ formatFileSize(userStats.total_storage_used) }}</div>
            <div class="stat-label">存储使用</div>
          </div>
        </div>
      </div>
      
      <!-- 功能特性 -->
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">🎬</div>
          <h3>文生视频</h3>
          <p>根据文字描述生成高质量视频</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🖼️</div>
          <h3>图生视频</h3>
          <p>将静态图片转换为动态视频</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🎨</div>
          <h3>风格预设</h3>
          <p>多种预设风格，轻松创作</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h3>高效处理</h3>
          <p>快速生成，支持多种分辨率</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'
import type { 
  TextToVideoRequest, 
  ImageToVideoRequest,
  VideoTaskResponse,
  UserVideoStats,
  VideoStylePreset
} from '@/services/api'

const toast = useToast()

// 表单数据
const textToVideoForm = reactive<TextToVideoRequest>({
  prompt: '',
  model: 'wanx2.1-t2v-turbo',
  resolution: '1280*720',
  duration: 5,
  fps: 25,
  style_preset: ''
})

const imageToVideoForm = reactive<ImageToVideoRequest>({
  prompt: '',
  model: 'wanx2.1-i2v',
  resolution: '1280*720',
  duration: 5,
  fps: 25
})

// 状态
const t2vGenerating = ref(false)
const i2vGenerating = ref(false)

// 文件相关
const imageInput = ref<HTMLInputElement>()
const selectedImage = ref<File | null>(null)
const imagePreview = ref<string | null>(null)

// 结果
const t2vResult = ref<VideoTaskResponse | null>(null)
const i2vResult = ref<VideoTaskResponse | null>(null)
const userStats = ref<UserVideoStats | null>(null)
const stylePresets = ref<VideoStylePreset[]>([])

// 计算属性
const selectedStylePreset = computed(() => {
  if (!textToVideoForm.style_preset) return null
  return stylePresets.value.find(p => p.id.toString() === textToVideoForm.style_preset.toString())
})

// 生命周期
onMounted(() => {
  loadUserStats()
  loadStylePresets()
})

// 文生视频
const generateVideo = async () => {
  if (!textToVideoForm.prompt.trim()) {
    toast.error('请输入视频描述')
    return
  }
  
  t2vGenerating.value = true
  try {
    // 应用风格预设
    let finalForm = { ...textToVideoForm }
    if (selectedStylePreset.value) {
      finalForm.resolution = selectedStylePreset.value.default_resolution
      finalForm.duration = selectedStylePreset.value.default_duration
      finalForm.fps = selectedStylePreset.value.default_fps
      
      // 增强提示词
      finalForm.prompt = `${textToVideoForm.prompt}, ${selectedStylePreset.value.style_keywords}`
    }
    
    const response = await apiService.textToVideo(finalForm)
    
    if (response.code === 200) {
      t2vResult.value = response.data
      toast.success('文生视频任务已提交！')
      
      // 如果是异步任务，轮询状态
      if (response.data.status === 'processing') {
        pollVideoTaskStatus(response.data.task_id, 't2v')
      }
    } else {
      toast.error(response.message || '文生视频失败')
    }
  } catch (error) {
    console.error('文生视频异常:', error)
    toast.error('文生视频失败，请重试')
  } finally {
    t2vGenerating.value = false
  }
}

// 图生视频
const generateImageVideo = async () => {
  if (!selectedImage.value) {
    toast.error('请选择图片文件')
    return
  }
  
  i2vGenerating.value = true
  try {
    const requestData: ImageToVideoRequest = {
      ...imageToVideoForm,
      image_file: selectedImage.value
    }
    
    const response = await apiService.imageToVideo(requestData)
    
    if (response.code === 200) {
      i2vResult.value = response.data
      toast.success('图生视频任务已提交！')
      
      // 轮询任务状态
      if (response.data.status === 'processing') {
        pollVideoTaskStatus(response.data.task_id, 'i2v')
      }
    } else {
      toast.error(response.message || '图生视频失败')
    }
  } catch (error) {
    console.error('图生视频异常:', error)
    toast.error('图生视频失败，请重试')
  } finally {
    i2vGenerating.value = false
  }
}

// 轮询任务状态
const pollVideoTaskStatus = async (taskId: string, type: 't2v' | 'i2v') => {
  const maxAttempts = 60 // 视频生成需要更长时间，最多轮询60次
  let attempts = 0
  
  const poll = async () => {
    try {
      attempts++
      const response = await apiService.getVideoTaskStatus(taskId)
      
      if (response.code === 200) {
        const task = response.data
        
        if (task.status === 'completed') {
          // 更新对应的结果
          if (type === 't2v') {
            t2vResult.value = task
          } else if (type === 'i2v') {
            i2vResult.value = task
          }
          
          toast.success('视频生成完成！')
          loadUserStats() // 刷新统计
          return
        } else if (task.status === 'failed') {
          toast.error('视频生成失败: ' + (task.error_message || '未知错误'))
          return
        } else if (task.status === 'processing' && attempts < maxAttempts) {
          // 继续轮询
          setTimeout(poll, 3000) // 视频任务轮询间隔3秒
        } else if (attempts >= maxAttempts) {
          toast.warning('视频生成时间较长，请稍后查看历史记录')
        }
      }
    } catch (error) {
      console.error('轮询视频任务状态失败:', error)
    }
  }
  
  setTimeout(poll, 3000) // 3秒后开始轮询
}

// 文件处理
const triggerImageInput = () => {
  imageInput.value?.click()
}

const handleImageSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    selectedImage.value = file
    i2vResult.value = null // 清除之前的结果
    
    // 生成预览
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const handleImageDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const file = event.dataTransfer.files[0]
    selectedImage.value = file
    i2vResult.value = null
    
    // 生成预览
    const reader = new FileReader()
    reader.onload = (e) => {
      imagePreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

// 工具函数
const downloadVideo = (url: string) => {
  const link = document.createElement('a')
  link.href = url
  link.download = `video_${Date.now()}.mp4`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  toast.success('视频下载已开始')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const loadUserStats = async () => {
  try {
    const response = await apiService.getUserVideoStats()
    if (response.code === 200) {
      userStats.value = response.data
    }
  } catch (error) {
    console.error('加载用户视频统计失败:', error)
  }
}

const loadStylePresets = async () => {
  try {
    const response = await apiService.getVideoStylePresets()
    if (response.code === 200) {
      stylePresets.value = response.data
    }
  } catch (error) {
    console.error('加载风格预设失败:', error)
  }
}
</script>

<style scoped>
.ai-video-view {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
  background: var(--color-background);
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

.input-section label {
  display: block;
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.input-section textarea {
  width: 100%;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--input-background);
  color: var(--color-text);
  font-size: 1rem;
  resize: vertical;
  font-family: inherit;
}

.settings-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.setting-group {
  display: flex;
  flex-direction: column;
}

.setting-group label {
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.setting-group select {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--input-background);
  color: var(--color-text);
  font-size: 1rem;
}

.style-preset-info {
  background: var(--input-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
}

.style-preset-info h4 {
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.style-preset-info p {
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
}

.preset-keywords {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.keyword-tag {
  background: var(--color-primary-alpha);
  color: var(--color-primary);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.action-section {
  display: flex;
  justify-content: center;
}

.generate-btn {
  background: linear-gradient(135deg, #5e9bff 0%, #a569ff 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  min-width: 120px;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(94, 155, 255, 0.3);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.result-section h3 {
  color: var(--color-text);
  margin-bottom: 1rem;
}

.video-player {
  background: var(--input-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
}

.video-element {
  width: 100%;
  max-height: 400px;
}

.video-placeholder {
  padding: 3rem 2rem;
  text-align: center;
  font-size: 1.2rem;
  color: var(--color-text-secondary);
}

.video-placeholder p {
  margin-top: 1rem;
  font-size: 1rem;
  color: var(--color-text);
}

.video-info {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  background: var(--card-background);
}

.video-controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--card-background);
}

.download-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.download-btn:hover {
  background: var(--color-primary-dark);
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

.selected-file {
  color: var(--color-primary);
  font-weight: 500;
}

.image-preview {
  display: flex;
  justify-content: center;
  margin: 1rem 0;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.stat-item {
  text-align: center;
  padding: 1.5rem;
  background: var(--input-background);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.stat-value {
  font-size: 2rem;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
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
  .ai-video-view {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .demo-card {
    padding: 1.5rem;
  }
  
  .settings-section {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .video-info {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>