<template>
  <div class="ai-audio-view">
    <div class="page-header">
      <h1 class="page-title">AI 音频处理</h1>
      <p class="page-description">智能语音合成与处理功能</p>
    </div>
    
    <div class="content-container">
      <!-- 文字转语音 -->
      <div class="demo-card">
        <div class="card-header">
          <h2>文字转语音</h2>
          <p>将文字转换为自然流畅的语音</p>
        </div>
        
        <div class="demo-content">
          <div class="input-section">
            <label for="textInput">输入文本：</label>
            <textarea 
              id="textInput" 
              v-model="textToSpeechForm.text" 
              placeholder="请输入要转换为语音的文本内容..."
              rows="4"
            ></textarea>
          </div>
          
          <div class="settings-section">
            <div class="setting-group">
              <label>语音类型：</label>
              <select v-model="textToSpeechForm.voice">
                <option value="zhifeng_emo">智锋情感</option>
                <option value="zhiyan">志燕</option>
                <option value="zhiqin">志琴</option>
                <option value="zhitong">志童</option>
                <option value="zhiwei">志伟</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>语速：</label>
              <input 
                type="range" 
                v-model="textToSpeechForm.speed" 
                min="0.5" 
                max="2" 
                step="0.1"
                class="slider"
              >
              <span class="slider-value">{{ textToSpeechForm.speed }}x</span>
            </div>
            
            <div class="setting-group">
              <label>音量：</label>
              <input 
                type="range" 
                v-model="textToSpeechForm.volume" 
                min="0" 
                max="100" 
                step="5"
                class="slider"
              >
              <span class="slider-value">{{ textToSpeechForm.volume }}</span>
            </div>

            <div class="setting-group">
              <label>音调：</label>
              <input 
                type="range" 
                v-model="textToSpeechForm.pitch" 
                min="0.5" 
                max="2" 
                step="0.1"
                class="slider"
              >
              <span class="slider-value">{{ textToSpeechForm.pitch }}x</span>
            </div>
          </div>
          
          <div class="action-section">
            <button class="generate-btn" @click="generateSpeech" :disabled="ttsGenerating">
              <span v-if="ttsGenerating">生成中...</span>
              <span v-else>生成语音</span>
            </button>
          </div>
          
          <div class="result-section" v-if="ttsResult">
            <h3>生成结果</h3>
            <div class="audio-player">
              <audio v-if="ttsResult.result_url" controls class="audio-element">
                <source :src="ttsResult.result_url" type="audio/mpeg">
                您的浏览器不支持音频播放
              </audio>
              <div v-else class="audio-placeholder">
                🎵 语音生成完成，任务ID: {{ ttsResult.task_id }}
              </div>
              <button v-if="ttsResult.result_url" class="download-btn" @click="downloadAudio(ttsResult.result_url)">下载音频</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 语音转文字 -->
      <div class="demo-card">
        <div class="card-header">
          <h2>语音转文字</h2>
          <p>将语音转换为文字</p>
        </div>
        
        <div class="demo-content">
          <div class="upload-section">
            <div class="upload-area" @click="triggerAudioInput" @dragover.prevent @drop.prevent="handleAudioDrop">
              <input 
                ref="audioInput" 
                type="file" 
                accept="audio/*" 
                @change="handleAudioSelect" 
                style="display: none"
              >
              <div class="upload-icon">🎵</div>
              <p v-if="!selectedAudio">点击或拖拽音频文件到此处上传</p>
              <p v-else class="selected-file">已选择: {{ selectedAudio.name }}</p>
              <small>支持 MP3, WAV, M4A 格式</small>
            </div>
          </div>

          <div class="settings-section" v-if="selectedAudio">
            <div class="setting-group">
              <label>识别语言：</label>
              <select v-model="speechToTextForm.language">
                <option value="zh-cn">中文</option>
                <option value="en-us">英文</option>
                <option value="ja-jp">日语</option>
                <option value="ko-kr">韩语</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>识别模型：</label>
              <select v-model="speechToTextForm.model">
                <option value="paraformer-realtime-v1">Paraformer实时</option>
                <option value="paraformer-v1">Paraformer标准</option>
              </select>
            </div>
          </div>
          
          <div class="recognition-section" v-if="selectedAudio">
            <button class="recognize-btn" @click="recognizeSpeech" :disabled="sttRecognizing">
              <span v-if="sttRecognizing">识别中...</span>
              <span v-else>开始识别</span>
            </button>
            
            <div v-if="sttResult" class="recognition-result">
              <h4>识别结果：</h4>
              <div class="result-text">{{ sttResult.result_text }}</div>
              <div class="result-meta" v-if="sttResult.confidence">
                <span>置信度: {{ (sttResult.confidence * 100).toFixed(1) }}%</span>
                <span v-if="sttResult.duration">时长: {{ sttResult.duration }}秒</span>
              </div>
              <button class="copy-btn" @click="copyResult(sttResult.result_text)">复制文本</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 语音克隆 -->
      <div class="demo-card">
        <div class="card-header">
          <h2>语音克隆</h2>
          <p>基于参考音频克隆特定的语音风格</p>
        </div>
        
        <div class="demo-content">
          <div class="input-section">
            <label for="referenceText">参考音频对应文本：</label>
            <textarea 
              id="referenceText" 
              v-model="voiceCloneForm.reference_text" 
              placeholder="请输入参考音频中说话的内容..."
              rows="2"
            ></textarea>
          </div>

          <div class="upload-section">
            <div class="upload-area" @click="triggerReferenceAudioInput" @dragover.prevent @drop.prevent="handleReferenceAudioDrop">
              <input 
                ref="referenceAudioInput" 
                type="file" 
                accept="audio/*" 
                @change="handleReferenceAudioSelect" 
                style="display: none"
              >
              <div class="upload-icon">🎤</div>
              <p v-if="!selectedReferenceAudio">上传参考音频文件</p>
              <p v-else class="selected-file">已选择: {{ selectedReferenceAudio.name }}</p>
              <small>建议使用清晰的人声录音，时长3-10秒</small>
            </div>
          </div>

          <div class="input-section">
            <label for="targetText">目标生成文本：</label>
            <textarea 
              id="targetText" 
              v-model="voiceCloneForm.target_text" 
              placeholder="请输入要使用克隆声音说出的内容..."
              rows="3"
            ></textarea>
          </div>
          
          <div class="action-section">
            <button class="generate-btn" @click="cloneVoice" :disabled="voiceCloning || !canCloneVoice">
              <span v-if="voiceCloning">克隆中...</span>
              <span v-else>克隆语音</span>
            </button>
          </div>
          
          <div class="result-section" v-if="cloneResult">
            <h3>克隆结果</h3>
            <div class="audio-player">
              <audio v-if="cloneResult.result_url" controls class="audio-element">
                <source :src="cloneResult.result_url" type="audio/mpeg">
                您的浏览器不支持音频播放
              </audio>
              <div v-else class="audio-placeholder">
                🎭 语音克隆完成，任务ID: {{ cloneResult.task_id }}
              </div>
              <button v-if="cloneResult.result_url" class="download-btn" @click="downloadAudio(cloneResult.result_url)">下载音频</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 使用统计 -->
      <div class="demo-card" v-if="userStats">
        <div class="card-header">
          <h2>使用统计</h2>
          <p>您的音频处理使用情况</p>
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
          <div class="feature-icon">🗣️</div>
          <h3>文本转语音</h3>
          <p>高质量的语音合成技术，支持多种音色</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">👂</div>
          <h3>语音识别</h3>
          <p>准确的语音转文字功能，支持多种语言</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🎭</div>
          <h3>语音克隆</h3>
          <p>个性化声音模型，克隆任意音色</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h3>实时处理</h3>
          <p>快速响应，高效的音频处理能力</p>
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
  TextToSpeechRequest, 
  SpeechToTextRequest, 
  VoiceCloneRequest,
  AudioTaskResponse,
  UserAudioStats
} from '@/services/api'

const toast = useToast()

// 表单数据
const textToSpeechForm = reactive<TextToSpeechRequest>({
  text: '',
  voice: 'zhifeng_emo',
  speed: 1.0,
  volume: 50,
  pitch: 1.0,
  format: 'mp3'
})

const speechToTextForm = reactive<SpeechToTextRequest>({
  language: 'zh-cn',
  model: 'paraformer-realtime-v1'
})

const voiceCloneForm = reactive<VoiceCloneRequest>({
  reference_text: '',
  target_text: '',
  model: 'sambert-v1'
})

// 状态
const ttsGenerating = ref(false)
const sttRecognizing = ref(false)
const voiceCloning = ref(false)

// 文件相关
const audioInput = ref<HTMLInputElement>()
const referenceAudioInput = ref<HTMLInputElement>()
const selectedAudio = ref<File | null>(null)
const selectedReferenceAudio = ref<File | null>(null)

// 结果
const ttsResult = ref<AudioTaskResponse | null>(null)
const sttResult = ref<AudioTaskResponse | null>(null)
const cloneResult = ref<AudioTaskResponse | null>(null)
const userStats = ref<UserAudioStats | null>(null)

// 计算属性
const canCloneVoice = computed(() => {
  return voiceCloneForm.reference_text.trim() && 
         voiceCloneForm.target_text.trim() && 
         selectedReferenceAudio.value
})

// 生命周期
onMounted(() => {
  loadUserStats()
})

// 文字转语音
const generateSpeech = async () => {
  if (!textToSpeechForm.text.trim()) {
    toast.error('请输入要转换的文本')
    return
  }
  
  ttsGenerating.value = true
  try {
    const response = await apiService.textToSpeech(textToSpeechForm)
    
    if (response.code === 200) {
      ttsResult.value = response.data
      toast.success('文字转语音成功！')
      
      // 如果是异步任务，可以轮询状态
      if (response.data.status === 'processing') {
        pollTaskStatus(response.data.task_id, 'tts')
      }
    } else {
      toast.error(response.message || '文字转语音失败')
    }
  } catch (error) {
    console.error('文字转语音异常:', error)
    toast.error('文字转语音失败，请重试')
  } finally {
    ttsGenerating.value = false
  }
}

// 语音转文字
const recognizeSpeech = async () => {
  if (!selectedAudio.value) {
    toast.error('请选择音频文件')
    return
  }
  
  sttRecognizing.value = true
  try {
    const requestData: SpeechToTextRequest = {
      ...speechToTextForm,
      audio_file: selectedAudio.value
    }
    
    const response = await apiService.speechToText(requestData)
    
    if (response.code === 200) {
      sttResult.value = response.data
      toast.success('语音识别成功！')
      
      // 如果是异步任务，可以轮询状态
      if (response.data.status === 'processing') {
        pollTaskStatus(response.data.task_id, 'stt')
      }
    } else {
      toast.error(response.message || '语音识别失败')
    }
  } catch (error) {
    console.error('语音识别异常:', error)
    toast.error('语音识别失败，请重试')
  } finally {
    sttRecognizing.value = false
  }
}

// 语音克隆
const cloneVoice = async () => {
  if (!canCloneVoice.value) {
    toast.error('请填写完整信息并上传参考音频')
    return
  }
  
  voiceCloning.value = true
  try {
    const requestData: VoiceCloneRequest = {
      ...voiceCloneForm,
      reference_audio: selectedReferenceAudio.value!
    }
    
    const response = await apiService.voiceClone(requestData)
    
    if (response.code === 200) {
      cloneResult.value = response.data
      toast.success('语音克隆任务已提交！')
      
      // 轮询任务状态
      if (response.data.status === 'processing') {
        pollTaskStatus(response.data.task_id, 'clone')
      }
    } else {
      toast.error(response.message || '语音克隆失败')
    }
  } catch (error) {
    console.error('语音克隆异常:', error)
    toast.error('语音克隆失败，请重试')
  } finally {
    voiceCloning.value = false
  }
}

// 轮询任务状态
const pollTaskStatus = async (taskId: string, type: 'tts' | 'stt' | 'clone') => {
  const maxAttempts = 30 // 最多轮询30次
  let attempts = 0
  
  const poll = async () => {
    try {
      attempts++
      const response = await apiService.getAudioTaskStatus(taskId)
      
      if (response.code === 200) {
        const task = response.data
        
        if (task.status === 'completed') {
          // 更新对应的结果
          if (type === 'tts') {
            ttsResult.value = task
          } else if (type === 'stt') {
            sttResult.value = task
          } else if (type === 'clone') {
            cloneResult.value = task
          }
          
          toast.success('任务完成！')
          loadUserStats() // 刷新统计
          return
        } else if (task.status === 'failed') {
          toast.error('任务失败: ' + (task.error_message || '未知错误'))
          return
        } else if (task.status === 'processing' && attempts < maxAttempts) {
          // 继续轮询
          setTimeout(poll, 2000)
        } else if (attempts >= maxAttempts) {
          toast.warning('任务处理时间较长，请稍后查看历史记录')
        }
      }
    } catch (error) {
      console.error('轮询任务状态失败:', error)
    }
  }
  
  setTimeout(poll, 2000) // 2秒后开始轮询
}

// 文件处理
const triggerAudioInput = () => {
  audioInput.value?.click()
}

const triggerReferenceAudioInput = () => {
  referenceAudioInput.value?.click()
}

const handleAudioSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedAudio.value = target.files[0]
    sttResult.value = null // 清除之前的结果
  }
}

const handleReferenceAudioSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    selectedReferenceAudio.value = target.files[0]
    cloneResult.value = null // 清除之前的结果
  }
}

const handleAudioDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedAudio.value = event.dataTransfer.files[0]
    sttResult.value = null
  }
}

const handleReferenceAudioDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    selectedReferenceAudio.value = event.dataTransfer.files[0]
    cloneResult.value = null
  }
}

// 工具函数
const copyResult = (text: string) => {
  navigator.clipboard.writeText(text).then(() => {
    toast.success('文本已复制到剪贴板')
  }).catch(() => {
    toast.error('复制失败，请手动复制')
  })
}

const downloadAudio = (url: string) => {
  const link = document.createElement('a')
  link.href = url
  link.download = `audio_${Date.now()}.mp3`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
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
    const response = await apiService.getUserAudioStats()
    if (response.code === 200) {
      userStats.value = response.data
    }
  } catch (error) {
    console.error('加载用户统计失败:', error)
  }
}
</script>

<style scoped>
.ai-audio-view {
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

.slider {
  width: 100%;
  margin-bottom: 0.5rem;
}

.slider-value {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  text-align: center;
  display: block;
}

.action-section {
  display: flex;
  justify-content: center;
}

.generate-btn, .recognize-btn {
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

.generate-btn:hover:not(:disabled),
.recognize-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(94, 155, 255, 0.3);
}

.generate-btn:disabled,
.recognize-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.result-section h3 {
  color: var(--color-text);
  margin-bottom: 1rem;
}

.audio-player {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  background: var(--input-background);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.audio-element {
  width: 100%;
}

.audio-placeholder {
  text-align: center;
  font-size: 1.1rem;
  color: var(--color-text-secondary);
  padding: 2rem;
}

.download-btn, .copy-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  align-self: center;
}

.download-btn:hover, .copy-btn:hover {
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

.recognition-result {
  background: var(--input-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
}

.result-text {
  margin: 1rem 0;
  line-height: 1.6;
  color: var(--color-text);
  background: var(--card-background);
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid var(--color-border);
}

.result-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
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
  .ai-audio-view {
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
}
</style>