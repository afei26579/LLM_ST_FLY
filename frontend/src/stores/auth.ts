import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '../services/api'

// 用户信息接口
interface UserInfo {
  id: number
  username: string
  email?: string
  role: string
  permissions?: string[]
  real_name?: string
  nickname?: string
  phone?: string
  department?: string
  bio?: string
  avatar?: string
  theme?: string
  gender?: string
  birthday?: string
  country?: string
  province?: string
  city?: string
  district?: string
  address?: string
  last_login_ip?: string
  qq?: string
}

// 从localStorage获取用户信息
const getUserInfoFromStorage = (): UserInfo | null => {
  const userInfoStr = localStorage.getItem('userInfo')
  if (userInfoStr) {
    try {
      return JSON.parse(userInfoStr)
    } catch (e) {
      console.error('解析用户信息失败:', e)
      return null
    }
  }
  return null
}

// 保存用户信息到localStorage
const saveUserInfoToStorage = (info: UserInfo) => {
  localStorage.setItem('userInfo', JSON.stringify(info))
}

// 定义认证状态管理 store
export const useAuthStore = defineStore('auth', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem('token'))
  const userInfo = ref<UserInfo | null>(getUserInfoFromStorage())
  const loading = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => userInfo.value?.role || '')
  const hasPermission = (permission: string) => {
    return userInfo.value?.permissions?.includes(permission) || false
  }

  // 动作
  // 登录
  const login = async (username: string, password: string): Promise<{ success: boolean, message?: string }> => {
    loading.value = true
    try {
      // 调用API服务进行登录
      const response = await apiService.login({ username, password })
      
      // 如果返回的状态码不是成功的状态码(200-299)
      if (response.code < 200 || response.code >= 300) {
        return { 
          success: false, 
          message: response.message || '登录失败，请检查用户名和密码' 
        }
      }
      
      // 登录成功，获取返回的数据
      const data = response.data
      if (!data || !data.token) {
        return { 
          success: false, 
          message: '服务器返回数据格式错误' 
        }
      }

      // 保存令牌到本地存储和状态中
      const accessToken = data.token.access
      
      // 如果有刷新令牌，也保存它
      if (data.token.refresh) {
        localStorage.setItem('refresh_token', data.token.refresh)
      }
      
      localStorage.setItem('token', accessToken)
      token.value = accessToken

      // 保存用户信息
      userInfo.value = data.user
      // 保存用户信息到localStorage
      saveUserInfoToStorage(data.user)

      return { success: true }
    } catch (error) {
      console.error('登录过程发生错误:', error)
      return { 
        success: false, 
        message: '登录过程发生错误，请稍后再试' 
      }
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
    localStorage.removeItem('userInfo')
    userInfo.value = null
  }

  // 获取用户信息
  const fetchUserInfo = async (): Promise<{ success: boolean, message?: string }> => {
    if (!token.value) {
      return { success: false, message: '未登录，请先登录' }
    }
    
    loading.value = true
    try {
      // 调用API服务获取用户信息
      const response = await apiService.getUserInfo()
     
      // 检查响应状态
      if (response.code < 200 || response.code >= 300) {
        return { 
          success: false, 
          message: response.message || '获取用户信息失败' 
        }
      }
      
      // 获取成功，保存用户信息
      const userData = response.data
      if (!userData) {
        return { 
          success: false, 
          message: '服务器返回数据格式错误' 
        }
      }
      
      userInfo.value = userData
      // 保存用户信息到localStorage
      saveUserInfoToStorage(userData)
      return { success: true }
    } catch (error) {
      console.error('获取用户信息过程发生错误:', error)
      return { 
        success: false, 
        message: '获取用户信息失败，请稍后再试' 
      }
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
    hasPermission,
    
    // 更新用户信息
    updateUserInfo: (updatedInfo: Partial<UserInfo>) => {
      if (userInfo.value) {
        userInfo.value = { ...userInfo.value, ...updatedInfo }
        // 更新localStorage中的用户信息
        saveUserInfoToStorage(userInfo.value)
      }
    }
  }
}) 