<template>
  <div class="roles-container">
    <div class="page-header">
      <h1>角色管理</h1>
      <button class="add-role-btn">添加角色</button>
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
              <button class="edit-btn" title="编辑">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button class="permissions-btn" title="管理权限">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Role {
  id: number
  name: string
  description: string
  createdAt: string
}

// 模拟角色数据
const roles = ref<Role[]>([
  {
    id: 1,
    name: '管理员',
    description: '系统管理员，拥有所有权限',
    createdAt: '2023-06-15T10:30:00Z'
  },
  {
    id: 2,
    name: '运营',
    description: '运营人员，负责内容管理',
    createdAt: '2023-06-16T14:20:00Z'
  },
  {
    id: 3,
    name: '客服',
    description: '客服人员，负责用户咨询',
    createdAt: '2023-06-17T09:15:00Z'
  },
  {
    id: 4,
    name: '普通用户',
    description: '普通用户，基础功能权限',
    createdAt: '2023-06-18T16:45:00Z'
  }
])

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
</style> 