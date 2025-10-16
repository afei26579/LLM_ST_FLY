<template>
  <div class="ai-image-view">
    <!-- 如果显示生成组件 -->
    <ImageGenerationView v-if="currentView === 'generation'" @go-back="currentView = 'main'" />
    
    <!-- 如果显示编辑组件 -->
    <ImageEditView v-else-if="currentView === 'editing'" @go-back="currentView = 'main'" />
    
    <!-- 如果显示理解组件 -->
    <ImageUnderstandingView v-else-if="currentView === 'understanding'" @go-back="currentView = 'main'" />
    
    <!-- 主功能选择页面 -->
    <div v-else class="main-view">
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1 class="page-title">AI 图像处理</h1>
            <p class="page-description">智能图像理解、编辑与生成</p>
        </div>
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
                  </div>
                  
      <div class="content-container">
        <!-- 功能卡片网格 -->
        <div class="features-grid">
          <!-- 图像理解 -->
          <div class="feature-card understanding-card" @click="currentView = 'understanding'">
            <div class="card-header">
              <div class="feature-icon">🔍</div>
              <h2>图像理解</h2>
              <p>AI智能解析图像内容</p>
                  </div>
                  
            <div class="card-content">
              <div class="feature-list">
                <div class="feature-item" @click="goToUnderstanding('description')">
                  <span class="feature-icon-small">🔍</span>
                  <span>图像描述</span>
                  </div>
                <div class="feature-item" @click="goToUnderstanding('question')">
                  <span class="feature-icon-small">📚</span>
                  <span>题目解答</span>
                  </div>
                <div class="feature-item" @click="goToUnderstanding('ocr')">
                  <span class="feature-icon-small">📄</span>
                  <span>OCR识别</span>
                </div>
                <div class="feature-item" @click="goToUnderstanding('detection')">
                  <span class="feature-icon-small">🎯</span>
                  <span>物体定位</span>
              </div>
          </div>
              <button class="start-btn" @click="goToUnderstanding('description')">
                ✨ 开始解析
              </button>
            </div>
          </div>

          <!-- 图像编辑 -->
          <div class="feature-card edit-card">
            <div class="card-header">
              <div class="feature-icon">✏️</div>
              <h2>图像编辑</h2>
              <p>智能修改背景、风格，多图融合</p>
              </div>
              
            <div class="card-content">
              <div class="feature-list">
                <div class="feature-item" @click="goToEdit('background')">
                  <span class="feature-icon-small">🌆</span>
                  <span>修改背景</span>
            </div>
                <div class="feature-item" @click="goToEdit('style')">
                  <span class="feature-icon-small">🎭</span>
                  <span>修改风格</span>
              </div>
                <div class="feature-item" @click="goToEdit('prompt')">
                  <span class="feature-icon-small">📝</span>
                  <span>描述修改</span>
              </div>
                <div class="feature-item" @click="goToEdit('merge')">
                  <span class="feature-icon-small">🎨</span>
                  <span>多图融合</span>
            </div>
          </div>
              <button class="start-btn" @click="goToEdit('background')">
                ✨ 开始编辑
              </button>
            </div>
            </div>
            
          <!-- 开始绘图 -->
          <div class="feature-card create-card">
            <div class="card-header">
              <div class="feature-icon">🎨</div>
              <h2>开始绘图</h2>
              <p>使用AI从零创作精美图像</p>
            </div>
                
            <div class="card-content">
              <div class="create-content">
                <div class="create-description">
                  <ul>
                    <li>🎯 智能提示词优化</li>
                    <li>🎨 多种艺术风格</li>
                    <li>📐 灵活的图像尺寸</li>
                    <li>⚡ 快速生成结果</li>
                  </ul>
          </div>
                <button class="start-btn" @click="currentView = 'generation'">
                  ✨ 开始绘图
            </button>
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
      @createSimilar="handleCreateSimilar"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useToast } from 'vue-toastification'
import ImageGenerationView from './components/ImageGenerationView.vue'
import ImageEditView from './components/ImageEditView.vue'
import ImageUnderstandingView from './components/ImageUnderstandingView.vue'
import MyGallery from '@/components/MyGallery.vue'

const toast = useToast()

// 当前视图状态
const currentView = ref<'main' | 'generation' | 'editing' | 'understanding'>('main')

// 我的相册
const showGallery = ref(false)

// 画同款 - 跳转到生成页面并填充参数
const handleCreateSimilar = (image: any) => {
  console.log('画同款 - 图片参数:', image)
  
  // 关闭相册
  showGallery.value = false
  
  // 切换到生成视图
  currentView.value = 'generation'
  
  // 将参数存储到localStorage
  const params = {
    prompt: image.orig_prompt || image.actual_prompt || '',
    negative_prompt: image.negative_prompt || '',
    size: image.task_size || '1328*1328',
    prompt_extend: image.prompt_extend !== undefined ? image.prompt_extend : true,
    watermark: image.watermark !== undefined ? image.watermark : true,
    style: image.style || '',
    shot_type: image.shot_type || '',
    angle: image.angle || '',
    shooting_technique: image.shooting_technique || '',
    lighting: image.lighting || ''
  }
  
  localStorage.setItem('similarImageParams', JSON.stringify(params))
  toast.success('✨ 参数已加载，开始画同款吧！')
}

// 跳转到编辑页面，并指定激活的tab
const goToEdit = (tab: 'background' | 'style' | 'prompt' | 'merge') => {
  currentView.value = 'editing'
  localStorage.setItem('editTabToActivate', tab)
}

// 跳转到图像理解页面，并指定激活的tab
const goToUnderstanding = (tab: 'description' | 'question' | 'ocr' | 'detection') => {
  currentView.value = 'understanding'
  localStorage.setItem('understandingTabToActivate', tab)
}
</script>

<style scoped>
.ai-image-view {
  min-height: 100vh;
  background: var(--color-background);
  color: var(--color-text);
}

.main-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 3rem;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.title-section {
  flex: 1;
  text-align: center;
}

.page-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-description {
  font-size: 1.2rem;
  color: var(--color-textSecondary);
}

.gallery-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  font-size: 1rem;
  box-shadow: 0 4px 12px rgba(94, 155, 255, 0.3);
  white-space: nowrap;
}

.gallery-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(94, 155, 255, 0.4);
}

.content-container {
  display: flex;
  flex-direction: column;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
  align-items: stretch;
}

.feature-card {
  background: var(--card-background);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  height: 100%;
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 2rem;
  text-align: center;
  border-bottom: 1px solid var(--card-border);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.card-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--color-text);
}

.card-header p {
  color: var(--color-textSecondary);
  margin: 0;
}

.card-content {
  padding: 2rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.create-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  text-align: center;
  flex: 1;
  justify-content: space-between;
}

.create-description ul {
  list-style: none;
  padding: 0;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.create-description li {
  padding: 0.5rem 0;
  color: var(--color-text);
  display: inline-block;
}

/* 统一的开始按钮样式 */
.start-btn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(94, 155, 255, 0.3);
  width: 100%;
}

.start-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(94, 155, 255, 0.4);
}

/* 卡片特殊样式 */
.understanding-card {
  background: linear-gradient(135deg, 
    rgba(94, 155, 255, 0.05) 0%, 
    rgba(255, 193, 7, 0.05) 100%
  );
}

.edit-card {
  background: linear-gradient(135deg, 
    rgba(165, 105, 255, 0.05) 0%, 
    rgba(94, 155, 255, 0.05) 100%
  );
}

.create-card {
  background: linear-gradient(135deg, 
    rgba(94, 155, 255, 0.05) 0%, 
    rgba(165, 105, 255, 0.05) 100%
  );
}

.feature-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

/* 图像理解卡片特殊处理 - 4个项目 */
.understanding-card .feature-list {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  color: var(--color-text);
  transition: all 0.2s ease;
  cursor: pointer;
}

.feature-item:hover {
  background: var(--color-primary-alpha);
  border-color: var(--color-primary);
  transform: translateX(4px);
}

.feature-icon-small {
  font-size: 1.5rem;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-view {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 2.5rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .title-section {
    text-align: center;
  }
  
  .gallery-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
