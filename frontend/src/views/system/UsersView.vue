<template>
  <div class="users-container">
    <div class="page-header">
      <h1>用户管理</h1>
      <button class="add-user-btn" @click="openUserModal()">添加用户</button>
    </div>

    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>邮箱</th>
            <th>角色</th>
            <th>状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.role?.name || '无角色' }}</td>
            <td>
              <span class="status" :class="{'active': user.isActive, 'inactive': !user.isActive}">
                {{ user.isActive ? '激活' : '停用' }}
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
              <button 
                class="status-btn" 
                :title="user.isActive ? '停用' : '激活'" 
                @click="toggleUserStatus(user)"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                  <circle cx="8.5" cy="7" r="4"></circle>
                  <line x1="18" y1="8" x2="23" y2="13"></line>
                  <line x1="23" y1="8" x2="18" y2="13"></line>
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
              />
            </div>
            <div class="form-group">
              <label for="email">邮箱</label>
              <input 
                id="email" 
                type="email"
                v-model="currentUser.email" 
                placeholder="请输入邮箱地址" 
                required
              />
            </div>
            <div class="form-group" v-if="!isEditing">
              <label for="password">密码</label>
              <input 
                id="password" 
                type="password"
                v-model="currentUser.password" 
                placeholder="请输入密码" 
                :required="!isEditing"
              />
            </div>
            <div class="form-group">
              <label for="role">角色</label>
              <select id="role" v-model="currentUser.roleId">
                <option value="">无角色</option>
                <option v-for="role in roles" :key="role.id" :value="role.id">{{ role.name }}</option>
              </select>
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
    
    <!-- 操作结果提示 -->
    <div v-if="notification.show" class="notification" :class="notification.type">
      {{ notification.message }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'

// 定义类型接口
interface Role {
  id: number
  name: string
  description: string
}

interface User {
  id: number
  username: string
  email: string
  password?: string
  roleId?: number
  role?: Role
  isActive: boolean
  createdAt: string
}

// 模拟角色数据
const roles = ref<Role[]>([
  { id: 1, name: '管理员', description: '系统管理员，拥有所有权限' },
  { id: 2, name: '运营', description: '运营人员，负责内容管理' },
  { id: 3, name: '用户', description: '普通用户，仅有基本访问权限' }
])

// 模拟用户数据
const users = ref<User[]>([
  {
    id: 1,
    username: 'admin',
    email: 'admin@example.com',
    roleId: 1,
    role: roles.value[0],
    isActive: true,
    createdAt: '2023-06-10T08:30:00Z'
  },
  {
    id: 2,
    username: 'operator',
    email: 'operator@example.com',
    roleId: 2,
    role: roles.value[1],
    isActive: true,
    createdAt: '2023-06-12T10:20:00Z'
  },
  {
    id: 3,
    username: 'user1',
    email: 'user1@example.com',
    roleId: 3,
    role: roles.value[2],
    isActive: false,
    createdAt: '2023-06-15T14:45:00Z'
  }
])

// 弹窗状态
const showUserModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)

// 当前操作的用户
const currentUser = ref<User>({
  id: 0,
  username: '',
  email: '',
  password: '',
  roleId: undefined,
  isActive: true,
  createdAt: new Date().toISOString()
})

// 消息通知
const notification = reactive({
  show: false,
  message: '',
  type: 'success',
  timeout: null as number | null
})

// 显示通知消息
function showNotification(message: string, type: 'success' | 'error' = 'success') {
  if (notification.timeout) {
    clearTimeout(notification.timeout)
  }
  
  notification.message = message
  notification.type = type
  notification.show = true
  
  // 3秒后自动关闭
  notification.timeout = setTimeout(() => {
    notification.show = false
  }, 3000) as unknown as number
}

// 打开用户编辑/添加弹窗
function openUserModal(user?: User) {
  if (user) {
    // 编辑模式
    isEditing.value = true
    currentUser.value = { ...user }
    // 编辑模式不需要密码字段
    delete currentUser.value.password
  } else {
    // 添加模式
    isEditing.value = false
    currentUser.value = {
      id: 0,
      username: '',
      email: '',
      password: '',
      roleId: undefined,
      isActive: true,
      createdAt: new Date().toISOString()
    }
  }
  showUserModal.value = true
}

// 关闭用户编辑/添加弹窗
function closeUserModal() {
  showUserModal.value = false
}

// 保存用户信息
function saveUser() {
  if (isEditing.value) {
    // 更新现有用户
    const index = users.value.findIndex(u => u.id === currentUser.value.id)
    if (index !== -1) {
      // 更新角色信息
      if (currentUser.value.roleId) {
        currentUser.value.role = roles.value.find(r => r.id === currentUser.value.roleId)
      } else {
        currentUser.value.role = undefined
      }
      users.value[index] = { ...currentUser.value }
      showNotification('用户更新成功')
    }
  } else {
    // 添加新用户
    const newId = users.value.length > 0 ? Math.max(...users.value.map(u => u.id)) + 1 : 1
    const newUser: User = {
      ...currentUser.value,
      id: newId
    }
    
    // 设置角色信息
    if (newUser.roleId) {
      newUser.role = roles.value.find(r => r.id === newUser.roleId)
    }
    
    users.value.push(newUser)
    showNotification('用户添加成功')
  }
  
  // 关闭弹窗
  closeUserModal()
}

// 确认删除用户
function confirmDelete(user: User) {
  currentUser.value = { ...user }
  showDeleteModal.value = true
}

// 关闭删除确认弹窗
function closeDeleteModal() {
  showDeleteModal.value = false
}

// 删除用户
function deleteUser() {
  const index = users.value.findIndex(u => u.id === currentUser.value.id)
  if (index !== -1) {
    users.value.splice(index, 1)
    showNotification('用户已删除')
  }
  closeDeleteModal()
}

// 切换用户状态（激活/停用）
function toggleUserStatus(user: User) {
  const index = users.value.findIndex(u => u.id === user.id)
  if (index !== -1) {
    users.value[index].isActive = !users.value[index].isActive
    showNotification(`用户状态已${users.value[index].isActive ? '激活' : '停用'}`)
  }
}

// 格式化日期
function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 组件挂载时，可以在这里调用API获取数据
onMounted(() => {
  // 这里可以添加API调用，获取用户数据和角色数据
  console.log('用户管理组件已挂载，准备获取数据')
})
</script>

<style scoped>
/* 用户管理页面样式 */
.users-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.add-user-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s;
}

.add-user-btn:hover {
  background-color: #3e8e41;
}

/* 表格样式 */
.users-table {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th, td {
  padding: 12px 15px;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background-color: #f5f5f5;
}

/* 状态标签 */
.status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.85rem;
}

.status.active {
  background-color: #e6f7e6;
  color: #2e7d32;
}

.status.inactive {
  background-color: #ffebee;
  color: #c62828;
}

/* 操作按钮 */
.actions {
  display: flex;
  gap: 8px;
}

.actions button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background-color: #e3f2fd;
  color: #1565c0;
}

.status-btn:hover {
  background-color: #fff8e1;
  color: #f57f17;
}

.delete-btn:hover {
  background-color: #ffebee;
  color: #c62828;
}

/* 弹窗样式 */
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
  z-index: 100;
}

.modal {
  background-color: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
}

.delete-modal {
  width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

input, select, textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: #4CAF50;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:hover {
  background-color: #3e8e41;
}

.cancel-btn {
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.delete-confirm-btn {
  background-color: #f44336;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.delete-confirm-btn:hover {
  background-color: #d32f2f;
}

.delete-message {
  font-size: 16px;
  margin-bottom: 10px;
}

/* 通知消息 */
.notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  border-radius: 4px;
  color: white;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease-out forwards;
}

.notification.success {
  background-color: #4CAF50;
}

.notification.error {
  background-color: #f44336;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style> 