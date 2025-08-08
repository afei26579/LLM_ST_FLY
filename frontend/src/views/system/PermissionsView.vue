<template>
  <div class="permissions-container">
    <div class="page-header">
      <h1>权限管理</h1>
      <button class="add-permission-btn">添加权限</button>
    </div>

    <div class="permissions-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>权限代码</th>
            <th>权限名称</th>
            <th>描述</th>
            <th>模块</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="permission in permissions" :key="permission.id">
            <td>{{ permission.id }}</td>
            <td>{{ permission.code }}</td>
            <td>{{ permission.name }}</td>
            <td>{{ permission.description }}</td>
            <td><span class="module-badge">{{ permission.module }}</span></td>
            <td class="actions">
              <button class="edit-btn" title="编辑">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button class="delete-btn" title="删除">
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
    
    <div class="permission-group-section">
      <h2>权限分配</h2>
      <div class="role-permission-grid">
        <div class="role-list">
          <div class="role-item" v-for="(role, index) in roles" :key="index" 
               :class="{ active: selectedRoleIndex === index }"
               @click="selectRole(index)">
            <span class="role-name">{{ role.name }}</span>
          </div>
        </div>
        
        <div class="permission-assignment">
          <h3>{{ roles[selectedRoleIndex]?.name }} 的权限分配</h3>
          
          <div class="permission-modules">
            <div class="module-section" v-for="(group, module) in groupedPermissions" :key="module">
              <div class="module-header">
                <h4>{{ module }}</h4>
                <label class="select-all">
                  <input type="checkbox" :checked="isModuleSelected(module)" @change="toggleModule(module)">
                  全选
                </label>
              </div>
              
              <div class="permission-checklist">
                <div class="permission-checkbox" v-for="perm in group" :key="perm.id">
                  <label>
                    <input 
                      type="checkbox" 
                      :value="perm.id"
                      v-model="rolePermissions[selectedRoleIndex]"
                    >
                    {{ perm.name }}
                    <span class="permission-desc">{{ perm.description }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          <div class="actions-footer">
            <button class="save-btn">保存权限设置</button>
            <button class="cancel-btn">取消</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Permission {
  id: number
  code: string
  name: string
  description: string
  module: string
}

interface Role {
  id: number
  name: string
}

// 模拟权限数据
const permissions = ref<Permission[]>([
  {
    id: 1,
    code: 'user:view',
    name: '查看用户',
    description: '允许查看用户列表和详情',
    module: '用户管理'
  },
  {
    id: 2,
    code: 'user:create',
    name: '创建用户',
    description: '允许创建新用户',
    module: '用户管理'
  },
  {
    id: 3,
    code: 'user:edit',
    name: '编辑用户',
    description: '允许编辑用户信息',
    module: '用户管理'
  },
  {
    id: 4,
    code: 'user:delete',
    name: '删除用户',
    description: '允许删除用户',
    module: '用户管理'
  },
  {
    id: 5,
    code: 'role:view',
    name: '查看角色',
    description: '允许查看角色列表和详情',
    module: '角色管理'
  },
  {
    id: 6,
    code: 'role:create',
    name: '创建角色',
    description: '允许创建新角色',
    module: '角色管理'
  },
  {
    id: 7,
    code: 'role:edit',
    name: '编辑角色',
    description: '允许编辑角色信息',
    module: '角色管理'
  },
  {
    id: 8,
    code: 'role:delete',
    name: '删除角色',
    description: '允许删除角色',
    module: '角色管理'
  },
  {
    id: 9,
    code: 'system:config',
    name: '系统配置',
    description: '允许修改系统配置',
    module: '系统设置'
  },
  {
    id: 10,
    code: 'system:log',
    name: '查看日志',
    description: '允许查看系统日志',
    module: '系统设置'
  }
])

// 模拟角色数据
const roles = ref<Role[]>([
  { id: 1, name: '管理员' },
  { id: 2, name: '运营' },
  { id: 3, name: '客服' },
  { id: 4, name: '普通用户' }
])

// 当前选择的角色索引
const selectedRoleIndex = ref(0)

// 记录每个角色拥有的权限 ID
const rolePermissions = ref<number[][]>([
  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], // 管理员拥有所有权限
  [1, 3, 5, 9],                     // 运营
  [1, 5],                           // 客服
  [1]                               // 普通用户
])

// 按模块分组权限
const groupedPermissions = computed(() => {
  const grouped: Record<string, Permission[]> = {}
  permissions.value.forEach(permission => {
    if (!grouped[permission.module]) {
      grouped[permission.module] = []
    }
    grouped[permission.module].push(permission)
  })
  return grouped
})

// 选择角色
const selectRole = (index: number) => {
  selectedRoleIndex.value = index
}

// 检查模块是否被全选
const isModuleSelected = (module: string) => {
  const modulePermIds = permissions.value
    .filter(p => p.module === module)
    .map(p => p.id)
  
  return modulePermIds.every(id => rolePermissions.value[selectedRoleIndex.value].includes(id))
}

// 切换模块所有权限
const toggleModule = (module: string) => {
  const modulePermIds = permissions.value
    .filter(p => p.module === module)
    .map(p => p.id)
  
  const isAllSelected = isModuleSelected(module)
  
  if (isAllSelected) {
    // 取消选择所有此模块权限
    rolePermissions.value[selectedRoleIndex.value] = rolePermissions.value[selectedRoleIndex.value]
      .filter(id => !modulePermIds.includes(id))
  } else {
    // 选择所有此模块权限
    const newPerms = [...rolePermissions.value[selectedRoleIndex.value]]
    modulePermIds.forEach(id => {
      if (!newPerms.includes(id)) {
        newPerms.push(id)
      }
    })
    rolePermissions.value[selectedRoleIndex.value] = newPerms
  }
}
</script>

<style scoped>
.permissions-container {
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

h1, h2 {
  font-size: 1.75rem;
  color: #1a2233;
  font-weight: 600;
}

h2 {
  font-size: 1.5rem;
  margin: 2rem 0 1.5rem;
}

h3 {
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

h4 {
  font-size: 1rem;
  margin: 0;
}

.add-permission-btn {
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

.add-permission-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(79, 116, 227, 0.3);
}

.permissions-table {
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

.module-badge {
  display: inline-block;
  background-color: #e8f5e9;
  color: #388e3c;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.edit-btn, .delete-btn {
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

.delete-btn:hover {
  background-color: #feeceb;
  color: #ea4335;
}

/* 角色权限分配部分 */
.permission-group-section {
  margin-top: 3rem;
}

.role-permission-grid {
  display: flex;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.role-list {
  width: 200px;
  border-right: 1px solid #eef2f6;
  background-color: #f8fafc;
}

.role-item {
  padding: 1rem;
  cursor: pointer;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}

.role-item:hover {
  background-color: #f1f5f9;
}

.role-item.active {
  background-color: #f1f5f9;
  border-left-color: #4f74e3;
  font-weight: 500;
}

.permission-assignment {
  flex: 1;
  padding: 1.5rem;
}

.permission-modules {
  max-height: 500px;
  overflow-y: auto;
}

.module-section {
  margin-bottom: 1.5rem;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eef2f6;
  margin-bottom: 1rem;
}

.select-all {
  display: flex;
  align-items: center;
  font-size: 0.85rem;
  cursor: pointer;
}

.select-all input {
  margin-right: 0.5rem;
}

.permission-checklist {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.permission-checkbox label {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
}

.permission-checkbox input {
  margin-right: 0.5rem;
  margin-top: 0.25rem;
}

.permission-desc {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.25rem;
  margin-left: 1.5rem;
}

.actions-footer {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.save-btn, .cancel-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
}

.save-btn {
  background: linear-gradient(90deg, #4f74e3 0%, #5e60ce 100%);
  color: white;
  border: none;
  box-shadow: 0 4px 6px rgba(79, 116, 227, 0.2);
}

.cancel-btn {
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #64748b;
}

.save-btn:hover {
  box-shadow: 0 6px 10px rgba(79, 116, 227, 0.3);
}
</style> 