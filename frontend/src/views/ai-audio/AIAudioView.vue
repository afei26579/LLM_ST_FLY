<template>
  <div class="ai-audio-view">
    <div class="page-header">
      <h1 class="page-title">AI 声音</h1>
      <p class="page-description">智能语音合成与处理功能</p>
    </div>
    
    <div class="content-container">
      <div class="demo-card">
        <div class="card-header">
          <h2>文本转语音</h2>
          <p>将文字转换为自然流畅的语音</p>
        </div>
        
        <div class="demo-content">
          <div class="input-section">
            <label for="textInput">输入文本：</label>
            <textarea 
              id="textInput" 
              v-model="textInput" 
              placeholder="请输入要转换为语音的文本内容..."
              rows="4"
            ></textarea>
          </div>
          
          <div class="settings-section">
            <div class="setting-group">
              <label>语音类型：</label>
              <select v-model="voiceType">
                <option value="female-sweet">女声-甜美</option>
                <option value="female-professional">女声-专业</option>
                <option value="male-warm">男声-温暖</option>
                <option value="male-deep">男声-深沉</option>
                <option value="child-cute">童声-可爱</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>语速：</label>
              <input 
                type="range" 
                v-model="speechRate" 
                min="0.5" 
                max="2" 
                step="0.1"
                class="slider"
              >
              <span class="slider-value">{{ speechRate }}x</span>
            </div>
            
            <div class="setting-group">
              <label>音调：</label>
              <input 
                type="range" 
                v-model="pitch" 
                min="0.5" 
                max="2" 
                step="0.1"
                class="slider"
              >
              <span class="slider-value">{{ pitch }}x</span>
            </div>
          </div>
          
          <div class="action-section">
            <button class="generate-btn" @click="generateSpeech" :disabled="generating">
              <span v-if="generating">生成中...</span>
              <span v-else>生成语音</span>
            </button>
          </div>
          
          <div class="result-section" v-if="audioGenerated">
            <h3>生成结果</h3>
            <div class="audio-player">
              <div class="audio-placeholder">
                🎵 语音已生成完成
              </div>
              <button class="download-btn" @click="downloadAudio">下载音频</button>
            </div>
          </div>
        </div>
      </div>
      
      <div class="demo-card">
        <div class="card-header">
          <h2>语音识别</h2>
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
              <p v-else class="selected-file">已选择音频文件</p>
              <small>支持 MP3, WAV, M4A 格式</small>
            </div>
          </div>
          
          <div class="recognition-section" v-if="selectedAudio">
            <button class="recognize-btn" @click="recognizeSpeech" :disabled="recognizing">
              <span v-if="recognizing">识别中...</span>
              <span v-else>开始识别</span>
            </button>
            
            <div v-if="recognitionResult" class="recognition-result">
              <h4>识别结果：</h4>
              <div class="result-text">{{ recognitionResult }}</div>
              <button class="copy-btn" @click="copyResult">复制文本</button>
            </div>
          </div>
          
          <div class="live-recognition">
            <h4>实时语音识别</h4>
            <button 
              class="record-btn" 
              :class="{ recording: isRecording }"
              @click="toggleRecording"
            >
              <span v-if="isRecording">🔴 停止录音</span>
              <span v-else>🎤 开始录音</span>
            </button>
            
            <div v-if="liveTranscript" class="live-transcript">
              <h5>实时转录：</h5>
              <p>{{ liveTranscript }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">🗣️</div>
          <h3>文本转语音</h3>
          <p>高质量的语音合成技术</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">👂</div>
          <h3>语音识别</h3>
          <p>准确的语音转文字功能</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🎭</div>
          <h3>语音克隆</h3>
          <p>个性化声音模型训练</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🌍</div>
          <h3>多语言支持</h3>
          <p>支持多种语言和方言</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const textInput = ref('')
const voiceType = ref('female-sweet')
const speechRate = ref(1.0)
const pitch = ref(1.0)
const generating = ref(false)
const audioGenerated = ref(false)

const audioInput = ref<HTMLInputElement>()
const selectedAudio = ref<string | null>(null)
const recognizing = ref(false)
const recognitionResult = ref('')

const isRecording = ref(false)
const liveTranscript = ref('')

const generateSpeech = async () => {
  if (!textInput.value.trim()) {
    alert('请输入要转换的文本')
    return
  }
  
  generating.value = true
  
  // 模拟API调用
  setTimeout(() => {
    audioGenerated.value = true
    generating.value = false
  }, 2000)
}

const triggerAudioInput = () => {
  audioInput.value?.click()
}

const handleAudioSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    const reader = new FileReader()
    reader.onload = (e) => {
      selectedAudio.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const handleAudioDrop = (event: DragEvent) => {
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    const file = event.dataTransfer.files[0]
    const reader = new FileReader()
    reader.onload = (e) => {
      selectedAudio.value = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

const recognizeSpeech = () => {
  recognizing.value = true
  
  setTimeout(() => {
    recognitionResult.value = '这是语音识别的示例结果。在实际应用中，这里会显示从音频文件中识别出的文字内容。AI语音识别技术可以准确地将语音转换为文字，支持多种语言和方言。'
    recognizing.value = false
  }, 3000)
}

const copyResult = () => {
  navigator.clipboard.writeText(recognitionResult.value)
  alert('文本已复制到剪贴板')
}

const toggleRecording = () => {
  isRecording.value = !isRecording.value
  
  if (isRecording.value) {
    // 模拟实时转录
    setTimeout(() => {
      liveTranscript.value = '正在实时转录您的语音...'
    }, 1000)
  } else {
    liveTranscript.value = '录音已停止，最终转录结果：这是实时语音识别的示例结果。'
  }
}

const downloadAudio = () => {
  alert('音频下载功能演示')
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

.slider {
  width: 100%;
  margin-bottom: 0.5rem;
}

.slider-value {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
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
}

.result-section h3 {
  color: var(--color-text);
  margin-bottom: 1rem;
}

.audio-player {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--input-background);
  border-radius: 8px;
  border: 1px solid var(--color-border);
}

.audio-placeholder {
  flex: 1;
  text-align: center;
  font-size: 1.2rem;
  color: var(--color-text-secondary);
}

.download-btn, .copy-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
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

.recognition-result {
  background: var(--input-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
}

.result-text {
  margin: 1rem 0;
  line-height: 1.6;
}

.live-recognition {
  text-align: center;
}

.record-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 50px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.record-btn.recording {
  background: #ff4757;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.live-transcript {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--input-background);
  border-radius: 8px;
  border: 1px solid var(--color-border);
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
}
</style>