<template>
  <div class="login-container">
    <div class="login-box">
      <h2>系统登录</h2>
      <div v-if="loginError" class="error-message">
        {{ loginError }}
      </div>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            type="text"
            id="username"
            v-model="loginForm.username"
            placeholder="请输入用户名"
            required
          />
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input
            type="password"
            id="password"
            v-model="loginForm.password"
            placeholder="请输入密码"
            required
          />
        </div>
        <div class="form-group">
          <button type="submit" class="login-button" :disabled="authStore.loading">
            {{ authStore.loading ? '登录中...' : '登录' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 登录表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loginError = ref('')

// 处理登录请求
const handleLogin = async () => {
  loginError.value = '' // 清除之前的错误信息
  
  try {
    // 调用auth store的登录方法
    const success = await authStore.login(loginForm.username, loginForm.password)
    
    if (success) {
      // 获取用户信息
      await authStore.fetchUserInfo()
      
      // 登录成功后根据query参数重定向
      const redirectPath = route.query.redirect as string || '/'
      router.push(redirectPath)
    } else {
      loginError.value = '登录失败，请检查用户名和密码'
    }
  } catch (error) {
    console.error('登录过程发生错误:', error)
    loginError.value = '登录异常，请稍后再试'
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f5f5;
}

.login-box {
  width: 350px;
  padding: 2rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.login-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.login-button:hover {
  background-color: #388e3c;
}

.login-button:disabled {
  background-color: #9e9e9e;
  cursor: not-allowed;
}

.error-message {
  padding: 0.5rem;
  margin-bottom: 1rem;
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: 4px;
  text-align: center;
}
</style> 