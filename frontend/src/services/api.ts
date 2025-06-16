// API服务类：封装所有与后端API交互的方法
// 使用axios进行HTTP请求

import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'

// API基础配置
const API_CONFIG = {
  // 后端API的基础URL
  BASE_URL: 'http://localhost:8000/api/',
  // 请求超时时间（毫秒）
  TIMEOUT: 15000,
}

// 响应数据接口
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data?: T;
}

// 登录请求参数接口
interface LoginRequest {
  username: string;
  password: string;
}

// 登录响应数据接口
interface LoginResponse {
  token: string;
  user: {
    id: number;
    username: string;
    email?: string;
    role: string;
    permissions?: string[];
  }
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
        message: '网络错误，请检查网络连接'
      };
    }
  }
  
  // 获取用户信息API
  async getUserInfo(): Promise<ApiResponse> {
    try {
      const response = await this.instance.get<ApiResponse>('users/me/');
      return response.data;
    } catch (error: any) {
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '获取用户信息失败',
          data: error.response.data
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接'
      };
    }
  }
}

// 创建单例并导出
export const apiService = new ApiService(); 