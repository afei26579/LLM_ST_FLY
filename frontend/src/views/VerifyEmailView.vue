<template>
  <div class="verify-email-container">
    <div class="verify-card">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>正在验证邮箱，请稍候...</p>
      </div>
      
      <div v-else-if="verified" class="success-state">
        <div class="icon-success">✓</div>
        <h2>验证成功</h2>
        <p>{{ message }}</p>
        <button class="primary-button" @click="goToHome">返回首页</button>
      </div>
      
      <div v-else class="error-state">
        <div class="icon-error">✗</div>
        <h2>验证失败</h2>
        <p>{{ message }}</p>
        <button class="primary-button" @click="goToHome">返回首页</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiService } from '@/services/api'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const verified = ref(false)
const message = ref('')

onMounted(async () => {
  try {
    // 从URL参数中获取token和email
    const token = route.query.token as string
    const email = route.query.email as string
    const type = route.query.type as string
    
    if (!token || !email) {
      loading.value = false
      verified.value = false
      message.value = '无效的验证链接，缺少必要参数'
      return
    }
    
    // 根据类型调用不同的API
    if (type === 'bind') {
      // 调用验证邮箱绑定的API
      const response = await apiService.verifyEmailBind(token, email)
      
      if (response.code === 200) {
        verified.value = true
        message.value = '邮箱绑定成功！'
        // 更新本地存储的用户信息
        const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
        userInfo.email = email
        localStorage.setItem('userInfo', JSON.stringify(userInfo))
      } else {
        verified.value = false
        message.value = response.message || '验证失败，链接可能已过期或无效'
      }
    } else {
      verified.value = false
      message.value = '未知的验证类型'
    }
  } catch (error) {
    console.error('验证过程发生错误:', error)
    verified.value = false
    message.value = '验证过程发生错误，请稍后重试'
  } finally {
    loading.value = false
  }
})

const goToHome = () => {
  router.push('/')
}
</script>

<style scoped>
.verify-email-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.verify-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 500px;
  text-align: center;
}

.loading-state, .success-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #409eff;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.icon-success, .icon-error {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin-bottom: 20px;
}

.icon-success {
  background-color: #67c23a;
  color: white;
}

.icon-error {
  background-color: #f56c6c;
  color: white;
}

h2 {
  margin-bottom: 16px;
  font-weight: 500;
}

p {
  margin-bottom: 24px;
  color: #606266;
}

.primary-button {
  display: inline-block;
  line-height: 1;
  white-space: nowrap;
  cursor: pointer;
  background: #409eff;
  border: 1px solid #409eff;
  color: #fff;
  text-align: center;
  box-sizing: border-box;
  outline: none;
  margin: 0;
  transition: .1s;
  font-weight: 500;
  padding: 12px 20px;
  font-size: 14px;
  border-radius: 4px;
}

.primary-button:hover {
  background: #66b1ff;
  border-color: #66b1ff;
  color: #fff;
}
</style> 