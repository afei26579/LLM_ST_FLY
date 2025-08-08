# LLM ST FLY - 智能管理系统

一个基于Django + Vue.js的现代化智能管理系统，集成了用户管理、AI聊天功能和系统管理等核心功能。

## 🚀 项目特性

- **现代化技术栈**: Django 5.2.3 + Vue.js 3 + TypeScript
- **用户认证系统**: JWT认证，支持用户注册、登录、权限管理
- **智能聊天功能**: 集成DashScope API，支持AI对话
- **用户管理**: 完整的用户CRUD操作，支持角色权限管理
- **响应式设计**: 支持桌面端和移动端访问
- **API文档**: 完整的OpenAPI 3.0规范文档
- **多环境配置**: 支持开发、生产环境配置

## 📁 项目结构

```
llm_st_fly/
├── backend/                 # Django后端
│   ├── core/               # 核心配置
│   │   ├── settings.py     # Django设置
│   │   ├── urls.py         # 主路由配置
│   │   └── wsgi.py         # WSGI配置
│   ├── users/              # 用户管理模块
│   │   ├── models.py       # 用户模型
│   │   ├── views.py        # 用户视图
│   │   ├── serializers.py  # 序列化器
│   │   └── middleware.py   # 中间件
│   ├── chat/               # 聊天功能模块
│   │   ├── models.py       # 对话和消息模型
│   │   ├── views.py        # 聊天视图
│   │   └── serializers.py  # 聊天序列化器
│   ├── tools/              # 工具模块
│   ├── test/               # 测试文件
│   ├── media/              # 媒体文件存储
│   ├── .env.development    # 开发环境配置
│   ├── .env.production     # 生产环境配置
│   ├── .env.example        # 环境变量模板
│   ├── requirements.txt    # Python依赖
│   ├── manage.py          # Django管理脚本
│   ├── gunicorn_config.py # Gunicorn配置
│   └── schema.yml         # API文档
├── frontend/               # Vue.js前端
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   │   ├── system/    # 系统管理页面
│   │   │   ├── HomeView.vue
│   │   │   ├── LoginView.vue
│   │   │   └── AboutView.vue
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # Pinia状态管理
│   │   ├── services/      # API服务
│   │   ├── assets/        # 静态资源
│   │   └── main.ts        # 应用入口
│   ├── public/            # 公共静态资源
│   ├── package.json       # 前端依赖
│   └── vite.config.ts     # Vite配置
└── README.md              # 项目说明
```

## 🛠️ 技术栈

### 后端
- **框架**: Django 5.2.3
- **数据库**: PostgreSQL (支持MySQL)
- **认证**: Django REST Framework + JWT
- **API文档**: drf-spectacular
- **部署**: Gunicorn + Nginx
- **AI集成**: DashScope API
- **其他**: django-cors-headers, django-environ

### 前端
- **框架**: Vue.js 3.5.13 + TypeScript 5.8.0
- **构建工具**: Vite 6.2.4
- **状态管理**: Pinia 3.0.1
- **路由**: Vue Router 4.5.0
- **HTTP客户端**: Axios 1.9.0
- **UI通知**: Vue-Toastification 2.0.0-rc.5
- **包管理器**: PNPM 10.8.1

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 16+
- PostgreSQL 14+
- PNPM (推荐)

### 后端设置

1. **克隆项目**
```bash
git clone <repository-url>
cd llm_st_fly
```

2. **创建虚拟环境**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **环境配置**
```bash
# 复制环境变量模板
cp .env.example .env.development

# 编辑 .env.development 文件，填入真实配置：
# - SECRET_KEY: Django密钥
# - PSQL_PWD: PostgreSQL密码
# - DASHSCOPE_API_KEY: DashScope API密钥
# - EMAIL_HOST_PASSWORD: 邮箱授权码
```

5. **数据库设置**
```sql
-- 创建PostgreSQL数据库
CREATE DATABASE llm_st_fly;
```

```bash
# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

6. **启动开发服务器**
```bash
python manage.py runserver
```

### 前端设置

1. **安装依赖**
```bash
cd frontend
pnpm install
```

2. **启动开发服务器**
```bash
pnpm dev
```

3. **构建生产版本**
```bash
pnpm build
```

## 📋 功能模块

### 用户管理
- **用户模型**: 扩展Django用户模型，支持头像、角色、个人信息等
- **角色权限**: 管理员、工作人员、普通用户三级权限
- **用户资料**: 支持个人信息、地址、联系方式等完整资料
- **登录追踪**: 记录用户登录IP和时间

### 聊天系统
- **对话管理**: 支持多对话会话管理
- **消息存储**: 完整的消息历史记录
- **AI集成**: 集成DashScope API实现智能对话
- **令牌统计**: 跟踪API使用情况

### 系统管理
- **用户管理**: 用户CRUD操作，角色分配
- **权限管理**: 基于Django权限系统的细粒度权限控制
- **系统监控**: 用户活动追踪

## 🌐 API接口

### 认证相关
- `POST /api/v1/auth/login/` - 用户登录
- `POST /api/v1/auth/register/` - 用户注册
- `POST /api/v1/auth/token/` - 获取JWT令牌
- `POST /api/v1/auth/token/refresh/` - 刷新令牌
- `POST /api/v1/auth/token/verify/` - 验证令牌

### 用户管理
- `GET /api/v1/auth/users/` - 获取用户列表
- `POST /api/v1/auth/users/` - 创建用户
- `GET /api/v1/auth/users/{id}/` - 获取用户详情
- `PUT /api/v1/auth/users/{id}/` - 更新用户
- `DELETE /api/v1/auth/users/{id}/` - 删除用户
- `GET /api/v1/auth/users/me/` - 获取当前用户信息

## 🎯 前端路由

- `/` - 首页 (需要认证)
- `/login` - 登录页面
- `/about` - 关于页面 (需要认证)
- `/verify-email` - 邮箱验证页面
- `/users` - 用户管理 (需要认证)
- `/roles` - 角色管理 (需要认证)
- `/permissions` - 权限管理 (需要认证)

## 📖 API文档

访问 `http://localhost:8000/docs/` 查看完整的API文档（由drf-spectacular自动生成）。

## 🔧 开发工具

### 后端
- **Django Admin**: `http://localhost:8000/admin/`
- **API Schema**: `http://localhost:8000/schema/`
- **环境管理**: django-environ

### 前端
- **ESLint**: 代码检查
- **Prettier**: 代码格式化
- **TypeScript**: 类型检查
- **Vue DevTools**: Vue开发工具

## 🚀 部署

### 生产环境配置

1. **后端部署**
```bash
# 使用生产环境配置
export DJANGO_ENV=production

# 收集静态文件
python manage.py collectstatic

# 使用Gunicorn启动
gunicorn -c gunicorn_config.py core.wsgi:application
```

2. **前端部署**
```bash
# 构建生产版本
pnpm build

# 部署到Web服务器
# 将dist目录内容部署到Nginx等Web服务器
```

### 环境变量

生产环境需要配置的关键环境变量：
- `SECRET_KEY`: Django安全密钥
- `DEBUG`: 设置为False
- `ALLOWED_HOSTS`: 允许的主机列表
- `PSQL_PWD`: 数据库密码
- `DASHSCOPE_API_KEY`: AI API密钥
- `EMAIL_HOST_PASSWORD`: 邮件服务密码
- `FRONTEND_URL`: 前端地址

## 📝 开发规范

- 后端遵循Django最佳实践
- 前端使用Vue 3 Composition API
- 代码风格统一使用ESLint + Prettier
- 提交信息遵循Conventional Commits规范
- API设计遵循RESTful原则

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: 490095023@qq.com

---

**注意**: 请确保在生产环境中正确配置所有环境变量，特别是数据库连接和API密钥等敏感信息。