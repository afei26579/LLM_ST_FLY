<template>
  <div class="map-panel">
    <!-- 头部 -->
    <div class="map-header">
      <h3>🗺️ 地图视图</h3>
      <div class="header-info" v-if="currentCity">
        <span class="city-badge">📍 {{ currentCity }}</span>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="map-search">
      <div class="search-input-group">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索景点、餐厅、酒店..."
          @keydown.enter="handleSearch"
        />
        <button @click="handleSearch" :disabled="!searchKeyword.trim()" class="search-btn">
          🔍
        </button>
      </div>
      <button @click="clearMap" class="clear-btn" title="清除标记">
        🧹 清除
      </button>
    </div>

    <!-- 搜索结果列表 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div class="results-header">
        <span>找到 {{ searchResults.length }} 个结果</span>
        <button @click="searchResults = []" class="close-btn">×</button>
      </div>
      <div class="results-list">
        <div
          v-for="poi in searchResults"
          :key="poi.id"
          class="result-item"
          @click="handlePOIClick(poi)"
        >
          <div class="poi-info">
            <h4>{{ poi.name }}</h4>
            <p v-if="poi.address">{{ poi.address }}</p>
            <div class="poi-meta">
              <span v-if="poi.type" class="poi-type">{{ poi.type }}</span>
              <span v-if="poi.tel" class="poi-tel">📞 {{ poi.tel }}</span>
            </div>
          </div>
          <button @click.stop="addToItinerary(poi)" class="add-btn">+</button>
        </div>
      </div>
    </div>

    <!-- 地图容器 -->
    <div :id="mapContainerId" class="map-container"></div>

    <!-- 加载提示 -->
    <div v-if="!isMapReady" class="map-loading">
      <div class="loading-spinner"></div>
      <p>地图加载中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

// Props
interface Props {
  mapContainerId?: string
  currentCity?: string
  markers?: Array<{
    id: string
    position: [number, number]
    title: string
    poi?: any
  }>
  isMapReady?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  mapContainerId: 'travel-map',
  currentCity: '',
  markers: () => [],
  isMapReady: false
})

// Emits
const emit = defineEmits<{
  'map-ready': []
  'search-poi': [keyword: string, city: string]
  'poi-click': [poi: any]
  'add-to-itinerary': [poi: any]
  'clear-markers': []
}>()

// 状态
const searchKeyword = ref('')
const searchResults = ref<any[]>([])

// 方法
const handleSearch = () => {
  if (!searchKeyword.value.trim()) return
  
  emit('search-poi', searchKeyword.value, props.currentCity || '全国')
  searchKeyword.value = ''
}

const handlePOIClick = (poi: any) => {
  emit('poi-click', poi)
}

const addToItinerary = (poi: any) => {
  emit('add-to-itinerary', poi)
}

const clearMap = () => {
  searchResults.value = []
  emit('clear-markers')
}

// 暴露方法供父组件调用
defineExpose({
  setSearchResults: (results: any[]) => {
    searchResults.value = results
  },
  clearSearchResults: () => {
    searchResults.value = []
  }
})

onMounted(() => {
  emit('map-ready')
})
</script>

<style scoped>
.map-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--card-background);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
  position: relative;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--button-secondary);
  color: var(--button-secondaryText);
}

.map-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.city-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
}

.map-search {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-secondary, #f5f5f5);
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.search-input-group {
  flex: 1;
  display: flex;
  gap: 8px;
}

.search-input-group input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color, #ddd);
  border-radius: 6px;
  font-size: 14px;
}

.search-input-group input:focus {
  outline: none;
  border-color: #f093fb;
}

.search-btn,
.clear-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.search-btn {
  background: var(--button-secondary);
  color: var(--button-secondaryText);
}

.search-btn:hover:not(:disabled) {
  background: var(--button-secondaryHover);
}

.search-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clear-btn {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.clear-btn:hover {
  background: #ffebe6;
  border-color: #ff7875;
  color: #ff7875;
}

.search-results {
  position: absolute;
  top: 120px;
  left: 16px;
  right: 16px;
  max-height: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  z-index: 10;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-secondary, #f5f5f5);
  border-bottom: 1px solid var(--border-color, #e0e0e0);
  font-size: 13px;
  color: var(--text-secondary, #666);
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: var(--text-secondary, #666);
  padding: 0;
  width: 24px;
  height: 24px;
}

.close-btn:hover {
  color: var(--text-primary, #333);
}

.results-list {
  flex: 1;
  overflow-y: auto;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
  cursor: pointer;
  transition: background 0.2s;
}

.result-item:hover {
  background: var(--bg-secondary, #f9f9f9);
}

.result-item:last-child {
  border-bottom: none;
}

.poi-info {
  flex: 1;
}

.poi-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: var(--text-primary, #333);
}

.poi-info p {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary, #666);
}

.poi-meta {
  display: flex;
  gap: 12px;
  margin-top: 4px;
}

.poi-type,
.poi-tel {
  font-size: 11px;
  color: var(--text-tertiary, #999);
}

.add-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  transition: transform 0.2s;
}

.add-btn:hover {
  transform: scale(1.1);
}

.map-container {
  flex: 1;
  position: relative;
  min-height: 400px;
}

.map-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 5;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 12px;
  border: 4px solid var(--border-color, #f0f0f0);
  border-top-color: #f093fb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.map-loading p {
  color: var(--text-secondary, #666);
  font-size: 14px;
}

/* 滚动条样式 */
.results-list::-webkit-scrollbar {
  width: 6px;
}

.results-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.results-list::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.results-list::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>

