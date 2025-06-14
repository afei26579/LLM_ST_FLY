<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import AppHeader from './components/AppHeader.vue'

const authStore = useAuthStore()

// 在组件挂载时尝试恢复用户会话
onMounted(async () => {
  // 检查是否有保存的token
  if (authStore.token) {
    // 获取用户信息
    await authStore.fetchUserInfo()
  }
})
</script>

<template>
  <!-- 使用我们的自定义头部组件 -->
  <AppHeader v-if="authStore.isAuthenticated" />

  <!-- 路由视图 -->
  <div class="main-container" :class="{ 'with-header': authStore.isAuthenticated }">
    <RouterView />
  </div>
</template>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333;
  background-color: #f5f5f5;
  line-height: 1.5;
}

.main-container {
  height: 100vh;
}

.main-container.with-header {
  height: calc(100vh - 60px);
  padding-top: 60px;
}
</style>
