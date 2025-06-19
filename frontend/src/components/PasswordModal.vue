<template>
  <div v-if="isOpen" class="modal-overlay">
    <div class="modal-container">
      <div class="modal-header">
        <h2>{{ mode === 'change' ? '修改密码' : '重置密码' }}</h2>
        <button class="close-btn" @click="close">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="modal-content">
        <!-- 密码修改模式 -->
        <form v-if="mode === 'change'" @submit.prevent="submitPasswordChange">
          <div class="form-group">
            <label for="old-password">当前密码</label>
            <div class="password-input">
              <input
                :type="showOldPassword ? 'text' : 'password'"
                id="old-password"
                v-model="oldPassword"
                placeholder="请输入当前密码"
                required
              />
              <button type="button" class="toggle-password" @click="showOldPassword = !showOldPassword">
                <svg v-if="!showOldPassword" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <div class="error-message" v-if="errors.oldPassword">{{ errors.oldPassword }}</div>
          </div>

          <div class="form-group">
            <label for="new-password">新密码</label>
            <div class="password-input">
              <input
                :type="showNewPassword ? 'text' : 'password'"
                id="new-password"
                v-model="newPassword"
                placeholder="请输入新密码"
                required
              />
              <button type="button" class="toggle-password" @click="showNewPassword = !showNewPassword">
                <svg v-if="!showNewPassword" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <div class="error-message" v-if="errors.newPassword">{{ errors.newPassword }}</div>
          </div>

          <div class="form-group">
            <label for="confirm-password">确认新密码</label>
            <div class="password-input">
              <input
                :type="showConfirmPassword ? 'text' : 'password'"
                id="confirm-password"
                v-model="confirmPassword"
                placeholder="请再次输入新密码"
                required
              />
              <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword">
                <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <div class="error-message" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</div>
          </div>

          <div class="forgot-password">
            <a href="#" @click.prevent="switchToForgotPassword">忘记密码？</a>
          </div>

          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="close">取消</button>
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              <span v-if="!isSubmitting">确认修改</span>
              <span v-else>修改中...</span>
            </button>
          </div>
        </form>

        <!-- 忘记密码模式 -->
        <form v-else @submit.prevent="submitPasswordReset">
          <div class="reset-method-tabs">
            <div 
              class="tab" 
              :class="{ active: resetMethod === 'phone' }" 
              @click="resetMethod = 'phone'"
            >
              手机号重置
            </div>
            <div 
              class="tab" 
              :class="{ active: resetMethod === 'email' }" 
              @click="resetMethod = 'email'"
            >
              邮箱重置
            </div>
          </div>

          <!-- 手机号重置 -->
          <div v-if="resetMethod === 'phone'">
            <div class="form-group">
              <label for="phone">手机号</label>
              <input
                type="tel"
                id="phone"
                v-model="phone"
                placeholder="请输入手机号"
                required
              />
              <div class="error-message" v-if="errors.phone">{{ errors.phone }}</div>
            </div>
            
            <div class="form-group verification-code">
              <label for="phone-code">验证码</label>
              <div class="code-input-group">
                <input
                  type="text"
                  id="phone-code"
                  v-model="phoneCode"
                  placeholder="请输入验证码"
                  required
                />
                <button 
                  type="button" 
                  class="send-code-btn" 
                  :disabled="countdown > 0" 
                  @click="sendPhoneCode"
                >
                  {{ countdown > 0 ? `${countdown}秒后重发` : '获取验证码' }}
                </button>
              </div>
              <div class="error-message" v-if="errors.phoneCode">{{ errors.phoneCode }}</div>
            </div>
          </div>

          <!-- 邮箱重置 -->
          <div v-else>
            <div class="form-group">
              <label for="email">邮箱地址</label>
              <input
                type="email"
                id="email"
                v-model="email"
                placeholder="请输入邮箱地址"
                required
              />
              <div class="error-message" v-if="errors.email">{{ errors.email }}</div>
            </div>
            
            <div class="form-group verification-code">
              <label for="email-code">验证码</label>
              <div class="code-input-group">
                <input
                  type="text"
                  id="email-code"
                  v-model="emailCode"
                  placeholder="请输入验证码"
                  required
                />
                <button 
                  type="button" 
                  class="send-code-btn" 
                  :disabled="countdown > 0" 
                  @click="sendEmailCode"
                >
                  {{ countdown > 0 ? `${countdown}秒后重发` : '获取验证码' }}
                </button>
              </div>
              <div class="error-message" v-if="errors.emailCode">{{ errors.emailCode }}</div>
            </div>
          </div>

          <!-- 新密码设置（重置模式） -->
          <div class="form-group">
            <label for="reset-new-password">新密码</label>
            <div class="password-input">
              <input
                :type="showNewPassword ? 'text' : 'password'"
                id="reset-new-password"
                v-model="newPassword"
                placeholder="请输入新密码"
                required
              />
              <button type="button" class="toggle-password" @click="showNewPassword = !showNewPassword">
                <svg v-if="!showNewPassword" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <div class="error-message" v-if="errors.newPassword">{{ errors.newPassword }}</div>
          </div>

          <div class="form-group">
            <label for="reset-confirm-password">确认新密码</label>
            <div class="password-input">
              <input
                :type="showConfirmPassword ? 'text' : 'password'"
                id="reset-confirm-password"
                v-model="confirmPassword"
                placeholder="请再次输入新密码"
                required
              />
              <button type="button" class="toggle-password" @click="showConfirmPassword = !showConfirmPassword">
                <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <div class="error-message" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</div>
          </div>

          <div class="back-to-login">
            <a href="#" @click.prevent="switchToPasswordChange">返回修改密码</a>
          </div>

          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="close">取消</button>
            <button type="submit" class="submit-btn" :disabled="isSubmitting">
              <span v-if="!isSubmitting">重置密码</span>
              <span v-else>重置中...</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, defineProps, defineEmits } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'password-changed'])
const authStore = useAuthStore()

// 模式状态（密码修改/密码重置）
const mode = ref('change') // 'change' 或 'reset'

// 表单数据
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const phone = ref('')
const email = ref('')
const phoneCode = ref('')
const emailCode = ref('')
const resetMethod = ref('phone') // 'phone' 或 'email'

// 显示/隐藏密码
const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// 验证码倒计时
const countdown = ref(0)
const countdownTimer = ref<number | null>(null)

// 表单状态
const isSubmitting = ref(false)
const errors = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: '',
  phone: '',
  email: '',
  phoneCode: '',
  emailCode: ''
})

// 切换到忘记密码模式
const switchToForgotPassword = () => {
  mode.value = 'reset'
  resetForm()
}

// 切换回密码修改模式
const switchToPasswordChange = () => {
  mode.value = 'change'
  resetForm()
}

// 关闭弹窗
const close = () => {
  resetForm()
  emit('close')
}

// 重置表单
const resetForm = () => {
  oldPassword.value = ''
  newPassword.value = ''
  confirmPassword.value = ''
  phone.value = ''
  email.value = ''
  phoneCode.value = ''
  emailCode.value = ''
  showOldPassword.value = false
  showNewPassword.value = false
  showConfirmPassword.value = false
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = ''
  })
  stopCountdown()
}

// 验证表单
const validateForm = () => {
  let isValid = true
  errors.oldPassword = ''
  errors.newPassword = ''
  errors.confirmPassword = ''

  // 验证密码修改模式下的字段
  if (mode.value === 'change') {
    if (!oldPassword.value.trim()) {
      errors.oldPassword = '请输入当前密码'
      isValid = false
    }
  }

  // 验证重置密码模式下的字段
  if (mode.value === 'reset') {
    if (resetMethod.value === 'phone') {
      if (!phone.value.trim()) {
        errors.phone = '请输入手机号'
        isValid = false
      } else if (!/^1[3-9]\d{9}$/.test(phone.value)) {
        errors.phone = '请输入有效的手机号'
        isValid = false
      }

      if (!phoneCode.value.trim()) {
        errors.phoneCode = '请输入验证码'
        isValid = false
      }
    } else {
      if (!email.value.trim()) {
        errors.email = '请输入邮箱'
        isValid = false
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
        errors.email = '请输入有效的邮箱地址'
        isValid = false
      }

      if (!emailCode.value.trim()) {
        errors.emailCode = '请输入验证码'
        isValid = false
      }
    }
  }

  // 验证新密码
  if (!newPassword.value.trim()) {
    errors.newPassword = '请输入新密码'
    isValid = false
  } else if (newPassword.value.length < 8) {
    errors.newPassword = '密码长度至少为8位'
    isValid = false
  }

  // 验证确认密码
  if (!confirmPassword.value.trim()) {
    errors.confirmPassword = '请确认新密码'
    isValid = false
  } else if (confirmPassword.value !== newPassword.value) {
    errors.confirmPassword = '两次输入的密码不一致'
    isValid = false
  }

  return isValid
}

// 发送手机验证码
const sendPhoneCode = async () => {
  // 验证手机号
  if (!phone.value.trim()) {
    errors.phone = '请输入手机号'
    return
  } else if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    errors.phone = '请输入有效的手机号'
    return
  }

  try {
    // 发送验证码请求
    await axios.post('/api/users/send-sms-code', {
      phone: phone.value
    })
    
    // 开始倒计时
    startCountdown()
  } catch (error: any) {
    if (error.response?.data?.message) {
      errors.phone = error.response.data.message
    } else {
      errors.phone = '发送验证码失败，请稍后重试'
    }
  }
}

// 发送邮箱验证码
const sendEmailCode = async () => {
  // 验证邮箱
  if (!email.value.trim()) {
    errors.email = '请输入邮箱'
    return
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    errors.email = '请输入有效的邮箱地址'
    return
  }

  try {
    // 发送验证码请求
    await axios.post('/api/users/send-email-code', {
      email: email.value
    })
    
    // 开始倒计时
    startCountdown()
  } catch (error: any) {
    if (error.response?.data?.message) {
      errors.email = error.response.data.message
    } else {
      errors.email = '发送验证码失败，请稍后重试'
    }
  }
}

// 开始倒计时
const startCountdown = () => {
  countdown.value = 60
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
  }
  
  countdownTimer.value = window.setInterval(() => {
    if (countdown.value > 0) {
      countdown.value--
    } else {
      stopCountdown()
    }
  }, 1000)
}

// 停止倒计时
const stopCountdown = () => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
    countdownTimer.value = null
  }
  countdown.value = 0
}

// 提交密码修改
const submitPasswordChange = async () => {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true
  try {
    const response = await axios.post('/api/users/change-password', {
      oldPassword: oldPassword.value,
      newPassword: newPassword.value
    })

    // 密码修改成功
    emit('password-changed')
    close()
  } catch (error: any) {
    // 处理错误
    if (error.response?.data?.message) {
      if (error.response.data.field === 'oldPassword') {
        errors.oldPassword = error.response.data.message
      } else {
        errors.newPassword = error.response.data.message
      }
    } else {
      errors.oldPassword = '密码修改失败，请稍后重试'
    }
  } finally {
    isSubmitting.value = false
  }
}

// 提交密码重置
const submitPasswordReset = async () => {
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true
  try {
    let requestData = {}
    
    if (resetMethod.value === 'phone') {
      requestData = {
        phone: phone.value,
        code: phoneCode.value,
        newPassword: newPassword.value
      }
    } else {
      requestData = {
        email: email.value,
        code: emailCode.value,
        newPassword: newPassword.value
      }
    }

    const response = await axios.post(
      `/api/users/reset-password-${resetMethod.value}`, 
      requestData
    )

    // 密码重置成功
    emit('password-changed')
    close()
  } catch (error: any) {
    // 处理错误
    if (error.response?.data?.message) {
      const field = error.response.data.field
      if (field === 'phone') errors.phone = error.response.data.message
      else if (field === 'phoneCode') errors.phoneCode = error.response.data.message
      else if (field === 'email') errors.email = error.response.data.message
      else if (field === 'emailCode') errors.emailCode = error.response.data.message
      else errors.newPassword = error.response.data.message
    } else {
      errors.newPassword = '密码重置失败，请稍后重试'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  width: 450px;
  max-width: 90%;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1a202c;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  padding: 4px;
  border-radius: 4px;
  color: #64748b;
  transition: background-color 0.2s, color 0.2s;
}

.close-btn:hover {
  background-color: #f1f5f9;
  color: #334155;
}

.modal-content {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #334155;
  font-size: 14px;
}

input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 14px;
  color: #1e293b;
  background-color: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.password-input {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  cursor: pointer;
  color: #64748b;
  display: flex;
  padding: 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-btn,
.submit-btn {
  padding: 10px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.cancel-btn {
  background-color: #f1f5f9;
  color: #334155;
  border: 1px solid #e2e8f0;
}

.cancel-btn:hover {
  background-color: #e2e8f0;
}

.submit-btn {
  background-color: #3b82f6;
  color: #fff;
  border: none;
}

.submit-btn:hover {
  background-color: #2563eb;
}

.submit-btn:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

.error-message {
  color: #ef4444;
  font-size: 12px;
  margin-top: 4px;
}

.forgot-password,
.back-to-login {
  margin-top: 12px;
  text-align: right;
  font-size: 14px;
}

.forgot-password a,
.back-to-login a {
  color: #3b82f6;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password a:hover,
.back-to-login a:hover {
  color: #2563eb;
  text-decoration: underline;
}

.reset-method-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 12px;
  cursor: pointer;
  color: #64748b;
  font-weight: 500;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.tab:hover {
  color: #334155;
}

.tab.active {
  color: #3b82f6;
  border-bottom: 2px solid #3b82f6;
}

.verification-code .code-input-group {
  display: flex;
  gap: 8px;
}

.send-code-btn {
  white-space: nowrap;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 0 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-code-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.send-code-btn:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}
</style>