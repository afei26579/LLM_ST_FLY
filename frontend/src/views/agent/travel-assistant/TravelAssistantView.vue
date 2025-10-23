<template>
  <div class="travel-assistant-view">
    <!-- 顶部工具栏 -->
    <div class="top-toolbar">
      <div class="toolbar-left">
        <h1>🧳 LangGraph 旅游助手</h1>
        <span v-if="currentCity" class="city-indicator">📍 {{ currentCity }}</span>
      </div>
      <div class="toolbar-right">
        <button @click="toggleLayout" class="layout-btn" title="切换布局">
          {{ isHorizontalLayout ? '⬌' : '⬍' }}
        </button>
      </div>
    </div>

    <!-- 确认对话框 -->
    <ConfirmDialog
      v-model:is-open="showConfirmDialog"
      title="清空对话"
      message="确定要清空所有对话记录吗？此操作不可撤销。"
      icon="🗑️"
      confirm-text="清空"
      cancel-text="取消"
      confirm-type="danger"
      @confirm="confirmClearChat"
      @cancel="showConfirmDialog = false"
    />

    <!-- 主内容区域 -->
    <div class="main-content" :class="{ 'horizontal-layout': isHorizontalLayout }">
      <!-- 聊天面板 -->
      <div class="panel chat-panel-wrapper">
        <ChatPanel
          ref="chatPanelRef"
          :messages="messages"
          :is-loading="isLoading"
          :user-preferences="userPreferences"
          @send-message="handleSendMessage"
          @send-suggestion="handleSendSuggestion"
          @update-preferences="handleUpdatePreferences"
          @toggle-preferences="handleTogglePreferences"
          @clear-chat="handleClearChat"
        />
      </div>

      <!-- 地图面板 -->
      <div class="panel map-panel-wrapper">
        <MapPanel
          ref="mapPanelRef"
          :map-container-id="mapContainerId"
          :current-city="currentCity"
          :is-map-ready="isMapReady"
          @map-ready="handleMapReady"
          @search-poi="handleSearchPOI"
          @poi-click="handlePOIClick"
          @add-to-itinerary="handleAddToItinerary"
          @clear-markers="handleClearMarkers"
        />
      </div>

      <!-- 行程面板 -->
      <div class="panel itinerary-panel-wrapper">
        <ItineraryPanel
          :itinerary-data="itineraryData"
          :user-preferences="userPreferences"
          @activity-click="handleActivityClick"
          @export-itinerary="exportItinerary"
          @optimize-itinerary="handleOptimizeItinerary"
          @add-more="handleAddMore"
          @regenerate="handleRegenerate"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import ChatPanel from './components/ChatPanel.vue'
import MapPanel from './components/MapPanel.vue'
import ItineraryPanel from './components/ItineraryPanel.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import { useTravelChat } from './hooks/useTravelChat'
import { useGDMap } from './hooks/useGDMap'

// Toast
const toast = useToast()

// 布局状态
const isHorizontalLayout = ref(true)
const mapContainerId = ref('travel-map')
const showConfirmDialog = ref(false)

// 组件引用
const chatPanelRef = ref<InstanceType<typeof ChatPanel> | null>(null)
const mapPanelRef = ref<InstanceType<typeof MapPanel> | null>(null)

// 使用 Hooks
const {
  messages,
  isLoading,
  currentCity,
  userPreferences,
  itineraryData,
  sendMessage,
  updatePreferences,
  setCurrentCity,
  clearMessages,
  exportItinerary
} = useTravelChat()

const {
  isMapReady,
  initMap,
  addMarker,
  addMarkers,
  clearMarkers,
  searchPOI,
  setCenter,
  setCity
} = useGDMap(mapContainerId)

// 方法
const toggleLayout = () => {
  isHorizontalLayout.value = !isHorizontalLayout.value
}

const handleMapReady = async () => {
  try {
    await initMap({
      city: currentCity.value || '北京',
      zoom: 12
    })
    toast.success('地图加载成功')
  } catch (error: any) {
    console.error('地图初始化失败:', error)
    toast.error('地图加载失败，请检查网络连接')
  }
}

const handleSendMessage = async (content: string, useStream: boolean) => {
  try {
    await sendMessage(content, useStream)
  } catch (error: any) {
    toast.error(`发送失败: ${error.message}`)
  }
}

const handleSendSuggestion = (suggestion: string) => {
  handleSendMessage(suggestion, false)
}

const handleUpdatePreferences = (prefs: any) => {
  updatePreferences(prefs)
  // 静默更新，不显示提示
}

const handleTogglePreferences = () => {
  chatPanelRef.value?.togglePreferences()
}

const handleClearChat = () => {
  showConfirmDialog.value = true
}

const confirmClearChat = () => {
  clearMessages()
  clearMarkers()
  toast.info('对话已清空')
}

const handleSearchPOI = async (keyword: string, city: string) => {
  try {
    toast.info(`正在搜索: ${keyword}`)
    
    const results = await searchPOI(keyword, city)
    
    if (results.length === 0) {
      toast.warning('未找到相关结果')
      return
    }

    // 显示搜索结果
    mapPanelRef.value?.setSearchResults(results)

    // 在地图上添加标记
    const markers = results.map(poi => ({
      id: poi.id,
      position: [poi.location.lng, poi.location.lat] as [number, number],
      title: poi.name,
      poi
    }))
    
    addMarkers(markers)
    toast.success(`找到 ${results.length} 个结果`)
  } catch (error: any) {
    console.error('POI搜索失败:', error)
    toast.error('搜索失败，请重试')
  }
}

const handlePOIClick = (poi: any) => {
  // 在地图上高亮显示
  if (poi.location) {
    setCenter([poi.location.lng, poi.location.lat], 15)
  }
  toast.info(`已选中: ${poi.name}`)
}

const handleAddToItinerary = (poi: any) => {
  // 通过发送消息来添加到行程
  const message = `请将"${poi.name}"添加到我的行程中`
  handleSendMessage(message, false)
}

const handleClearMarkers = () => {
  clearMarkers()
  mapPanelRef.value?.clearSearchResults()
  toast.info('已清除所有标记')
}

const handleActivityClick = (activity: any) => {
  // 如果活动有位置信息，在地图上定位
  if (activity.poi?.location) {
    setCenter([activity.poi.location.lng, activity.poi.location.lat], 15)
    toast.info(`正在定位: ${activity.title}`)
  } else if (activity.location) {
    // 如果只有地址，发送消息请求定位
    const message = `请在地图上标记"${activity.location}"`
    handleSendMessage(message, false)
  }
}

const handleOptimizeItinerary = () => {
  const message = '请帮我优化当前的行程安排，使路线更合理'
  handleSendMessage(message, false)
}

const handleAddMore = () => {
  const message = '请推荐更多值得去的地方'
  handleSendMessage(message, false)
}

const handleRegenerate = () => {
  const message = '请重新为我规划一个行程'
  handleSendMessage(message, false)
}

// 监听当前城市变化，更新地图
const watchCurrentCity = () => {
  if (currentCity.value && isMapReady.value) {
    setCity(currentCity.value)
  }
}

// 生命周期
onMounted(() => {
  // 监听城市变化
  watchCurrentCity()
})
</script>

<style scoped>
.travel-assistant-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--color-background);
  overflow: hidden;
}

.top-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--header-background);
  border-bottom: 1px solid var(--header-border);
  box-shadow: var(--card-shadow);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--header-text);
}

.city-indicator {
  padding: 6px 12px;
  background: var(--button-primary);
  color: var(--button-primaryText);
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(var(--color-primary-rgb, 94, 155, 255), 0.2);
}

.layout-btn {
  padding: 8px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  color: var(--color-text);
  transition: all 0.2s;
}

.layout-btn:hover {
  background: var(--button-secondary);
  color: var(--button-secondaryText);
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(var(--color-secondary-rgb, 156, 163, 175), 0.2);
}

.main-content {
  flex: 1;
  display: grid;
  gap: 16px;
  padding: 16px;
  overflow: hidden;
}

/* 水平布局（默认）*/
.main-content.horizontal-layout {
  grid-template-columns: 1fr 1.2fr 1fr;
  grid-template-rows: 1fr;
}

.main-content.horizontal-layout .chat-panel-wrapper {
  grid-column: 1;
  grid-row: 1;
}

.main-content.horizontal-layout .map-panel-wrapper {
  grid-column: 2;
  grid-row: 1;
}

.main-content.horizontal-layout .itinerary-panel-wrapper {
  grid-column: 3;
  grid-row: 1;
}

/* 垂直布局 */
.main-content:not(.horizontal-layout) {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
}

.main-content:not(.horizontal-layout) .chat-panel-wrapper {
  grid-column: 1;
  grid-row: 1 / 3;
}

.main-content:not(.horizontal-layout) .map-panel-wrapper {
  grid-column: 2;
  grid-row: 1;
}

.main-content:not(.horizontal-layout) .itinerary-panel-wrapper {
  grid-column: 2;
  grid-row: 2;
}

.panel {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .main-content.horizontal-layout {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: 1fr 1fr;
  }

  .main-content.horizontal-layout .chat-panel-wrapper {
    grid-column: 1;
    grid-row: 1 / 3;
  }

  .main-content.horizontal-layout .map-panel-wrapper {
    grid-column: 2;
    grid-row: 1;
  }

  .main-content.horizontal-layout .itinerary-panel-wrapper {
    grid-column: 2;
    grid-row: 2;
  }
}

@media (max-width: 768px) {
  .main-content,
  .main-content.horizontal-layout,
  .main-content:not(.horizontal-layout) {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    overflow-y: auto;
  }

  .main-content .chat-panel-wrapper,
  .main-content .map-panel-wrapper,
  .main-content .itinerary-panel-wrapper {
    grid-column: 1 !important;
    min-height: 400px;
  }

  .main-content .chat-panel-wrapper {
    grid-row: 1 !important;
  }

  .main-content .map-panel-wrapper {
    grid-row: 2 !important;
  }

  .main-content .itinerary-panel-wrapper {
    grid-row: 3 !important;
  }
}
</style>

