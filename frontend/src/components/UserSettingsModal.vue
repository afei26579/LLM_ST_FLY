<template>
  <div>
    <!-- 全局提示信息，不在ModalStyle内部 -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
    
    <ModalStyle :is-open="isOpen" title="个人设置" @close="closeModal" :wide="true">
      <!-- 个人资料 -->
      <div class="tab-content">
        <div v-if="isLoading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>正在加载用户信息...</p>
        </div>
        
        <form v-else @submit.prevent="saveSettings">
          <!-- 头像（放在第一行并居中） -->
          <div class="form-group avatar-container">
            <div class="avatar-uploader">
              <div class="avatar-preview" @click="triggerFileInput">
                <span v-if="!previewImage">{{ userInfo.username?.[0]?.toUpperCase() || 'U' }}</span>
                <img v-else :src="previewImage" alt="头像预览" />
                <div class="avatar-hover-overlay">
                  <span>点击更换头像</span>
                </div>
              </div>
              <input 
                type="file" 
                ref="fileInput"
                @change="handleFileChange" 
                accept="image/*" 
                style="display:none"
              />
            </div>
          </div>

          <!-- 昵称 -->
          <div class="form-group-row">
            <label for="nickname">昵称</label>
            <div class="form-field">
              <input
                type="text"
                id="nickname"
                v-model="userInfo.nickname"
                placeholder="请输入昵称"
                :class="{ 'error': errors.nickname }"
              />
              <div v-if="errors.nickname" class="error-message">{{ errors.nickname }}</div>
            </div>
          </div>
          
          <!-- 性别 (删除了"其他"选项) -->
          <div class="form-group-row align-center">
            <label for="gender">性别</label>
            <div class="form-field">
              <div class="radio-group no-padding">
                <label class="radio-label">
                  <input type="radio" v-model="userInfo.gender" value="male" />
                  <span>男</span>
                </label>
                <label class="radio-label">
                  <input type="radio" v-model="userInfo.gender" value="female" />
                  <span>女</span>
                </label>
              </div>
            </div>
          </div>

          <!-- 生日 -->
          <div class="form-group-row">
            <label for="birthday">生日</label>
            <div class="form-field">
              <input
                type="date"
                id="birthday"
                v-model="userInfo.birthday"
                placeholder="请选择生日"
              />
            </div>
          </div>

          <!-- 地区 -->
          <div class="form-group-row">
            <label for="location">地区</label>
            <div class="form-field location-selector">
              <select v-model="userInfo.province">
                <option value="">请选择省份</option>
                <option v-for="province in provinces" :key="province.code" :value="province.name">{{ province.name }}</option>
              </select>
              
              <select v-model="userInfo.city" :disabled="!userInfo.province">
                <option value="">请选择城市</option>
                <option v-for="city in cities" :key="city.code" :value="city.name">{{ city.name }}</option>
              </select>
              
              <select v-model="userInfo.district" :disabled="!userInfo.city">
                <option value="">请选择区县</option>
                <option v-for="district in districts" :key="district.code" :value="district.name">{{ district.name }}</option>
              </select>
            </div>
          </div>

          <!-- QQ号码 -->
          <div class="form-group-row">
            <label for="qq">QQ号码</label>
            <div class="form-field">
              <input
                type="text"
                id="qq"
                v-model="userInfo.qq"
                placeholder="请输入QQ号码"
                :class="{ 'error': errors.qq }"
                @input="onQQInput"
              />
              <div v-if="errors.qq" class="error-message">{{ errors.qq }}</div>
            </div>
          </div>

          <!-- 个人简介 -->
          <div class="form-group-row">
            <label for="bio">简介</label>
            <div class="form-field">
              <textarea
                id="bio"
                v-model="userInfo.bio"
                placeholder="请输入个人简介"
                rows="4"
              ></textarea>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeModal">取消</button>
            <button type="submit" class="primary-btn" :disabled="isSaving">
              {{ isSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </ModalStyle>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { apiService, type UserProfileUpdate } from '../services/api'
import ModalStyle from './ModalStyle.vue'
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

// 提示信息
const notification = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

// 显示提示信息
const showNotification = (message: string, type: 'success' | 'error') => {
  notification.message = message
  notification.type = type
  notification.show = true
  
  // 设置自动隐藏
  setTimeout(() => {
    notification.show = false
  }, type === 'success' ? 1000 : 3000)
}

// 加载用户信息
const loadUserInfo = async () => {
  isLoading.value = true;
  try {
    // 从后端获取最新的用户信息
    const response = await apiService.getUserInfo();
    console.log(response, 'response~~~~~~~~~~~~')
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
        
        // 立即关闭模态框
        emit('save')
        closeModal()
        
        // 显示成功提示，不等待直接显示
        showNotification('保存成功', 'success')
      } else {
        console.error('保存设置失败:', response.message);
        // 立即关闭模态框
        closeModal()
        // 显示错误提示
        showNotification(`保存失败: ${response.message}`, 'error')
      }
    } catch (error) {
      console.error('保存设置失败:', error);
      // 立即关闭模态框
      closeModal()
      // 显示错误提示
      showNotification(`保存失败: ${error instanceof Error ? error.message : '未知错误'}`, 'error')
    }
  } catch (error) {
    console.error('保存设置失败', error)
    // 立即关闭模态框
    closeModal()
    // 显示错误提示
    showNotification('保存失败，请稍后再试', 'error')
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
/* 修改全局提示消息样式 */
.notification {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 500;
  z-index: 2000;
  text-align: center;
  width: auto;
  min-width: 200px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: fade-in 0.3s ease-out;
}

.notification.success {
  background: linear-gradient(90deg, #4ade80 0%, #34d399 100%);
  color: #fff;
}

.notification.error {
  background: linear-gradient(90deg, #f87171 0%, #ef4444 100%);
  color: #fff;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%);
  }
}

/* 添加加载和错误状态的样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #e1e6f5;
  min-height: 200px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin-bottom: 1rem;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  border-top-color: #5e9bff;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  text-align: center;
  color: #f87171;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
}

.retry-btn {
  margin-left: 0.5rem;
  background-color: rgba(255, 255, 255, 0.1);
  color: #e1e6f5;
  border: none;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.tab-content {
  min-height: 300px;
}

/* 新的行布局 */
.form-group-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.form-group-row label {
  width: 100px;
  flex-shrink: 0;
  padding-top: 0.75rem;
  color: #e1e6f5;
  font-size: 0.875rem;
  font-weight: 500;
}

.form-field {
  flex: 1;
}

/* 头像居中显示 */
.avatar-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 2rem;
  text-align: center;
}

/* 表单控件样式 */
.form-field input, 
.form-field textarea,
.form-field select {
  width: 100%;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #e1e6f5;
  transition: all 0.2s;
}

.form-field input:focus,
.form-field textarea:focus,
.form-field select:focus {
  outline: none;
  border-color: #5e9bff;
  box-shadow: 0 0 0 3px rgba(94, 155, 255, 0.2);
}

.form-field input::placeholder,
.form-field textarea::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

/* 头像上传 */
.avatar-uploader {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: rgba(94, 155, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: 600;
  color: #5e9bff;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  border: 2px solid rgba(255, 255, 255, 0.1);
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.2s;
}

.avatar-preview:hover .avatar-hover-overlay {
  opacity: 1;
}

.avatar-hover-overlay {
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
  color: white;
  font-size: 0.8rem;
  font-weight: normal;
}

.avatar-preview:hover {
  border-color: #5e9bff;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.help-text {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 8px;
}

textarea {
  font-family: inherit;
  resize: vertical;
  min-height: 100px;
}

/* 单选框样式 */
.radio-group {
  display: flex;
  gap: 1.5rem;
  padding-top: 0.75rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  appearance: none;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.05);
  position: relative;
  margin: 0;
  cursor: pointer;
}

.radio-label input[type="radio"]:checked {
  border-color: #5e9bff;
}

.radio-label input[type="radio"]:checked::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 0.625rem;
  height: 0.625rem;
  border-radius: 50%;
  background: #5e9bff;
}

.radio-label span {
  color: #e1e6f5;
  font-size: 0.875rem;
}

/* 日期选择器 */
input[type="date"] {
  color-scheme: dark;
}

input[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(0.7);
  cursor: pointer;
}

/* 省市区选择器 */
.location-selector {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.location-selector select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23e1e6f5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  padding-right: 2.5rem;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(94, 155, 255, 0.3);
}

.location-selector select:focus {
  border-color: #5e9bff;
  box-shadow: 0 0 0 2px rgba(94, 155, 255, 0.2);
}

.location-selector select option {
  background-color: #1e293b;
  color: #e1e6f5;
}

/* 自定义滚动条样式 */
.location-selector select::-webkit-scrollbar {
  width: 8px;
}

.location-selector select::-webkit-scrollbar-track {
  background-color: #0f172a;
}

.location-selector select::-webkit-scrollbar-thumb {
  background-color: #334155;
  border-radius: 4px;
}

.location-selector select::-webkit-scrollbar-thumb:hover {
  background-color: #475569;
}

.location-selector select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.primary-btn {
  background: linear-gradient(90deg, #5e9bff 0%, #a569ff 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  background: transparent;
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #e1e6f5;
}

/* 新增垂直居中的样式 */
.form-group-row.align-center {
  align-items: center;
}

/* 修改单选框组在垂直居中时不需要额外的顶部内边距 */
.radio-group.no-padding {
  padding-top: 0;
}

@media (max-width: 768px) {
  .form-group-row {
    flex-direction: column;
  }
  
  .form-group-row label {
    width: 100%;
    margin-bottom: 0.5rem;
    padding-top: 0;
  }
  
  .location-selector {
    grid-template-columns: 1fr;
  }
}
</style> 