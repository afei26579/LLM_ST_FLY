// API服务类：封装所有与后端API交互的方法
// 使用axios进行HTTP请求

import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// 聊天消息接口
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: Date;
  id?: number;
  tokens_used?: number;
}

// 对话接口
export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: ChatMessage[];
  message_count: number;
  last_message?: ChatMessage;
}

// 用户列表接口
export interface UserListItem {
  id: number;
  username: string;
  email: string;
  password?: string;
  roleId?: number;
  role?: {
    id: number;
    name: string;
    description?: string;
  };
  isActive: boolean;
  createdAt: string;
}

// 角色列表项接口
export interface RoleItem {
  id: number;
  name: string;
  description?: string;
}

// API基础配置
const API_CONFIG = {
  // 后端API的基础URL
  BASE_URL: 'http://localhost:8000/api/v1/',
  // 请求超时时间（毫秒）
  TIMEOUT: 15000,
}

// 标准API响应接口
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 登录请求参数接口
interface LoginRequest {
  username: string;
  password: string;
}

// 登录响应数据接口
interface LoginResponse {
  user: {
    id: number;
    username: string;
    email?: string;
    role: string;
    permissions?: string[];
    real_name?: string;
    nickname?: string;
    phone?: string;
    department?: string;
    bio?: string;
    avatar?: string;
    theme?: string;
    gender?: string;
    birthday?: string;
    country?: string;
    province?: string;
    city?: string;
    district?: string;
    address?: string;
    last_login_ip?: string;
    qq?: string;
  };
  token: {
    refresh: string;
    access: string;
  };
}

// 用户信息更新接口
export interface UserProfileUpdate {
  username: string;
  real_name?: string;
  nickname?: string;
  email?: string;
  phone?: string;
  department?: string;
  bio?: string;
  avatar?: string | File;
  theme?: string;
  gender?: string;
  birthday?: string;
  country?: string;
  province?: string;
  city?: string;
  district?: string;
  address?: string;
  qq?: string;
}

// 密码修改请求接口
export interface ChangePasswordRequest {
  oldPassword: string;
  newPassword: string;
}

// 手机号重置密码请求接口
export interface ResetPasswordPhoneRequest {
  phone: string;
  code: string;
  newPassword: string;
}

// 邮箱重置密码请求接口
export interface ResetPasswordEmailRequest {
  email: string;
  code: string;
  newPassword: string;
}

// 绑定手机号请求接口
export interface BindPhoneRequest {
  phone: string;
  code: string;
}

// 绑定邮箱请求接口
export interface BindEmailRequest {
  email: string;
}

// API服务类
class ApiService {
  private instance: AxiosInstance;
  
  constructor() {
    // 创建axios实例
    this.instance = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // 从localStorage中获取token
        const token = localStorage.getItem('token');
        
        // 如果存在token，则添加到请求头
        if (token && config.headers) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        
        return config;
      },
      (error: any) => {
        return Promise.reject(error);
      }
    );
    
    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error: any) => {
        // 处理响应错误
        if (error.response) {
          // 如果响应状态码为401（未授权），可能是token过期
          if (error.response.status === 401) {
            // 清除本地token
            localStorage.removeItem('token');
            // 可以在这里添加重定向到登录页的逻辑
          }
        }
        return Promise.reject(error);
      }
    );
  }
  
  // 登录API
  async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
    try {
      const response = await this.instance.post<ApiResponse<LoginResponse>>(
        'auth/login/',
        credentials
      );
      
      return response.data;
    } catch (error: any) {
      // 如果是API返回的错误
      if (error.response) {
        console.error('登录失败:', error.response.data);
        // 返回API的错误信息
        return {
          code: error.response.status,
          message: error.response.data.message || '登录失败，请检查用户名和密码',
          data: error.response.data
        };
      }
      // 如果是网络错误或其他错误
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: {} as LoginResponse
      };
    }
  }
  
  // 获取用户信息API
  async getUserInfo(): Promise<ApiResponse<LoginResponse['user']>> {
    try {
      const response = await this.instance.get<ApiResponse<LoginResponse['user']>>('auth/users/me/');
      return response.data;
    } catch (error: any) {
      console.error('获取用户信息失败:', error);
      throw error;
    }
  }
  
  // 修改密码API
  async changePassword(data: ChangePasswordRequest): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.post<ApiResponse<any>>('auth/users/change-password/', data);
      return response.data;
    } catch (error: any) {
      console.error('修改密码失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '修改密码失败',
          data: error.response.data
        };
      }
      throw error;
    }
  }

  // 发送手机验证码API
  async sendSmsCode(phone: string, purpose: string = 'binding'): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.post<ApiResponse<any>>('/auth/users/send-sms-code/', { 
        phone,
        purpose 
      });
      return response.data;
    } catch (error: any) {
      console.error('发送验证码失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '发送验证码失败',
          data: error.response.data
        };
      }
      throw error;
    }
  }

  // 发送邮箱验证码API
  async sendEmailCode(email: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.post<ApiResponse<any>>('users/send-email-code', { email });
      return response.data;
    } catch (error: any) {
      console.error('发送验证码失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '发送验证码失败',
          data: error.response.data
        };
      }
      throw error;
    }
  }

  // 通过手机重置密码API
  async resetPasswordPhone(data: ResetPasswordPhoneRequest): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.post<ApiResponse<any>>('auth/users/reset-password-phone/', data);
      return response.data;
    } catch (error: any) {
      console.error('重置密码失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '重置密码失败',
          data: error.response.data
        };
      }
      throw error;
    }
  }

  // 通过邮箱重置密码API
  async resetPasswordEmail(data: ResetPasswordEmailRequest): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.post<ApiResponse<any>>('auth/users/reset-password-email/', data);
      return response.data;
    } catch (error: any) {
      console.error('重置密码失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '重置密码失败',
          data: error.response.data
        };
      }
      throw error;
    }
  }
  
  // 调试API支持的方法
  async testApiMethods(): Promise<void> {
    const testEndpoint = 'auth/users/me/';
    
    try {
      console.log(`Testing GET method on ${testEndpoint}`);
      const getResponse = await this.instance.get(testEndpoint);
      console.log(`GET method succeeded:`, getResponse.data);
    } catch (error: any) {
      console.error(`GET method failed:`, error.response?.data || error.message);
    }
    
    try {
      console.log(`Testing POST method on ${testEndpoint}`);
      const postResponse = await this.instance.post(testEndpoint, { test: true });
      console.log(`POST method succeeded:`, postResponse.data);
    } catch (error: any) {
      console.error(`POST method failed:`, error.response?.data || error.message);
    }
    
    try {
      console.log(`Testing PUT method on ${testEndpoint}`);
      const putResponse = await this.instance.put(testEndpoint, { test: true });
      console.log(`PUT method succeeded:`, putResponse.data);
    } catch (error: any) {
      console.error(`PUT method failed:`, error.response?.data || error.message);
    }
    
    try {
      console.log(`Testing PATCH method on ${testEndpoint}`);
      const patchResponse = await this.instance.patch(testEndpoint, { test: true });
      console.log(`PATCH method succeeded:`, patchResponse.data);
    } catch (error: any) {
      console.error(`PATCH method failed:`, error.response?.data || error.message);
    }
  }
  
  // 更新用户信息API
  async updateUserProfile(profileData: UserProfileUpdate): Promise<ApiResponse<LoginResponse['user']>> {
    try {
      // 创建FormData对象用于提交数据
      const formData = new FormData();
      
      // 添加所有字段到FormData
      Object.keys(profileData).forEach(key => {
        const value = profileData[key as keyof UserProfileUpdate];
        if (value !== undefined && value !== null) {
          if (key === 'avatar') {
            // 处理头像字段 - 可能是File对象或字符串URL
            console.log(`处理头像字段: ${typeof value}`, value instanceof File ? '文件对象' : value);
            if (value instanceof File) {
              // 如果是File对象，直接添加
              formData.append(key, value);
            } else if (typeof value === 'string' && value.trim() !== '') {
              // 如果是非空字符串URL，则作为字符串添加
              formData.append(key, value);
            }
            // 如果是空字符串，则不添加此字段
          } else {
            // 其他字段正常添加
            formData.append(key, String(value));
          }
        }
      });
      
      // 使用FormData发送请求，统一使用multipart/form-data格式
      const response = await this.instance.put<ApiResponse<LoginResponse['user']>>('auth/users/me/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      console.error('更新用户信息失败:', error);
      throw error;
    }
  }
  
  // 上传用户头像API
  async uploadAvatar(file: File): Promise<ApiResponse<LoginResponse['user']>> {
    try {
      console.log(file, 'file~~~~~~~~~~~~')
      const formData = new FormData();
      formData.append('avatar', file);
      
      const response = await this.instance.post<ApiResponse<LoginResponse['user']>>('auth/users/me/avatar/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      console.error('上传头像失败:', error);
      throw error;
    }
  }

  // 绑定手机号API
  async bindPhone(data: BindPhoneRequest): Promise<ApiResponse<LoginResponse['user']>> {
    try {
      const response = await this.instance.post<ApiResponse<LoginResponse['user']>>(
        'auth/users/bind-phone/', 
        data
      );
      return response.data;
    } catch (error: any) {
      console.error('绑定手机号失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '绑定手机号失败',
          data: error.response.data
        };
      }
      throw error;
    }
  }
  
  // 发送邮箱绑定链接API
  async sendEmailBind(email: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.post<ApiResponse<any>>(
        'auth/users/send-email-bind/', 
        { email }
      );
      return response.data;
    } catch (error: any) {
      console.error('发送邮箱绑定链接失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '发送邮箱绑定链接失败',
          data: error.response.data
        };
      }
      throw error;
    }
  }
  
  // 验证邮箱绑定API
  async verifyEmailBind(token: string, email: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.get<ApiResponse<any>>(`auth/users/verify-email/?token=${token}&email=${email}`);
      return response.data;
    } catch (error: any) {
      console.error('验证邮箱失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '验证邮箱失败',
          data: error.response.data
        };
      }
      throw error;
    }
  }

  // 聊天完成API - 使用DashScope大模型
  async chatCompletion(messages: ChatMessage[], conversationId?: number): Promise<ApiResponse<any>> {
    try {
      console.log("发送聊天请求:", { messages, conversation_id: conversationId })
      const response = await this.instance.post<ApiResponse<any>>('chat/completion/', { 
        messages,
        conversation_id: conversationId,
        timeout: 60000
      });
      console.log("聊天请求原始响应:", response)
      
      // 后端已经返回标准格式 { code, message, data }，直接返回即可
      return response.data;
    } catch (error: any) {
      console.error('聊天请求失败:', error);
      
      // 详细记录错误信息
      if (error.response) {
        console.error('错误响应数据:', error.response.data);
        console.error('错误状态码:', error.response.status);
        
        return {
          code: error.response.status,
          message: error.response.data?.message || '聊天请求失败，服务器返回错误',
          data: {
            content: "抱歉，服务器处理请求时出错，请稍后再试。",
            conversation_id: conversationId
          }
        };
      }
      
      if (error.request) {
        console.error('请求已发送但未收到响应');
        return {
          code: 500,
          message: '聊天请求超时，未收到服务器响应',
          data: {
            content: "抱歉，服务器响应超时，请检查网络连接并稍后再试。",
            conversation_id: conversationId
          }
        };
      }
      
      return {
        code: 500,
        message: error.message || '网络错误，请检查网络连接',
        data: {
          content: "抱歉，发生网络错误，请检查网络连接并稍后再试。",
          conversation_id: conversationId
        }
      };
    }
  }

  // 获取对话列表
  async getConversations(): Promise<ApiResponse<Conversation[]>> {
    try {
      console.log("获取对话列表")
      const response = await this.instance.get<ApiResponse<Conversation[]>>('chat/conversations/');
      console.log("获取对话列表原始响应:", response)
      
      // 后端已经返回标准格式 { code, message, data }，直接返回即可
      return response.data;
    } catch (error: any) {
      console.error('获取对话列表失败:', error);
      
      if (error.response) {
        console.error('错误响应数据:', error.response.data);
        console.error('错误状态码:', error.response.status);
        
        return {
          code: error.response.status,
          message: error.response.data?.message || '获取对话列表失败，服务器返回错误',
          data: []
        };
      }
      
      if (error.request) {
        console.error('请求已发送但未收到响应');
        return {
          code: 500,
          message: '请求超时，未收到服务器响应',
          data: []
        };
      }
      
      return {
        code: 500,
        message: error.message || '网络错误，请检查网络连接',
        data: []
      };
    }
  }

  // 获取单个对话详情
  async getConversation(id: number): Promise<ApiResponse<Conversation>> {
    try {
      console.log("获取对话详情:", id)
      const response = await this.instance.get<ApiResponse<Conversation>>(`chat/conversations/${id}/`);
      console.log("获取对话详情原始响应:", response)
      
      // 后端已经返回标准格式 { code, message, data }，直接返回即可
      return response.data;
    } catch (error: any) {
      console.error('获取对话详情失败:', error);
      
      if (error.response) {
        console.error('错误响应数据:', error.response.data);
        console.error('错误状态码:', error.response.status);
        
        return {
          code: error.response.status,
          message: error.response.data?.message || '获取对话详情失败，服务器返回错误',
          data: {} as Conversation
        };
      }
      
      if (error.request) {
        console.error('请求已发送但未收到响应');
        return {
          code: 500,
          message: '请求超时，未收到服务器响应',
          data: {} as Conversation
        };
      }
      
      return {
        code: 500,
        message: error.message || '网络错误，请检查网络连接',
        data: {} as Conversation
      };
    }
  }

  // 创建新对话
  async createConversation(title: string): Promise<ApiResponse<Conversation>> {
    try {
      console.log("创建新对话:", title)
      const response = await this.instance.post<ApiResponse<Conversation>>('chat/conversations/', { title });
      console.log("创建对话原始响应:", response)
      
      // 后端已经返回标准格式 { code, message, data }，直接返回即可
      return response.data;
    } catch (error: any) {
      console.error('创建对话失败:', error);
      
      if (error.response) {
        console.error('错误响应数据:', error.response.data);
        console.error('错误状态码:', error.response.status);
        
        return {
          code: error.response.status,
          message: error.response.data?.message || '创建对话失败，服务器返回错误',
          data: {} as Conversation
        };
      }
      
      if (error.request) {
        console.error('请求已发送但未收到响应');
        return {
          code: 500,
          message: '请求超时，未收到服务器响应',
          data: {} as Conversation
        };
      }
      
      return {
        code: 500,
        message: error.message || '网络错误，请检查网络连接',
        data: {} as Conversation
      };
    }
  }

  // 删除对话
  async deleteConversation(id: number): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.delete<ApiResponse<any>>(`chat/conversations/${id}/`);
      return response.data;
    } catch (error: any) {
      console.error('删除对话失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '删除对话失败',
          data: {}
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: {}
      };
    }
  }

  // 清空对话消息
  async clearConversationMessages(id: number): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.delete<ApiResponse<any>>(`chat/conversations/${id}/clear_messages/`);
      return response.data;
    } catch (error: any) {
      console.error('清空对话消息失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '清空对话消息失败',
          data: {}
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: {}
      };
    }
  }

  // 获取用户列表
  async getUserList(): Promise<ApiResponse<UserListItem[]>> {
    try {
      const response = await this.instance.get<ApiResponse<UserListItem[]>>('auth/user-management/');
      return response.data;
    } catch (error: any) {
      console.error('获取用户列表失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '获取用户列表失败',
          data: []
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: []
      };
    }
  }
  
  // 获取用户详情
  async getUserDetail(id: number): Promise<ApiResponse<UserListItem>> {
    try {
      const response = await this.instance.get<ApiResponse<UserListItem>>(`auth/user-management/${id}/`);
      return response.data;
    } catch (error: any) {
      console.error('获取用户详情失败:', error);
      throw error;
    }
  }
  
  // 创建用户
  async createUser(userData: Partial<UserListItem>): Promise<ApiResponse<UserListItem>> {
    try {
      const response = await this.instance.post<ApiResponse<UserListItem>>('auth/user-management/', userData);
      return response.data;
    } catch (error: any) {
      console.error('创建用户失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '创建用户失败',
          data: {} as UserListItem
        };
      }
      throw error;
    }
  }
  
  // 更新用户信息
  async updateUser(id: number, userData: Partial<UserListItem>): Promise<ApiResponse<UserListItem>> {
    try {
      const response = await this.instance.put<ApiResponse<UserListItem>>(`auth/user-management/${id}/`, userData);
      return response.data;
    } catch (error: any) {
      console.error('更新用户失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '更新用户失败',
          data: {} as UserListItem
        };
      }
      throw error;
    }
  }
  
  // 删除用户
  async deleteUser(id: number): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.delete<ApiResponse<any>>(`auth/user-management/${id}/`);
      return response.data;
    } catch (error: any) {
      console.error('删除用户失败:', error);
      throw error;
    }
  }
  
  // 更新用户状态
  async updateUserStatus(id: number, isActive: boolean): Promise<ApiResponse<UserListItem>> {
    try {
      const response = await this.instance.patch<ApiResponse<UserListItem>>(`auth/user-management/${id}/status/`, {
        isActive
      });
      return response.data;
    } catch (error: any) {
      console.error('更新用户状态失败:', error);
      throw error;
    }
  }
  
  // 获取角色列表
  async getRoleList(): Promise<ApiResponse<RoleItem[]>> {
    try {
      const response = await this.instance.get<ApiResponse<RoleItem[]>>('auth/roles/');
      return response.data;
    } catch (error: any) {
      console.error('获取角色列表失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '获取角色列表失败',
          data: []
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: []
      };
    }
  }
}

// 创建并导出实例
export const apiService = new ApiService();

// 同时提供类作为默认导出
export default ApiService; 