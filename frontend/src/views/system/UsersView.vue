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
          <tr v-if="loading">
            <td colspan="7" class="loading-row">加载中...</td>
          </tr>
          <tr v-if="!loading && users.length === 0">
            <td colspan="7" class="empty-row">暂无用户数据</td>
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
              <button type="submit" class="save-btn" :disabled="submitting">{{ submitting ? '保存中...' : '保存' }}</button>
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
            <button type="button" class="delete-confirm-btn" @click="deleteUserConfirm" :disabled="submitting">
              {{ submitting ? '删除中...' : '删除' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'vue-toastification'
import ApiService from '@/services/api'
import type { UserListItem, RoleItem } from '@/services/api'

// 创建API服务实例
const api = new ApiService()
// 创建toast实例
const toast = useToast()

// 定义角色类型接口
interface Role extends RoleItem {}

// 状态变量
const users = ref<UserListItem[]>([])
const roles = ref<Role[]>([])
const loading = ref(false)
const submitting = ref(false)
const showUserModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)

// 当前操作的用户
const currentUser = ref<UserListItem>({
  id: 0,
  username: '',
  email: '',
  password: '',
  roleId: undefined,
  isActive: true,
  createdAt: new Date().toISOString()
} as UserListItem)

// 显示通知消息
function showNotification(message: string, type: 'success' | 'error' = 'success') {
  if (type === 'success') {
    toast.success(message, {
      timeout: 3000
    })
  } else {
    toast.error(message, {
      timeout: 5000
    })
  }
}

// 获取用户列表
async function fetchUsers() {
  loading.value = true
  try {
    const response = await api.getUserList()
    console.log(response)
    if (response.code === 200 || response.code === 0) {
      users.value = response.data
    } else {
      showNotification(response.message || '获取用户列表失败', 'error')
    }
  } catch (error: any) {
    console.error('获取用户列表失败:', error)
    showNotification('获取用户列表失败: ' + error.message, 'error')
  } finally {
    loading.value = false
  }
}

// 获取角色列表
async function fetchRoles() {
  try {
    const response = await api.getRoleList()
    if (response.code === 200 || response.code === 0) {
      roles.value = response.data
    } else {
      showNotification(response.message || '获取角色列表失败', 'error')
    }
  } catch (error: any) {
    console.error('获取角色列表失败:', error)
    showNotification('获取角色列表失败: ' + error.message, 'error')
  }
}

// 打开用户编辑/添加弹窗
function openUserModal(user?: UserListItem) {
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
    } as UserListItem
  }
  showUserModal.value = true
}

// 关闭用户编辑/添加弹窗
function closeUserModal() {
  showUserModal.value = false
}

// 保存用户信息
async function saveUser() {
  submitting.value = true
  try {
    let response
    
    if (isEditing.value) {
      // 更新现有用户
      response = await api.updateUser(currentUser.value.id, {
        username: currentUser.value.username,
        email: currentUser.value.email,
        roleId: currentUser.value.roleId,
        isActive: currentUser.value.isActive
      })
      
      if (response.code === 200 || response.code === 0) {
        showNotification('用户更新成功')
      } else {
        showNotification(response.message || '用户更新失败', 'error')
        submitting.value = false
        return
      }
    } else {
      // 添加新用户
      response = await api.createUser(currentUser.value)
      
      if (response.code === 200 || response.code === 0) {
        showNotification('用户添加成功')
      } else {
        showNotification(response.message || '用户添加失败', 'error')
        submitting.value = false
        return
      }
    }
    
    // 重新获取用户列表
    await fetchUsers()
    // 关闭弹窗
    closeUserModal()
  } catch (error: any) {
    console.error('保存用户失败:', error)
    showNotification('保存用户失败: ' + error.message, 'error')
  } finally {
    submitting.value = false
  }
}

// 确认删除用户
function confirmDelete(user: UserListItem) {
  currentUser.value = { ...user }
  showDeleteModal.value = true
}

// 关闭删除确认弹窗
function closeDeleteModal() {
  showDeleteModal.value = false
}

// 删除用户
async function deleteUserConfirm() {
  submitting.value = true
  try {
    const response = await api.deleteUser(currentUser.value.id)
    
    if (response.code === 200 || response.code === 0) {
      showNotification('用户已删除')
      // 重新获取用户列表
      await fetchUsers()
      closeDeleteModal()
    } else {
      showNotification(response.message || '删除用户失败', 'error')
    }
  } catch (error: any) {
    console.error('删除用户失败:', error)
    showNotification('删除用户失败: ' + error.message, 'error')
  } finally {
    submitting.value = false
  }
}

// 切换用户状态（激活/停用）
async function toggleUserStatus(user: UserListItem) {
  try {
    const response = await api.updateUserStatus(user.id, !user.isActive)
    
    if (response.code === 200 || response.code === 0) {
      // 更新本地状态
      user.isActive = !user.isActive
      showNotification(`用户状态已${user.isActive ? '激活' : '停用'}`)
    } else {
      showNotification(response.message || '更新用户状态失败', 'error')
    }
  } catch (error: any) {
    console.error('更新用户状态失败:', error)
    showNotification('更新用户状态失败: ' + error.message, 'error')
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

// 组件挂载时获取数据
onMounted(async () => {
  await Promise.all([fetchUsers(), fetchRoles()])
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

.loading-row, .empty-row {
  text-align: center;
  padding: 20px;
  color: #666;
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

.save-btn:hover:not(:disabled) {
  background-color: #3e8e41;
}

.save-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
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

.delete-confirm-btn:hover:not(:disabled) {
  background-color: #d32f2f;
}

.delete-confirm-btn:disabled {
  background-color: #ffcccc;
  cursor: not-allowed;
}

.delete-message {
  font-size: 16px;
  margin-bottom: 10px;
}
</style> 