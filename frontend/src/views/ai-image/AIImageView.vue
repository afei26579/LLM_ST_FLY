<template>
  <div class="ai-image-view">
    <div class="page-header">
      <h1 class="page-title">AI 图片</h1>
      <p class="page-description">智能图片生成与处理功能</p>
    </div>
    
    <div class="content-container">
      <div class="demo-card">
        <div class="card-header">
          <h2>AI 图片生成</h2>
          <p>通过文字描述生成精美的AI图片</p>
        </div>
        
        <div class="demo-content">
          <div class="input-section">
            <label for="imagePrompt">图片描述：</label>
            <textarea 
              id="imagePrompt" 
              v-model="imagePrompt" 
              placeholder="请描述您想要生成的图片内容，例如：一只可爱的小猫坐在花园里..."
              rows="3"
            ></textarea>
          </div>
          
          <div class="settings-section">
            <div class="setting-group">
              <label>图片尺寸：</label>
              <select v-model="imageSize">
                <option value="512x512">512x512 (正方形)</option>
                <option value="768x512">768x512 (横向)</option>
                <option value="512x768">512x768 (纵向)</option>
                <option value="1024x1024">1024x1024 (高清正方形)</option>
              </select>
            </div>
            
            <div class="setting-group">
              <label>艺术风格：</label>
              <select v-model="artStyle">
                <option value="realistic">写实风格</option>
                <option value="cartoon">卡通风格</option>
                <option value="oil-painting">油画风格</option>
                <option value="watercolor">水彩风格</option>
                <option value="digital-art">数字艺术</option>
              </select>
            </div>
          </div>
          
          <div class="action-section">
            <button class="generate-btn" @click="generateImage" :disabled="generating">
              <span v-if="generating">生成中...</span>
              <span v-else>生成图片</span>
            </button>
          </div>
          
          <div class="result-section" v-if="generatedImages.length > 0">
            <h3>生成结果</h3>
            <div class="image-gallery">
              <div 
                v-for="(image, index) in generatedImages" 
                :key="index" 
                class="image-item"
                @click="openImageModal(image)"
              >
                <img :src="image.url" :alt="image.prompt" />
                <div class="image-overlay">
                  <button class="download-btn" @click.stop="downloadImage(image)">
                    下载
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="feature-grid">
        <div class="feature-card">
          <div class="feature-icon">🎨</div>
          <h3>文本生图</h3>
          <p>根据文字描述生成高质量图片</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">✨</div>
          <h3>图片增强</h3>
          <p>提升图片清晰度和质量</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🎭</div>
          <h3>风格转换</h3>
          <p>将图片转换为不同艺术风格</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🔍</div>
          <h3>超分辨率</h3>
          <p>智能放大图片并保持清晰</p>
        </div>
      </div>
    </div>
    
    <!-- 图片预览模态框 -->
    <div v-if="modalImage" class="image-modal" @click="closeImageModal">
      <div class="modal-content" @click.stop>
        <img :src="modalImage.url" :alt="modalImage.prompt" />
        <button class="close-btn" @click="closeImageModal">×</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const imagePrompt = ref('')
const imageSize = ref('512x512')
const artStyle = ref('realistic')
const generating = ref(false)
const generatedImages = ref<Array<{url: string, prompt: string}>>([])
const modalImage = ref<{url: string, prompt: string} | null>(null)

const generateImage = async () => {
  if (!imagePrompt.value.trim()) {
    alert('请输入图片描述')
    return
  }
  
  generating.value = true
  
  // 模拟API调用
  setTimeout(() => {
    // 使用占位图片服务生成示例图片
    const newImage = {
      url: `https://picsum.photos/512/512?random=${Date.now()}`,
      prompt: imagePrompt.value
    }
    generatedImages.value.unshift(newImage)
    generating.value = false
  }, 3000)
}

const openImageModal = (image: {url: string, prompt: string}) => {
  modalImage.value = image
}

const closeImageModal = () => {
  modalImage.value = null
}

const downloadImage = (image: {url: string, prompt: string}) => {
  // 模拟下载功能
  const link = document.createElement('a')
  link.href = image.url
  link.download = `ai-generated-${Date.now()}.jpg`
  link.click()
}
</script>

<style scoped>
.ai-image-view {
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

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.image-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}

.image-item:hover {
  transform: scale(1.05);
}

.image-item img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.image-overlay {
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
  transition: opacity 0.2s;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.download-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
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

.image-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
}

.modal-content img {
  max-width: 100%;
  max-height: 100%;
  border-radius: 8px;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
}

@media (max-width: 768px) {
  .ai-image-view {
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