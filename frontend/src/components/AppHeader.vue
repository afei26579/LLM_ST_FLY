<template>
  <header class="app-header">
    <div class="logo">
      <RouterLink to="/">后台管理系统</RouterLink>
    </div>

    <nav class="main-nav">
      <RouterLink to="/" class="nav-item">首页</RouterLink>
      <RouterLink to="/about" class="nav-item">关于</RouterLink>
    </nav>

    <div class="user-menu" v-if="authStore.isAuthenticated">
      <div class="user-info" @click="toggleDropdown">
        <span>{{ authStore.userInfo?.username || '用户' }}</span>
        <span class="role-badge">{{ authStore.userRole }}</span>
        <span class="dropdown-arrow">▼</span>
      </div>
      
      <div class="dropdown-menu" v-show="showDropdown" ref="dropdown">
        <RouterLink to="/profile" class="dropdown-item">个人资料</RouterLink>
        <div class="dropdown-divider"></div>
        <a href="#" class="dropdown-item" @click.prevent="handleLogout">退出登录</a>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()
const showDropdown = ref(false)
const dropdown = ref<HTMLElement | null>(null)

// 切换下拉菜单
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

// 处理退出登录
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

// 点击其他区域关闭下拉菜单
const closeDropdown = (event: MouseEvent) => {
  if (dropdown.value && !dropdown.value.contains(event.target as Node) && showDropdown.value) {
    showDropdown.value = false
  }
}

// 监听点击事件
onMounted(() => {
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  padding: 0 1.5rem;
  height: 60px;
  background-color: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: relative;
}

.logo {
  font-size: 1.25rem;
  font-weight: 600;
  margin-right: 2rem;
}

.logo a {
  color: #333;
  text-decoration: none;
}

.main-nav {
  flex: 1;
  display: flex;
}

.nav-item {
  margin-right: 1.5rem;
  color: #666;
  text-decoration: none;
  padding: 0.5rem 0;
}

.nav-item:hover,
.nav-item.router-link-active {
  color: #4caf50;
  border-bottom: 2px solid #4caf50;
}

.user-menu {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.role-badge {
  font-size: 0.75rem;
  padding: 0.15rem 0.35rem;
  background-color: #e8f5e9;
  color: #388e3c;
  border-radius: 10px;
  margin: 0 0.5rem;
}

.dropdown-arrow {
  font-size: 0.75rem;
  color: #666;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 160px;
  background-color: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 100;
  margin-top: 0.5rem;
}

.dropdown-item {
  display: block;
  padding: 0.75rem 1rem;
  color: #333;
  text-decoration: none;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.dropdown-divider {
  height: 1px;
  background-color: #eee;
  margin: 0.25rem 0;
}
</style> 