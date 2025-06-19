<template>
  <div class="sidebar" :class="{ 'collapsed': isCollapsed }">
    <div class="sidebar-header">
      <div class="logo">
        <span v-if="!isCollapsed">AI管理系统</span>
        <span v-else>AI</span>
      </div>
      <button class="toggle-btn" @click="toggleSidebar">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path v-if="isCollapsed" d="M13 17l5-5-5-5M6 17l5-5-5-5"></path>
          <path v-else d="M11 17l-5-5 5-5M18 17l-5-5 5-5"></path>
        </svg>
      </button>
    </div>

    <div class="sidebar-content">
      <div class="nav-section">
        <nav class="main-nav">
          <router-link to="/" class="nav-item" title="主页">
            <div class="nav-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
            </div>
            <span class="nav-text">主页</span>
          </router-link>

          <!-- 系统管理菜单项 -->
          <div class="nav-item-group">
            <div class="nav-item has-submenu" @click="toggleSystemMenu">
              <div class="nav-header">
                <div class="nav-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="3"></circle>
                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
                  </svg>
                </div>
                <span class="nav-text">系统管理</span>
                <div class="submenu-icon" :class="{ 'rotated': isSystemMenuOpen }">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </div>
              </div>
            </div>

            <!-- 二级菜单 -->
            <div class="submenu" v-show="!isCollapsed && isSystemMenuOpen">
              <router-link to="/roles" class="submenu-item">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                  </svg>
                </div>
                <span>角色管理</span>
              </router-link>

              <router-link to="/permissions" class="submenu-item">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                </div>
                <span>权限管理</span>
              </router-link>
            </div>
          </div>
        </nav>
      </div>
    </div>

    <div class="sidebar-footer">
      <div v-if="!isCollapsed" class="user-menu">
        <div class="user-info" @click="toggleUserDropdown">
          <div class="avatar" v-if="authStore.userInfo?.avatar">
            <img :src="authStore.userInfo.avatar" alt="用户头像" />
          </div>
          <div class="avatar" v-else>
            {{ getInitial }}
          </div>
          <div class="user-details">
            <div class="username">{{ displayName }}</div>
            
          </div>
          <div class="dropdown-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
        </div>
        
        <div class="user-dropdown" v-show="isUserDropdownOpen">
          <div class="dropdown-item" @click="showSettings">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            <span>个人设置</span>
          </div>
          <div class="dropdown-item" @click="showPasswordModal">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <span>修改密码</span>
          </div>
          <div class="dropdown-divider"></div>
          <div class="dropdown-item logout" @click="handleLogout">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
              <polyline points="16 17 21 12 16 7"></polyline>
              <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
            <span>退出登录</span>
          </div>
        </div>
      </div>
      
      <div class="avatar mini-avatar" v-else @click="toggleSidebar" title="展开菜单">
        <img v-if="authStore.userInfo?.avatar" :src="authStore.userInfo.avatar" alt="用户头像" />
        <template v-else>{{ getInitial }}</template>
      </div>
    </div>
  </div>
  
  <!-- 使用单独的个人设置组件 -->
  <UserSettingsModal 
    :is-open="isSettingsModalOpen" 
    @close="closeSettingsModal"
    @save="handleSettingsSaved"
  />
  
  <!-- 使用密码修改组件 -->
  <PasswordModal
    :is-open="isPasswordModalOpen"
    @close="closePasswordModal"
    @password-changed="handlePasswordChanged"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import UserSettingsModal from './UserSettingsModal.vue'
import PasswordModal from './PasswordModal.vue'

const router = useRouter()
const authStore = useAuthStore()

const isCollapsed = ref(false)
const isSystemMenuOpen = ref(true)
const isUserDropdownOpen = ref(false)
const isSettingsModalOpen = ref(false)
const isPasswordModalOpen = ref(false)

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleSystemMenu = () => {
  if (!isCollapsed.value) {
    isSystemMenuOpen.value = !isSystemMenuOpen.value
  } else {
    // 如果侧边栏折叠，点击展开侧边栏
    isCollapsed.value = false
    isSystemMenuOpen.value = true
  }
}

// 用户下拉菜单控制
const toggleUserDropdown = () => {
  isUserDropdownOpen.value = !isUserDropdownOpen.value
}

// 个人设置页面
const showSettings = () => {
  isSettingsModalOpen.value = true
  isUserDropdownOpen.value = false
}

// 关闭设置弹框
const closeSettingsModal = () => {
  isSettingsModalOpen.value = false
}

// 处理设置保存成功
const handleSettingsSaved = () => {
  // 可以在这里添加一些通知或其他操作
  console.log('用户设置已保存')
}

// 显示密码修改弹框
const showPasswordModal = () => {
  isPasswordModalOpen.value = true
  isUserDropdownOpen.value = false
}

// 关闭密码修改弹框
const closePasswordModal = () => {
  isPasswordModalOpen.value = false
}

// 处理密码修改成功
const handlePasswordChanged = () => {
  // 可以在这里添加一些通知或其他操作
  console.log('密码修改成功')
}

// 处理退出登录
const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

// 计算属性：显示名称（优先显示昵称，如果没有则显示用户名）
const displayName = computed(() => {
  return authStore.userInfo?.nickname || authStore.userInfo?.username || '用户'
})

// 计算属性：获取名称首字母
const getInitial = computed(() => {
  const name = authStore.userInfo?.nickname || authStore.userInfo?.username
  return name ? name[0].toUpperCase() : 'U'
})
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: 250px;
  height: 100vh;
  background: linear-gradient(180deg, #1a2233 0%, #0c1425 100%);
  color: #e1e6f5;
  transition: width 0.3s ease;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 100;
  overflow-x: hidden;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  height: 60px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  font-size: 1.25rem;
  font-weight: 600;
  background: linear-gradient(90deg, #5e9bff 0%, #a569ff 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  white-space: nowrap;
}

.toggle-btn {
  background: transparent;
  border: none;
  color: #e1e6f5;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.toggle-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.nav-section {
  margin-bottom: 1.5rem;
}

.main-nav {
  display: flex;
  flex-direction: column;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: #e1e6f5;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px;
  margin: 0 0.5rem 0.25rem;
  white-space: nowrap;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.nav-item.router-link-active {
  background-color: rgba(94, 155, 255, 0.15);
  color: #5e9bff;
}

.nav-icon {
  margin-right: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
}

.nav-text {
  flex: 1;
}

.submenu-icon {
  transition: transform 0.2s;
}

.submenu-icon.rotated {
  transform: rotate(180deg);
}

.nav-header {
  display: flex;
  align-items: center;
  width: 100%;
}

.nav-item-group {
  display: flex;
  flex-direction: column;
}

.submenu {
  display: flex;
  flex-direction: column;
  margin-left: 0;
  padding-left: 3.5rem;
  background-color: rgba(0, 0, 0, 0.15);
}

.submenu-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: #e1e6f5;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px;
  margin-bottom: 0.25rem;
}

.submenu-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.submenu-item.router-link-active {
  background-color: rgba(94, 155, 255, 0.15);
  color: #5e9bff;
}

.submenu-icon {
  margin-right: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
}

/* 折叠时隐藏文本 */
.sidebar.collapsed .nav-text,
.sidebar.collapsed .submenu,
.sidebar.collapsed .submenu-icon {
  display: none;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
}

.sidebar.collapsed .nav-icon {
  margin-right: 0;
}

/* 底部用户信息 */
.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: auto;
  position: relative;
}

.user-menu {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px;
  padding: 0.5rem;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.dropdown-icon {
  margin-left: auto;
  opacity: 0.7;
  transition: transform 0.2s;
}

.user-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  width: 100%;
  background: #1e293b;
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  margin-bottom: 0.5rem;
  overflow: hidden;
  z-index: 100;
  animation: dropdown-appear 0.2s ease-out;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

@keyframes dropdown-appear {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: #e1e6f5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item svg {
  margin-right: 0.75rem;
  opacity: 0.7;
}

.dropdown-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.dropdown-divider {
  height: 1px;
  background-color: rgba(255, 255, 255, 0.1);
  margin: 0.25rem 0;
}

.logout {
  color: #f87171;
}

.logout svg {
  stroke: #f87171;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #5e9bff 0%, #a569ff 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-right: 0.75rem;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mini-avatar {
  margin: 0 auto;
  cursor: pointer;
}

.user-details {
  overflow: hidden;
}

.username {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.role {
  font-size: 0.75rem;
  opacity: 0.7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style> 