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
            <!--button class="upload-btn" @click="triggerFileInput">更换头像</button-->
          </div>
          
          <!-- 用户信息表单 -->
          <div class="settings-form">
            <div class="form-group">
              <div class="inline-form-row">
                <label>昵称 <span class="required">*</span></label>
                <div class="input-container">
                  <input type="text" v-model="userInfo.nickname" class="form-control" :class="{ 'error': errors.nickname }" />
                  <span v-if="errors.nickname" class="error-message">{{ errors.nickname }}</span>
                </div>
              </div>
            </div>
            
            <!-- 性别选择 -->
            <div class="form-group">
              <div class="inline-form-row">
                <label>性别</label>
                <div class="radio-group">
                  <label class="radio-label">
                    <input type="radio" v-model="userInfo.gender" value="male" /> 男
                  </label>
                  <label class="radio-label">
                    <input type="radio" v-model="userInfo.gender" value="female" /> 女
                  </label>
                </div>
              </div>
            </div>
                     <!-- QQ号码 -->
            <div class="form-group">
              <div class="inline-form-row">
                <label>QQ号码</label>
                <div class="input-container">
                  <input 
                    type="text" 
                    v-model="userInfo.qq" 
                    class="form-control" 
                    placeholder="请输入QQ号码" 
                    :class="{ 'error': errors.qq }"
                    @input="onQQInput"
                  />
                  <span v-if="errors.qq" class="error-message">{{ errors.qq }}</span>
                </div>
              </div>
            </div>
            
            <!-- 生日选择 -->
            <div class="form-group">
              <div class="inline-form-row">
                <label>生日</label>
                <input type="date" v-model="userInfo.birthday" class="form-control" />
              </div>
            </div>
            
            <!-- 省份 -->
            <div class="form-group">
              <div class="inline-form-row">
                <label>省份</label>
                <select v-model="userInfo.province" class="form-control">
                  <option value="">请选择省份</option>
                  <option v-for="province in provinces" :key="province.code" :value="province.name">{{ province.name }}</option>
                </select>
              </div>
            </div>
            
            <!-- 城市 -->
            <div class="form-group">
              <div class="inline-form-row">
                <label>城市</label>
                <select v-model="userInfo.city" class="form-control">
                  <option value="">请选择城市</option>
                  <option v-for="city in cities" :key="city.code" :value="city.name">{{ city.name }}</option>
                </select>
              </div>
            </div>
            
            <!-- 区县 -->
            <div class="form-group">
              <div class="inline-form-row">
                <label>区县</label>
                <select v-model="userInfo.district" class="form-control">
                  <option value="">请选择区县</option>
                  <option v-for="district in districts" :key="district.code" :value="district.name">{{ district.name }}</option>
                </select>
              </div>
            </div>
            
   
            <div class="form-group">
              <div class="inline-form-row">
              <label>个人简介</label>
              <textarea v-model="userInfo.bio" rows="3" class="form-control"></textarea>
            </div>
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
import pcaData from '../assets/data/pca-code.json'

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
  theme: 'light',
  gender: 'male',
  birthday: '',
  province: '',
  city: '',
  district: '',
  qq: ''
})

// 表单错误信息
const errors = reactive({
  email: '',
  phone: '',
  nickname: '',
  qq: ''
})

// 省市区数据
const provinces = ref(pcaData)
const cities = ref<any[]>([])
const districts = ref<any[]>([])

// 监听省份变化，更新城市列表
watch(() => userInfo.province, (newProvince) => {
  if (newProvince) {
    const province = provinces.value.find(p => p.name === newProvince)
    cities.value = province?.children || []
    userInfo.city = ''
    userInfo.district = ''
    districts.value = []
  } else {
    cities.value = []
    districts.value = []
  }
})

// 监听城市变化，更新区县列表
watch(() => userInfo.city, (newCity) => {
  if (newCity) {
    const city = cities.value.find(c => c.name === newCity)
    districts.value = city?.children || []
    userInfo.district = ''
  } else {
    districts.value = []
  }
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

watch(() => userInfo.qq, (newVal) => {
  validateQQ(newVal);
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
      
      // 新增字段
      userInfo.gender = response.data.gender || 'male';
      userInfo.birthday = response.data.birthday || '';
      userInfo.province = response.data.province || '';
      userInfo.city = response.data.city || '';
      userInfo.district = response.data.district || '';
      userInfo.qq = response.data.qq || '';
      
      // 验证字段
      validateNickname(userInfo.nickname);
      if (userInfo.qq) {
        validateQQ(userInfo.qq);
      }
      
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
    
    // 新增字段
    userInfo.gender = authStore.userInfo.gender || 'male';
    userInfo.birthday = authStore.userInfo.birthday || '';
    userInfo.province = authStore.userInfo.province || '';
    userInfo.city = authStore.userInfo.city || '';
    userInfo.district = authStore.userInfo.district || '';
    userInfo.qq = authStore.userInfo.qq || '';
    
    // 验证字段
    validateNickname(userInfo.nickname);
    if (userInfo.qq) {
      validateQQ(userInfo.qq);
    }
    
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

// QQ号码输入处理
const onQQInput = (event: Event) => {
  const input = event.target as HTMLInputElement;
  // 只保留数字
  const value = input.value.replace(/\D/g, '');
  userInfo.qq = value;
  validateQQ(value);
}

// 验证QQ号码
const validateQQ = (value: string) => {
  errors.qq = '';
  if (value) {
    if (value.length < 6 || value.length > 12) {
      errors.qq = 'QQ号码长度应为6-12位';
      return false;
    }
  }
  return true;
}

// 表单验证
const validateForm = () => {
  // 验证所有字段
  const isNicknameValid = validateNickname(userInfo.nickname);
  const isQQValid = validateQQ(userInfo.qq);
  
  return isNicknameValid && isQQValid;
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
      bio: userInfo.bio,
      theme: userInfo.theme,
      gender: userInfo.gender,
      birthday: userInfo.birthday,
      province: userInfo.province,
      city: userInfo.city,
      district: userInfo.district,
      qq: userInfo.qq
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
  max-width: 550px;
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
  padding: 0.2rem;
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
  max-height: 70vh;
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
  margin-bottom: 0.25rem;
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
  margin-bottom: 0.25rem;
}

.inline-form-row {
  display: flex;
  align-items: center;
  width: 100%;
}

.inline-form-row label {
  min-width: 70px;
  margin-bottom: 0;
  margin-right: 10px;
  font-weight: 500;
  color: #374151;
}

.inline-form-row .form-control,
.inline-form-row .radio-group,
.inline-form-row .input-container {
  flex: 1;
}

.input-container {
  position: relative;
  width: 100%;
}

.input-container .error-message {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.8rem;
  color: #ef4444;
  margin-right: 8px;
  white-space: nowrap;
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

.radio-group {
  display: flex;
  gap: 20px;
  align-items: center;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  margin: 0;
}

input[type="date"] {
  color: #374151;
  font-family: inherit;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0.6;
}

input[type="date"]::-webkit-calendar-picker-indicator:hover {
  opacity: 1;
}
</style> 