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
              @input="handleTextInput"
              placeholder="请输入要转换为语音的文本内容（支持智能语种识别）..."
              rows="4"
            ></textarea>
            <div v-if="detectedLanguage" class="language-hint">
              <span class="hint-icon">🔍</span>
              检测到语言: {{ detectedLanguage }}
            </div>
          </div>
          
          <div class="settings-section-horizontal">
            <div class="setting-row">
              <label>语音类型：</label>
              <CustomSelect 
                v-model="textToSpeechForm.voice"
                :options="voiceOptions"
              />
            </div>
            
            <div class="setting-row">
              <label>语言类型：</label>
              <CustomSelect 
                v-model="textToSpeechForm.language_type"
                :options="languageOptions"
              />
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
              <audio 
                v-if="ttsResult.audio_url" 
                controls 
                class="audio-element"
                :key="ttsResult.task_id"
              >
                <source :src="ttsResult.audio_url" type="audio/wav">
                您的浏览器不支持音频播放
              </audio>
              <div v-else class="audio-placeholder">
                🎵 语音生成完成，任务ID: {{ ttsResult.task_id }}
              </div>
              <button v-if="ttsResult.audio_url" class="download-btn" @click="downloadAudio(ttsResult.audio_url)">下载音频</button>
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
              <small>支持 MP3, WAV, M4A 等音频格式</small>
            </div>
          </div>
          
          <div class="action-section" v-if="selectedAudio">
            <button class="recognize-btn" @click="recognizeSpeech" :disabled="sttRecognizing">
              <span v-if="sttRecognizing">识别中...</span>
              <span v-else>开始识别</span>
            </button>
          </div>
          
          <div class="result-section" v-if="sttResult">
            <h3>识别结果 
              <span v-if="sttResult.status === 'processing'" class="status-badge recognizing">识别中...</span>
              <span v-else-if="sttResult.status === 'completed'" class="status-badge completed">✓ 完成</span>
            </h3>
            <div class="recognition-result" :key="sttResult.task_id">
              <div class="result-text">
                <span v-if="sttResult.result_text">{{ sttResult.result_text }}</span>
                <span v-else class="waiting-text">等待识别结果...</span>
              </div>
              <div class="result-actions" v-if="sttResult.status === 'completed'">
                <div class="result-meta">
                  <span v-if="sttResult.confidence">✓ 置信度: {{ (sttResult.confidence * 100).toFixed(1) }}%</span>
                  <span v-if="sttResult.duration">⏱ 时长: {{ sttResult.duration }}秒</span>
                </div>
                <button class="copy-btn" @click="copyResult(sttResult.result_text || '')">
                  📋 复制文本
                </button>
              </div>
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
              <audio 
                v-if="cloneResult.audio_url" 
                controls 
                class="audio-element"
                :key="cloneResult.task_id"
              >
                <source :src="cloneResult.audio_url" type="audio/mpeg">
                您的浏览器不支持音频播放
              </audio>
              <div v-else class="audio-placeholder">
                🎭 语音克隆完成，任务ID: {{ cloneResult.task_id }}
              </div>
              <button v-if="cloneResult.audio_url" class="download-btn" @click="downloadAudio(cloneResult.audio_url)">下载音频</button>
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
            <div class="stat-value">{{ userStats.total_text_to_speech }}</div>
            <div class="stat-label">文字转语音</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userStats.total_speech_to_text }}</div>
            <div class="stat-label">语音转文字</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ Math.round(userStats.total_audio_duration / 60) }}</div>
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
import CustomSelect from '@/components/CustomSelect.vue'
import type { 
  TextToSpeechRequest, 
  SpeechToTextRequest, 
  VoiceCloneRequest,
  AudioTaskResponse,
  UserAudioStats
} from '@/services/api'

const toast = useToast()

// 音色列表（根据 audio_style_list.csv）
const voiceOptions = [
  { value: 'Cherry', label: '芊悦 - 阳光积极、亲切自然小姐姐' },
  { value: 'Ethan', label: '晨煦 - 阳光、温暖、活力、朝气' },
  { value: 'Nofish', label: '不吃鱼 - 不会翘舌音的设计师' },
  { value: 'Jennifer', label: '詹妮弗 - 品牌级、电影质感般美语女声' },
  { value: 'Ryan', label: '甜茶 - 节奏拉满，戏感炸裂' },
  { value: 'Katerina', label: '卡捷琳娜 - 御姐音色，韵律回味十足' },
  { value: 'Elias', label: '墨讲师 - 学科严谨性与叙事技巧' },
  { value: 'Jada', label: '上海-阿珍 - 风风火火的沪上阿姐' },
  { value: 'Dylan', label: '北京-晓东 - 北京胡同里长大的少年' },
  { value: 'Sunny', label: '四川-晴儿 - 甜到你心里的川妹子' },
  { value: 'Li', label: '南京-老李 - 耐心的瑜伽老师' },
  { value: 'Marcus', label: '陕西-秦川 - 面宽话短，心实声沉' },
  { value: 'Roy', label: '闽南-阿杰 - 诙谐直爽、市井活泼' },
  { value: 'Peter', label: '天津-李彼得 - 天津相声，专业捧人' },
  { value: 'Rocky', label: '粤语-阿强 - 幽默风趣的阿强' },
  { value: 'Kiki', label: '粤语-阿清 - 甜美的港妹闺蜜' }
]

// 语言类型选项
const languageOptions = [
  { value: 'Chinese', label: '中文' },
  { value: 'English', label: '英语' },
  { value: 'French', label: '法语' },
  { value: 'German', label: '德语' },
  { value: 'Russian', label: '俄语' },
  { value: 'Italian', label: '意大利语' },
  { value: 'Spanish', label: '西班牙语' },
  { value: 'Portuguese', label: '葡萄牙语' },
  { value: 'Japanese', label: '日语' },
  { value: 'Korean', label: '韩语' }
]

// 表单数据
const textToSpeechForm = reactive<TextToSpeechRequest>({
  text: '',
  voice: 'Cherry',
  language_type: 'Chinese',
  format: 'wav'
})

const speechToTextForm = reactive<SpeechToTextRequest>({
  language: 'auto',  // 自动检测语言
  model: 'qwen-audio-turbo-latest'  // 使用最新模型
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

// 语言检测
const detectedLanguage = ref<string>('')

// 计算属性
const canCloneVoice = computed(() => {
  return voiceCloneForm.reference_text.trim() && 
         voiceCloneForm.target_text.trim() && 
         selectedReferenceAudio.value
})

// 语言检测函数
const detectLanguage = (text: string): string => {
  if (!text.trim()) return ''
  
  // 统计各种字符
  const chineseChars = text.match(/[\u4e00-\u9fa5]/g)?.length || 0
  const englishChars = text.match(/[a-zA-Z]/g)?.length || 0
  const japaneseChars = text.match(/[\u3040-\u309f\u30a0-\u30ff]/g)?.length || 0
  const koreanChars = text.match(/[\uac00-\ud7af]/g)?.length || 0
  const frenchChars = text.match(/[àâäæçéèêëïîôùûüÿœ]/gi)?.length || 0
  const germanChars = text.match(/[äöüß]/gi)?.length || 0
  const russianChars = text.match(/[а-яА-ЯёЁ]/g)?.length || 0
  const spanishChars = text.match(/[áéíóúñü¿¡]/gi)?.length || 0
  const portugueseChars = text.match(/[ãõáàâéêíóôúç]/gi)?.length || 0
  
  const totalChars = text.length
  
  // 计算各语言占比
  const chineseRatio = chineseChars / totalChars
  const englishRatio = englishChars / totalChars
  const japaneseRatio = japaneseChars / totalChars
  const koreanRatio = koreanChars / totalChars
  const russianRatio = russianChars / totalChars
  
  // 判断语言（按优先级）
  if (chineseRatio > 0.3) return 'Chinese'
  if (japaneseRatio > 0.2) return 'Japanese'
  if (koreanRatio > 0.2) return 'Korean'
  if (russianRatio > 0.3) return 'Russian'
  if (germanChars > 2 && englishRatio > 0.5) return 'German'
  if (frenchChars > 2 && englishRatio > 0.5) return 'French'
  if (spanishChars > 2 && englishRatio > 0.5) return 'Spanish'
  if (portugueseChars > 2 && englishRatio > 0.5) return 'Portuguese'
  if (englishRatio > 0.5) return 'English'
  
  // 默认返回中文（如果有少量中文字符）
  if (chineseChars > 0) return 'Chinese'
  
  // 最后默认英文
  return 'English'
}

// 获取语言显示名称
const getLanguageDisplayName = (langCode: string): string => {
  const langMap: Record<string, string> = {
    'Chinese': '中文',
    'English': '英语',
    'French': '法语',
    'German': '德语',
    'Russian': '俄语',
    'Italian': '意大利语',
    'Spanish': '西班牙语',
    'Portuguese': '葡萄牙语',
    'Japanese': '日语',
    'Korean': '韩语'
  }
  return langMap[langCode] || langCode
}

// 处理文本输入
const handleTextInput = () => {
  const text = textToSpeechForm.text
  
  if (text.trim()) {
    const detected = detectLanguage(text)
    if (detected) {
      // 自动设置语言类型
      textToSpeechForm.language_type = detected
      detectedLanguage.value = getLanguageDisplayName(detected)
      
      console.log(`🔍 智能检测: 文本语言为 ${detectedLanguage.value}，已自动选择`)
    }
  } else {
    detectedLanguage.value = ''
  }
}

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
  
  // 清空上一次的结果，避免显示旧的音频
  ttsResult.value = null
  
  ttsGenerating.value = true
  try {
    const response = await apiService.textToSpeech(textToSpeechForm)
    
    if (response.code === 200) {
      // 添加时间戳参数防止浏览器缓存
      const audioData = { ...response.data }
      if (audioData.audio_url) {
        audioData.audio_url = addTimestampToUrl(audioData.audio_url)
      }
      
      ttsResult.value = audioData
      toast.success('文字转语音成功！')
      
      // 刷新统计数据
      loadUserStats()
      
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

// 语音转文字（流式输出）
const recognizeSpeech = async () => {
  if (!selectedAudio.value) {
    toast.error('请选择音频文件')
    return
  }
  
  // 清空上一次的结果
  sttResult.value = null
  
  sttRecognizing.value = true
  
  try {
    // 准备表单数据
    const formData = new FormData()
    formData.append('audio_file', selectedAudio.value)
    formData.append('language', speechToTextForm.language || 'auto')
    formData.append('model', speechToTextForm.model || 'qwen-audio-turbo-latest')
    
    // 获取 token
    const token = localStorage.getItem('token')
    
    // 使用 fetch 进行流式请求
    const response = await fetch('http://localhost:8000/api/v1/chat/ai-audio/speech-to-text/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('语音识别请求失败')
    }
    
    // 读取流式响应
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    
    let fullText = ''
    let taskId = `stt-${Date.now()}`
    
    // 初始化结果对象
    sttResult.value = {
      task_id: taskId,
      result_text: '',
      status: 'processing',
      confidence: 0,
      task_type: 'speech_to_text',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
    
    while (reader) {
      const { done, value } = await reader.read()
      
      if (done) break
      
      // 解码数据
      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const jsonData = JSON.parse(line.slice(6))
            
            if (jsonData.type === 'chunk') {
              // 更新文本（增量更新）
              fullText = jsonData.full_text
              if (sttResult.value) {
                sttResult.value.result_text = fullText
              }
            } else if (jsonData.type === 'done') {
              // 识别完成
              fullText = jsonData.text
              if (sttResult.value) {
                sttResult.value.result_text = fullText
                sttResult.value.confidence = jsonData.confidence || 0.95
                sttResult.value.status = 'completed'
              }
              
              toast.success('语音识别成功！')
              loadUserStats()  // 刷新统计数据
            } else if (jsonData.type === 'error') {
              // 错误处理
              throw new Error(jsonData.message || '识别失败')
            }
          } catch (parseError) {
            console.error('解析流式数据失败:', parseError)
          }
        }
      }
    }
    
  } catch (error: any) {
    console.error('语音识别异常:', error)
    toast.error(error.message || '语音识别失败，请重试')
    
    // 清空结果
    sttResult.value = null
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
  
  // 清空上一次的结果
  cloneResult.value = null
  
  voiceCloning.value = true
  try {
    const requestData: VoiceCloneRequest = {
      ...voiceCloneForm,
      reference_audio: selectedReferenceAudio.value!
    }
    
    const response = await apiService.voiceClone(requestData)
    
    if (response.code === 200) {
      // 添加时间戳防止缓存
      const audioData = { ...response.data }
      if (audioData.audio_url) {
        audioData.audio_url = addTimestampToUrl(audioData.audio_url)
      }
      
      cloneResult.value = audioData
      toast.success('语音克隆任务已提交！')
      
      // 刷新统计数据
      loadUserStats()
      
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
            // 添加时间戳防止缓存
            const audioUrl = task.output_audio_url ? addTimestampToUrl(task.output_audio_url) : ''
            
            ttsResult.value = {
              task_id: task.task_id,
              status: task.status,
              audio_url: audioUrl,
              task_type: task.task_type,
              created_at: task.created_at,
              updated_at: task.updated_at,
              completed_at: task.completed_at
            }
          } else if (type === 'stt') {
            sttResult.value = {
              task_id: task.task_id,
              status: task.status,
              result_text: task.output_text,
              task_type: task.task_type,
              created_at: task.created_at,
              updated_at: task.updated_at,
              completed_at: task.completed_at
            }
          } else if (type === 'clone') {
            // 添加时间戳防止缓存
            const audioUrl = task.output_audio_url ? addTimestampToUrl(task.output_audio_url) : ''
            
            cloneResult.value = {
              task_id: task.task_id,
              status: task.status,
              audio_url: audioUrl,
              task_type: task.task_type,
              created_at: task.created_at,
              updated_at: task.updated_at,
              completed_at: task.completed_at
            }
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
const addTimestampToUrl = (url: string): string => {
  // 添加时间戳参数防止浏览器缓存
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}t=${Date.now()}`
}

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
  min-height: 100vh;
  background: var(--color-background);
}

/* 确保不同主题下背景色一致 */
:global(body) {
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

.language-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-primary-alpha);
  border-left: 3px solid var(--color-primary);
  border-radius: 4px;
  font-size: 0.9rem;
  color: var(--color-text);
  animation: fadeIn 0.3s ease;
}

.hint-icon {
  font-size: 1rem;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

.setting-group {
  display: flex;
  flex-direction: column;
}

.setting-group label {
  font-weight: 500;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

/* 原生 select 样式已被自定义组件替代，保留此处以防需要回退 */

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
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--input-background);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1.5rem;
}

.result-text {
  line-height: 1.8;
  color: var(--color-text);
  background: var(--card-background);
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  font-size: 1rem;
  min-height: 120px;
  white-space: pre-wrap;
  word-wrap: break-word;
  position: relative;
}

.waiting-text {
  color: var(--color-text-secondary);
  font-style: italic;
}

.status-badge {
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  margin-left: 0.5rem;
}

.status-badge.recognizing {
  background: linear-gradient(135deg, #5e9bff 0%, #a569ff 100%);
  color: white;
  animation: pulse 1.5s ease-in-out infinite;
}

.status-badge.completed {
  background: #27ae60;
  color: white;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.result-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.result-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  flex: 1;
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

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>