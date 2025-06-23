<template>
  <div v-if="isOpen" :class="{ 'modal-overlay': !embedded, 'embedded-modal': embedded }">
    <div :class="{ 'modal-container': !embedded }">
      <div class="modal-header" v-if="!embedded">
        <h2>{{ mode === 'change' ? '修改密码' : '重置密码' }}</h2>
        <button class="close-btn" @click="close">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div :class="{ 'modal-content': !embedded }">
        <!-- 密码修改模式 -->
        <form v-if="mode === 'change'" @submit.prevent="submitPasswordChange">
          
          <div class="form-group">
            <label for="old-password">当前密码</label>
            <span class="error-message" v-if="errors.oldPassword">{{ errors.oldPassword }}</span>
            <div class="password-input">
                              <input
                  :type="showOldPassword ? 'text' : 'password'"
                  id="old-password"
                  v-model="oldPassword"
                  @input="validateOldPassword"
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
          </div>

          <div class="form-group">
            <label for="new-password">新密码</label>
            <span class="error-message" v-if="errors.newPassword">{{ errors.newPassword }}</span>
            <div class="password-input">
                              <input
                  :type="showNewPassword ? 'text' : 'password'"
                  id="new-password"
                  v-model="newPassword"
                  @input="validateNewPassword"
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
          </div>

          <div class="form-group">
            <label for="confirm-password">确认新密码</label>
            <span class="error-message" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</span>
            <div class="password-input">
                              <input
                  :type="showConfirmPassword ? 'text' : 'password'"
                  id="confirm-password"
                  v-model="confirmPassword"
                  @input="validateConfirmPassword"
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
          </div>

          <div class="forgot-password">
            <a href="#" @click.prevent="switchToForgotPassword">忘记密码？</a>
          </div>

          <div class="form-actions">
           
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
              <span class="error-message" v-if="errors.phone">{{ errors.phone }}</span>
                              <input
                  type="tel"
                  id="phone"
                  v-model="phone"
                  @input="validatePhone"
                  placeholder="请输入手机号"
                  required
                />
            </div>
            
            <div class="form-group verification-code">
              <label for="phone-code">验证码</label>
              <span class="error-message" v-if="errors.phoneCode">{{ errors.phoneCode }}</span>
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
            </div>
          </div>

          <!-- 邮箱重置 -->
          <div v-else>
            <div class="form-group">
              <label for="email">邮箱地址</label>
              <span class="error-message" v-if="errors.email">{{ errors.email }}</span>
                              <input
                  type="email"
                  id="email"
                  v-model="email"
                  @input="validateEmail"
                  placeholder="请输入邮箱地址"
                  required
                />
            </div>
            
            <div class="form-group verification-code">
              <label for="email-code">验证码</label>
              <span class="error-message" v-if="errors.emailCode">{{ errors.emailCode }}</span>
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
            </div>
          </div>

          <!-- 新密码设置（重置模式） -->
          <div class="form-group">
            <label for="reset-new-password">新密码</label>
            <span class="error-message" v-if="errors.newPassword">{{ errors.newPassword }}</span>
            <div class="password-input">
                              <input
                :type="showNewPassword ? 'text' : 'password'"
                id="reset-new-password"
                v-model="newPassword"
                @input="validateNewPassword"
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
          </div>

          <div class="form-group">
            <label for="reset-confirm-password">确认新密码</label>
            <span class="error-message" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</span>
            <div class="password-input">
                              <input
                :type="showConfirmPassword ? 'text' : 'password'"
                id="reset-confirm-password"
                v-model="confirmPassword"
                @input="validateConfirmPassword"
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
    
    <!-- 操作结果提示框 -->
    <div v-if="showToast" class="toast" :class="[
      { 'toast-success': toastType === 'success', 'toast-error': toastType === 'error' },
      { 'embedded-toast': embedded }
    ]">
      <div class="toast-content">
        <svg v-if="toastType === 'success'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>{{ toastMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, defineProps, defineEmits } from 'vue'
import { useAuthStore } from '../stores/auth'
import { apiService } from '../services/api'
import { useRouter } from 'vue-router'
import type { ChangePasswordRequest, ResetPasswordPhoneRequest, ResetPasswordEmailRequest } from '../services/api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  embedded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'password-changed'])
const authStore = useAuthStore()
const router = useRouter()

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

// 提示框状态
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref<'success' | 'error'>('success')
const toastTimer = ref<number | null>(null)

// 显示提示框
const showToastMessage = (message: string, type: 'success' | 'error' = 'success') => {
  // 清除之前的定时器
  if (toastTimer.value) {
    clearTimeout(toastTimer.value)
    toastTimer.value = null
  }
  
  // 设置提示信息
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  
  // 根据类型设置显示时间
  const duration = type === 'success' ? 1000 : 3000
  
  // 设置自动关闭
  toastTimer.value = window.setTimeout(() => {
    showToast.value = false
    toastTimer.value = null
  }, duration)
}

// 实时验证密码
const validateNewPassword = () => {
  if (!newPassword.value.trim()) {
    errors.newPassword = '请输入新密码'
    return false
  } else if (newPassword.value.length < 6) {
    errors.newPassword = '密码长度至少为6位'
    return false
  }
  errors.newPassword = ''
  return true
}

// 实时验证确认密码
const validateConfirmPassword = () => {
  if (!confirmPassword.value.trim()) {
    errors.confirmPassword = '请确认新密码'
    return false
  } else if (confirmPassword.value !== newPassword.value) {
    errors.confirmPassword = '两次输入的密码不一致'
    return false
  }
  errors.confirmPassword = ''
  return true
}

// 实时验证旧密码
const validateOldPassword = () => {
  if (!oldPassword.value.trim()) {
    errors.oldPassword = '请输入当前密码'
    return false
  }
  errors.oldPassword = ''
  return true
}

// 实时验证手机号
const validatePhone = () => {
  if (!phone.value.trim()) {
    errors.phone = '请输入手机号'
    return false
  } else if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    errors.phone = '请输入有效的手机号'
    return false
  }
  errors.phone = ''
  return true
}

// 实时验证邮箱
const validateEmail = () => {
  if (!email.value.trim()) {
    errors.email = '请输入邮箱'
    return false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    errors.email = '请输入有效的邮箱地址'
    return false
  }
  errors.email = ''
  return true
}

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
  
  // 验证密码修改模式下的字段
  if (mode.value === 'change') {
    if (!validateOldPassword()) isValid = false
  }

  // 验证重置密码模式下的字段
  if (mode.value === 'reset') {
    if (resetMethod.value === 'phone') {
      if (!validatePhone()) isValid = false

      if (!phoneCode.value.trim()) {
        errors.phoneCode = '请输入验证码'
        isValid = false
      }
    } else {
      if (!validateEmail()) isValid = false

      if (!emailCode.value.trim()) {
        errors.emailCode = '请输入验证码'
        isValid = false
      }
    }
  }

  // 验证新密码和确认密码
  if (!validateNewPassword()) isValid = false
  if (!validateConfirmPassword()) isValid = false

  return isValid
}

// 发送手机验证码
const sendPhoneCode = async () => {
  // 验证手机号
  if (!validatePhone()) {
    return
  }

  try {
    // 发送验证码请求
    const response = await apiService.sendSmsCode(phone.value)
    
    // 检查响应状态
    if (response.code === 200) {
      // 开始倒计时
      startCountdown()
    } else {
      errors.phone = response.message || '发送验证码失败，请稍后重试'
    }
  } catch (error: any) {
    console.error('发送手机验证码失败:', error)
    errors.phone = '发送验证码失败，请稍后重试'
  }
}

// 发送邮箱验证码
const sendEmailCode = async () => {
  // 验证邮箱
  if (!validateEmail()) {
    return
  }

  try {
    // 发送验证码请求
    const response = await apiService.sendEmailCode(email.value)
    
    // 检查响应状态
    if (response.code === 200) {
      // 开始倒计时
      startCountdown()
    } else {
      errors.email = response.message || '发送验证码失败，请稍后重试'
    }
  } catch (error: any) {
    console.error('发送邮箱验证码失败:', error)
    errors.email = '发送验证码失败，请稍后重试'
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
    const requestData: ChangePasswordRequest = {
      oldPassword: oldPassword.value,
      newPassword: newPassword.value
    }
    
    const response = await apiService.changePassword(requestData)

    // 检查响应状态
    if (response.code === 200) {
      // 密码修改成功
      showToastMessage('密码修改成功，即将跳转到登录页面', 'success')
      // 注销用户
      setTimeout(() => {
        authStore.logout()
        router.push('/login')
      }, 1000)
    } else {
      // 处理错误
      console.log(response)
      console.log(response.data?.data?.field)
      if (response.data?.data?.field === 'oldPassword') {
        errors.oldPassword = response.data.data.message || '当前密码不正确'
        showToastMessage(response.data.data.message || '当前密码不正确', 'error')
      } else {
        errors.newPassword = response.data.data.message || '密码修改失败'
        showToastMessage(response.data.data.message || '密码修改失败', 'error')
      }
    }
  } catch (error: any) {
    console.error('修改密码失败:', error)
    errors.oldPassword = '密码修改失败，请稍后重试'
    showToastMessage('密码修改失败，请稍后重试', 'error')
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
    let response;
    
    if (resetMethod.value === 'phone') {
      const requestData: ResetPasswordPhoneRequest = {
        phone: phone.value,
        code: phoneCode.value,
        newPassword: newPassword.value
      }
      response = await apiService.resetPasswordPhone(requestData)
    } else {
      const requestData: ResetPasswordEmailRequest = {
        email: email.value,
        code: emailCode.value,
        newPassword: newPassword.value
      }
      response = await apiService.resetPasswordEmail(requestData)
    }

    // 检查响应状态
    if (response.code === 200) {
      // 密码重置成功
      showToastMessage('密码重置成功，即将跳转到登录页面', 'success')
      setTimeout(() => {
        router.push('/login')
      }, 1000)
    } else {
      // 处理错误
      const errorMsg = handleResetErrorResponse(response)
      showToastMessage(errorMsg, 'error')
    }
  } catch (error: any) {
    console.error('重置密码失败:', error)
    errors.newPassword = '密码重置失败，请稍后重试'
    showToastMessage('密码重置失败，请稍后重试', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 处理重置密码错误响应
const handleResetErrorResponse = (response: any) => {
  const field = response.data?.data?.field
  const message = response.data?.data?.message || '重置密码失败'
  
  if (field === 'phone') {
    errors.phone = message
  } else if (field === 'code' && resetMethod.value === 'phone') {
    errors.phoneCode = message
  } else if (field === 'email') {
    errors.email = message
  } else if (field === 'code' && resetMethod.value === 'email') {
    errors.emailCode = message
  } else {
    errors.newPassword = message
  }
  
  return message
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
  background-color: #1f2937;
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #e1e6f5;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  padding: 4px;
  border-radius: 4px;
  color: #94a3b8;
  transition: background-color 0.2s, color 0.2s;
}

.close-btn:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: #e1e6f5;
}

.modal-content {
  padding: 20px;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 16px;
}

label {
  display: inline-block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #e1e6f5;
  font-size: 14px;
}

input {
  width: 100%;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 14px;
  color: #e1e6f5;
  transition: border-color 0.2s, box-shadow 0.2s;
}

input:focus {
  outline: none;
  border-color: rgba(94, 155, 255, 0.5);
  box-shadow: 0 0 0 2px rgba(94, 155, 255, 0.1);
}

input::placeholder {
  color: rgba(255, 255, 255, 0.3);
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
  color: #94a3b8;
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
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.cancel-btn {
  background: transparent;
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.cancel-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.05);
  color: #e1e6f5;
}

.cancel-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-btn {
  background-color: #5e9bff;
  color: white;
  border: none;
}

.submit-btn:hover:not(:disabled) {
  background-color: #4b8bff;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: #ff6b6b;
  font-size: 12px;
  margin-left: 8px;
  display: inline-block;
}

.forgot-password,
.back-to-login {
  margin-top: 12px;
  text-align: right;
  font-size: 14px;
}

.forgot-password a,
.back-to-login a {
  color: #5e9bff;
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password a:hover,
.back-to-login a:hover {
  color: #4b8bff;
  text-decoration: underline;
}

.reset-method-tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.tab {
  flex: 1;
  text-align: center;
  padding: 12px;
  cursor: pointer;
  color: #94a3b8;
  font-weight: 500;
  transition: all 0.2s;
  border-bottom: 2px solid transparent;
}

.tab:hover {
  color: #e1e6f5;
}

.tab.active {
  color: #5e9bff;
  border-bottom: 2px solid #5e9bff;
}

.verification-code .code-input-group {
  display: flex;
  gap: 8px;
}

.send-code-btn {
  white-space: nowrap;
  background: rgba(94, 155, 255, 0.2);
  color: #5e9bff;
  border: 1px solid rgba(94, 155, 255, 0.3);
  border-radius: 8px;
  padding: 0 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-code-btn:hover:not(:disabled) {
  background: rgba(94, 155, 255, 0.3);
}

.send-code-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1100;
  animation: fadeIn 0.3s ease-out;
}

.toast-success {
  background-color: #4ade80;
  color: white;
}

.toast-error {
  background-color: #ff6b6b;
  color: white;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -40%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -50%);
  }
}

/* Add embedded mode styles */
.embedded-modal {
  width: 100%;
  display: block;
}

.embedded-modal form {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  padding: 1.5rem;
}

.embedded-modal h4 {
  margin: 0 0 1.5rem 0;
  color: #e1e6f5;
  font-size: 1.25rem;
  font-weight: 500;
}

.embedded-toast {
  position: relative;
  top: 10px;
  left: 0;
  width: 100%;
  transform: none;
}
</style>