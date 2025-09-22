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
  // 新增字段支持流式输出
  thinking_process?: string;
  has_thinking?: boolean;
  is_thinking?: boolean;
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

export interface ConversationList {
  list?: Conversation[];
  total?: number; 
  page?: number;
  pagesize?: number;
}

// 用户列表接口
export interface UserListItem {
  id: number;
  username: string;
  email: string;
  password?: string;
  user_role?: number;
  user_role_name?: string;
  role?: {
    id: number;
    name: string;
    description?: string;
  };
  is_active: boolean;
  date_joined: string;
}

// 分页用户列表接口
export interface PaginatedUserList {
  list: UserListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// 分页角色列表接口
export interface PaginatedRoleList {
  list: RoleItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// 角色列表项接口
export interface RoleItem {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
  updated_at?: string;
}

// 权限接口
export interface Permission {
  id: number;
  name: string;
  codename: string;
  content_type: number;
}

// 角色详情接口（包含权限）
export interface RoleDetail extends RoleItem {
  permissions: Permission[];
}

// 角色创建/更新请求接口
export interface RoleRequest {
  name: string;
  description?: string;
  permissions?: number[];
}

// AI图像生成相关接口
export interface ImageGenerationRequest {
  prompt: string;
  negative_prompt?: string;
  size?: string;
  n?: number;
  prompt_extend?: boolean;
  watermark?: boolean;
  style?: string;
  shot_type?: string;
  angle?: string;
  shooting_technique?: string;
  lighting?: string;
}

export interface GeneratedImage {
  original_url: string;
  saved_path: string;
  saved_url: string;
  filename: string;
  size: number;
  download_time: string;
  orig_prompt?: string;
  actual_prompt?: string;
}

export interface ImageGenerationResponse {
  task_id: string;
  status: string;
  images: GeneratedImage[];
  usage: any;
  request_id: string;
  enhanced_prompt: string;
  submit_time?: string;
  end_time?: string;
}

export interface ImagePresets {
  sizes: Array<{value: string, label: string, aspect_ratio: string}>;
  styles: Array<{value: string, label: string}>;
  shot_types: Array<{value: string, label: string}>;
  angles: Array<{value: string, label: string}>;
  shooting_techniques: Array<{value: string, label: string}>;
  lighting: Array<{value: string, label: string}>;
}

// AI音频处理相关接口
export interface SpeechToTextRequest {
  audio_file?: File;
  audio_url?: string;
  language?: string;
  model?: string;
}

export interface TextToSpeechRequest {
  text: string;
  voice?: string;
  speed?: number;
  volume?: number;
  pitch?: number;
  format?: string;
}

export interface VoiceCloneRequest {
  reference_audio?: File;
  reference_url?: string;
  reference_text: string;
  target_text: string;
  model?: string;
}

export interface AudioTaskResponse {
  task_id: string;
  status: string;
  task_type: string;
  result_url?: string;
  result_text?: string;
  confidence?: number;
  duration?: number;
  file_size?: number;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface AudioHistoryItem {
  task_id: string;
  task_type: string;
  status: string;
  created_at: string;
  completed_at?: string;
  result_url?: string;
  result_text?: string;
  duration?: number;
}

export interface UserAudioStats {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  total_duration: number;
  total_storage_used: number;
  speech_to_text_count: number;
  text_to_speech_count: number;
  voice_clone_count: number;
}

// AI视频生成相关接口
export interface TextToVideoRequest {
  prompt: string;
  model?: string;
  resolution?: string;
  duration?: number;
  fps?: number;
  style_preset?: string;
}

export interface ImageToVideoRequest {
  image_file?: File;
  image_url?: string;
  image_base64?: string;
  prompt?: string;
  model?: string;
  resolution?: string;
  duration?: number;
  fps?: number;
  style_preset?: string;
}

export interface VideoTaskResponse {
  task_id: string;
  status: string;
  task_type: string;
  result_url?: string;
  thumbnail_url?: string;
  duration?: number;
  file_size?: number;
  resolution?: string;
  fps?: number;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface VideoHistoryItem {
  task_id: string;
  task_type: string;
  status: string;
  created_at: string;
  completed_at?: string;
  result_url?: string;
  thumbnail_url?: string;
  duration?: number;
  resolution?: string;
}

export interface UserVideoStats {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  total_duration: number;
  total_storage_used: number;
  text_to_video_count: number;
  image_to_video_count: number;
}

export interface VideoStylePreset {
  id: number;
  name: string;
  description: string;
  style_keywords: string;
  recommended_model: string;
  default_resolution: string;
  default_duration: number;
  default_fps: number;
}

// 智能体相关接口
export interface Agent {
  id: string;
  name: string;
  type: string;
  type_display: string;
  description: string;
  avatar?: string;
  greeting_message: string;
  is_active: boolean;
  created_at: string;
}

export interface Message {
  id: string;
  type: string;
  type_display: string;
  content: string;
  metadata?: any;
  created_at: string;
  tokens_used: number;
}

export interface AgentConversation {
  id: string;
  title: string;
  agent_name: string;
  agent_type: string;
  agent_avatar?: string;
  started_at: string;
  last_message_at: string;
  is_active: boolean;
  message_count: number;
  messages?: Message[];
  agent?: Agent;
}

export interface UserAgentStats {
  username: string;
  total_conversations: number;
  total_messages: number;
  total_tokens_used: number;
  travel_conversations: number;
  poetry_conversations: number;
  service_conversations: number;
  last_used_at?: string;
  created_at: string;
}

export interface AgentChatRequest {
  message: string;
  conversation_id?: string;
  agent_type: string;
}

export interface AgentChatResponse {
  conversation_id: string;
  message: string;
  message_id: string;
  agent: Agent;
  tokens_used: number;
  is_new_conversation: boolean;
}

export interface CreateAgentConversationRequest {
  agent_type: string;
  title?: string;
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
  old_password: string;
  new_password: string;
  new_password_confirm: string;
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
      console.log(response.data,"~~~~~~~~~~~~~~~~~");
      return response.data;
    } catch (error: any) {
      console.error('获取用户信息失败:', error);
      throw error;
    }
  }
  
  // 修改密码API
  async changePassword(data: ChangePasswordRequest): Promise<ApiResponse<any>> {
    try {
      // 转换字段名格式以匹配后端期望
      const requestData = {
        old_password: data.old_password,
        new_password: data.new_password,
        new_password_confirm: data.new_password_confirm
      };
      
      const response = await this.instance.post<ApiResponse<any>>('auth/users/change_password/', requestData);
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
      console.log(formData, "formData")
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

  // 聊天完成API - 使用DashScope大模型（支持流式响应）
  async chatCompletion(
    messages: ChatMessage[], 
    conversationId?: number, 
    options?: {
      deepThinking?: boolean
      webSearch?: boolean
      onChunk?: (chunk: any) => void
    }
  ): Promise<ApiResponse<any>> {
    try {
      const requestData = {
        messages,
        conversation_id: conversationId,
        deep_thinking: options?.deepThinking || false,
        web_search: options?.webSearch || false,
        stream: true // 启用流式响应
      };

      console.log("📤 [流式请求] 发送流式聊天请求:", requestData);

      // 使用fetch API处理流式响应
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_CONFIG.BASE_URL}chat/completion/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify(requestData)
      });

      console.log("📡 [流式请求] 服务器响应状态:", response.status, response.statusText);

      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ [流式请求] 服务器返回错误:", response.status, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        console.error("❌ [流式请求] 无法获取响应流");
        throw new Error('无法获取响应流');
      }

      console.log("🚀 [流式响应] 开始处理流式数据...");

      let buffer = '';
      let conversationId_result = conversationId;
      let fullContent = '';
      let thinkingProcess = '';
      let usage = {};
      let requestId = '';
      let chunkCount = 0;

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const jsonStr = line.slice(6).trim();
                if (!jsonStr) continue;
                
                const data = JSON.parse(jsonStr);
                
                // 添加浏览器控制台日志：显示服务器流式输出的实时返回消息
                console.log('🔄 [流式响应] 收到服务器数据:', data);
                console.log('📊 [流式响应] 数据详情:', {
                  type: data.type,
                  timestamp: new Date().toLocaleTimeString(),
                  dataSize: JSON.stringify(data).length + ' 字节'
                });
                
                if (data.error) {
                  console.error('❌ [流式响应] 服务器返回错误:', data.error);
                  throw new Error(data.error);
                }
                
                if (data.type === 'conversation_id') {
                  conversationId_result = data.conversation_id;
                  console.log('🆔 [流式响应] 对话ID:', data.conversation_id);
                } else if (data.type === 'thinking') {
                  thinkingProcess = data.full_thinking || '';
                  console.log('🤔 [流式响应] 思考过程片段:', {
                    content: data.content,
                    fullThinking: thinkingProcess.length + ' 字符'
                  });
                  if (options?.onChunk) {
                    options.onChunk({
                      type: 'thinking',
                      content: data.content,
                      fullThinking: thinkingProcess
                    });
                  }
                } else if (data.type === 'content') {
                  fullContent = data.full_content || '';
                  console.log('💬 [流式响应] 内容片段:', {
                    content: data.content,
                    fullContent: fullContent.length + ' 字符'
                  });
                  if (options?.onChunk) {
                    options.onChunk({
                      type: 'content',
                      content: data.content,
                      fullContent: fullContent
                    });
                  }
                } else if (data.type === 'final') {
                  fullContent = data.content;
                  usage = data.usage || {};
                  requestId = data.request_id || '';
                  if (data.thinking_process) {
                    thinkingProcess = data.thinking_process;
                  }
                  console.log('✅ [流式响应] 最终结果:', {
                    contentLength: fullContent.length + ' 字符',
                    thinkingLength: thinkingProcess.length + ' 字符',
                    usage: usage,
                    requestId: requestId
                  });
                } else if (data.type === 'done') {
                  console.log('🏁 [流式响应] 响应完成');
                  break;
                } else {
                  console.log('ℹ️ [流式响应] 其他类型数据:', data.type, data);
                }
              } catch (parseError) {
                console.warn('⚠️ [流式响应] 解析SSE数据失败:', parseError, 'Line:', line);
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      console.log("✅ [流式响应] 流式响应完成:", { 
        contentLength: fullContent.length + ' 字符',
        thinkingLength: thinkingProcess.length + ' 字符',
        totalChunks: chunkCount,
        usage: usage,
        conversationId: conversationId_result
      });

      return {
        code: 200,
        data: {
          conversation_id: conversationId_result,
          message: fullContent,
          thinking_process: thinkingProcess,
          has_thinking: !!thinkingProcess,
          usage: usage,
          request_id: requestId
        },
        message: '回复成功'
      };

    } catch (error: any) {
      console.error('聊天请求失败:', error);
      
      return {
        code: 500,
        message: error.message || '网络请求失败',
        data: {
          content: "抱歉，我遇到了一些问题。",
          conversation_id: conversationId
        }
      };
    }
  }

  // 备用的非流式聊天API（用于兼容性）
  async chatCompletionNonStream(
    messages: ChatMessage[], 
    conversationId?: number, 
    options?: {
      deepThinking?: boolean
      webSearch?: boolean
    }
  ): Promise<ApiResponse<any>> {
    try {
      console.log("发送非流式聊天请求:", { 
        messages, 
        conversation_id: conversationId,
        deep_thinking: options?.deepThinking || false,
        web_search: options?.webSearch || false
      })
      const response = await this.instance.post<ApiResponse<any>>('chat/completion/', { 
        messages,
        conversation_id: conversationId,
        deep_thinking: options?.deepThinking || false,
        web_search: options?.webSearch || false,
        stream: false
      },
      {
        timeout: 60 * 1000 // 增加超时时间
      }
    );
      console.log("聊天请求原始响应:", response)
      
      return response.data;
    } catch (error: any) {
      console.error('聊天请求失败:', error);
      
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

  // 发送消息（支持深度思考和联网搜索）
  async sendMessage(data: {
    conversation_id?: number
    message: string
    role: string
    deep_thinking?: boolean
    web_search?: boolean
  }): Promise<ApiResponse<any>> {
    try {
      console.log("发送消息请求:", data)
      const response = await this.instance.post<ApiResponse<any>>('chat/send/', data);
      console.log("发送消息响应:", response)
      
      return response.data;
    } catch (error: any) {
      console.error('发送消息失败:', error);
      
      if (error.response) {
        console.error('错误响应数据:', error.response.data);
        console.error('错误状态码:', error.response.status);
        
        return {
          code: error.response.status,
          message: error.response.data?.message || '发送消息失败，服务器返回错误',
          data: {
            ai_message: {
              content: "抱歉，服务器处理请求时出错，请稍后再试。"
            },
            conversation_id: data.conversation_id
          }
        };
      }
      
      if (error.request) {
        console.error('请求已发送但未收到响应');
        return {
          code: 500,
          message: '发送消息超时，未收到服务器响应',
          data: {
            ai_message: {
              content: "抱歉，服务器响应超时，请检查网络连接并稍后再试。"
            },
            conversation_id: data.conversation_id
          }
        };
      }
      
      return {
        code: 500,
        message: error.message || '网络错误，请检查网络连接',
        data: {
          ai_message: {
            content: "抱歉，发生网络错误，请检查网络连接并稍后再试。"
          },
          conversation_id: data.conversation_id
        }
      };
    }
  }

  // 获取对话列表
  async getConversations(conversationType?: 'default' | 'ai_chat'): Promise<ApiResponse<ConversationList>> {
    try {
      console.log(`获取${conversationType ? conversationType : '所有'}对话列表`)
      const url = conversationType 
        ? `chat/conversations/?type=${conversationType}` 
        : 'chat/conversations/';
      const response = await this.instance.get<ApiResponse<ConversationList>>(url);
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
          data: {}
        };
      }
      
      if (error.request) {
        console.error('请求已发送但未收到响应');
        return {
          code: 500,
          message: '请求超时，未收到服务器响应',
          data: {}
        };
      }
      
      return {
        code: 500,
        message: error.message || '网络错误，请检查网络连接',
        data: {}
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
  async deleteConversation(id: number, isAIChat: boolean = false): Promise<ApiResponse<any>> {
    try {
      const url = isAIChat 
        ? `chat/ai_chat/conversations/${id}/` 
        : `chat/conversations/${id}/`;
      const response = await this.instance.delete<ApiResponse<any>>(url);
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
  async clearConversationMessages(id: number, isAIChat: boolean = false): Promise<ApiResponse<any>> {
    try {
      const url = isAIChat 
        ? `chat/ai_chat/conversations/${id}/clear_messages/` 
        : `chat/conversations/${id}/clear_messages/`;
      const response = await this.instance.delete<ApiResponse<any>>(url);
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
  async getUserList(): Promise<ApiResponse<PaginatedUserList>> {
    try {
      const response = await this.instance.get<ApiResponse<PaginatedUserList>>('auth/user-management/');
      console.log("获取用户列表原始响应:", response.data)
      return response.data;
    } catch (error: any) {
      console.error('获取用户列表失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '获取用户列表失败',
          data: {
            list: [],
            total: 0,
            page: 1,
            page_size: 10,
            total_pages: 0,
            has_next: false,
            has_previous: false
          }
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: {
          list: [],
          total: 0,
          page: 1,
          page_size: 10,
          total_pages: 0,
          has_next: false,
          has_previous: false
        }
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
  async updateUserStatus(id: number, is_active: boolean): Promise<ApiResponse<UserListItem>> {
    try {
      const response = await this.instance.patch<ApiResponse<UserListItem>>(`auth/user-management/${id}/status/`, {
        is_active
      });
      return response.data;
    } catch (error: any) {
      console.error('更新用户状态失败:', error);
      throw error;
    }
  }
  
  // 获取角色列表
  async getRoleList(): Promise<ApiResponse<PaginatedRoleList>> {
    try {
      const response = await this.instance.get<ApiResponse<PaginatedRoleList>>('auth/roles/');
      return response.data;
    } catch (error: any) {
      console.error('获取角色列表失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '获取角色列表失败',
          data: {
            list: [],
            total: 0,
            page: 1,
            page_size: 20,
            total_pages: 0,
            has_next: false,
            has_previous: false
          }
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: {
          list: [],
          total: 0,
          page: 1,
          page_size: 20,
          total_pages: 0,
          has_next: false,
          has_previous: false
        }
      };
    }
  }

  // 获取角色详情
  async getRoleDetail(id: number): Promise<ApiResponse<RoleDetail>> {
    try {
      const response = await this.instance.get<ApiResponse<RoleDetail>>(`auth/roles/${id}/`);
      return response.data;
    } catch (error: any) {
      console.error('获取角色详情失败:', error);
      if (error.response) {
        // 如果后端没有角色详情接口，返回模拟数据
        if (error.response.status === 404) {
          return {
            code: 200,
            message: '获取角色详情成功',
            data: {
              id,
              name: `角色${id}`,
              permissions: []
            }
          };
        }
        return {
          code: error.response.status,
          message: error.response.data.message || '获取角色详情失败',
          data: {} as RoleDetail
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: {} as RoleDetail
      };
    }
  }

  // 创建角色
  async createRole(roleData: RoleRequest): Promise<ApiResponse<RoleItem>> {
    try {
      console.log('创建角色请求数据:', roleData);
      const response = await this.instance.post<ApiResponse<RoleItem>>('auth/roles/', roleData);
      console.log('创建角色响应:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('创建角色失败:', error);
      if (error.response) {
        console.error('创建角色错误响应:', error.response.data);
        return {
          code: error.response.status,
          message: error.response.data.message || '创建角色失败',
          data: {} as RoleItem
        };
      }
      throw error;
    }
  }

  // 更新角色
  async updateRole(id: number, roleData: RoleRequest): Promise<ApiResponse<RoleItem>> {
    try {
      console.log('更新角色请求数据:', { id, roleData });
      const response = await this.instance.put<ApiResponse<RoleItem>>(`auth/roles/${id}/`, roleData);
      console.log('更新角色响应:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('更新角色失败:', error);
      if (error.response) {
        console.error('更新角色错误响应:', error.response.data);
        return {
          code: error.response.status,
          message: error.response.data.message || '更新角色失败',
          data: {} as RoleItem
        };
      }
      throw error;
    }
  }

  // 删除角色
  async deleteRole(id: number): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.delete<ApiResponse<any>>(`auth/roles/${id}/`);
      return response.data;
    } catch (error: any) {
      console.error('删除角色失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data.message || '删除角色失败',
          data: {}
        };
      }
      throw error;
    }
  }

  // 获取权限列表 (暂时返回模拟数据，因为后端可能没有对应接口)
  async getPermissionList(): Promise<ApiResponse<Permission[]>> {
    try {
      // 由于后端可能没有权限列表接口，我们返回模拟数据
      const mockPermissions: Permission[] = [
        { id: 1, name: '查看用户', codename: 'view_user', content_type: 1 },
        { id: 2, name: '添加用户', codename: 'add_user', content_type: 1 },
        { id: 3, name: '修改用户', codename: 'change_user', content_type: 1 },
        { id: 4, name: '删除用户', codename: 'delete_user', content_type: 1 },
        { id: 5, name: '查看组', codename: 'view_group', content_type: 2 },
        { id: 6, name: '添加组', codename: 'add_group', content_type: 2 },
        { id: 7, name: '修改组', codename: 'change_group', content_type: 2 },
        { id: 8, name: '删除组', codename: 'delete_group', content_type: 2 },
        { id: 9, name: '查看权限', codename: 'view_permission', content_type: 3 },
        { id: 10, name: '查看对话', codename: 'view_conversation', content_type: 4 },
        { id: 11, name: '添加对话', codename: 'add_conversation', content_type: 4 },
        { id: 12, name: '删除对话', codename: 'delete_conversation', content_type: 4 }
      ];
      
      return {
        code: 200,
        message: '获取权限列表成功',
        data: mockPermissions
      };
    } catch (error: any) {
      console.error('获取权限列表失败:', error);
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: []
      };
    }
  }

  // 更新角色权限 (暂时返回成功，因为后端可能没有对应接口)
  async updateRolePermissions(id: number, permissionIds: number[]): Promise<ApiResponse<RoleDetail>> {
    try {
      // 由于后端可能没有角色权限更新接口，我们暂时返回成功
      console.log(`更新角色 ${id} 的权限:`, permissionIds);
      
      return {
        code: 200,
        message: '权限更新成功',
        data: {
          id,
          name: '角色',
          permissions: permissionIds.map(pid => ({
            id: pid,
            name: `权限${pid}`,
            codename: `perm_${pid}`,
            content_type: 1
          }))
        }
      };
    } catch (error: any) {
      console.error('更新角色权限失败:', error);
      return {
        code: 500,
        message: '更新角色权限失败',
        data: {} as RoleDetail
      };
    }
  }

  // AI图像生成API方法
  
  // 生成图像
  async generateImage(data: ImageGenerationRequest): Promise<ApiResponse<ImageGenerationResponse>> {
    try {
      console.log('发送图像生成请求:', data);
      const response = await this.instance.post<ApiResponse<ImageGenerationResponse>>(
        'ai-image/generate/', 
        data,
        {
          timeout: 60000 // 图像生成超时时间设置为60秒
        }
      );
      console.log('图像生成响应:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('图像生成失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data?.message || '图像生成失败',
          data: {} as ImageGenerationResponse
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: {} as ImageGenerationResponse
      };
    }
  }

  // 获取图像生成预设参数
  async getImagePresets(): Promise<ApiResponse<ImagePresets>> {
    try {
      const response = await this.instance.get<ApiResponse<ImagePresets>>('ai-image/presets/');
      return response.data;
    } catch (error: any) {
      console.error('获取预设参数失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data?.message || '获取预设参数失败',
          data: {} as ImagePresets
        };
      }
      return {
        code: 500,
        message: '网络错误，请检查网络连接',
        data: {} as ImagePresets
      };
    }
  }

  // 查询图像生成任务状态
  async getImageTaskStatus(taskId: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.get<ApiResponse<any>>(
        `ai-image/task/status/?task_id=${taskId}`
      );
      return response.data;
    } catch (error: any) {
      console.error('查询任务状态失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data?.message || '查询任务状态失败',
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

  // 获取图像生成历史
  async getImageHistory(page: number = 1, pageSize: number = 20): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.get<ApiResponse<any>>(
        `ai-image/history/?page=${page}&page_size=${pageSize}`
      );
      return response.data;
    } catch (error: any) {
      console.error('获取图像历史失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data?.message || '获取图像历史失败',
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

  // 获取用户图像统计
  async getImageStats(days: number = 30): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.get<ApiResponse<any>>(
        `ai-image/stats/?days=${days}`
      );
      return response.data;
    } catch (error: any) {
      console.error('获取图像统计失败:', error);
      if (error.response) {
        return {
          code: error.response.status,
          message: error.response.data?.message || '获取图像统计失败',
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

  // =============================================================================
  // AI音频处理API方法
  // =============================================================================

  // 语音转文字
  async speechToText(data: SpeechToTextRequest): Promise<ApiResponse<AudioTaskResponse>> {
    try {
      const formData = new FormData();
      if (data.audio_file) {
        formData.append('audio_file', data.audio_file);
      }
      if (data.audio_url) {
        formData.append('audio_url', data.audio_url);
      }
      if (data.language) {
        formData.append('language', data.language);
      }
      if (data.model) {
        formData.append('model', data.model);
      }

      const response = await this.instance.post<ApiResponse<AudioTaskResponse>>(
        'chat/ai-audio/speech-to-text/', 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('语音转文字失败:', error);
      return this.handleApiError(error, '语音转文字失败');
    }
  }

  // 文字转语音
  async textToSpeech(data: TextToSpeechRequest): Promise<ApiResponse<AudioTaskResponse>> {
    try {
      const response = await this.instance.post<ApiResponse<AudioTaskResponse>>(
        'chat/ai-audio/text-to-speech/', 
        data,
        {
          timeout: 60000
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('文字转语音失败:', error);
      return this.handleApiError(error, '文字转语音失败');
    }
  }

  // 语音克隆
  async voiceClone(data: VoiceCloneRequest): Promise<ApiResponse<AudioTaskResponse>> {
    try {
      const formData = new FormData();
      if (data.reference_audio) {
        formData.append('reference_audio', data.reference_audio);
      }
      if (data.reference_url) {
        formData.append('reference_url', data.reference_url);
      }
      formData.append('reference_text', data.reference_text);
      formData.append('target_text', data.target_text);
      if (data.model) {
        formData.append('model', data.model);
      }

      const response = await this.instance.post<ApiResponse<AudioTaskResponse>>(
        'chat/ai-audio/voice-clone/', 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 60000
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('语音克隆失败:', error);
      return this.handleApiError(error, '语音克隆失败');
    }
  }

  // 获取音频任务状态
  async getAudioTaskStatus(taskId: string): Promise<ApiResponse<AudioTaskResponse>> {
    try {
      const response = await this.instance.get<ApiResponse<AudioTaskResponse>>(
        `chat/ai-audio/task/${taskId}/status/`
      );
      return response.data;
    } catch (error: any) {
      console.error('获取音频任务状态失败:', error);
      return this.handleApiError(error, '获取任务状态失败');
    }
  }

  // 获取音频处理历史
  async getAudioHistory(params?: { task_type?: string; limit?: number }): Promise<ApiResponse<AudioHistoryItem[]>> {
    try {
      const response = await this.instance.get<ApiResponse<AudioHistoryItem[]>>(
        'chat/ai-audio/history/',
        { params }
      );
      return response.data;
    } catch (error: any) {
      console.error('获取音频历史失败:', error);
      return this.handleApiError(error, '获取音频历史失败');
    }
  }

  // 获取用户音频统计
  async getUserAudioStats(): Promise<ApiResponse<UserAudioStats>> {
    try {
      const response = await this.instance.get<ApiResponse<UserAudioStats>>(
        'chat/ai-audio/stats/'
      );
      return response.data;
    } catch (error: any) {
      console.error('获取音频统计失败:', error);
      return this.handleApiError(error, '获取音频统计失败');
    }
  }

  // =============================================================================
  // AI视频生成API方法
  // =============================================================================

  // 文生视频
  async textToVideo(data: TextToVideoRequest): Promise<ApiResponse<VideoTaskResponse>> {
    try {
      const response = await this.instance.post<ApiResponse<VideoTaskResponse>>(
        'chat/ai-video/text-to-video/', 
        data,
        {
          timeout: 120000 // 视频生成需要更长时间
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('文生视频失败:', error);
      return this.handleApiError(error, '文生视频失败');
    }
  }

  // 图生视频
  async imageToVideo(data: ImageToVideoRequest): Promise<ApiResponse<VideoTaskResponse>> {
    try {
      const formData = new FormData();
      if (data.image_file) {
        formData.append('image_file', data.image_file);
      }
      if (data.image_url) {
        formData.append('image_url', data.image_url);
      }
      if (data.image_base64) {
        formData.append('image_base64', data.image_base64);
      }
      if (data.prompt) {
        formData.append('prompt', data.prompt);
      }
      if (data.model) {
        formData.append('model', data.model);
      }
      if (data.resolution) {
        formData.append('resolution', data.resolution);
      }
      if (data.duration) {
        formData.append('duration', data.duration.toString());
      }
      if (data.fps) {
        formData.append('fps', data.fps.toString());
      }
      if (data.style_preset) {
        formData.append('style_preset', data.style_preset);
      }

      const response = await this.instance.post<ApiResponse<VideoTaskResponse>>(
        'chat/ai-video/image-to-video/', 
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 120000
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('图生视频失败:', error);
      return this.handleApiError(error, '图生视频失败');
    }
  }

  // 获取视频任务状态
  async getVideoTaskStatus(taskId: string): Promise<ApiResponse<VideoTaskResponse>> {
    try {
      const response = await this.instance.get<ApiResponse<VideoTaskResponse>>(
        `chat/ai-video/task/${taskId}/status/`
      );
      return response.data;
    } catch (error: any) {
      console.error('获取视频任务状态失败:', error);
      return this.handleApiError(error, '获取任务状态失败');
    }
  }

  // 获取视频生成历史
  async getVideoHistory(params?: { task_type?: string; limit?: number }): Promise<ApiResponse<VideoHistoryItem[]>> {
    try {
      const response = await this.instance.get<ApiResponse<VideoHistoryItem[]>>(
        'chat/ai-video/history/',
        { params }
      );
      return response.data;
    } catch (error: any) {
      console.error('获取视频历史失败:', error);
      return this.handleApiError(error, '获取视频历史失败');
    }
  }

  // 获取用户视频统计
  async getUserVideoStats(): Promise<ApiResponse<UserVideoStats>> {
    try {
      const response = await this.instance.get<ApiResponse<UserVideoStats>>(
        'chat/ai-video/stats/'
      );
      return response.data;
    } catch (error: any) {
      console.error('获取视频统计失败:', error);
      return this.handleApiError(error, '获取视频统计失败');
    }
  }

  // 获取视频风格预设
  async getVideoStylePresets(): Promise<ApiResponse<VideoStylePreset[]>> {
    try {
      const response = await this.instance.get<ApiResponse<VideoStylePreset[]>>(
        'chat/ai-video/style-presets/'
      );
      return response.data;
    } catch (error: any) {
      console.error('获取视频风格预设失败:', error);
      return this.handleApiError(error, '获取视频风格预设失败');
    }
  }

  // =============================================================================
  // 智能体API方法
  // =============================================================================

  // 获取智能体列表
  async getAgents(): Promise<ApiResponse<Agent[]>> {
    try {
      const response = await this.instance.get<ApiResponse<Agent[]>>('agent/agents/');
      return response.data;
    } catch (error: any) {
      console.error('获取智能体列表失败:', error);
      return this.handleApiError(error, '获取智能体列表失败');
    }
  }

  // 与智能体聊天
  async agentChat(data: AgentChatRequest): Promise<ApiResponse<AgentChatResponse>> {
    try {
      const response = await this.instance.post<ApiResponse<AgentChatResponse>>(
        'agent/chat/', 
        data,
        {
          timeout: 30000 // 聊天可能需要较长时间
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('智能体聊天失败:', error);
      return this.handleApiError(error, '智能体聊天失败');
    }
  }

  // 创建智能体对话
  async createAgentConversation(data: CreateAgentConversationRequest): Promise<ApiResponse<AgentConversation>> {
    try {
      const response = await this.instance.post<ApiResponse<AgentConversation>>(
        'agent/conversations/create/', 
        data
      );
      return response.data;
    } catch (error: any) {
      console.error('创建智能体对话失败:', error);
      return this.handleApiError(error, '创建智能体对话失败');
    }
  }

  // 获取智能体对话列表
  async getAgentConversations(params?: { agent_type?: string; limit?: number; offset?: number }): Promise<ApiResponse<AgentConversation[]>> {
    try {
      const response = await this.instance.get<ApiResponse<AgentConversation[]>>(
        'agent/conversations/',
        { params }
      );
      return response.data;
    } catch (error: any) {
      console.error('获取智能体对话列表失败:', error);
      return this.handleApiError(error, '获取智能体对话列表失败');
    }
  }

  // 获取智能体对话详情
  async getAgentConversationDetail(conversationId: string): Promise<ApiResponse<AgentConversation>> {
    try {
      const response = await this.instance.get<ApiResponse<AgentConversation>>(
        `agent/conversations/${conversationId}/`
      );
      return response.data;
    } catch (error: any) {
      console.error('获取智能体对话详情失败:', error);
      return this.handleApiError(error, '获取智能体对话详情失败');
    }
  }

  // 删除智能体对话
  async deleteAgentConversation(conversationId: string): Promise<ApiResponse<any>> {
    try {
      const response = await this.instance.delete<ApiResponse<any>>(
        `agent/conversations/${conversationId}/delete/`
      );
      return response.data;
    } catch (error: any) {
      console.error('删除智能体对话失败:', error);
      return this.handleApiError(error, '删除智能体对话失败');
    }
  }

  // 获取用户智能体统计
  async getUserAgentStats(): Promise<ApiResponse<UserAgentStats>> {
    try {
      const response = await this.instance.get<ApiResponse<UserAgentStats>>('agent/stats/');
      return response.data;
    } catch (error: any) {
      console.error('获取用户智能体统计失败:', error);
      return this.handleApiError(error, '获取用户智能体统计失败');
    }
  }

  // 通用错误处理方法
  private handleApiError(error: any, defaultMessage: string): ApiResponse<any> {
    if (error.response) {
      return {
        code: error.response.status,
        message: error.response.data?.message || defaultMessage,
        data: error.response.data?.data || null
      };
    }
    return {
      code: 500,
      message: '网络错误，请检查网络连接',
      data: null
    };
  }
}

// 创建并导出实例
export const apiService = new ApiService();

// 同时提供类作为默认导出
export default ApiService;