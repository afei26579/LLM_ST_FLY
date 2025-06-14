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
      <div class="user-info" v-if="!isCollapsed">
        <div class="avatar">{{ authStore.userInfo?.username?.[0]?.toUpperCase() || 'U' }}</div>
        <div class="user-details">
          <div class="username">{{ authStore.userInfo?.username || '用户' }}</div>
          <div class="role">{{ authStore.userRole }}</div>
        </div>
      </div>
      <div class="avatar mini-avatar" v-else @click="toggleSidebar" title="展开菜单">
        {{ authStore.userInfo?.username?.[0]?.toUpperCase() || 'U' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const isCollapsed = ref(false)
const isSystemMenuOpen = ref(true)

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
}

.user-info {
  display: flex;
  align-items: center;
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