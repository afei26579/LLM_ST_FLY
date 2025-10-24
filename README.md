# LLM ST FLY - 智能管理系统

一个基于 Django + Vue.js 的现代化智能管理系统，集成了多种 AI 功能、用户管理、智能体系统等核心功能。

## 🚀 项目特性

- **现代化技术栈**: Django 5.2.3 + Vue.js 3 + TypeScript
- **用户认证系统**: JWT 认证，支持用户注册、登录、权限管理
- **多种 AI 功能**: 
  - 智能对话（AI Chat）- 支持流式输出、深度思考模式
  - AI 阅读理解
  - AI 图像生成
  - AI 音频处理（语音转文字、文字转语音、语音克隆）
  - AI 视频生成（文生视频、图生视频）
- **智能体系统**:
  - 旅行助手 - 智能旅行规划
  - 诗画创作 - 古诗词与绘画结合
  - 客服助手 - 基于 LangGraph 的智能客服（支持知识库、向量检索）
- **完整的用户管理**: 用户 CRUD 操作，角色权限管理
- **响应式设计**: 支持桌面端和移动端访问
- **多主题支持**: 浅色、深色、未来科技三种主题
- **统一 API 规范**: 标准化的响应格式
- **完整的日志系统**: 系统日志、用户日志、API 日志、错误日志

## 📁 项目结构

```
llm_st_fly/
├── backend/                        # Django 后端
│   ├── core/                       # 核心配置
│   │   ├── settings.py             # Django 设置
│   │   ├── urls.py                 # 主路由配置
│   │   ├── response.py             # 统一响应格式
│   │   ├── views.py                # 基础视图类
│   │   ├── middleware.py           # 中间件
│   │   └── exceptions.py           # 异常处理
│   ├── users/                      # 用户管理模块
│   │   ├── models.py               # 用户模型
│   │   ├── views.py                # 用户视图
│   │   ├── serializers.py          # 序列化器
│   │   └── permissions.py          # 权限管理
│   ├── chat/                       # 聊天功能模块
│   │   ├── ai-chat/                # AI 对话
│   │   ├── ai-reading/             # AI 阅读
│   │   ├── ai-image/               # AI 图像生成
│   │   ├── ai-audio/               # AI 音频处理
│   │   ├── ai-video/               # AI 视频生成
│   │   ├── models.py               # 对话和消息模型
│   │   ├── views.py                # 聊天视图
│   │   └── services.py             # AI 服务
│   ├── agent/                      # 智能体模块
│   │   ├── customer_service/       # 客服助手
│   │   │   ├── langgraph_service.py    # LangGraph 工作流
│   │   │   ├── vector_service.py       # 向量检索
│   │   │   ├── document_processor.py   # 文档处理
│   │   │   ├── models.py               # 知识库模型
│   │   │   └── views_extended.py       # 扩展视图
│   │   ├── travel_assistant/       # 旅行助手
│   │   ├── poetry_painting/        # 诗画创作
│   │   ├── models.py               # 智能体模型
│   │   └── views.py                # 智能体视图
│   ├── logs/                       # 日志管理模块
│   │   ├── models.py               # 日志模型
│   │   ├── middleware.py           # 日志中间件
│   │   └── views.py                # 日志视图
│   ├── docs/                       # API 文档
│   │   └── api_response_format.md  # 响应格式说明
│   ├── media/                      # 媒体文件存储
│   ├── requirements.txt            # Python 依赖
│   ├── manage.py                   # Django 管理脚本
│   └── gunicorn_config.py          # Gunicorn 配置
├── frontend/                       # Vue.js 前端
│   ├── src/
│   │   ├── components/             # Vue 组件
│   │   ├── views/                  # 页面视图
│   │   │   ├── ai-chat/            # AI 对话页面
│   │   │   ├── ai-reading/         # AI 阅读页面
│   │   │   ├── ai-image/           # AI 图像页面
│   │   │   ├── ai-audio/           # AI 音频页面
│   │   │   ├── ai-video/           # AI 视频页面
│   │   │   ├── agent/              # 智能体页面
│   │   │   │   ├── travel-assistant/      # 旅行助手
│   │   │   │   ├── poetry-painting/       # 诗画创作
│   │   │   │   └── customer-service/      # 客服助手
│   │   │   └── system/             # 系统管理页面
│   │   ├── router/                 # 路由配置
│   │   ├── stores/                 # Pinia 状态管理
│   │   │   ├── auth.ts             # 认证状态
│   │   │   ├── theme.ts            # 主题状态
│   │   │   └── chat.ts             # 聊天状态
│   │   ├── services/               # API 服务
│   │   │   └── api.ts              # API 封装
│   │   ├── styles/                 # 样式文件
│   │   │   └── themes.css          # 主题样式
│   │   ├── utils/                  # 工具函数
│   │   └── main.ts                 # 应用入口
│   ├── package.json                # 前端依赖
│   └── vite.config.ts              # Vite 配置
├── start-dev.bat                   # Windows 启动脚本
├── start-dev.sh                    # Linux/Mac 启动脚本
├── 开发准则.md                     # 开发规范文档
├── 接口说明.md                     # API 接口文档
├── 前端主题设置.md                 # 主题配置文档
└── README.md                       # 项目说明
```

## 🛠️ 技术栈

### 后端
- **框架**: Django 5.2.3
- **数据库**: PostgreSQL / MySQL
- **认证**: Django REST Framework + JWT
- **API 文档**: drf-spectacular
- **部署**: Gunicorn + Nginx
- **AI 集成**: 
  - DashScope API (阿里云通义千问)
  - OpenAI API
  - LangChain / LangGraph
  - ChromaDB (向量数据库)
- **文档处理**: PyPDF2, python-docx, pandas, openpyxl
- **其他**: django-cors-headers, django-environ

### 前端
- **框架**: Vue.js 3.5.13 + TypeScript 5.8.0
- **构建工具**: Vite 6.2.4
- **状态管理**: Pinia 3.0.1
- **路由**: Vue Router 4.5.0
- **HTTP 客户端**: Axios 1.9.0
- **UI 通知**: Vue-Toastification 2.0.0-rc.5
- **包管理器**: PNPM 10.8.1

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 16+
- PostgreSQL 14+ / MySQL 8.0+
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
# - SECRET_KEY: Django 密钥
# - PSQL_PWD: PostgreSQL 密码
# - DASHSCOPE_API_KEY: DashScope API 密钥
# - EMAIL_HOST_PASSWORD: 邮箱授权码
```

5. **数据库设置**
```sql
-- 创建 PostgreSQL 数据库
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

### 一键启动（推荐）

项目提供了一键启动脚本：

**Windows:**
```bash
start-dev.bat
```

**Linux/Mac:**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

## 📋 功能模块

### 用户管理
- ✅ 用户模型：扩展 Django 用户模型，支持头像、角色、个人信息等
- ✅ 角色权限：管理员、工作人员、普通用户三级权限
- ✅ 用户资料：支持个人信息、地址、联系方式等完整资料
- ✅ 登录追踪：记录用户登录 IP 和时间

### AI 对话系统
- ✅ 流式输出：支持实时流式返回
- ✅ 深度思考：集成思考过程展示
- ✅ 联网搜索：支持实时网络信息检索
- ✅ 对话管理：支持多对话会话管理、置顶、重命名
- ✅ 消息历史：完整的消息历史记录
- ✅ 令牌统计：跟踪 API 使用情况

### AI 图像生成
- ✅ 文生图：基于文本描述生成图像
- ✅ 提示词增强：自动优化生成效果
- ✅ 风格控制：多种风格、镜头、角度、光照选项
- ✅ 图像编辑：背景编辑、风格重绘、合并等

### AI 音频处理
- ✅ 语音转文字：支持多语言识别
- ✅ 文字转语音：多种音色选择
- ✅ 语音克隆：基于参考音频克隆声音
- ✅ 历史记录：完整的处理历史

### AI 视频生成
- ✅ 文生视频：基于文本描述生成视频
- ✅ 图生视频：图片转视频
- ✅ 风格预设：多种风格模板
- ✅ 异步处理：支持长时间任务

### 智能体系统

#### 旅行助手
- ✅ 智能行程规划
- ✅ 景点推荐
- ✅ 路线优化

#### 诗画创作
- ✅ 古诗词生成
- ✅ AI 绘画配图
- ✅ 诗画结合展示

#### 客服助手（基于 LangGraph）
- ✅ 知识库管理：支持多格式文档上传（PDF、Word、Excel、TXT）
- ✅ 向量检索：基于 ChromaDB 的语义搜索
- ✅ 文档分块：智能文档分块处理
- ✅ 意图识别：智能识别用户意图
- ✅ 助手配置：自定义助手人设和行为
- ✅ 推荐问题：基于知识库自动生成推荐问题

### 系统管理
- ✅ 用户管理：用户 CRUD 操作，角色分配
- ✅ 角色管理：角色创建、编辑、删除
- ✅ 权限管理：基于 Django 权限系统的细粒度权限控制
- ✅ 日志管理：系统日志、用户日志、API 日志、错误日志

### 主题系统
- ✅ 三种主题：浅色、深色、未来科技
- ✅ 实时切换：无需刷新页面
- ✅ 持久化：主题选择自动保存
- ✅ 完整适配：所有组件完全适配三种主题

## 🌐 API 接口

### 认证相关
- `POST /api/v1/auth/login/` - 用户登录
- `POST /api/v1/auth/register/` - 用户注册
- `POST /api/v1/auth/token/` - 获取 JWT 令牌
- `POST /api/v1/auth/token/refresh/` - 刷新令牌
- `POST /api/v1/auth/token/verify/` - 验证令牌

### 用户管理
- `GET /api/v1/auth/users/` - 获取用户列表
- `POST /api/v1/auth/users/` - 创建用户
- `GET /api/v1/auth/users/{id}/` - 获取用户详情
- `PUT /api/v1/auth/users/{id}/` - 更新用户
- `DELETE /api/v1/auth/users/{id}/` - 删除用户
- `GET /api/v1/auth/users/me/` - 获取当前用户信息
- `PUT /api/v1/auth/users/me/` - 更新当前用户信息

### AI 对话
- `POST /api/v1/chat/ai-chat/stream-chat/` - 流式对话（推荐）
- `POST /api/v1/chat/send/` - 发送消息
- `GET /api/v1/chat/conversations/` - 获取对话列表
- `POST /api/v1/chat/conversations/` - 创建对话
- `DELETE /api/v1/chat/conversations/{id}/` - 删除对话
- `POST /api/v1/chat/conversations/{id}/pin/` - 置顶对话
- `PATCH /api/v1/chat/conversations/{id}/rename/` - 重命名对话

### AI 图像生成
- `POST /api/v1/ai-image/generate/` - 生成图像
- `GET /api/v1/ai-image/presets/` - 获取预设参数
- `GET /api/v1/ai-image/history/` - 获取历史记录

### AI 音频处理
- `POST /api/v1/chat/ai-audio/speech-to-text/` - 语音转文字
- `POST /api/v1/chat/ai-audio/text-to-speech/` - 文字转语音
- `POST /api/v1/chat/ai-audio/voice-clone/` - 语音克隆

### AI 视频生成
- `POST /api/v1/chat/ai-video/text-to-video/` - 文生视频
- `POST /api/v1/chat/ai-video/image-to-video/` - 图生视频
- `GET /api/v1/chat/ai-video/history/` - 获取历史记录

### 智能体 - 客服助手
- `GET /api/v1/agent/customer-service/assistants/` - 获取助手列表
- `POST /api/v1/agent/customer-service/assistants/` - 创建助手
- `GET /api/v1/agent/customer-service/knowledge-bases/` - 获取知识库列表
- `POST /api/v1/agent/customer-service/knowledge-bases/` - 创建知识库
- `POST /api/v1/agent/customer-service/chat/` - 客服对话
- `POST /api/v1/agent/customer-service/recommended-questions/` - 获取推荐问题

详细的 API 文档请查看：[接口说明.md](接口说明.md)

## 🎯 前端路由

- `/` - 首页（重定向到 AI 对话）
- `/login` - 登录页面
- `/about` - 关于页面

**AI 功能：**
- `/ai-chat` - AI 对话
- `/ai-reading` - AI 阅读
- `/ai-image` - AI 图像生成
- `/ai-audio` - AI 音频处理
- `/ai-video` - AI 视频生成

**智能体：**
- `/agent/travel-assistant` - 旅行助手
- `/agent/poetry-painting` - 诗画创作
- `/agent/customer-service` - 客服对话
- `/agent/customer-service/manage` - 客服管理

**系统管理：**
- `/users` - 用户管理
- `/roles` - 角色管理
- `/permissions` - 权限管理
- `/logs` - 日志管理
- `/logs/system` - 系统日志
- `/logs/user` - 用户日志
- `/logs/api` - API 日志
- `/logs/error` - 错误日志

## 📖 API 文档

访问 `http://localhost:8000/api/schema/swagger-ui/` 查看完整的 API 文档（由 drf-spectacular 自动生成）。

## 🔧 开发规范

详细的开发规范请查看：[开发准则.md](开发准则.md)

## 🎨 主题设置

详细的主题配置和使用说明请查看：[前端主题设置.md](前端主题设置.md)

## 🚀 部署

### 生产环境配置

1. **后端部署**
```bash
# 使用生产环境配置
export DJANGO_ENV=production

# 收集静态文件
python manage.py collectstatic

# 使用 Gunicorn 启动
gunicorn -c gunicorn_config.py core.wsgi:application
```

2. **前端部署**
```bash
# 构建生产版本
pnpm build

# 部署到 Web 服务器
# 将 dist 目录内容部署到 Nginx 等 Web 服务器
```

### 环境变量

生产环境需要配置的关键环境变量：
- `SECRET_KEY`: Django 安全密钥
- `DEBUG`: 设置为 False
- `ALLOWED_HOSTS`: 允许的主机列表
- `PSQL_PWD`: 数据库密码
- `DASHSCOPE_API_KEY`: AI API 密钥
- `EMAIL_HOST_PASSWORD`: 邮件服务密码
- `FRONTEND_URL`: 前端地址

## 📝 项目亮点

1. **统一响应格式**：所有 API 接口遵循统一的响应结构
2. **流式输出**：AI 对话支持流式返回，提升用户体验
3. **向量检索**：客服助手基于 ChromaDB 实现语义搜索
4. **文档处理**：支持多格式文档的智能分块和向量化
5. **多主题支持**：三种精美主题，完全适配所有组件
6. **完整的日志系统**：全方位的日志记录和追踪
7. **代码规范**：遵循最佳实践，代码结构清晰

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目地址: [https://github.com/afei26579/LLM_ST_FLY/]
- 问题反馈: [Issues]
- 邮箱: 631008153@qq.com

## 📚 相关文档

- [开发准则.md](开发准则.md) - 开发规范和最佳实践
- [接口说明.md](接口说明.md) - API 接口详细文档
- [前端主题设置.md](前端主题设置.md) - 主题配置和使用指南
- [backend/docs/api_response_format.md](backend/docs/api_response_format.md) - API 响应格式说明

---

**注意**: 请确保在生产环境中正确配置所有环境变量，特别是数据库连接和 API 密钥等敏感信息。
