<template>
  <div class="welcome-card">
    <h2>{{ greeting }}，{{ userDisplayName }}，欢迎使用AI助手</h2>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getGreeting } from '@/utils/dateUtils'

// Props
interface Props {
  // 可以接收自定义问候消息
  customMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  customMessage: ''
})

// 状态管理
const authStore = useAuthStore()

// 计算属性
const userDisplayName = computed(() => {
  return authStore.userInfo?.nickname || authStore.userInfo?.username || '用户'
})

const greeting = computed(() => {
  return getGreeting()
})
</script>

<style scoped>
.welcome-card {
  background: transparent;
  color: var(--color-text, #1f2937);
  padding: 2rem;
  border-radius: 20px;
  text-align: center;
  position: relative;
  margin-bottom: 2rem;
}

.welcome-card h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 0.5px;
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .welcome-card {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  .welcome-card h2 {
    font-size: 1.25rem;
  }
}
</style>
