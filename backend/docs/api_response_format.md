# 统一API返回格式文档

## 概述

本项目已实现统一的API返回格式，所有接口都遵循相同的响应结构，便于前端处理和后期维护。

## 返回格式结构

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "uuid-string"
}
```

### 字段说明

- **code**: 业务状态码
  - 200: 成功
  - 400: 客户端错误（参数错误等）
  - 401: 未授权
  - 403: 禁止访问
  - 404: 资源不存在
  - 500: 服务器内部错误

- **message**: 响应消息，用于前端显示给用户
- **data**: 实际数据内容
- **timestamp**: 响应时间戳
- **request_id**: 请求唯一标识，便于日志追踪

## 不同场景的返回示例

### 1. 成功响应（列表数据）

```json
{
  "code": 200,
  "message": "获取用户列表成功",
  "data": {
    "list": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  },
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "req-123456"
}
```

### 2. 成功响应（单个对象）

```json
{
  "code": 200,
  "message": "获取用户信息成功",
  "data": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "created_at": "2025-01-01T00:00:00Z"
  },
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "req-123457"
}
```

### 3. 创建成功响应

```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 2,
    "username": "newuser",
    "email": "newuser@example.com"
  },
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "req-123458"
}
```

### 4. 删除成功响应

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null,
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "req-123459"
}
```

### 5. 参数验证错误

```json
{
  "code": 400,
  "message": "参数验证失败",
  "data": {
    "errors": {
      "username": ["用户名不能为空"],
      "email": ["邮箱格式不正确"]
    }
  },
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "req-123460"
}
```

### 6. 认证错误

```json
{
  "code": 401,
  "message": "未认证，请先登录",
  "data": null,
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "req-123461"
}
```

### 7. 权限不足

```json
{
  "code": 403,
  "message": "权限不足",
  "data": null,
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "req-123462"
}
```

### 8. 资源不存在

```json
{
  "code": 404,
  "message": "资源不存在",
  "data": null,
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "req-123463"
}
```

### 9. 服务器内部错误

```json
{
  "code": 500,
  "message": "服务器内部错误",
  "data": null,
  "timestamp": "2025-01-08T19:00:00Z",
  "request_id": "req-123464"
}
```

## 实现特性

### 1. 自动判断数据类型

系统会自动判断返回的数据是单个对象还是列表：

- **单个对象**: 直接返回对象数据
- **列表数据**: 包装为带分页信息的格式

### 2. 统一异常处理

所有异常都会被统一处理并返回标准格式：

- DRF验证异常
- Django异常
- 自定义异常

### 3. 请求追踪

每个请求都会生成唯一的 `request_id`，便于：

- 日志追踪
- 问题排查
- 性能监控

### 4. 响应头信息

系统会在响应头中添加 `X-Request-ID`，方便调试。

## 使用方法

### 在视图中使用

```python
from core.response import StandardResponse

# 成功响应
return StandardResponse.success(
    data=serializer.data,
    message="操作成功",
    request_id=getattr(request, 'request_id', None)
)

# 错误响应
return StandardResponse.error(
    message="操作失败",
    code=400,
    data={'field': 'error_message'},
    request_id=getattr(request, 'request_id', None)
)
```

### 使用标准化视图类

```python
from core.views import StandardModelViewSet

class UserViewSet(StandardModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # 自动使用统一返回格式
```

## 前端处理建议

```typescript
interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  timestamp: string;
  request_id: string;
}

// 处理响应
const handleResponse = (response: ApiResponse) => {
  if (response.code === 200) {
    // 成功处理
    return response.data;
  } else {
    // 错误处理
    throw new Error(response.message);
  }
};
```

## 配置说明

统一返回格式通过以下组件实现：

1. **StandardResponse**: 响应工具类
2. **StandardPagination**: 标准分页器
3. **custom_exception_handler**: 异常处理器
4. **RequestIDMiddleware**: 请求ID中间件
5. **StandardModelViewSet**: 标准化视图集

所有配置已在 `settings.py` 中完成，无需额外配置即可使用。