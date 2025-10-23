# 📘 API调用规范

> **项目**: LLM ST FLY - 智能客服系统  
> **更新日期**: 2025-10-22  
> **状态**: ✅ 已规范化

---

## 🎯 核心规则

### 规则 1️⃣: 使用 `apiService.instance`

```typescript
import { apiService } from '@/services/api'

// ✅ 正确
apiService.instance.get(...)
apiService.instance.post(...)
apiService.instance.delete(...)
apiService.instance.put(...)
apiService.instance.patch(...)

// ❌ 错误
apiService.get(...)      // 不存在此方法！
apiService.post(...)     // 不存在此方法！
```

### 规则 2️⃣: 路径不要包含 `/api/v1/`

```typescript
// ✅ 正确 - 直接从模块开始
'/agent/customer-service/assistants/'
'/agent/poetry-painting/works/'
'/chat/conversations/'

// ❌ 错误 - 会导致路径重复
'/api/v1/agent/customer-service/assistants/'
'/api/v1/agent/poetry-painting/works/'
```

**原因**: `BASE_URL` 已经包含了 `/api/v1/`

```typescript
// frontend/src/services/api.ts
const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api/v1/',  // ← 已包含
  TIMEOUT: 15000,
}
```

---

## 📋 标准模板

### GET 请求

```typescript
const fetchData = async () => {
  try {
    const response = await apiService.instance.get('/agent/customer-service/assistants/')
    
    if (response.data?.success) {
      // 处理成功数据
      const data = response.data.data
      return data
    }
  } catch (error: any) {
    console.error('获取数据失败:', error)
    // 错误处理
    if (error.response?.status === 404) {
      console.log('资源不存在')
    }
  }
}
```

### POST 请求

```typescript
const createData = async (payload: any) => {
  try {
    const response = await apiService.instance.post(
      '/agent/customer-service/assistants/',
      payload
    )
    
    if (response.data?.success) {
      toast.success('创建成功')
      return response.data.data
    }
  } catch (error: any) {
    console.error('创建失败:', error)
    toast.error(error.response?.data?.message || '创建失败')
  }
}
```

### DELETE 请求

```typescript
const deleteData = async (id: number) => {
  if (!confirm('确定删除吗？')) return
  
  try {
    const response = await apiService.instance.delete(
      `/agent/customer-service/assistants/${id}/`
    )
    
    if (response.data?.success) {
      toast.success('删除成功')
      // 刷新列表等后续操作
    }
  } catch (error: any) {
    console.error('删除失败:', error)
    toast.error('删除失败')
  }
}
```

### PUT/PATCH 请求

```typescript
const updateData = async (id: number, payload: any) => {
  try {
    const response = await apiService.instance.put(
      `/agent/customer-service/assistants/${id}/`,
      payload
    )
    
    if (response.data?.success) {
      toast.success('更新成功')
      return response.data.data
    }
  } catch (error: any) {
    console.error('更新失败:', error)
    toast.error('更新失败')
  }
}
```

---

## 🗺️ 客服系统API路径映射

### 完整URL构建示例

| 前端路径 | BASE_URL | 最终完整URL |
|---------|----------|------------|
| `/agent/customer-service/assistants/` | `http://localhost:8000/api/v1/` | `http://localhost:8000/api/v1/agent/customer-service/assistants/` |
| `/agent/customer-service/knowledge-bases/` | `http://localhost:8000/api/v1/` | `http://localhost:8000/api/v1/agent/customer-service/knowledge-bases/` |
| `/agent/customer-service/chat/` | `http://localhost:8000/api/v1/` | `http://localhost:8000/api/v1/agent/customer-service/chat/` |

### 客服系统所有API端点

```typescript
// 助手管理
GET    /agent/customer-service/assistants/              // 获取助手列表
POST   /agent/customer-service/assistants/              // 创建助手
GET    /agent/customer-service/assistants/{id}/         // 获取助手详情
PUT    /agent/customer-service/assistants/{id}/         // 更新助手
DELETE /agent/customer-service/assistants/{id}/         // 删除助手

// 知识库管理
GET    /agent/customer-service/knowledge-bases/         // 获取知识库列表
POST   /agent/customer-service/knowledge-bases/         // 创建知识库
GET    /agent/customer-service/knowledge-bases/{id}/    // 获取知识库详情
PUT    /agent/customer-service/knowledge-bases/{id}/    // 更新知识库
DELETE /agent/customer-service/knowledge-bases/{id}/    // 删除知识库

// 文档管理
POST   /agent/customer-service/knowledge-bases/{kb_id}/documents/        // 上传文档
GET    /agent/customer-service/knowledge-bases/{kb_id}/documents/        // 获取文档列表
DELETE /agent/customer-service/knowledge-bases/{kb_id}/documents/{id}/  // 删除文档

// 聊天功能
POST   /agent/customer-service/chat/                    // 发送消息
GET    /agent/customer-service/sessions/                // 获取会话列表
GET    /agent/customer-service/sessions/{id}/           // 获取会话详情
POST   /agent/customer-service/feedback/                // 提交反馈

// 其他
GET    /agent/customer-service/greeting/                // 获取欢迎语
GET    /agent/customer-service/stats/                   // 获取统计信息
```

---

## 📚 项目中的参考示例

### 诗词绘画模块（参考标准）

```typescript
// ✅ 标准用法
// frontend/src/views/agent/poetry-painting/hooks/usePoetryPainting.ts

// 创建作品
const response = await apiService.instance.post(
  `/agent/poetry-painting/${currentWorkId.value}/iterate/`,
  { /* payload */ }
)

// 获取列表
const response = await apiService.instance.get(
  '/agent/poetry-painting/works/'
)

const response = await apiService.instance.get(
  '/agent/poetry-painting/conversations/'
)
```

### 用户管理模块

```typescript
// frontend/src/views/users/UserManagement.vue

const response = await apiService.instance.get(
  `/users/?page=${currentPage.value}&page_size=${pageSize.value}`
)
```

---

## ⚠️ 常见错误

### 错误 1: 路径重复

```typescript
// ❌ 错误
apiService.instance.get('/api/v1/agent/customer-service/assistants/')
// 结果: http://localhost:8000/api/v1/api/v1/agent/customer-service/assistants/
//                                  ^^^^^^^^^ 重复！

// ✅ 正确
apiService.instance.get('/agent/customer-service/assistants/')
// 结果: http://localhost:8000/api/v1/agent/customer-service/assistants/
```

### 错误 2: 直接调用不存在的方法

```typescript
// ❌ 错误
apiService.get('/agent/...')
// TypeError: apiService.get is not a function

// ✅ 正确
apiService.instance.get('/agent/...')
```

### 错误 3: 忘记处理响应格式

```typescript
// ❌ 不完整
const response = await apiService.instance.get('/agent/...')
const data = response.data  // 可能是 { success: true, data: [...] }

// ✅ 正确
const response = await apiService.instance.get('/agent/...')
if (response.data?.success) {
  const data = response.data.data  // 正确获取实际数据
}
```

---

## 🔍 调试技巧

### 1. 检查实际请求URL

在浏览器开发者工具中：
1. 打开 Network 标签
2. 发起请求
3. 查看 Request URL

```
✅ 正确: http://localhost:8000/api/v1/agent/customer-service/assistants/
❌ 错误: http://localhost:8000/api/v1/api/v1/agent/customer-service/assistants/
```

### 2. 查看控制台错误

```javascript
// TypeError 错误
TypeError: (intermediate value).get is not a function
→ 使用了 apiService.get() 而不是 apiService.instance.get()

// 404 错误
AxiosError: Request failed with status code 404
→ 路径错误或后端API未实现

// 401 错误
AxiosError: Request failed with status code 401
→ 未登录或token过期
```

### 3. 添加调试日志

```typescript
const response = await apiService.instance.get('/agent/...')
console.log('Response:', response)
console.log('Data:', response.data)
console.log('Success:', response.data?.success)
console.log('Actual Data:', response.data?.data)
```

---

## 📝 开发清单

在开发新组件时，请检查：

- [ ] 使用 `import { apiService } from '@/services/api'`（命名导入）
- [ ] 使用 `apiService.instance.get/post/...`（不是直接 `apiService.get`）
- [ ] API路径以 `/` 开头但不包含 `/api/v1/`
- [ ] 正确处理 `response.data.success` 和 `response.data.data`
- [ ] 添加了错误处理 `try-catch`
- [ ] 检查 Network 面板确认请求URL正确
- [ ] 参考现有代码（如诗词绘画模块）

---

## 🎓 学习资源

### 相关文件

1. **API服务定义**  
   `frontend/src/services/api.ts` - 查看 ApiService 类结构

2. **标准示例**  
   `frontend/src/views/agent/poetry-painting/hooks/usePoetryPainting.ts`

3. **Bug修复记录**  
   `frontend/src/views/agent/customer-service/BUGFIX.md`

### 响应格式

所有API都遵循统一的响应格式：

```typescript
{
  "success": true,           // 请求是否成功
  "message": "操作成功",      // 提示消息
  "data": { /* ... */ },     // 实际数据
  "code": 200                // 状态码
}
```

---

## ✅ 验证清单

部署前检查：

- [ ] 所有API调用使用 `apiService.instance`
- [ ] 所有路径不包含 `/api/v1/` 前缀
- [ ] 错误处理完整
- [ ] 在浏览器 Network 面板验证URL正确
- [ ] 没有控制台错误（除了预期的404）

---

**📌 记住**: 
- ✅ `apiService.instance.get('/agent/...')`
- ❌ `apiService.get('/api/v1/agent/...')`

---

*API调用规范 v1.0 - 最后更新: 2025-10-22*

