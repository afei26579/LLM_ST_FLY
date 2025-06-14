import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

// 用户信息接口
interface UserInfo {
  id: number
  username: string
  email?: string
  role: string
  permissions?: string[]
}

// 定义认证状态管理 store
export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(null)
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => userInfo.value?.role || '')
  const hasPermission = (permission: string) => {
    return userInfo.value?.permissions?.includes(permission) || false
  }

  // 动作
  // 登录
  const login = async (username: string, password: string) => {
    loading.value = true
    try {
      // 这里以后会替换为实际的API调用
      // 模拟API调用返回结果
      const mockResponse = {
        token: 'mock_token_' + Date.now(),
        user: {
          id: 1,
          username,
          role: 'user',
          permissions: ['read']
        }
      }

      // 保存令牌到本地存储和状态中
      const newToken = mockResponse.token
      localStorage.setItem('token', newToken)
      token.value = newToken

      // 保存用户信息
      userInfo.value = mockResponse.user as UserInfo

      return true
    } catch (error) {
      console.error('登录失败:', error)
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = () => {
    // 清除令牌
    localStorage.removeItem('token')
    token.value = null
    
    // 清除用户信息
    userInfo.value = null
  }

  // 获取用户信息
  const fetchUserInfo = async () => {
    if (!token.value) return null
    
    loading.value = true
    try {
      // 这里以后会替换为实际的API调用
      // 模拟API调用返回用户信息
      const mockUserInfo: UserInfo = {
        id: 1,
        username: 'demo_user',
        email: 'demo@example.com',
        role: 'user',
        permissions: ['read', 'write']
      }
      
      userInfo.value = mockUserInfo
      return mockUserInfo
    } catch (error) {
      console.error('获取用户信息失败:', error)
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    token,
    userInfo,
    loading,
    
    // 计算属性
    isAuthenticated,
    userRole,
    
    // 方法
    login,
    logout,
    fetchUserInfo,
    hasPermission
  }
}) 