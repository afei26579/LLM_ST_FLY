import axios from 'axios'

// 创建axios实例
const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 从localStorage获取token并添加到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 根据后端API的响应结构进行调整
    // 假设后端返回的格式为 { code: number, data: any, message: string }
    if (res.code !== 200 && res.code !== 0) {
      // 控制台输出错误信息
      console.error(res.message || '请求错误')
      
      // 处理特定错误码，如401未授权
      if (res.code === 401) {
        // 重定向到登录页或刷新token
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
      
      return Promise.reject(new Error(res.message || '未知错误'))
    } else {
      // 正常返回数据
      return res.data || res
    }
  },
  error => {
    // 处理HTTP错误状态码
    const message = error.response?.data?.message || error.message || '网络错误'
    console.error('响应错误:', message)
    
    return Promise.reject(error)
  }
)

export default service 