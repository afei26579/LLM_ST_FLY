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
          <!-- AI助手菜单项 -->
          <div class="nav-item-group">
            <div class="nav-item has-submenu" @click="toggleAIMenu">
              <div class="nav-header">
                <div class="nav-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    <polyline points="9 22 9 12 15 12 15 22"></polyline>
                  </svg>
                </div>
                <span class="nav-text">AI助手</span>
                <div class="submenu-icon" :class="{ 'rotated': isAIMenuOpen }">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </div>
              </div>
            </div>

            <!-- AI助手二级菜单 -->
            <div class="submenu" v-show="!isCollapsed && isAIMenuOpen">
              <router-link to="/ai-text" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                </div>
                <span>AI 文本</span>
              </router-link>
              
              <router-link to="/ai-reading" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
                    <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
                  </svg>
                </div>
                <span>AI 阅读</span>
              </router-link>

              <router-link to="/ai-image" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                    <circle cx="8.5" cy="8.5" r="1.5"></circle>
                    <polyline points="21 15 16 10 5 21"></polyline>
                  </svg>
                </div>
                <span>AI 图片</span>
              </router-link>

              <router-link to="/ai-audio" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                  </svg>
                </div>
                <span>AI 声音</span>
              </router-link>

              <router-link to="/ai-video" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="23 7 16 12 23 17 23 7"></polygon>
                    <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
                  </svg>
                </div>
                <span>AI 视频</span>
              </router-link>
            </div>
          </div>

          <!-- 智能体菜单项 -->
          <div class="nav-item-group">
            <div class="nav-item has-submenu" @click="toggleAgentMenu">
              <div class="nav-header">
                <div class="nav-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 13c0 5-3.5 7.5-7.5 7.5-1.79 0-3.43-.73-4.61-1.91a5.73 5.73 0 0 1-1.64-4.04 5.73 5.73 0 0 1 1.64-4.04C8.57 9.73 10.21 9 12 9c4 0 7.5 2.5 7.5 7.5z"></path>
                    <path d="M12 5c2.5 0 4.5-2 4.5-4.5S14.5-2 12-2s-4.5 2-4.5 4.5S9.5 5 12 5z"></path>
                    <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
                  </svg>
                </div>
                <span class="nav-text">智能体</span>
                <div class="submenu-icon" :class="{ 'rotated': isAgentMenuOpen }">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="6 9 12 15 18 9"></polyline>
                  </svg>
                </div>
              </div>
            </div>

            <!-- 智能体二级菜单 -->
            <div class="submenu" v-show="!isCollapsed && isAgentMenuOpen">
              <router-link to="/agent/travel-assistant" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                    <circle cx="12" cy="10" r="3"></circle>
                  </svg>
                </div>
                <span>旅游助手</span>
              </router-link>
              
              <router-link to="/agent/poetry-painting" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                </div>
                <span>诗词绘画</span>
              </router-link>

              <router-link to="/agent/customer-service" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 16.5v2.8A2.7 2.7 0 0 0 5.7 22h2.8a2.7 2.7 0 0 0 2.7-2.7V16.5"></path>
                    <path d="M15 16.5v2.8a2.7 2.7 0 0 0 2.7 2.7h2.8a2.7 2.7 0 0 0 2.7-2.7V16.5"></path>
                    <path d="M9 7.5V5.3A2.7 2.7 0 0 1 11.7 2.6h.6A2.7 2.7 0 0 1 15 5.3v2.2"></path>
                    <path d="M3 11.5v2a2 2 0 0 0 2 2h1v-6H5a2 2 0 0 0-2 2z"></path>
                    <path d="M18 11.5v2a2 2 0 0 1-2 2h-1v-6h1a2 2 0 0 1 2 2z"></path>
                  </svg>
                </div>
                <span>客服助手</span>
              </router-link>
            </div>
          </div>

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
              <router-link to="/users" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </div>
                <span>用户管理</span>
              </router-link>
              
              <router-link to="/roles" class="submenu-item" @click="handleSubMenuClick">
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

              <router-link to="/permissions" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                  </svg>
                </div>
                <span>权限管理</span>
              </router-link>

              <router-link to="/logs" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                  </svg>
                </div>
                <span>日志管理</span>
              </router-link>

              <router-link to="/theme-showcase" class="submenu-item" @click="handleSubMenuClick">
                <div class="submenu-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="13.5" cy="6.5" r=".5"></circle>
                    <circle cx="17.5" cy="10.5" r=".5"></circle>
                    <circle cx="8.5" cy="7.5" r=".5"></circle>
                    <circle cx="6.5" cy="12.5" r=".5"></circle>
                    <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"></path>
                  </svg>
                </div>
                <span>主题展示</span>
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
          <div class="dropdown-item" @click="showSecuritySettings">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
              <circle cx="12" cy="16" r="1"></circle>
            </svg>
            <span>安全设置</span>
          </div>
          <div class="dropdown-item" @click="showThemeSettings">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="5"></circle>
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"></path>
            </svg>
            <span>主题设置</span>
          </div>
          <!--div class="dropdown-item" @click="showPasswordModal">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            <span>修改密码</span>
          </div-->
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
  
  <!-- 安全设置弹窗 -->
  <SecuritySettingsModal
    :is-open="isSecurityModalOpen"
    @close="closeSecurityModal"
    @binding-updated="handleBindingUpdated"
  />
  
  <!-- 主题设置弹窗 -->
  <ThemeSettingsModal
    :is-open="isThemeModalOpen"
    @close="closeThemeModal"
    @applied="handleThemeApplied"
  />
  
  <!-- 使用密码修改组件 -->
  <PasswordModal
    :is-open="isPasswordModalOpen"
    @close="closePasswordModal"
    @password-changed="handlePasswordChanged"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useThemeStore } from '../stores/theme'
import { useRouter } from 'vue-router'
import UserSettingsModal from './UserSettingsModal.vue'
import PasswordModal from './PasswordModal.vue'
import SecuritySettingsModal from './SecuritySettingsModal.vue'
import ThemeSettingsModal from './ThemeSettingsModal.vue'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isCollapsed = ref(false)
const isSystemMenuOpen = ref(true)
const isAIMenuOpen = ref(true)
const isAgentMenuOpen = ref(true)
const isUserDropdownOpen = ref(false)
const isSettingsModalOpen = ref(false)
const isPasswordModalOpen = ref(false)
const isSecurityModalOpen = ref(false)
const isThemeModalOpen = ref(false)

// 初始化主题
onMounted(() => {
  themeStore.loadTheme()
})

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

const toggleAIMenu = () => {
  if (!isCollapsed.value) {
    isAIMenuOpen.value = !isAIMenuOpen.value
  } else {
    // 如果侧边栏折叠，点击展开侧边栏
    isCollapsed.value = false
    isAIMenuOpen.value = true
  }
}

const toggleAgentMenu = () => {
  if (!isCollapsed.value) {
    isAgentMenuOpen.value = !isAgentMenuOpen.value
  } else {
    // 如果侧边栏折叠，点击展开侧边栏
    isCollapsed.value = false
    isAgentMenuOpen.value = true
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

// 显示安全设置弹框
const showSecuritySettings = () => {
  isSecurityModalOpen.value = true
  isUserDropdownOpen.value = false
}

// 关闭安全设置弹框
const closeSecurityModal = () => {
  isSecurityModalOpen.value = false
}

// 处理绑定信息更新
const handleBindingUpdated = (type: string) => {
  // 可以在这里添加通知或其他处理
  console.log(`${type}绑定更新成功`)
}

// 显示主题设置弹框
const showThemeSettings = () => {
  isThemeModalOpen.value = true
  isUserDropdownOpen.value = false
}

// 关闭主题设置弹框
const closeThemeModal = () => {
  isThemeModalOpen.value = false
}

// 处理主题应用成功
const handleThemeApplied = (theme: string) => {
  console.log(`主题已切换为: ${theme}`)
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

// 处理子菜单点击
const handleSubMenuClick = () => {
  // 可以在这里添加子菜单点击的处理逻辑
  console.log('子菜单点击')
}
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: 250px;
  height: 100vh;
  background: var(--sidebar-background);
  color: var(--sidebar-text);
  transition: width 0.3s ease;
  box-shadow: var(--card-shadow);
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
  border-bottom: 1px solid var(--sidebar-border);
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
  color: var(--sidebar-text);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.toggle-btn:hover {
  background-color: var(--sidebar-hoverBackground);
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
  color: var(--sidebar-text);
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px;
  margin: 0 0.5rem 0.25rem;
  white-space: nowrap;
}

.nav-item:hover {
  background-color: var(--sidebar-hoverBackground);
}

.nav-item.router-link-active {
  background: var(--sidebar-activeBackground);
  color: var(--sidebar-activeText);
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
  background-color: var(--sidebar-hoverBackground);
}

.submenu-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  color: var(--sidebar-text);
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.2s;
  border-radius: 8px;
  margin-bottom: 0.25rem;
}

.submenu-item:hover {
  background-color: var(--sidebar-hoverBackground);
}

.submenu-item.router-link-active {
  background: var(--sidebar-activeBackground);
  color: var(--sidebar-activeText);
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
  border-top: 1px solid var(--sidebar-border);
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
  background-color: var(--sidebar-hoverBackground);
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
  background: var(--card-background);
  border-radius: 8px;
  box-shadow: var(--card-shadow);
  margin-bottom: 0.5rem;
  overflow: hidden;
  z-index: 100;
  animation: dropdown-appear 0.2s ease-out;
  border: 1px solid var(--card-border);
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
  color: var(--color-text);
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item svg {
  margin-right: 0.75rem;
  opacity: 0.7;
}

.dropdown-item:hover {
  background-color: var(--sidebar-hoverBackground);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--color-border);
  margin: 0.25rem 0;
}

.logout {
  color: var(--color-error);
}

.logout svg {
  stroke: var(--color-error);
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