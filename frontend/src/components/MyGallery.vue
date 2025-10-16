<template>
  <!-- 我的相册模态框 -->
  <div v-if="showGallery" class="gallery-modal" @click="$emit('close')">
    <div class="gallery-modal-content" @click.stop>
      <div class="gallery-header">
        <h2>我的相册</h2>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      
      <!-- 相册分类tab -->
      <div class="gallery-tabs">
        <button 
          class="gallery-tab-btn"
          :class="{ active: activeTab === 'text_to_image' }"
          @click="switchTab('text_to_image')"
        >
          <span class="tab-icon">🎨</span>
          <span>文生图</span>
        </button>
        <button 
          class="gallery-tab-btn"
          :class="{ active: activeTab === 'image_edit' }"
          @click="switchTab('image_edit')"
        >
          <span class="tab-icon">✏️</span>
          <span>图像编辑</span>
        </button>
      </div>
      
      <div class="gallery-body">
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner-large"></div>
          <p>加载中...</p>
        </div>
        
        <div v-else-if="images.length > 0" class="gallery-grid">
          <div 
            v-for="image in images" 
            :key="image.id" 
            class="gallery-item"
          >
            <div class="gallery-image-container">
              <img :src="image.saved_url || image.original_url" :alt="image.orig_prompt" />
              <div class="gallery-image-overlay">
                <div class="overlay-actions">
                  <!-- 文生图：显示画同款 + 下载 -->
                  <template v-if="image.image_source === 'text_to_image'">
                    <button class="gallery-action-btn create-similar-btn" @click.stop="handleCreateSimilar(image)" title="画同款">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 19l7-7 3 3-7 7-3-3z"></path>
                        <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path>
                        <path d="M2 2l7.586 7.586"></path>
                        <circle cx="11" cy="11" r="2"></circle>
                      </svg>
                    </button>
                    <button class="gallery-action-btn download-btn" @click.stop="handleDownload(image)" title="下载图片">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                      </svg>
                    </button>
                  </template>
                  
                  <!-- 图像编辑：只显示下载 -->
                  <template v-else>
                    <button class="gallery-action-btn download-btn single-btn" @click.stop="handleDownload(image)" title="下载图片">
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
        <div v-if="pagination.total_pages > 1" class="gallery-pagination">
          <button 
            class="page-btn" 
            :disabled="!pagination.has_previous"
            @click="loadPage(pagination.page - 1)"
          >
            上一页
          </button>
          <span class="page-info">{{ pagination.page }} / {{ pagination.total_pages }}</span>
          <button 
            class="page-btn" 
            :disabled="!pagination.has_next"
            @click="loadPage(pagination.page + 1)"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { apiService } from '@/services/api'

interface Props {
  showGallery: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['close', 'createSimilar'])

const toast = useToast()

// 状态
const loading = ref(false)
const images = ref<any[]>([])
const activeTab = ref<'text_to_image' | 'image_edit'>('text_to_image')
const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0,
  total_pages: 0,
  has_next: false,
  has_previous: false
})

// 确保URL是完整的绝对路径
const ensureAbsoluteUrl = (url: string): string => {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  const baseUrl = 'http://localhost:8000'
  return url.startsWith('/') ? `${baseUrl}${url}` : `${baseUrl}/${url}`
}

// 切换tab
const switchTab = (tab: 'text_to_image' | 'image_edit') => {
  activeTab.value = tab
  loadImages(1)
}

// 加载图片
const loadImages = async (page: number = 1) => {
  loading.value = true
  try {
    const response = await apiService.getImageHistory(page, 20)
    
    if (response.code === 200) {
      let allImages = response.data.list.map((img: any) => ({
        ...img,
        saved_url: ensureAbsoluteUrl(img.saved_url),
        original_url: ensureAbsoluteUrl(img.original_url)
      }))
      
      // 根据当前tab过滤
      allImages = allImages.filter((img: any) => img.image_source === activeTab.value)
      
      images.value = allImages
      pagination.value = {
        page: response.data.page,
        page_size: response.data.page_size,
        total: allImages.length,
        total_pages: Math.ceil(allImages.length / response.data.page_size),
        has_next: response.data.has_next,
        has_previous: response.data.has_previous
      }
    }
  } catch (error) {
    console.error('加载图片失败:', error)
    toast.error('加载图片失败')
  } finally {
    loading.value = false
  }
}

const loadPage = (page: number) => {
  loadImages(page)
}

// 画同款
const handleCreateSimilar = (image: any) => {
  emit('createSimilar', image)
}

// 下载图片
const handleDownload = async (image: any) => {
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
    console.error('下载失败:', error)
    toast.error('下载失败，请稍后重试')
  }
}

// 格式化文件大小
const formatFileSize = (bytes: number) => {
  if (!bytes) return '未知'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

// 格式化日期
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

// 监听显示状态
watch(() => props.showGallery, (newValue) => {
  if (newValue) {
    loadImages()
  }
})
</script>

<style scoped>
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

.close-btn {
  width: 36px;
  height: 36px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  color: var(--color-textSecondary);
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--color-error);
  color: white;
  border-color: var(--color-error);
  transform: rotate(90deg);
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

.gallery-action-btn.single-btn {
  margin: 0 auto;
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

@keyframes spin {
  to { transform: rotate(360deg); }
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

/* 滚动条样式 */
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

/* 响应式 */
@media (max-width: 768px) {
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
}
</style>

