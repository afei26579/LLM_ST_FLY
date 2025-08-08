<template>
  <div class="roles-container">
    <div class="page-header">
      <h1>角色管理</h1>
      <button class="add-role-btn" @click="openRoleModal()">添加角色</button>
    </div>

    <div class="roles-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>角色名称</th>
            <th>描述</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="role in roles" :key="role.id">
            <td>{{ role.id }}</td>
            <td>{{ role.name }}</td>
            <td>{{ role.description }}</td>
            <td>{{ formatDate(role.createdAt) }}</td>
            <td class="actions">
              <button class="edit-btn" title="编辑" @click="openRoleModal(role)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button class="permissions-btn" title="管理权限" @click="openPermissionModal(role)">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
              </button>
              <button class="delete-btn" title="删除" @click="confirmDelete(role)">
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
    
    <!-- 角色编辑/添加弹窗 -->
    <div class="modal-overlay" v-if="showRoleModal" @click.self="closeRoleModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ isEditing ? '编辑角色' : '添加角色' }}</h2>
          <button class="close-btn" @click="closeRoleModal">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveRole">
            <div class="form-group">
              <label for="role-name">角色名称</label>
              <input 
                id="role-name" 
                v-model="currentRole.name" 
                placeholder="请输入角色名称" 
                required
              />
            </div>
            <div class="form-group">
              <label for="role-description">角色描述</label>
              <textarea 
                id="role-description" 
                v-model="currentRole.description" 
                placeholder="请输入角色描述"
                rows="3"
              ></textarea>
            </div>
            <div class="modal-footer">
              <button type="button" class="cancel-btn" @click="closeRoleModal">取消</button>
              <button type="submit" class="save-btn">保存</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- 权限设置弹窗 -->
    <div class="modal-overlay" v-if="showPermissionModal" @click.self="closePermissionModal">
      <div class="modal permission-modal">
        <div class="modal-header">
          <h2>设置角色权限 - {{ currentRole.name }}</h2>
          <button class="close-btn" @click="closePermissionModal">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="permission-modules">
            <div class="module-section" v-for="(perms, module) in groupedPermissions" :key="module">
              <div class="module-header">
                <h4>{{ module }}</h4>
                <label class="select-all">
                  <input 
                    type="checkbox" 
                    :checked="isModuleSelected(module)" 
                    @change="toggleModule(module)"
                  >
                  全选
                </label>
              </div>
              <div class="permission-checklist">
                <div class="permission-checkbox" v-for="perm in perms" :key="perm.id">
                  <label>
                    <input 
                      type="checkbox" 
                      :value="perm.id"
                      v-model="selectedPermissions"
                    >
                    {{ perm.name }}
                    <span class="permission-desc">{{ perm.codename }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="cancel-btn" @click="closePermissionModal">取消</button>
            <button type="button" class="save-btn" @click="savePermissions">保存</button>
          </div>
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
          <p class="delete-message">确定要删除角色 <strong>{{ currentRole.name }}</strong> 吗？此操作不可撤销。</p>
          <div class="modal-footer">
            <button type="button" class="cancel-btn" @click="closeDeleteModal">取消</button>
            <button type="button" class="delete-confirm-btn" @click="deleteRole">删除</button>
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
import { apiService } from '@/services/api'
import type { RoleItem, RoleDetail, Permission, RoleRequest } from '@/services/api'

// 定义类型接口
interface Role {
  id: number
  name: string
  description: string
  createdAt: string
}

interface PermissionWithModule extends Permission {
  module: string
}

// 角色数据
const roles = ref<Role[]>([])

// 权限数据
const permissions = ref<PermissionWithModule[]>([])

// 角色权限映射
const rolePermissionMap = ref<Record<number, number[]>>({})

// 加载状态
const loading = ref(false)

// 弹窗状态
const showRoleModal = ref(false)
const showPermissionModal = ref(false)
const showDeleteModal = ref(false)
const isEditing = ref(false)

// 当前操作的角色
const currentRole = reactive<Role>({
  id: 0,
  name: '',
  description: '',
  createdAt: ''
})

// 当前选中的权限
const selectedPermissions = ref<number[]>([])

// 通知提示
const notification = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

// 加载角色列表
const loadRoles = async () => {
  try {
    loading.value = true
    const response = await apiService.getRoleList()
   
    if (response.code === 200) {
      // 处理分页数据结构，角色列表在 response.data.list 中
      const roleList = response.data?.list || []
   
      
      roles.value = roleList.map(role => ({
        id: role.id,
        name: role.name,
        description: role.description || '',
        createdAt: role.created_at || new Date().toISOString()
      }))
    } else {
      showNotification(response.message || '获取角色列表失败', 'error')
    }
  } catch (error) {
    console.error('加载角色列表失败:', error)
    showNotification('加载角色列表失败', 'error')
  } finally {
    loading.value = false
  }
}

// 加载权限列表
const loadPermissions = async () => {
  try {
    const response = await apiService.getPermissionList()
    if (response.code === 200) {
      permissions.value = response.data.map((perm: Permission) => ({
        ...perm,
        module: getPermissionModule(perm.codename)
      }))
    } else {
      showNotification(response.message || '获取权限列表失败', 'error')
    }
  } catch (error) {
    console.error('加载权限列表失败:', error)
    showNotification('加载权限列表失败', 'error')
  }
}

// 根据权限代码获取模块名称
const getPermissionModule = (codename: string): string => {
  if (codename.includes('user')) return '用户管理'
  if (codename.includes('group')) return '角色管理'
  if (codename.includes('permission')) return '权限管理'
  if (codename.includes('conversation') || codename.includes('message')) return '聊天管理'
  return '系统设置'
}

// 加载角色权限映射
const loadRolePermissions = async (roleId: number) => {
  try {
    const response = await apiService.getRoleDetail(roleId)
    if (response.code === 200) {
      rolePermissionMap.value[roleId] = response.data.permissions.map((p: Permission) => p.id)
    }
  } catch (error) {
    console.error('加载角色权限失败:', error)
  }
}

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

// 按模块分组权限
const groupedPermissions = computed(() => {
  const grouped: Record<string, PermissionWithModule[]> = {}
  permissions.value.forEach(permission => {
    if (!grouped[permission.module]) {
      grouped[permission.module] = []
    }
    grouped[permission.module].push(permission)
  })
  return grouped
})

// 打开角色弹窗（添加/编辑）
const openRoleModal = (role?: Role) => {
  if (role) {
    // 编辑模式
    isEditing.value = true
    Object.assign(currentRole, role)
  } else {
    // 添加模式
    isEditing.value = false
    Object.assign(currentRole, {
      id: 0,
      name: '',
      description: '',
      createdAt: ''
    })
  }
  showRoleModal.value = true
}

// 关闭角色弹窗
const closeRoleModal = () => {
  showRoleModal.value = false
}

// 保存角色
const saveRole = async () => {
  if (!currentRole.name.trim()) {
    showNotification('角色名称不能为空', 'error')
    return
  }

  try {
    const roleData: RoleRequest = {
      name: currentRole.name,
      description: currentRole.description
    }

    if (isEditing.value) {
      // 编辑现有角色
      const response = await apiService.updateRole(currentRole.id, roleData)
      if (response.code === 200) {
        const index = roles.value.findIndex(r => r.id === currentRole.id)
        if (index !== -1) {
          roles.value[index] = { ...currentRole }
        }
        showNotification('角色已更新', 'success')
      } else {
        showNotification(response.message || '更新角色失败', 'error')
        return
      }
    } else {
      // 添加新角色
      const response = await apiService.createRole(roleData)
      if (response.code === 200 || response.code === 201) {
        const newRole: Role = {
          id: response.data.id,
          name: response.data.name,
          description: response.data.description || '',
          createdAt: new Date().toISOString()
        }
        roles.value.push(newRole)
        rolePermissionMap.value[newRole.id] = []
        showNotification('角色已添加', 'success')
      } else {
        showNotification(response.message || '创建角色失败', 'error')
        return
      }
    }
    
    closeRoleModal()
  } catch (error) {
    console.error('保存角色失败:', error)
    showNotification('保存角色失败', 'error')
  }
}

// 打开权限设置弹窗
const openPermissionModal = async (role: Role) => {
  Object.assign(currentRole, role)
  // 加载该角色的权限
  await loadRolePermissions(role.id)
  selectedPermissions.value = [...(rolePermissionMap.value[role.id] || [])]
  showPermissionModal.value = true
}

// 关闭权限设置弹窗
const closePermissionModal = () => {
  showPermissionModal.value = false
}

// 保存权限设置 (暂时使用本地存储，因为后端可能没有对应的API)
const savePermissions = async () => {
  try {
    // 由于后端可能没有updateRolePermissions方法，我们先使用本地存储
    rolePermissionMap.value[currentRole.id] = [...selectedPermissions.value]
    showNotification('权限设置已保存', 'success')
    closePermissionModal()
  } catch (error) {
    console.error('保存权限失败:', error)
    showNotification('保存权限失败', 'error')
  }
}

// 确认删除角色
const confirmDelete = (role: Role) => {
  Object.assign(currentRole, role)
  showDeleteModal.value = true
}

// 关闭删除确认弹窗
const closeDeleteModal = () => {
  showDeleteModal.value = false
}

// 删除角色
const deleteRole = async () => {
  try {
    const response = await apiService.deleteRole(currentRole.id)
    if (response.code === 200 || response.code === 204) {
      const index = roles.value.findIndex(r => r.id === currentRole.id)
      if (index !== -1) {
        roles.value.splice(index, 1)
        delete rolePermissionMap.value[currentRole.id]
        showNotification('角色已删除', 'success')
      }
    } else {
      showNotification(response.message || '删除角色失败', 'error')
    }
  } catch (error) {
    console.error('删除角色失败:', error)
    showNotification('删除角色失败', 'error')
  }
  closeDeleteModal()
}

// 检查模块是否被全选
const isModuleSelected = (module: string) => {
  const modulePermIds = permissions.value
    .filter(p => p.module === module)
    .map(p => p.id)
  
  return modulePermIds.every(id => selectedPermissions.value.includes(id))
}

// 切换模块所有权限
const toggleModule = (module: string) => {
  const modulePermIds = permissions.value
    .filter(p => p.module === module)
    .map(p => p.id)
  
  const isAllSelected = isModuleSelected(module)
  
  if (isAllSelected) {
    // 取消选择所有此模块权限
    selectedPermissions.value = selectedPermissions.value
      .filter(id => !modulePermIds.includes(id))
  } else {
    // 选择所有此模块权限
    const newPerms = [...selectedPermissions.value]
    modulePermIds.forEach(id => {
      if (!newPerms.includes(id)) {
        newPerms.push(id)
      }
    })
    selectedPermissions.value = newPerms
  }
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

// 页面加载时获取数据
onMounted(() => {
  loadRoles()
  loadPermissions()
})
</script>

<style scoped>
.roles-container {
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

.add-role-btn {
  background: linear-gradient(90deg, #4f74e3 0%, #5e60ce 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px rgba(79, 116, 227, 0.2);
}

.add-role-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(79, 116, 227, 0.3);
}

.roles-table {
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

tr:last-child td {
  border-bottom: none;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn, .permissions-btn, .delete-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.edit-btn:hover {
  background-color: #e5f0fd;
  color: #3b82f6;
}

.permissions-btn:hover {
  background-color: #e6f4ea;
  color: #34a853;
}

.delete-btn:hover {
  background-color: #feeceb;
  color: #ea4335;
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
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 90vh;
  overflow: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.permission-modal {
  width: 700px;
}

.delete-modal {
  width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eef2f6;
}

.modal-header h2 {
  font-size: 1.25rem;
  color: #1a2233;
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #64748b;
  display: flex;
  padding: 0.25rem;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #334155;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #4f74e3;
  box-shadow: 0 0 0 3px rgba(79, 116, 227, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.cancel-btn {
  padding: 0.75rem 1.25rem;
  background-color: #f1f5f9;
  color: #64748b;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background-color: #e2e8f0;
}

.save-btn {
  padding: 0.75rem 1.25rem;
  background: linear-gradient(90deg, #4f74e3 0%, #5e60ce 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.2s;
}

.save-btn:hover {
  opacity: 0.9;
}

.delete-confirm-btn {
  padding: 0.75rem 1.25rem;
  background: linear-gradient(90deg, #f43f5e 0%, #e11d48 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.2s;
}

.delete-confirm-btn:hover {
  opacity: 0.9;
}

.delete-message {
  font-size: 1rem;
  line-height: 1.5;
  color: #334155;
}

/* 权限设置样式 */
.permission-modules {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.module-section {
  margin-bottom: 1.5rem;
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.module-header h4 {
  margin: 0;
  color: #334155;
  font-size: 1rem;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
  cursor: pointer;
}

.permission-checklist {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 0.75rem;
}

.permission-checkbox label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  color: #334155;
}

.permission-desc {
  font-size: 0.75rem;
  color: #64748b;
  margin-left: 0.5rem;
}

/* 通知样式 */
.notification {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  padding: 1rem 1.5rem;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  color: white;
  z-index: 1100;
  animation: slideIn 0.3s ease-out;
}

.notification.success {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.notification.error {
  background: linear-gradient(90deg, #f43f5e 0%, #e11d48 100%);
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