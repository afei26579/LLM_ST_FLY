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
│   ├── public/       # 公共资源
│   ├── package.json  # 前端依赖配置
│   └── vite.config.ts # Vite配置
├── backend/          # Django后端项目
│   ├── core/         # 核心配置
│   ├── users/        # 用户认证与权限管理
│   ├── tools/        # 工具和实用函数
│   ├── media/        # 媒体文件
│   └── requirements.txt # 后端依赖配置
└── venv/             # Python虚拟环境
```

## 技术栈

### 前端
- Vue 3 (v3.5.13)
- Vue Router (v4.5.0)
- Pinia 状态管理 (v3.0.1)
- TypeScript (v5.8.0)
- Vite (v6.2.4)
- Vue-Toastification (v2.0.0-rc.5)
- Axios (v1.9.0)

### 后端
- Django (v5.2.3)
- Django REST framework (v3.16.0)
- JWT认证 (djangorestframework_simplejwt v5.5.0)
- MySQL数据库 (mysqlclient v2.2.7)
- Django CORS Headers (v4.7.0)
- DRF Spectacular (API文档, v0.28.0)

## 功能特性

- 用户认证（登录/注册）
- 用户权限管理
- JWT令牌认证
- 响应式界面
- API文档自动生成

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
访问 `http://localhost:8000/docs/` 查看API文档（由DRF Spectacular自动生成）。

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

## 开发工具
- PNPM (v10.8.1) - 包管理器
- ESLint (v9.22.0) - 代码检查
- Prettier (v3.5.3) - 代码格式化
- Vue DevTools - Vue开发工具 