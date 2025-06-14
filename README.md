# Web前后端分离项目

这是一个前后端分离的Web项目，前端使用Vue3，后端使用Django。

## 项目结构

```
llm_st_fly/
├── frontend/         # Vue3前端项目
│   ├── src/          # 源代码
│   │   ├── assets/   # 静态资源
│   │   ├── components/ # 组件
│   │   ├── router/   # 路由配置
│   │   ├── stores/   # Pinia状态管理
│   │   └── views/    # 页面视图
│   └── ...
├── backend/          # Django后端项目
│   ├── core/         # 核心配置
│   ├── users/        # 用户认证与权限管理
│   └── ...
└── venv/             # Python虚拟环境
```

## 技术栈

### 前端
- Vue 3
- Vue Router
- Pinia 状态管理
- TypeScript

### 后端
- Django
- Django REST framework
- JWT认证
- MySQL数据库

## 功能特性

- 用户认证（登录/注册）
- 用户权限管理
- JWT令牌认证
- 响应式界面

## 快速开始

### 后端设置
1. 激活虚拟环境
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

3. 创建数据库
```sql
CREATE DATABASE llm_st_fly CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. 迁移数据库
```bash
python manage.py migrate
```

5. 创建超级用户
```bash
python manage.py createsuperuser
```

6. 运行开发服务器
```bash
python manage.py runserver
```

### 前端设置
1. 安装依赖
```bash
cd frontend
pnpm install
```

2. 运行开发服务器
```bash
pnpm dev
```

3. 构建生产版本
```bash
pnpm build
```

## API文档
访问 `http://localhost:8000/docs/` 查看API文档。

## 主要路由
- 前端: `http://localhost:5173`
  - `/login` - 登录页面
  - `/` - 主页面 (需要认证)
  - `/about` - 关于页面 (需要认证)

- 后端: `http://localhost:8000`
  - `/admin/` - Django管理界面
  - `/api/v1/auth/login/` - 登录API
  - `/api/v1/auth/register/` - 注册API
  - `/api/v1/auth/users/` - 用户管理API 