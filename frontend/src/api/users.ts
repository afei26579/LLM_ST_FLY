import request from '@/utils/request'

// 用户接口类型定义
export interface UserData {
  id: number
  username: string
  email: string
  password?: string
  roleId?: number
  role?: {
    id: number
    name: string
    description?: string
  }
  isActive: boolean
  createdAt: string
}

// 获取用户列表
export function getUserList() {
  return request({
    url: '/auth/users/',
    method: 'get'
  })
}

// 获取用户详情
export function getUserDetail(id: number) {
  return request({
    url: `/auth/users/${id}/`,
    method: 'get'
  })
}

// 创建用户
export function createUser(data: Partial<UserData>) {
  return request({
    url: '/auth/users/',
    method: 'post',
    data
  })
}

// 更新用户信息
export function updateUser(id: number, data: Partial<UserData>) {
  return request({
    url: `/auth/users/${id}/`,
    method: 'put',
    data
  })
}

// 删除用户
export function deleteUser(id: number) {
  return request({
    url: `/auth/users/${id}/`,
    method: 'delete'
  })
}

// 更新用户状态
export function updateUserStatus(id: number, isActive: boolean) {
  return request({
    url: `/auth/users/${id}/status/`,
    method: 'patch',
    data: { isActive }
  })
}

// 获取角色列表
export function getRoleList() {
  return request({
    url: '/auth/roles/',
    method: 'get'
  })
} 