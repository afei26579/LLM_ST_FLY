<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import SideNav from './components/SideNav.vue'

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
  <!-- 使用侧边栏导航 -->
  <SideNav v-if="authStore.isAuthenticated" />

  <!-- 路由视图 -->
  <div class="main-container" :class="{ 'with-sidebar': authStore.isAuthenticated }">
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
  background-color: #f7f9fc;
  line-height: 1.5;
  overflow-x: hidden;
}

.main-container {
  height: 100vh;
  width: 100%;
  position: relative;
}

.main-container.with-sidebar {
  padding-left: 250px;
  transition: padding-left 0.3s ease;
}

@media (max-width: 768px) {
  .main-container.with-sidebar {
    padding-left: 70px;
  }
}
</style>
