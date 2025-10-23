<template>
  <div class="itinerary-panel">
    <!-- 头部 -->
    <div class="itinerary-header">
      <h3>📅 行程规划</h3>
      <div class="header-actions">
        <button 
          v-if="hasItinerary" 
          @click="emit('export-itinerary')" 
          class="btn-icon" 
          title="导出行程"
        >
          📥
        </button>
      </div>
    </div>

    <!-- 行程概览 -->
    <div v-if="itineraryData?.destination" class="itinerary-overview">
      <div class="overview-item">
        <span class="label">目的地</span>
        <span class="value">{{ itineraryData.destination }}</span>
      </div>
      <div class="overview-item" v-if="userPreferences?.budget">
        <span class="label">预算</span>
        <span class="value">{{ userPreferences.budget }}</span>
      </div>
      <div class="overview-item" v-if="userPreferences?.duration">
        <span class="label">时长</span>
        <span class="value">{{ userPreferences.duration }}</span>
      </div>
      <div class="overview-item" v-if="userPreferences?.travelStyle">
        <span class="label">风格</span>
        <span class="value">{{ userPreferences.travelStyle }}</span>
      </div>
    </div>

    <!-- 行程列表 -->
    <div class="itinerary-content">
      <div v-if="!hasItinerary" class="empty-state">
        <div class="empty-icon">📋</div>
        <p>暂无行程安排</p>
        <p class="hint">开始与助手对话，制定您的旅行计划</p>
      </div>

      <div v-else class="itinerary-list">
        <!-- 按天分组 -->
        <div
          v-for="(dayActivities, day) in groupedActivities"
          :key="day"
          class="day-section"
        >
          <div class="day-header">
            <h4>第 {{ day }} 天</h4>
            <span class="activity-count">{{ dayActivities.length }} 项活动</span>
          </div>

          <div class="activities-timeline">
            <div
              v-for="(activity, index) in dayActivities"
              :key="index"
              class="activity-item"
              @click="handleActivityClick(activity)"
            >
              <div class="activity-time">{{ activity.time }}</div>
              <div class="activity-content">
                <h5>{{ activity.title }}</h5>
                <p>{{ activity.description }}</p>
                <div v-if="activity.location" class="activity-location">
                  📍 {{ activity.location }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 快速操作 -->
        <div class="quick-actions">
          <button @click="emit('optimize-itinerary')" class="action-btn">
            ✨ 优化行程
          </button>
          <button @click="emit('add-more')" class="action-btn">
            ➕ 增加活动
          </button>
          <button @click="emit('regenerate')" class="action-btn secondary">
            🔄 重新生成
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props
interface Activity {
  day: number
  time: string
  title: string
  description: string
  location?: string
  poi?: any
}

interface ItineraryData {
  destination?: string
  days?: number
  activities?: Activity[]
}

interface UserPreferences {
  budget?: string
  duration?: string
  travelStyle?: string
  transportation?: string
}

interface Props {
  itineraryData?: ItineraryData
  userPreferences?: UserPreferences
}

const props = withDefaults(defineProps<Props>(), {
  itineraryData: () => ({}),
  userPreferences: () => ({})
})

// Emits
const emit = defineEmits<{
  'activity-click': [activity: Activity]
  'export-itinerary': []
  'optimize-itinerary': []
  'add-more': []
  'regenerate': []
}>()

// 计算属性
const hasItinerary = computed(() => {
  return props.itineraryData?.activities && props.itineraryData.activities.length > 0
})

const groupedActivities = computed(() => {
  if (!props.itineraryData?.activities) return {}

  return props.itineraryData.activities.reduce((acc, activity) => {
    const day = activity.day || 1
    if (!acc[day]) {
      acc[day] = []
    }
    acc[day].push(activity)
    return acc
  }, {} as Record<number, Activity[]>)
})

// 方法
const handleActivityClick = (activity: Activity) => {
  emit('activity-click', activity)
}
</script>

<style scoped>
.itinerary-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--card-background);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--card-shadow);
  border: 1px solid var(--card-border);
}

.itinerary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--button-info);
  color: var(--button-infoText);
}

.itinerary-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 16px;
  transition: background 0.2s;
  color: white;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.3);
}

.itinerary-overview {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 16px 20px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.overview-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.overview-item .label {
  font-size: 11px;
  color: var(--text-tertiary, #999);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.overview-item .value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.itinerary-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 8px 0;
  color: var(--text-secondary, #666);
}

.empty-state .hint {
  font-size: 13px;
  color: var(--text-tertiary, #999);
}

.itinerary-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.day-section {
  background: var(--color-surface);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--color-border);
}

.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--border-color, #e0e0e0);
}

.day-header h4 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary, #333);
}

.activity-count {
  font-size: 12px;
  color: var(--text-tertiary, #999);
  background: white;
  padding: 4px 12px;
  border-radius: 12px;
}

.activities-timeline {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
}

.activities-timeline::before {
  content: '';
  position: absolute;
  left: 60px;
  top: 12px;
  bottom: 12px;
  width: 2px;
  background: linear-gradient(to bottom, #4facfe, #00f2fe);
  opacity: 0.3;
}

.activity-item {
  display: flex;
  gap: 16px;
  background: white;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.activity-item:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.activity-item::before {
  content: '';
  position: absolute;
  left: 48px;
  top: 20px;
  width: 8px;
  height: 8px;
  background: #4facfe;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #4facfe;
  z-index: 1;
}

.activity-time {
  min-width: 50px;
  font-size: 13px;
  font-weight: 600;
  color: #4facfe;
}

.activity-content {
  flex: 1;
}

.activity-content h5 {
  margin: 0 0 6px 0;
  font-size: 14px;
  color: var(--text-primary, #333);
}

.activity-content p {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary, #666);
  line-height: 1.5;
}

.activity-location {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

.quick-actions {
  display: flex;
  gap: 8px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.action-btn {
  flex: 1;
  min-width: 120px;
  padding: 10px 16px;
  background: var(--button-info);
  color: var(--button-infoText);
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: var(--button-infoHover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(var(--color-info-rgb, 0, 170, 255), 0.3);
}

.action-btn.secondary {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.action-btn.secondary:hover {
  background: var(--color-background);
  border-color: var(--color-primary);
}

/* 滚动条样式 */
.itinerary-content::-webkit-scrollbar {
  width: 6px;
}

.itinerary-content::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.itinerary-content::-webkit-scrollbar-thumb {
  background: #4facfe;
  border-radius: 3px;
}

.itinerary-content::-webkit-scrollbar-thumb:hover {
  background: #00f2fe;
}
</style>

