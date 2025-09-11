<template>
  <div class="ai-video-view">
    <div class="page-header">
      <h1 class="page-title">AI 视频</h1>
      <p class="page-description">智能视频生成与处理功能</p>
    </div>
    
    <div class="content-container">
      <div class="demo-card">
        <div class="card-header">
          <h2>文本生成视频</h2>
          <p>通过文字描述生成精彩的AI视频</p>
        </div>
        
        <div class="demo-content">
          <div class="input-section">
            <label for="videoPrompt">视频描述：</label>
            <textarea 
              id="videoPrompt" 
              v-model="videoPrompt" 
              placeholder="请描述您想要生成的视频内容，例如：一只可爱的小猫在花园里玩耍..."
              rows="4"
            ></textarea>
          </div>
          
          <div class="settings-section">
            <div class="setting-group">
              <label>视频时长：</label>
              <select v-model="videoDuration">
                <option value="5">5秒</option>
                <option value="10">10秒</option>
                <option value="15">15秒</option>
                <option value="30">30秒</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>视频质量：</label>
              <select v-model="videoQuality">
                <option value="720p">720p (标清)</option>
                <option value="1080p">1080p (高清)</option>
                <option value="4k">4K (超高清)</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>视频风格：</label>
              <select v-model="videoStyle">
                <option value="realistic">写实风格</option>
                <option value="cartoon">卡通风格</option>
                <option value="anime">动漫风格</option>
                <option value="cinematic">电影风格</option>
              </select>
            </div>
          </div>
          
          <div class="action-section">
            <button class="generate-btn" @click="generateVideo" :disabled="generating">
              <span v-if="generating">生成中...</span>
              <span v-else>生成视频</span>
            </button>
          </div>
          
          <div class="result-section" v-if="generatedVideo">
            <h3>生成结果</h3>
            <div class="video-player">
              <div class="video-placeholder">
                🎬 视频生成完成
                <p>{{ videoPrompt }}</p>
              </div>
              <div class="video-controls">
                <button class="play-btn">▶️ 播放</button>
                <button class="download-btn" @click="downloadVideo">下载视频</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="demo-card">
        <div class="card-header">
          <h2>视频处理</h2>
          <p>上传视频进行AI智能处理</p>
        </div>
        
        <div class="demo-content">
          <div class="upload-section">
            <div class="upload-area" @click="triggerVideoInput" @dragover.prevent @drop.prevent="handleVideoDrop">
              <input 
                ref="videoInput" 
                type="file" 
                accept="video/*" 
                @change="handleVideoSelect" 
                style="display: none"
              >
              <div class="upload-icon">🎥</div>
              <p v-if="!selectedVideo">点击或拖拽视频文件到此处上传</p>
              <p v-else class="selected-file">已选择视频文件</p>
              <small>支持 MP4, AVI, MOV 格式</small>
            </div>
          </div>
          
          <div class="processing-options" v-if="selectedVideo">
            <h4>处理选项：</h4>
            <div class="option-grid">
              <button class="option-btn" @click="enhanceVideo" :disabled="processing">
                <div class="option-icon">✨</div>
                <span>视频增强</span>
              </button>
              
              <button class="option-btn" @click="removeBackground" :disabled="processing">
                <div class="option-icon">🎭</div>
                <span>背景移除</span>
              </button>
              
              <button class="option-btn" @click="addSubtitles" :disabled="processing">
                <div class="option-icon">📝</div>
                <span>自动字幕</span>
              </button>
              
              <button class="option-btn" @click="styleTransfer" :disabled="processing">
                <div class="option-icon">🎨</div>
                <span>风格转换</span>
              </button>
            </div>
          </div>
          
          <div v-if="processing" class="processing-status">
            <div class="loading-spinner"></div>
            <p>处理中，请稍候...</p>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: processingProgress + '%' }"></div>
            </div>
            <span class="progress-text">{{ processingProgress }}%</span>
          </div>
        </div>
      </div>
      
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">🎬</div>
          <h3>文本生视频</h3>
          <p>根据文字描述生成高质量视频</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">✨</div>
          <h3>视频增强</h3>
          <p>提升视频清晰度和质量</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🎭</div>
          <h3>特效处理</h3>
          <p>添加各种视觉特效和滤镜</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🤖</div>
          <h3>智能分析</h3>
          <p>深度分析视频内容和场景</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const videoPrompt = ref('')
const videoDuration = ref('10')
const videoQuality = ref('1080p')
const videoStyle = ref('realistic')
const generating = ref(false)
const generatedVideo = ref(false)

const videoInput = ref<HTMLInputElement>()
const selectedVideo = ref<string | null>(null)
const processing = ref(false)
const processingProgress = ref(0)

const generateVideo = async () => {
  if (!videoPrompt.value.trim()) {
    alert('请输入视频描述')
    return
  }
  
  generating.value = true
  
  // 模拟API调用
  setTimeout(() => {
    generatedVideo.value = true
    generating.value = false
  }, 5000)
}

const triggerVideoInput = () => {
  videoInput.value?.click()
}

const handleVideoSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    selectedVideo.value = file.name
  }
}

const handleVideoDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const file = event.dataTransfer.files[0]
    selectedVideo.value = file.name
  }
}

const processVideo = (type: string) => {
  processing.value = true
  processingProgress.value = 0
  
  const interval = setInterval(() => {
    processingProgress.value += 10
    if (processingProgress.value >= 100) {
      clearInterval(interval)
      processing.value = false
      alert(`${type}处理完成！`)
    }
  }, 200)
}

const enhanceVideo = () => processVideo('视频增强')
const removeBackground = () => processVideo('背景移除')
const addSubtitles = () => processVideo('自动字幕')
const styleTransfer = () => processVideo('风格转换')

const downloadVideo = () => {
  alert('视频下载功能演示')
}
</script>

<style scoped>
.ai-video-view {
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
}

.settings-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.setting-group label {
  display: block;
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.setting-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--input-background);
  color: var(--color-text);
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
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(94, 155, 255, 0.3);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.video-placeholder {
  padding: 3rem 2rem;
  text-align: center;
  font-size: 1.5rem;
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
  padding: 1rem;
  background: var(--card-background);
}

.play-btn, .download-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.play-btn:hover, .download-btn:hover {
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

.processing-options h4 {
  color: var(--color-text);
  margin-bottom: 1rem;
}

.option-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.option-btn {
  background: var(--card-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: center;
}

.option-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.option-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.option-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.processing-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.progress-bar {
  width: 200px;
  height: 8px;
  background: var(--color-border);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.9rem;
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
  
  .option-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>