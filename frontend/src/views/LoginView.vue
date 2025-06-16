<template>
  <div class="login-container">
    <div class="login-bg">
      <!-- 背景动画效果 -->
      <canvas class="particles" id="particles"></canvas>
      <div class="light-beam"></div>
      <div class="grid-overlay"></div>
    </div>

    <div class="login-content">
      <div class="logo-container">
        <div class="logo">
          <span class="logo-text">AI</span>
          <span class="logo-dot"></span>
        </div>
        <h1 class="system-name">智能管理系统</h1>
      </div>
      
      <div class="card-container">
        <div class="login-card">
          <h2 class="card-title">系统登录</h2>
          
          <div v-if="loginError" class="error-message">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>{{ loginError }}</span>
          </div>
          
          <form @submit.prevent="handleLogin" class="login-form">
            <div class="form-group">
              <label for="username">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <span>用户名</span>
              </label>
              <div class="input-container" :class="{ 'has-error': formErrors.username }">
                <input
                  type="text"
                  id="username"
                  v-model="loginForm.username"
                  placeholder="请输入用户名"
                  @blur="validateForm"
                />
                <span class="input-focus-effect"></span>
                <div v-if="formErrors.username" class="field-error">{{ formErrors.username }}</div>
              </div>
            </div>
            
            <div class="form-group">
              <label for="password">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
                <span>密码</span>
              </label>
              <div class="input-container" :class="{ 'has-error': formErrors.password }">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  id="password"
                  v-model="loginForm.password"
                  placeholder="请输入密码"
                  @blur="validateForm"
                />
                <span class="input-focus-effect"></span>
                <button 
                  type="button" 
                  class="password-toggle" 
                  @click="togglePasswordVisibility"
                >
                  <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                  </svg>
                </button>
                <div v-if="formErrors.password" class="field-error">{{ formErrors.password }}</div>
              </div>
            </div>

            <div class="form-footer">
              <div class="remember-me">
                <input type="checkbox" id="remember" v-model="rememberMe" />
                <label for="remember">记住我</label>
              </div>
              <a href="#" class="forgot-password">忘记密码?</a>
            </div>
            
            <button type="submit" class="login-button" :disabled="authStore.loading">
              <span>{{ authStore.loading ? '登录中...' : '登录' }}</span>
              <svg class="login-arrow" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
              <div class="login-button-effect"></div>
            </button>
          </form>
        </div>
        
        <div class="system-info">
          <div class="info-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"></polyline>
              <path d="M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path>
            </svg>
            <span>智能化管理</span>
          </div>
          <div class="info-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
            <span>安全可靠</span>
          </div>
          <div class="info-item">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
              <line x1="9" y1="9" x2="9.01" y2="9"></line>
              <line x1="15" y1="9" x2="15.01" y2="9"></line>
            </svg>
            <span>用户友好</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 登录表单数据
const loginForm = reactive({
  username: localStorage.getItem('remembered_username') || '',
  password: ''
})

// 表单验证错误信息
const formErrors = reactive({
  username: '',
  password: ''
})

// 如果有记住的用户名，则默认选中"记住我"
const hasRememberedUsername = !!localStorage.getItem('remembered_username')

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const loginError = ref('')
const showPassword = ref(false)
const rememberMe = ref(hasRememberedUsername)

// 验证表单
const validateForm = (): boolean => {
  let isValid = true
  
  // 重置错误信息
  formErrors.username = ''
  formErrors.password = ''
  
  // 验证用户名
  if (!loginForm.username.trim()) {
    formErrors.username = '请输入用户名'
    isValid = false
  }
  
  // 验证密码
  if (!loginForm.password) {
    formErrors.password = '请输入密码'
    isValid = false
  }
  
  return isValid
}

// 处理登录请求
const handleLogin = async () => {
  loginError.value = '' // 清除之前的错误信息
  
  // 表单验证
  if (!validateForm()) {
    return
  }
  
  try {
    // 调用auth store的登录方法
    const result = await authStore.login(loginForm.username, loginForm.password)
    
    if (result.success) {
      // 获取用户信息
      const userResult = await authStore.fetchUserInfo()
      
      if (!userResult.success) {
        console.warn('获取用户信息失败:', userResult.message)
        // 获取用户信息失败不阻止登录流程，继续执行
      }
      
      // 记住用户名和密码，如果选择了"记住我"
      if (rememberMe.value) {
        localStorage.setItem('remembered_username', loginForm.username)
        // 注意：为了安全起见，不应该存储密码，但这里作为演示
        // 在生产环境中应当使用更安全的方式或者不存储密码
      } else {
        localStorage.removeItem('remembered_username')
      }
      
      // 登录成功后根据query参数重定向
      const redirectPath = route.query.redirect as string || '/'
      router.push(redirectPath)
    } else {
      // 显示从服务器返回的错误信息
      const errorMsg = result.message || '登录失败，请检查用户名和密码'
      loginError.value = errorMsg
    }
  } catch (error) {
    console.error('登录过程发生错误:', error)
    const errorMsg = '登录异常，请稍后再试'
    loginError.value = errorMsg
  }
}

// 切换密码可见性
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

// 初始化粒子动画
onMounted(() => {
  initParticles()
})

// 粒子动画
const initParticles = () => {
  const canvas = document.getElementById('particles') as HTMLCanvasElement
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight

  // 创建粒子
  const particlesArray: Particle[] = []
  const numberOfParticles = 100
  
  class Particle {
    x: number
    y: number
    size: number
    speedX: number
    speedY: number
    
    constructor() {
      this.x = Math.random() * canvas.width
      this.y = Math.random() * canvas.height
      this.size = Math.random() * 3
      this.speedX = Math.random() * 3 - 1.5
      this.speedY = Math.random() * 3 - 1.5
    }
    
    update() {
      this.x += this.speedX
      this.y += this.speedY
      
      if (this.x > canvas.width) this.x = 0
      else if (this.x < 0) this.x = canvas.width
      
      if (this.y > canvas.height) this.y = 0
      else if (this.y < 0) this.y = canvas.height
    }
    
    draw() {
      if (!ctx) return
      ctx.fillStyle = 'rgba(255, 255, 255, 0.7)'
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
      ctx.closePath()
      ctx.fill()
    }
  }
  
  // 初始化粒子
  function init() {
    for (let i = 0; i < numberOfParticles; i++) {
      particlesArray.push(new Particle())
    }
  }
  
  // 动画循环
  function animate() {
    if (!ctx) return
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    for (let i = 0; i < particlesArray.length; i++) {
      particlesArray[i].update()
      particlesArray[i].draw()
    }
    
    // 连接临近粒子
    connect()
    
    requestAnimationFrame(animate)
  }
  
  // 连接粒子
  function connect() {
    if (!ctx) return
    for (let a = 0; a < particlesArray.length; a++) {
      for (let b = a; b < particlesArray.length; b++) {
        const dx = particlesArray[a].x - particlesArray[b].x
        const dy = particlesArray[a].y - particlesArray[b].y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < 100) {
          ctx.strokeStyle = `rgba(135, 206, 250, ${0.8 - distance/100})`
          ctx.lineWidth = 0.5
          ctx.beginPath()
          ctx.moveTo(particlesArray[a].x, particlesArray[a].y)
          ctx.lineTo(particlesArray[b].x, particlesArray[b].y)
          ctx.stroke()
        }
      }
    }
  }
  
  // 窗口大小变化重新初始化
  window.addEventListener('resize', () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  })
  
  init()
  animate()
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  width: 100%;
  position: relative;
  background-color: #070b14;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.particles {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.light-beam {
  position: absolute;
  top: -50%;
  left: 20%;
  width: 60%;
  height: 200%;
  background: linear-gradient(135deg, rgba(32, 85, 255, 0.07) 0%, rgba(94, 155, 255, 0.03) 100%);
  transform: rotate(35deg);
  filter: blur(20px);
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: linear-gradient(rgba(11, 19, 38, 0.8) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(11, 19, 38, 0.8) 1px, transparent 1px);
  background-size: 40px 40px;
  background-position: center center;
}

.login-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 1200px;
  z-index: 5;
  position: relative;
}

.logo-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
  color: white;
}

.logo {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.logo-text {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  text-shadow: 0 0 10px rgba(94, 155, 255, 0.8);
  letter-spacing: 1px;
}

.logo-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #5e9bff 0%, #a569ff 100%);
  margin-left: 4px;
  box-shadow: 0 0 10px rgba(165, 105, 255, 0.8);
}

.system-name {
  font-size: 1.5rem;
  font-weight: 300;
  color: #e1e6f5;
  letter-spacing: 2px;
  margin: 0;
}

.card-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 400px;
}

.login-card {
  background: rgba(20, 29, 53, 0.7);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), 
              0 0 0 1px rgba(255, 255, 255, 0.1),
              inset 0 1px rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(10px);
  padding: 2rem;
  animation: card-appear 0.6s ease-out;
  position: relative;
  overflow: hidden;
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.05) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transform: skewX(-25deg);
  animation: card-shine 6s infinite;
}

@keyframes card-shine {
  0% {
    left: -100%;
  }
  20%, 100% {
    left: 200%;
  }
}

@keyframes card-appear {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-title {
  color: white;
  text-align: center;
  margin-top: 0;
  margin-bottom: 2rem;
  font-weight: 400;
  font-size: 1.5rem;
  letter-spacing: 1px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1.5rem;
  position: relative;
}

label {
  color: #a0aec0;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}

label svg {
  margin-right: 0.5rem;
}

.input-container {
  position: relative;
}

input {
  width: 100%;
  padding: 0.75rem;
  background-color: rgba(30, 41, 70, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  font-size: 1rem;
  color: white;
  transition: all 0.2s;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}

input:focus {
  outline: none;
  border-color: #5e9bff;
  box-shadow: 0 0 0 2px rgba(94, 155, 255, 0.3);
}

.input-container.has-error input {
  border-color: #f87171;
  box-shadow: 0 0 0 2px rgba(248, 113, 113, 0.3);
}

.field-error {
  position: absolute;
  left: 0;
  bottom: -20px;
  font-size: 0.75rem;
  color: #f87171;
  margin-top: 0.25rem;
}

.input-focus-effect {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #5e9bff, #a569ff);
  transform: translateX(-50%);
  transition: width 0.3s ease;
}

input:focus ~ .input-focus-effect {
  width: 100%;
}

.password-toggle {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.password-toggle:hover {
  color: white;
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.remember-me {
  display: flex;
  align-items: center;
}

.remember-me input {
  width: auto;
  margin-right: 0.5rem;
}

.remember-me label {
  margin-bottom: 0;
  font-size: 0.875rem;
}

.forgot-password {
  color: #5e9bff;
  font-size: 0.875rem;
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
}

.login-button {
  background: linear-gradient(90deg, #5e9bff, #a569ff);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0.9rem;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.login-button span {
  z-index: 1;
  transition: all 0.3s;
  margin-right: 0.5rem;
}

.login-arrow {
  transform: translateX(-5px);
  opacity: 0;
  transition: all 0.3s;
  z-index: 1;
}

.login-button:hover .login-arrow {
  transform: translateX(0);
  opacity: 1;
}

.login-button-effect {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0));
  transform: skewX(-20deg) translateX(-100%);
  transition: all 0.6s;
}

.login-button:hover .login-button-effect {
  transform: skewX(-20deg) translateX(100%);
}

.login-button:hover {
  box-shadow: 0 0 20px rgba(94, 155, 255, 0.5);
  transform: translateY(-2px);
}

.login-button:disabled {
  background: linear-gradient(90deg, #445175, #646fa9);
  cursor: not-allowed;
  box-shadow: none;
  transform: translateY(0);
}

.system-info {
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
  color: #a0aec0;
  width: 100%;
}

.info-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.error-message {
  padding: 0.75rem;
  margin-bottom: 1rem;
  background-color: rgba(220, 38, 38, 0.1);
  color: #f87171;
  border-radius: 6px;
  display: flex;
  align-items: center;
  animation: shake 0.5s linear;
  border: 1px solid rgba(220, 38, 38, 0.2);
}

.error-message svg {
  margin-right: 0.5rem;
  min-width: 16px;
  flex-shrink: 0;
}

.error-message span {
  flex: 1;
}

@keyframes shake {
  0% { transform: translateX(0); }
  20% { transform: translateX(-10px); }
  40% { transform: translateX(10px); }
  60% { transform: translateX(-5px); }
  80% { transform: translateX(5px); }
  100% { transform: translateX(0); }
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
    width: 90%;
    margin: 0 auto;
  }
  
  .system-info {
    flex-direction: column;
    gap: 1rem;
    align-items: center;
  }
}
</style> 