<template>
  <ModalStyle :is-open="isOpen" title="安全设置" @close="closeModal">
    <div class="tabs">
      <div 
        class="tab" 
        :class="{ 'active': activeTab === 'password' }"
        @click="activeTab = 'password'"
      >
        修改密码
      </div>
      <div 
        class="tab" 
        :class="{ 'active': activeTab === 'phone' }"
        @click="activeTab = 'phone'"
      >
        绑定手机
      </div>
      <div 
        class="tab" 
        :class="{ 'active': activeTab === 'email' }"
        @click="activeTab = 'email'"
      >
        绑定邮箱
      </div>
    </div>
    
    <!-- 密码管理 -->
    <div v-show="activeTab === 'password'" class="tab-content">
      <!-- 使用现有的PasswordModal组件 -->
      <PasswordModal 
        :is-open="true" 
        :embedded="true"
        @close="handlePasswordModalClose" 
        @password-changed="handlePasswordChanged"
      />
    </div>
    
    <!-- 手机绑定表单 -->
    <div v-show="activeTab === 'phone'" class="tab-content">
      <div class="binding-info" v-if="userPhone">
        <p>当前绑定手机：{{ maskPhone(userPhone) }}</p>
        <button class="secondary-btn" @click="showChangePhoneForm">更换绑定</button>
      </div>
      
      <form v-if="showPhoneForm" @submit.prevent="handlePhoneSubmit">
        <div class="form-group">
          <label for="phone">手机号码</label>
          <div class="input-with-button">
            <input 
              type="text" 
              id="phone" 
              v-model="phoneForm.phone" 
              placeholder="请输入手机号码" 
              required 
              pattern="^1[3-9]\d{9}$"
            >
          </div>
          <div class="error-message" v-if="phoneForm.errors.phone">{{ phoneForm.errors.phone }}</div>
        </div>
        
        <div class="form-group">
          <label for="phoneCode">验证码</label>
          <div class="input-with-button">
            <input 
              type="text" 
              id="phoneCode" 
              v-model="phoneForm.code" 
              placeholder="请输入验证码" 
              required 
              pattern="\d{6}"
            >
            <button 
              type="button" 
              class="send-code-btn" 
              @click="sendPhoneCode" 
              :disabled="phoneCountdown > 0"
            >
              {{ phoneCountdown > 0 ? `${phoneCountdown}秒后重试` : '获取验证码' }}
            </button>
          </div>
          <div class="error-message" v-if="phoneForm.errors.code">{{ phoneForm.errors.code }}</div>
        </div>
        
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="cancelPhoneForm">取消</button>
          <button type="submit" class="primary-btn" :disabled="phoneForm.submitting">{{ phoneForm.submitText }}</button>
        </div>
      </form>
      
      <div class="empty-state" v-else-if="!userPhone">
        <p>您还未绑定手机号</p>
        <button class="primary-btn" @click="showBindPhoneForm">立即绑定</button>
      </div>
    </div>
    
    <!-- 邮箱绑定表单 -->
    <div v-show="activeTab === 'email'" class="tab-content">
      <div class="binding-info" v-if="userEmail">
        <p>当前绑定邮箱：{{ maskEmail(userEmail) }}</p>
        <button class="secondary-btn" @click="showChangeEmailForm">更换绑定</button>
      </div>
      
      <form v-if="showEmailForm" @submit.prevent="handleEmailSubmit">
        <div class="form-group">
          <label for="email">邮箱地址</label>
          <input 
            type="email" 
            id="email" 
            v-model="emailForm.email" 
            placeholder="请输入邮箱地址" 
            required
          >
          <div class="error-message" v-if="emailForm.errors.email">{{ emailForm.errors.email }}</div>
        </div>
        
        <p class="form-hint">
          验证邮件将发送到您的邮箱，请按照邮件中的链接完成验证
        </p>
        
        <div class="form-actions">
          <button type="button" class="cancel-btn" @click="cancelEmailForm">取消</button>
          <button type="submit" class="primary-btn" :disabled="emailForm.submitting">{{ emailForm.submitText }}</button>
        </div>
      </form>
      
      <div v-else-if="emailSent" class="email-sent">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
          <polyline points="22,6 12,13 2,6"></polyline>
        </svg>
        <h4>验证邮件已发送</h4>
        <p>我们已向 {{ emailForm.email }} 发送了一封验证邮件，请查收并点击邮件中的链接完成验证。</p>
        <div class="form-actions">
          <button class="secondary-btn" @click="resendEmail" :disabled="emailCountdown > 0">
            {{ emailCountdown > 0 ? `${emailCountdown}秒后可重新发送` : '重新发送' }}
          </button>
          <button class="primary-btn" @click="closeModal">我知道了</button>
        </div>
      </div>
      
      <div class="empty-state" v-else-if="!userEmail">
        <p>您还未绑定邮箱</p>
        <button class="primary-btn" @click="showBindEmailForm">立即绑定</button>
      </div>
    </div>
  </ModalStyle>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '../stores/auth';
import ModalStyle from './ModalStyle.vue';
import PasswordModal from './PasswordModal.vue';

// Props
const props = defineProps<{
  isOpen: boolean;
}>();

// Emits
const emit = defineEmits(['close', 'binding-updated']);

// Store
const authStore = useAuthStore();

// State
const activeTab = ref('password');  // 将默认标签改为密码管理
const showPhoneForm = ref(false);
const showEmailForm = ref(false);
const emailSent = ref(false);
const phoneCountdown = ref(0);
const emailCountdown = ref(0);

// 用户绑定的手机号和邮箱
// 在实际应用中，这些数据应该从 authStore 中获取
const userPhone = ref(authStore.userInfo?.phone || '');
const userEmail = ref(authStore.userInfo?.email || '');

// 手机表单数据
const phoneForm = ref({
  phone: '',
  code: '',
  submitting: false,
  errors: {
    phone: '',
    code: ''
  },
  submitText: '绑定手机'
});

// 邮箱表单数据
const emailForm = ref({
  email: '',
  submitting: false,
  errors: {
    email: ''
  },
  submitText: '发送验证邮件'
});

// 监听弹窗打开状态，重置表单
watch(() => props.isOpen, (val) => {
  if (val) {
    resetForms();
  }
});

// 重置所有表单状态
const resetForms = () => {
  showPhoneForm.value = false;
  showEmailForm.value = false;
  emailSent.value = false;
  phoneForm.value = {
    phone: '',
    code: '',
    submitting: false,
    errors: { phone: '', code: '' },
    submitText: '绑定手机'
  };
  emailForm.value = {
    email: '',
    submitting: false,
    errors: { email: '' },
    submitText: '发送验证邮件'
  };
};

// 关闭弹窗
const closeModal = () => {
  emit('close');
  resetForms();
};

// 手机相关方法 //

// 显示绑定手机表单
const showBindPhoneForm = () => {
  phoneForm.value.submitText = '绑定手机';
  phoneForm.value.phone = '';
  showPhoneForm.value = true;
};

// 显示更换手机表单
const showChangePhoneForm = () => {
  phoneForm.value.submitText = '更换绑定';
  phoneForm.value.phone = '';
  showPhoneForm.value = true;
};

// 取消手机表单
const cancelPhoneForm = () => {
  showPhoneForm.value = false;
};

// 显示绑定邮箱表单
const showBindEmailForm = () => {
  emailForm.value.submitText = '发送验证邮件';
  emailForm.value.email = '';
  showEmailForm.value = true;
};

// 显示更换邮箱表单
const showChangeEmailForm = () => {
  emailForm.value.submitText = '发送验证邮件';
  emailForm.value.email = '';
  showEmailForm.value = true;
};

// 取消邮箱表单
const cancelEmailForm = () => {
  showEmailForm.value = false;
  emailSent.value = false;
};

// 发送手机验证码
const sendPhoneCode = async () => {
  // 验证手机号格式
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(phoneForm.value.phone)) {
    phoneForm.value.errors.phone = '请输入有效的手机号码';
    return;
  }
  
  phoneForm.value.errors.phone = '';
  
  try {
    // 模拟API调用
    // const response = await api.sendPhoneVerificationCode(phoneForm.value.phone);
    // console.log('验证码发送成功', response);
    
    // 开始倒计时
    phoneCountdown.value = 60;
    const timer = setInterval(() => {
      phoneCountdown.value--;
      if (phoneCountdown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);
    
  } catch (error) {
    console.error('发送验证码失败', error);
    phoneForm.value.errors.phone = '验证码发送失败，请稍后重试';
  }
};

// 提交手机绑定
const handlePhoneSubmit = async () => {
  // 验证手机号格式
  const phoneRegex = /^1[3-9]\d{9}$/;
  if (!phoneRegex.test(phoneForm.value.phone)) {
    phoneForm.value.errors.phone = '请输入有效的手机号码';
    return;
  }
  
  // 验证验证码格式
  const codeRegex = /^\d{6}$/;
  if (!codeRegex.test(phoneForm.value.code)) {
    phoneForm.value.errors.code = '请输入6位数字验证码';
    return;
  }
  
  phoneForm.value.errors.phone = '';
  phoneForm.value.errors.code = '';
  phoneForm.value.submitting = true;
  
  try {
    // 模拟API调用
    // const response = await api.bindPhone(phoneForm.value.phone, phoneForm.value.code);
    // console.log('手机绑定成功', response);
    
    // 模拟成功
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 更新用户信息
    userPhone.value = phoneForm.value.phone;
    showPhoneForm.value = false;
    
    // 通知父组件绑定成功
    emit('binding-updated', 'phone');
    
  } catch (error) {
    console.error('手机绑定失败', error);
    phoneForm.value.errors.code = '验证失败，请检查验证码是否正确';
  } finally {
    phoneForm.value.submitting = false;
  }
};

// 提交邮箱绑定
const handleEmailSubmit = async () => {
  // 验证邮箱格式
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(emailForm.value.email)) {
    emailForm.value.errors.email = '请输入有效的邮箱地址';
    return;
  }
  
  emailForm.value.errors.email = '';
  emailForm.value.submitting = true;
  
  try {
    // 模拟API调用
    // const response = await api.sendEmailVerification(emailForm.value.email);
    // console.log('验证邮件发送成功', response);
    
    // 模拟成功
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 显示邮件已发送界面
    showEmailForm.value = false;
    emailSent.value = true;
    
    // 开始邮件重发倒计时
    emailCountdown.value = 60;
    const timer = setInterval(() => {
      emailCountdown.value--;
      if (emailCountdown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);
    
  } catch (error) {
    console.error('邮件发送失败', error);
    emailForm.value.errors.email = '邮件发送失败，请稍后重试';
  } finally {
    emailForm.value.submitting = false;
  }
};

// 重新发送验证邮件
const resendEmail = async () => {
  if (emailCountdown.value > 0) return;
  
  try {
    // 模拟API调用
    // const response = await api.sendEmailVerification(emailForm.value.email);
    // console.log('验证邮件重新发送成功', response);
    
    // 开始邮件重发倒计时
    emailCountdown.value = 60;
    const timer = setInterval(() => {
      emailCountdown.value--;
      if (emailCountdown.value <= 0) {
        clearInterval(timer);
      }
    }, 1000);
    
  } catch (error) {
    console.error('邮件重发失败', error);
  }
};

// 隐藏部分手机号
const maskPhone = (phone: string) => {
  if (!phone || phone.length < 11) return phone;
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
};

// 隐藏部分邮箱
const maskEmail = (email: string) => {
  if (!email) return email;
  const [username, domain] = email.split('@');
  
  let maskedUsername = username;
  if (username.length > 3) {
    maskedUsername = username.substring(0, 3) + '****';
  } else if (username.length > 1) {
    maskedUsername = username.substring(0, 1) + '****';
  }
  
  return `${maskedUsername}@${domain}`;
};

// 处理密码修改后的逻辑
const handlePasswordChanged = () => {
  // 通知父组件密码已更新
  emit('binding-updated', 'password');
  
  // 可以在这里显示一个成功消息或执行其他操作
  console.log('密码修改成功');
};

// 处理密码修改对话框关闭后的逻辑
const handlePasswordModalClose = () => {
  // 在嵌入模式下，我们不需要真正关闭弹窗，只需保持在当前标签页
  // 如果需要额外的逻辑处理可以在这里添加
  console.log('密码修改对话框关闭');
};
</script>

<style scoped>
.tabs {
  display: flex;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 1.5rem;
}

.tab {
  padding: 0.75rem 1rem;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.2s;
  position: relative;
  border-bottom: 2px solid transparent;
}

.tab:hover {
  color: #e1e6f5;
}

.tab.active {
  color: #5e9bff;
  border-bottom-color: #5e9bff;
}

.tab-content {
  min-height: 200px;
}

.input-with-button {
  display: flex;
  gap: 10px;
}

.input-with-button input {
  flex: 1;
}

.send-code-btn {
  white-space: nowrap;
  background: rgba(94, 155, 255, 0.2);
  color: #5e9bff;
  border: 1px solid rgba(94, 155, 255, 0.3);
  border-radius: 8px;
  padding: 0 1rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
}

.send-code-btn:hover:not(:disabled) {
  background: rgba(94, 155, 255, 0.3);
}

.send-code-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.binding-info {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.binding-info p {
  margin: 0;
  color: #e1e6f5;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  text-align: center;
}

.empty-state p {
  color: #94a3b8;
  margin-bottom: 1.5rem;
}

.email-sent {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 2rem 1rem;
}

.email-sent svg {
  color: #5e9bff;
  margin-bottom: 1.25rem;
}

.email-sent h4 {
  color: #e1e6f5;
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
}

.email-sent p {
  color: #94a3b8;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #e1e6f5;
  font-size: 0.875rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #e1e6f5;
  transition: all 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: rgba(94, 155, 255, 0.5);
  box-shadow: 0 0 0 2px rgba(94, 155, 255, 0.1);
}

.form-group input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.error-message {
  font-size: 0.75rem;
  color: #ff6b6b;
  margin-top: 0.5rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.primary-btn {
  background: #5e9bff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn:hover:not(:disabled) {
  background: #4b8bff;
}

.primary-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.secondary-btn {
  background: rgba(94, 155, 255, 0.15);
  color: #5e9bff;
  border: 1px solid rgba(94, 155, 255, 0.3);
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.secondary-btn:hover:not(:disabled) {
  background: rgba(94, 155, 255, 0.25);
}

.secondary-btn:disabled {
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

.cancel-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.05);
  color: #e1e6f5;
}

.cancel-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style> 