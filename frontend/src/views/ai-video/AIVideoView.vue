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
          
          <div class="settings-section-horizontal">
            <div class="setting-row">
              <label>视频分辨率：</label>
              <CustomSelect 
                v-model="textToVideoForm.resolution"
                :options="resolutionOptions"
              />
            </div>
            
            <div class="setting-row">
              <label>视频时长：</label>
              <CustomSelect 
                v-model="textToVideoForm.duration"
                :options="durationOptions"
              />
            </div>
            
            <div class="setting-row seed-row">
              <label>随机种子：</label>
              <div class="seed-controls">
                <input 
                  type="number" 
                  v-model.number="textToVideoForm.seed" 
                  @blur="validateSeed"
                  @input="validateSeed"
                  min="0" 
                  max="2147483647"
                  step="1"
                  class="seed-input"
                  placeholder="0 - 2147483647"
                >
                <button class="random-seed-btn" @click="randomizeSeed" type="button" title="生成随机种子">
                  🎲
                </button>
              </div>
            </div>
          </div>
          
          <div class="action-section">
            <button class="generate-btn" @click="generateVideo" :disabled="t2vGenerating || !canGenerateVideo">
              <span v-if="t2vGenerating">生成中...</span>
              <span v-else>生成视频</span>
            </button>
          </div>
          
          <div class="result-section" v-if="t2vResult">
            <h3>生成结果</h3>
            <div class="video-player-wrapper">
              <div class="video-player">
                <video v-if="t2vResult.result_url" controls class="video-element" preload="metadata">
                  <source :src="t2vResult.result_url" type="video/mp4">
                  您的浏览器不支持视频播放
                </video>
                <div v-else class="video-placeholder">
                  🎬 视频生成中，任务ID: {{ t2vResult.task_id }}
                  <p v-if="t2vResult.status === 'processing'">正在处理中，请稍候...</p>
                </div>
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
          <!-- 隐藏的文件输入框 -->
          <input 
            ref="imageInput" 
            type="file" 
            accept="image/*" 
            @change="handleImageSelect" 
            style="display: none"
          >
          
          <!-- 上传区域（未选择图片时显示） -->
          <div class="upload-section" v-if="!selectedImage">
            <div class="upload-area" @click="triggerImageInput" @dragover.prevent @drop.prevent="handleImageDrop">
              <div class="upload-icon">🖼️</div>
              <p>点击或拖拽图片文件到此处上传</p>
              <small>支持 JPG, PNG, WebP 格式，建议分辨率不超过2048x2048</small>
            </div>
          </div>

          <!-- 图片和设置区域（选择图片后显示，横向布局） -->
          <div class="i2v-content-wrapper" v-if="selectedImage">
            <!-- 左侧：图片预览 -->
            <div class="i2v-left-panel">
              <div class="image-preview-card" @click="triggerImageInput">
                <img :src="imagePreview" alt="预览图片" class="preview-image" />
                <div class="change-image-hint">点击更换图片</div>
              </div>
            </div>
            
            <!-- 右侧：设置区域 -->
            <div class="i2v-right-panel">
              <div class="i2v-settings-container">
                <div class="input-section">
                  <label for="imageVideoPrompt">动态描述</label>
                  <textarea 
                    id="imageVideoPrompt" 
                    v-model="imageToVideoForm.prompt" 
                    placeholder="描述图片中的元素应该如何动起来..."
                    rows="8"
                    class="i2v-prompt-textarea"
                  ></textarea>
                </div>
                
                <div class="settings-section-horizontal">
                  <div class="setting-row">
                    <label>视频分辨率：</label>
                    <CustomSelect 
                      v-model="imageToVideoForm.resolution"
                      :options="i2vResolutionOptions"
                    />
                  </div>
                  
                  <div class="setting-row">
                    <label>视频时长：</label>
                    <CustomSelect 
                      v-model="imageToVideoForm.duration"
                      :options="i2vDurationOptions"
                    />
                  </div>
                </div>
              </div>
              
              <div class="action-section">
                <button class="generate-btn" @click="generateImageVideo" :disabled="i2vGenerating">
                  <span v-if="i2vGenerating">生成中...</span>
                  <span v-else>生成视频</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 生成结果 -->
          <div class="result-section" v-if="i2vResult">
            <h3>生成结果</h3>
            <div class="video-player-wrapper">
              <div class="video-player">
                <video v-if="i2vResult.result_url" controls class="video-element" preload="metadata">
                  <source :src="i2vResult.result_url" type="video/mp4">
                  您的浏览器不支持视频播放
                </video>
                <div v-else class="video-placeholder">
                  🎬 视频生成中，任务ID: {{ i2vResult.task_id }}
                  <p v-if="i2vResult.status === 'processing'">正在处理中，请稍候...</p>
                </div>
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
      <!--div class="feature-grid">
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
      </div -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'
import CustomSelect from '@/components/CustomSelect.vue'
import type { 
  TextToVideoRequest, 
  ImageToVideoRequest,
  VideoTaskResponse,
  UserVideoStats
} from '@/services/api'

const toast = useToast()

// 视频分辨率选项
const resolutionOptions = [
  { value: '854*480', label: '480P' },
  { value: '1280*720', label: '720P' },
  { value: '1920*1080', label: '1080P' }
]

// 视频时长选项
const durationOptions = [
  { value: 5, label: '5秒' },
  { value: 10, label: '10秒' }
]

// 图生视频分辨率选项（使用 P 格式，如 720P）
const i2vResolutionOptions = [
  { value: '480P', label: '480P' },
  { value: '720P', label: '720P' },
  { value: '1080P', label: '1080P' }
]

// 图生视频时长选项（与文生视频一致）
const i2vDurationOptions = [
  { value: 5, label: '5秒' },
  { value: 10, label: '10秒' }
]

// 表单数据
const textToVideoForm = reactive<any>({
  prompt: '',
  model: 'wan2.5-t2v-preview',
  resolution: '1280*720',
  duration: 5,
  fps: 24,
  seed: Math.floor(Math.random() * 2147483647)
})

const imageToVideoForm = reactive<any>({
  prompt: '',
  // 不传 model，使用后端默认的 wan2.5-i2v-preview
  resolution: '720P',  // 使用 P 格式
  duration: 5,
  fps: 24
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

// 计算属性
const canGenerateVideo = computed(() => {
  return textToVideoForm.prompt.trim().length > 0
})

// 验证随机种子
const validateSeed = () => {
  if (!textToVideoForm.seed) {
    textToVideoForm.seed = 0
    return
  }
  
  // 转换为整数
  textToVideoForm.seed = Math.floor(textToVideoForm.seed)
  
  // 确保在有效范围内
  if (textToVideoForm.seed < 0) {
    textToVideoForm.seed = 0
  } else if (textToVideoForm.seed > 2147483647) {
    textToVideoForm.seed = 2147483647
  }
}

// 生成随机种子
const randomizeSeed = () => {
  textToVideoForm.seed = Math.floor(Math.random() * 2147483647)
}

// 生命周期
onMounted(() => {
  loadUserStats()
})

// 文生视频
const generateVideo = async () => {
  if (!textToVideoForm.prompt.trim()) {
    toast.error('请输入视频描述')
    return
  }
  
  t2vGenerating.value = true
  try {
    const response = await apiService.textToVideo(textToVideoForm)
    
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
    // 不传 model，使用后端默认值
    const requestData = {
      prompt: imageToVideoForm.prompt,
      resolution: imageToVideoForm.resolution,
      duration: imageToVideoForm.duration,
      fps: imageToVideoForm.fps,
      image_file: selectedImage.value
      // model 不传，后端会使用默认的 wan2.5-i2v-preview
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

/* 横向排列的设置区域 */
.settings-section-horizontal {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.setting-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.setting-row label {
  font-weight: 500;
  color: var(--color-text);
  white-space: nowrap;
  flex-shrink: 0;
}

/* 自定义下拉组件会自动填充剩余空间 */

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

/* 种子输入行 */
.seed-row {
  flex: 1.2;  /* 种子输入框稍宽一些 */
}

.seed-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex: 1;
}

.seed-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--card-background);
  color: var(--color-text);
  font-size: 1rem;
  transition: border-color 0.2s;
}

.seed-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(94, 155, 255, 0.1);
}

.seed-input::-webkit-inner-spin-button,
.seed-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.seed-input[type=number] {
  -moz-appearance: textfield;
}

.random-seed-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.2rem;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}

.random-seed-btn:hover {
  background: var(--color-primary-dark);
  transform: scale(1.05);
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

.video-player-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.video-player {
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--input-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
  min-height: 400px;
  padding: 1rem;
}

.video-element {
  max-width: 100%;
  max-height: 600px;
  border-radius: 4px;
  display: block;
  margin: 0 auto;
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

.video-controls {
  display: flex;
  justify-content: center;
  gap: 1rem;
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

/* 图生视频：左右两栏布局 */
.i2v-content-wrapper {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 2rem;
  align-items: end;  /* 底部对齐 */
}

.i2v-left-panel {
  display: flex;
  flex-direction: column;
}

.i2v-right-panel {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.i2v-settings-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.i2v-prompt-textarea {
  min-height: 180px !important;
  flex: 1;
}

.image-preview-card {
  position: relative;
  background: var(--input-background);
  border: 2px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-preview-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 12px rgba(94, 155, 255, 0.2);
}

.image-preview-card:hover .change-image-hint {
  opacity: 1;
}

.preview-image {
  width: 100%;
  height: auto;
  display: block;
}

.change-image-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  text-align: center;
  padding: 0.75rem;
  font-size: 0.9rem;
  opacity: 0;
  transition: opacity 0.3s ease;
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

@media (max-width: 1024px) {
  .i2v-content-wrapper {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    align-items: start;  /* 移动端改为顶部对齐 */
  }
  
  .i2v-right-panel {
    height: auto;
  }
  
  .image-preview-card {
    max-width: 500px;
    margin: 0 auto;
  }
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
  
  .settings-section-horizontal {
    flex-direction: column;
    gap: 1rem;
  }
  
  .setting-row {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .setting-row label {
    margin-bottom: 0.5rem;
  }
  
  
  .seed-row .seed-controls {
    width: 100%;
  }
  
  .seed-input {
    width: 100%;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .image-preview-card {
    max-width: 100%;
  }
}
</style>