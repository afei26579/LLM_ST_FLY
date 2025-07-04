// API服务类：封装所有与后端API交互的方法
// 使用axios进行HTTP请求

import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

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
      const response = await this.instance.get<ApiResponse<any>>(
        `auth/users/verify-email/?token=${encodeURIComponent(token)}&email=${encodeURIComponent(email)}`
      );
      return response.data;
    } catch (error: any) {
      console.error('验证邮箱绑定失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '验证邮箱绑定失败',
          data: error.response.data
        };
      }
      throw error;
    }
  }
}

// 创建单例并导出
export const apiService = new ApiService(); 