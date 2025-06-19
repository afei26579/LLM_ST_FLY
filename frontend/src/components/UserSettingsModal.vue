<template>
  <div class="modal-overlay" v-if="isOpen" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h2>{{ userInfo.nickname }}</h2>
        <button class="close-btn" @click="closeModal">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      <div class="modal-body">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>加载用户信息中...</p>
        </div>
        
        <!-- 用户信息内容 -->
        <div v-else>
          <!-- 头像上传区域 -->
          <div class="avatar-section">
            <div class="avatar-container">
              <div v-if="previewImage" class="avatar-preview">
                <img :src="previewImage" alt="头像预览" />
              </div>
              <div v-else class="avatar-placeholder">
                {{ userInfo.username?.[0]?.toUpperCase() || 'U' }}
              </div>
              <div class="avatar-overlay" @click="triggerFileInput">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path>
                  <circle cx="12" cy="13" r="4"></circle>
                </svg>
              </div>
            </div>
            <input type="file" ref="fileInput" @change="handleFileChange" accept="image/*" style="display: none" />
            <button class="upload-btn" @click="triggerFileInput">更换头像</button>
          </div>
          
          <!-- 用户信息表单 -->
          <div class="settings-form">
            <div class="form-group">
              <div class="label-container">
                <label>昵称 <span class="required">*</span></label>
                <span v-if="errors.nickname" class="error-message">{{ errors.nickname }}</span>
              </div>
              <input type="text" v-model="userInfo.nickname" class="form-control" :class="{ 'error': errors.nickname }" />
              
            </div>
            
            <div class="form-group">
              <div class="label-container">
                <label>电子邮箱</label>
                <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
              </div>
              <input type="email" v-model="userInfo.email" class="form-control" :class="{ 'error': errors.email }" />
              
            </div>
            
            <div class="form-group">
              <div class="label-container">
                <label>手机号码</label>
                <span v-if="errors.phone" class="error-message">{{ errors.phone }}</span>
              </div>
              <input type="tel" v-model="userInfo.phone" class="form-control" :class="{ 'error': errors.phone }" />
             
            </div>
            
            <div class="form-group">
              <label>个人简介</label>
              <textarea v-model="userInfo.bio" rows="3" class="form-control"></textarea>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="closeModal">取消</button>
        <button class="btn btn-primary" @click="saveSettings" :disabled="isSaving || isLoading">
          <span v-if="isSaving">保存中...</span>
          <span v-else>保存设置</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { apiService, type UserProfileUpdate } from '../services/api'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits(['close', 'save'])

const authStore = useAuthStore()
const fileInput = ref<HTMLInputElement | null>(null)
const previewImage = ref<string | null>(null)
const isSaving = ref(false)
const isLoading = ref(false)

// 用户信息表单数据
const userInfo = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: '',
  bio: '',
  avatar: '',
  theme: 'light'
})

// 表单错误信息
const errors = reactive({
  email: '',
  phone: '',
  nickname: ''
})

// 初始化用户数据
onMounted(() => {
  loadUserInfo();
});

// 监听isOpen属性变化，当打开弹窗时加载用户信息
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadUserInfo();
  }
});

// 监听表单输入变化，实时验证
watch(() => userInfo.nickname, (newVal) => {
  validateNickname(newVal);
});

watch(() => userInfo.email, (newVal) => {
  validateEmail(newVal);
});

watch(() => userInfo.phone, (newVal) => {
  validatePhone(newVal);
});

// 加载用户信息
const loadUserInfo = async () => {
  isLoading.value = true;
  try {
    // 从后端获取最新的用户信息
    const response = await apiService.getUserInfo();
    
    // 使用API返回的数据
    if (response.code >= 200 && response.code < 300 && response.data) {
      // 更新authStore中的用户信息
      authStore.updateUserInfo(response.data);
      
      // 更新表单数据
      userInfo.username = response.data.username || '';
      userInfo.nickname = response.data.nickname || '';
      userInfo.email = response.data.email || '';
      userInfo.phone = response.data.phone || '';
      userInfo.bio = response.data.bio || '';
      userInfo.avatar = response.data.avatar || '';
      
      // 如果有头像，设置预览图
      if (response.data.avatar) {
        previewImage.value = response.data.avatar;
      } else {
        previewImage.value = null;
      }
    } else {
      // 如果获取失败，使用authStore中的数据
      fallbackToStoredUserInfo();
    }
  } catch (error) {
    console.error('获取用户信息失败', error);
    // 如果出错，使用authStore中的数据
    fallbackToStoredUserInfo();
  } finally {
    isLoading.value = false;
  }
}

// 使用本地存储的用户信息作为后备
const fallbackToStoredUserInfo = () => {
  if (authStore.userInfo) {
    userInfo.username = authStore.userInfo.username || '';
    userInfo.nickname = authStore.userInfo.nickname || '';
    userInfo.email = authStore.userInfo.email || '';
    userInfo.phone = authStore.userInfo.phone || '';
    userInfo.bio = authStore.userInfo.bio || '';
    
    // 如果有头像，设置预览图
    if (authStore.userInfo.avatar) {
      previewImage.value = authStore.userInfo.avatar;
    } else {
      previewImage.value = null;
    }
  }
}

// 触发文件选择
const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

// 处理文件选择
const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    
    // 检查文件类型
    if (!file.type.match('image.*')) {
      alert('请选择图片文件')
      return
    }
    
    // 检查文件大小（限制为2MB）
    if (file.size > 2 * 1024 * 1024) {
      alert('图片大小不能超过2MB')
      return
    }
    
    // 创建预览
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImage.value = e.target?.result as string
      userInfo.avatar = e.target?.result as string
    }
    reader.readAsDataURL(file)
  }
}

// 验证昵称
const validateNickname = (value: string) => {
  errors.nickname = '';
  if (!value || value.trim() === '') {
    errors.nickname = '昵称不能为空';
    return false;
  } else if (value && (value.length < 2 || value.length > 16)) {
    errors.nickname = '昵称必须是2-16个字符';
    return false;
  }
  return true;
}

// 验证邮箱
const validateEmail = (value: string) => {
  errors.email = '';
  if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    errors.email = '请输入有效的电子邮箱地址';
    return false;
  }
  return true;
}

// 验证手机号
const validatePhone = (value: string) => {
  errors.phone = '';
  if (value && !/^1[3-9]\d{9}$/.test(value)) {
    errors.phone = '请输入有效的手机号码';
    return false;
  }
  return true;
}

// 表单验证
const validateForm = () => {
  // 验证所有字段
  const isNicknameValid = validateNickname(userInfo.nickname);
  const isEmailValid = validateEmail(userInfo.email);
  const isPhoneValid = validatePhone(userInfo.phone);
  
  return isNicknameValid && isEmailValid && isPhoneValid;
}

// 保存设置
const saveSettings = async () => {
  if (!validateForm()) {
    return
  }
  
  isSaving.value = true
  
  try {
    // 处理头像上传
    let avatarUrl = previewImage.value || undefined
    let hasNewAvatar = false
    
    // 如果有新的头像文件，先上传头像
    if (userInfo.avatar && userInfo.avatar !== authStore.userInfo?.avatar && userInfo.avatar.startsWith('data:')) {
      hasNewAvatar = true
      // 将base64转换为文件对象
      const base64Response = await fetch(userInfo.avatar);
      const blob = await base64Response.blob();
      const file = new File([blob], "avatar.jpg", { type: "image/jpeg" });
      
      try {
        // 上传头像
        const avatarResponse = await apiService.uploadAvatar(file);
        if (avatarResponse.code >= 200 && avatarResponse.code < 300 && avatarResponse.data) {
          avatarUrl = avatarResponse.data.avatar;
        } else {
          console.error('头像上传失败:', avatarResponse.message);
        }
      } catch (error) {
        console.error('头像上传失败:', error);
      }
    }
    
    // 准备要更新的用户数据
    const profileData = {
      username: userInfo.username,
      nickname: userInfo.nickname,
      email: userInfo.email,
      phone: userInfo.phone,
      bio: userInfo.bio,
      theme: userInfo.theme,
    } as UserProfileUpdate
    
    // 只有在成功上传了新头像时，才添加avatar字段
    if (hasNewAvatar && avatarUrl) {
      console.log('头像已上传成功，无需在profileData中包含avatar字段');
    }
    
    try {
      // 调用API更新用户信息
      const response = await apiService.updateUserProfile(profileData);
      
      if (response.code >= 200 && response.code < 300 && response.data) {
        // 更新本地存储的用户信息
        authStore.updateUserInfo(response.data);
        
        emit('save')
        closeModal()
      } else {
        console.error('保存设置失败:', response.message);
        alert('保存设置失败: ' + response.message);
      }
    } catch (error) {
      console.error('保存设置失败:', error);
      alert('保存设置失败: ' + (error instanceof Error ? error.message : '未知错误'));
    }
  } catch (error) {
    console.error('保存设置失败', error)
    alert('保存设置失败，请稍后再试');
  } finally {
    isSaving.value = false
  }
}

// 关闭弹窗
const closeModal = () => {
  emit('close')
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
  background-color: #fff;
  border-radius: 8px;
  width: 95%;
  max-width: 500px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  max-height: 90vh;
  animation: modal-appear 0.3s ease-out;
}

@keyframes modal-appear {
  0% {
    opacity: 0;
    transform: translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #111827;
}

.close-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 50%;
  color: #6b7280;
}

.close-btn:hover {
  background-color: #f3f4f6;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
}

/* 头像上传区域 */
.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.5rem;
}

.avatar-container {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  margin-bottom: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, #5e9bff 0%, #a569ff 100%);
  color: white;
}

.avatar-preview {
  width: 100%;
  height: 100%;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
}

.avatar-overlay:hover {
  opacity: 1;
}

.avatar-overlay svg {
  color: white;
}

.upload-btn {
  background-color: #f3f4f6;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  cursor: pointer;
  color: #4b5563;
  transition: background-color 0.2s;
}

.upload-btn:hover {
  background-color: #e5e7eb;
}

/* 表单样式 */
.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  margin-bottom: 0.5rem;
}

.label-container {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.label-container label {
  font-weight: 500;
  color: #374151;
  margin-right: 0.5rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-control.error {
  border-color: #ef4444;
}

textarea.form-control {
  resize: vertical;
  min-height: 100px;
}

.form-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.error-message {
  font-size: 0.8rem;
  color: #ef4444;
}

.required {
  color: #ef4444;
  margin-left: 2px;
}

.btn {
  padding: 0.625rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  border: none;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-primary:disabled {
  background-color: #93c5fd;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #4b5563;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 200px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(59, 130, 246, 0.2);
  border-radius: 50%;
  border-top-color: #3b82f6;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0;
}
</style> 