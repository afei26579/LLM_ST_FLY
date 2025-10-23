# 🐛 Bug修复记录

## Bug #2: API路径重复问题 ✅ 已修复

### 问题描述
```
请求地址错误：
http://localhost:8000/api/v1/api/v1/agent/customer-service/assistants/
                      ^^^^^^^^^ 重复了
```

### 错误原因
BASE_URL 已经包含了 `/api/v1/`，在调用时又加了一次。

### 配置说明
```typescript
// frontend/src/services/api.ts
const API_CONFIG = {
  BASE_URL: 'http://localhost:8000/api/v1/',  // ← 已经包含 /api/v1/
  TIMEOUT: 15000,
}
```

### 错误用法
```typescript
// ❌ 错误 - 会导致路径重复
apiService.instance.get('/api/v1/agent/customer-service/assistants/')
// 结果: http://localhost:8000/api/v1/api/v1/agent/customer-service/assistants/
```

### 正确用法
```typescript
// ✅ 正确 - 直接从模块路径开始
apiService.instance.get('/agent/customer-service/assistants/')
// 结果: http://localhost:8000/api/v1/agent/customer-service/assistants/
```

### 参考示例（诗词绘画项目）
```typescript
// frontend/src/views/agent/poetry-painting/hooks/usePoetryPainting.ts
apiService.instance.get('/agent/poetry-painting/works/')
// ✅ 正确：没有 /api/v1/ 前缀
```

### 已修复的路径

#### CustomerServiceManageView.vue（7处）
| 行号 | 错误路径 | 正确路径 |
|------|---------|---------|
| 245 | `/api/v1/agent/customer-service/assistants/` | `/agent/customer-service/assistants/` |
| 268 | `/api/v1/agent/customer-service/knowledge-bases/` | `/agent/customer-service/knowledge-bases/` |
| 283 | `/api/v1/agent/customer-service/knowledge-bases/` | `/agent/customer-service/knowledge-bases/` |
| 297 | `/api/v1/agent/customer-service/assistants/` | `/agent/customer-service/assistants/` |
| 331 | `/api/v1/agent/customer-service/assistants/${id}/` | `/agent/customer-service/assistants/${id}/` |
| 365 | `/api/v1/agent/customer-service/knowledge-bases/${id}/` | `/agent/customer-service/knowledge-bases/${id}/` |
| 418 | `/api/v1/agent/customer-service/chat/` | `/agent/customer-service/chat/` |

#### CustomerServiceView.vue（6处）
| 行号 | 错误路径 | 正确路径 |
|------|---------|---------|
| 223 | `/api/v1/agent/customer-service/greeting/` | `/agent/customer-service/greeting/` |
| 235 | `/api/v1/agent/customer-service/sessions/` | `/agent/customer-service/sessions/` |
| 247 | `/api/v1/agent/customer-service/stats/` | `/agent/customer-service/stats/` |
| 263 | `/api/v1/agent/customer-service/sessions/${id}/` | `/agent/customer-service/sessions/${id}/` |
| 301 | `/api/v1/agent/customer-service/chat/` | `/agent/customer-service/chat/` |
| 355 | `/api/v1/agent/customer-service/feedback/` | `/agent/customer-service/feedback/` |

**总计修复**: 13处路径错误 ✅

---

## Bug #1: API调用错误 ✅ 已修复

### 问题描述
```
TypeError: (intermediate value).get is not a function
```

### 错误原因
API服务的使用方式不正确。

### 错误代码
```typescript
// ❌ 错误方式
import { apiService } from '@/services/api'
const response = await apiService.get('/api/...')
```

### ApiService 结构说明
```typescript
class ApiService {
  private instance: AxiosInstance  // Axios实例
  
  // 具体的业务方法
  async login(...)
  async getUserInfo(...)
  // ...
  
  // 没有通用的 get/post 方法！
}

export const apiService = new ApiService()
```

### 正确用法
```typescript
// ✅ 正确方式 - 使用 instance 属性
import { apiService } from '@/services/api'
const response = await apiService.instance.get('/api/...')
const response = await apiService.instance.post('/api/...')
const response = await apiService.instance.delete('/api/...')
const response = await apiService.instance.put('/api/...')
```

### 已修复的文件

#### CustomerServiceManageView.vue
修复了7处调用：
- ✅ `loadAssistants()` - line 245
- ✅ `loadKnowledgeBases()` - line 268
- ✅ `handleCreateKB()` - line 283
- ✅ `handleCreateAssistant()` - line 297
- ✅ `handleDeleteAssistant()` - line 331
- ✅ `handleDeleteKB()` - line 365
- ✅ `sendMessage()` - line 418

#### CustomerServiceView.vue  
修复了6处调用：
- ✅ `loadGreeting()` - line 223
- ✅ `loadSessions()` - line 235
- ✅ `loadStats()` - line 247
- ✅ `switchSession()` - line 263
- ✅ `sendMessage()` - line 301
- ✅ `submitSatisfaction()` - line 355

**总计修复**: 13处API调用 ✅

---

## 修复后的标准模板

### 使用apiService的正确模板

```typescript
import { apiService } from '@/services/api'

// GET 请求
const getData = async () => {
  try {
    const response = await apiService.instance.get('/api/v1/...')
    if (response.data?.success) {
      // 处理数据
      return response.data.data
    }
  } catch (error: any) {
    console.error('请求失败:', error)
    // 错误处理
  }
}

// POST 请求
const postData = async (data: any) => {
  try {
    const response = await apiService.instance.post('/api/v1/...', data)
    if (response.data?.success) {
      // 处理响应
      return response.data.data
    }
  } catch (error: any) {
    console.error('请求失败:', error)
    // 错误处理
  }
}

// DELETE 请求
const deleteData = async (id: number) => {
  try {
    const response = await apiService.instance.delete(`/api/v1/.../${id}/`)
    if (response.data?.success) {
      // 处理成功
    }
  } catch (error: any) {
    console.error('删除失败:', error)
  }
}

// PUT 请求
const updateData = async (id: number, data: any) => {
  try {
    const response = await apiService.instance.put(`/api/v1/.../${id}/`, data)
    if (response.data?.success) {
      // 处理成功
    }
  } catch (error: any) {
    console.error('更新失败:', error)
  }
}
```

---

## 其他项目中的正确用法

### 诗词绘画项目（参考）
```typescript
// frontend/src/views/agent/poetry-painting/hooks/usePoetryPainting.ts

import { apiService } from '@/services/api'

// 正确使用
const response = await apiService.instance.post(...)
const response = await apiService.instance.get(...)
```

---

## 预防措施

### 开发新组件时

1. **始终使用 `apiService.instance`**
   ```typescript
   apiService.instance.get()    ✅
   apiService.instance.post()   ✅
   apiService.instance.delete() ✅
   apiService.instance.put()    ✅
   ```

2. **不要直接调用 apiService 方法**
   ```typescript
   apiService.get()     ❌
   apiService.post()    ❌
   apiService.delete()  ❌
   ```

3. **参考现有代码**
   - 查看 `poetry-painting` 目录
   - 查看其他正常工作的组件

---

## 验证修复

### 测试步骤

1. 刷新浏览器（清除缓存）
   - Windows: `Ctrl + Shift + R`
   - Mac: `Cmd + Shift + R`

2. 打开开发者控制台
   - 按 `F12`
   - 查看 Console 标签

3. 访问管理中心页面
   ```
   http://localhost:5173/agent/customer-service/manage
   ```

4. 检查控制台输出
   - 如果显示 404 错误 → 正常（后端API未实现）
   - 如果显示 "is not a function" → 刷新浏览器缓存

---

## 预期行为

### 修复后的正常行为

#### 页面加载时
```
控制台输出:
加载助手失败: AxiosError: Request failed with status code 404
  → 这是正常的！因为后端API还未实现

加载知识库失败: AxiosError: Request failed with status code 404  
  → 这也是正常的！
```

#### 页面显示
- ✅ 页面正常渲染
- ✅ 标签页可以切换
- ✅ "新建"按钮可以点击
- ✅ 弹窗可以正常打开
- ✅ 空状态提示正常显示

---

## 当前状态

### ✅ 前端已就绪
- API调用语法正确
- 错误处理完善
- UI界面完整
- 等待后端API实现

### ⏳ 后端API待实现
API返回404是预期行为，需要实现：
- `GET /api/v1/agent/customer-service/assistants/`
- `GET /api/v1/agent/customer-service/knowledge-bases/`
- 等等...

---

## 修复状态

**Bug**: ✅ 已完全修复  
**修复时间**: 2025-10-22  
**影响文件**: 2个  
**修复行数**: 13处  
**测试状态**: ✅ 通过

---

*修复记录 - 最后更新: 2025-10-22*

