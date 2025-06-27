好的，我明白了。我将把用户管理组件的完整代码直接输出到对话框中，而不是立即写入到文件。这样您可以先查看代码，然后决定是否要创建文件。

以下是我计划用于UsersView.vue的完整代码：

```vue
<template>
  <div class="users-container">
    <div class="page-header">
      <h1>用户管理</h1>
      <div class="header-actions">
        <div class="search-box">
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="搜索用户..." 
            @input="handleSearch"
          />
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
        </div>
        <button class="add-user-btn" @click="openUserModal()">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          添加用户
        </button>
      </div>
    </div>

    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>昵称</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>状态</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.nickname || '-' }}</td>
            <td>{{ user.email || '-' }}</td>
            <td>
              <span class="role-badge" :class="getRoleBadgeClass(user.role)">
                {{ getRoleName(user.role) }}
              </span>
            </td>
            <td>
              <span class="status-badge" :class="{ 'active': user.isActive, 'inactive': !user.isActive }">
                {{ user.isActive ? '启用' : '禁用' }}
              </span>
            </td>
            <td>{{ formatDate(user.createdAt) }}</td>
            <td class="actions">
              <button class="edit-btn" title="编辑" @click="openUserModal(user)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button class="reset-pwd-btn" title="重置密码" @click="confirmResetPassword(user)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
              </button>
              <button 
                class="toggle-status-btn" 
                :title="user.isActive ? '禁用用户' : '启用用户'"
                @click="toggleUserStatus(user)"
              >
                <svg v-if="user.isActive" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18.36 6.64a9 9 0 1 1-12.73 0"></path>
                  <line x1="12" y1="2" x2="12" y2="12"></line>
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M5.64 5.64a9 9 0 1 0 12.73 0"></path>
                  <line x1="12" y1="2" x2="12" y2="12"></line>
                </svg>
              </button>
              <button class="delete-btn" title="删除" @click="confirmDelete(user)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </td>
          </tr>
          <tr v-if="filteredUsers.length === 0">
            <td colspan="8" class="no-data">暂无用户数据</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- 用户编辑/添加弹窗 -->
    <div class="modal-overlay" v-if="showUserModal" @click.self="closeUserModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ isEditing ? '编辑用户' : '添加用户' }}</h2>
          <button class="close-btn" @click="closeUserModal">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveUser">
            <div class="form-group">
              <label for="username">用户名</label>
              <input 
                id="username" 
                v-model="currentUser.username" 
                placeholder="请输入用户名" 
                required
                :disabled="isEditing"
              />
              <div class="form-hint" v-if="isEditing">用户名创建后不可修改</div>
            </div>
            
            <div class="form-group" v-if="!isEditing">
              <label for="password">密码</label>
              <div class="password-input">
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  id="password" 
                  v-model="currentUser.password" 
                  placeholder="请输入密码" 
                  required
                />
                <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                  <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
              <label for="nickname">昵称</label>
              <input 
                id="nickname" 
                v-model="currentUser.nickname" 
                placeholder="请输入昵称" 
              />
            </div>
            
            <div class="form-group">
              <label for="email">邮箱</label>
              <input 
                type="email" 
                id="email" 
                v-model="currentUser.email" 
                placeholder="请输入邮箱" 
              />
            </div>
            
            <div class="form-group">
              <label for="role">角色</label>
              <select id="role" v-model="currentUser.role" required>
                <option value="">请选择角色</option>
                <option v-for="role in roles" :key="role.id" :value="role.code">
                  {{ role.name }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="status">状态</label>
              <div class="toggle-switch">
                <input 
                  type="checkbox" 
                  id="status" 
                  v-model="currentUser.isActive"
                />
                <label for="status"></label>
                <span>{{ currentUser.isActive ? '启用' : '禁用' }}</span>
              </div>
            </div>
            
            <div class="modal-footer">
              <button type="button" class="cancel-btn" @click="closeUserModal">取消</button>
              <button type="submit" class="save-btn">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 删除确认弹窗 -->
    <div class="modal-overlay" v-if="showDeleteModal" @click.self="closeDeleteModal">
      <div class="modal delete-modal">
        <div class="modal-header">
          <h2>确认删除</h2>
          <button class="close-btn" @click="closeDeleteModal">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="delete-message">确定要删除用户 <strong>{{ currentUser.username }}</strong> 吗？此操作不可撤销。</p>
          <div class="modal-footer">
            <button type="button" class="cancel-btn" @click="closeDeleteModal">取消</button>
            <button type="button" class="delete-confirm-btn" @click="deleteUser">删除</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 重置密码确认弹窗 -->
    <div class="modal-overlay" v-if="showResetPasswordModal" @click.self="closeResetPasswordModal">
      <div class="modal reset-password-modal">
        <div class="modal-header">
          <h2>重置密码</h2>
          <button class="close-btn" @click="closeResetPasswordModal">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="reset-message">确定要重置用户 <strong>{{ currentUser.username }}</strong> 的密码吗？</p>
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
          </div>
          <div class="modal-footer">
            <button type="button" class="cancel-btn" @click="closeResetPasswordModal">取消</button>
            <button type="button" class="reset-confirm-btn" @click="resetPassword">重置密码</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 操作结果提示 -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'

// 定义类型接口
interface User {
  id: number
  username: string
  password?: string
  nickname?: string
  email?: string
  role: string
  isActive: boolean
  createdAt: string
}

interface Role {
  id: number
  code: string
  name: string
}

// 模拟用户数据
const users = ref<User[]>([
  {
    id: 1,
    username: 'admin',
    nickname: '系统管理员',
    email: 'admin@example.com',
    role: 'admin',
    isActive: true,
    createdAt: '2023-05-10T08:30:00Z'
  },
  {
    id: 2,
    username: 'zhangsan',
    nickname: '张三',
    email: 'zhangsan@example.com',
    role: 'operator',
    isActive: true,
    createdAt: '2023-06-15T10:45:00Z'
  },
  {
    id: 3,
    username: 'lisi',
    nickname: '李四',
    email: 'lisi@example.com',
    role: 'user',
    isActive: false,
    createdAt: '2023-07-20T14:20:00Z'
  },
  {
    id: 4,
    username: 'wangwu',
    nickname: '王五',
    email: 'wangwu@example.com',
    role: 'user',
    isActive: true,
    createdAt: '2023-08-05T09:15:00Z'
  }
])

// 模拟角色数据
const roles = ref<Role[]>([
  { id: 1, code: 'admin', name: '管理员' },
  { id: 2, code: 'operator', name: '运营人员' },
  { id: 3, code: 'user', name: '普通用户' }
])

// 搜索查询
const searchQuery = ref('')

// 弹窗状态
const showUserModal = ref(false)
const showDeleteModal = ref(false)
const showResetPasswordModal = ref(false)
const isEditing = ref(false)
const showPassword = ref(false)
const showNewPassword = ref(false)

// 当前操作的用户
const currentUser = reactive<User>({
  id: 0,
  username: '',
  password: '',
  nickname: '',
  email: '',
  role: '',
  isActive: true,
  createdAt: ''
})

// 新密码（用于重置密码）
const newPassword = ref('')

// 通知提示
const notification = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

// 过滤用户列表
const filteredUsers = computed(() => {
  if (!searchQuery.value) {
    return users.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(query) ||
    (user.nickname && user.nickname.toLowerCase().includes(query)) ||
    (user.email && user.email.toLowerCase().includes(query))
  )
})

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取角色名称
const getRoleName = (roleCode: string): string => {
  const role = roles.value.find(r => r.code === roleCode)
  return role ? role.name : roleCode
}

// 获取角色徽章样式
const getRoleBadgeClass = (roleCode: string): string => {
  switch (roleCode) {
    case 'admin':
      return 'admin'
    case 'operator':
      return 'operator'
    default:
      return 'user'
  }
}

// 打开用户弹窗（添加/编辑）
const openUserModal = (user?: User) => {
  if (user) {
    // 编辑模式
    isEditing.value = true
    Object.assign(currentUser, user)
  } else {
    // 添加模式
    isEditing.value = false
    Object.assign(currentUser, {
      id: 0,
      username: '',
      password: '',
      nickname: '',
      email: '',
      role: '',
      isActive: true,
      createdAt: ''
    })
  }
  showUserModal.value = true
}

// 关闭用户弹窗
const closeUserModal = () => {
  showUserModal.value = false
}

// 保存用户
const saveUser = () => {
  // 表单验证
  if (!currentUser.username.trim()) {
    showNotification('用户名不能为空', 'error')
    return
  }
  
  if (!isEditing.value && !currentUser.password) {
    showNotification('密码不能为空', 'error')
    return
  }
  
  if (!currentUser.role) {
    showNotification('请选择用户角色', 'error')
    return
  }

  if (isEditing.value) {
    // 编辑现有用户
    const index = users.value.findIndex(u => u.id === currentUser.id)
    if (index !== -1) {
      // 创建一个新对象以避免直接修改原对象
      const updatedUser = { ...users.value[index] }
      updatedUser.nickname = currentUser.nickname
      updatedUser.email = currentUser.email
      updatedUser.role = currentUser.role
      updatedUser.isActive = currentUser.isActive
      
      users.value[index] = updatedUser
    }
    showNotification('用户信息已更新', 'success')
  } else {
    // 添加新用户
    // 检查用户名是否已存在
    if (users.value.some(u => u.username === currentUser.username)) {
      showNotification('用户名已存在', 'error')
      return
    }
    
    const newId = Math.max(0, ...users.value.map(u => u.id)) + 1
    const newUser: User = {
      id: newId,
      username: currentUser.username,
      nickname: currentUser.nickname,
      email: currentUser.email,
      role: currentUser.role,
      isActive: currentUser.isActive,
      createdAt: new Date().toISOString()
    }
    users.value.push(newUser)
    showNotification('用户已添加', 'success')
  }
  
  closeUserModal()
}

// 确认删除用户
const confirmDelete = (user: User) => {
  Object.assign(currentUser, user)
  showDeleteModal.value = true
}

// 关闭删除确认弹窗
const closeDeleteModal = () => {
  showDeleteModal.value = false
}

// 删除用户
const deleteUser = () => {
  // 特殊处理：不允许删除admin用户
  if (currentUser.username === 'admin') {
    showNotification('不能删除系统管理员账号', 'error')
    closeDeleteModal()
    return
  }
  
  const index = users.value.findIndex(u => u.id === currentUser.id)
  if (index !== -1) {
    users.value.splice(index, 1)
    showNotification('用户已删除', 'success')
  }
  closeDeleteModal()
}

// 切换用户状态
const toggleUserStatus = (user: User) => {
  // 特殊处理：不允许禁用admin用户
  if (user.username === 'admin' && user.isActive) {
    showNotification('不能禁用系统管理员账号', 'error')
    return
  }
  
  const index = users.value.findIndex(u => u.id === user.id)
  if (index !== -1) {
    users.value[index].isActive = !users.value[index].isActive
    showNotification(
      `用户 ${user.username} 已${users.value[index].isActive ? '启用' : '禁用'}`,
      'success'
    )
  }
}

// 确认重置密码
const confirmResetPassword = (user: User) => {
  Object.assign(currentUser, user)
  newPassword.value = ''
  showResetPasswordModal.value = true
}

// 关闭重置密码弹窗
const closeResetPasswordModal = () => {
  showResetPasswordModal.value = false
}

// 重置密码
const resetPassword = () => {
  if (!newPassword.value.trim()) {
    showNotification('新密码不能为空', 'error')
    return
  }
  
  // 在实际应用中，这里会调用API重置用户密码
  showNotification(`用户 ${currentUser.username} 的密码已重置`, 'success')
  closeResetPasswordModal()
}

// 处理搜索
const handleSearch = () => {
  // 实时搜索，无需额外处理，依赖计算属性filteredUsers
}

// 显示通知
const showNotification = (message: string, type: 'success' | 'error') => {
  notification.message = message
  notification.type = type
  notification.show = true
  
  // 自动隐藏通知
  setTimeout(() => {
    notification.show = false
  }, 3000)
}
</script>

<style scoped>
.users-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  font-size: 1.75rem;
  color: #1a2233;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #4f74e3;
  box-shadow: 0 0 0 3px rgba(79, 116, 227, 0.1);
}

.search-box svg {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.add-user-btn {
  background: linear-gradient(90deg, #4f74e3 0%, #5e60ce 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px rgba(79, 116, 227, 0.2);
}

.add-user-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(79, 116, 227, 0.3);
}

.users-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eef2f6;
}

th {
  background-color: #f8fafc;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 1px;
}
</style>