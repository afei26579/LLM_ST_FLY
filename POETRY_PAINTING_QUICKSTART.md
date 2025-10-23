# 诗词绘画智能体 - 快速启动指南

## 🚀 3 分钟快速启动

### 步骤 1: 安装依赖

```bash
# 激活虚拟环境（Windows PowerShell）
venv\Scripts\activate

# 安装 LangGraph 相关依赖
pip install langgraph langchain
```

### 步骤 2: 数据库迁移

```bash
# 进入后端目录
cd backend

# 创建迁移文件
python manage.py makemigrations agent

# 执行迁移
python manage.py migrate
```

### 步骤 3: 配置 API 密钥

确认 `backend/.env` 或 `backend/.env.development` 中已配置：

```env
DASHSCOPE_API_KEY=your_api_key_here
```

### 步骤 4: 启动服务

```bash
# 后端（在 backend 目录）
python manage.py runserver

# 前端（新终端窗口，在 frontend 目录）
pnpm dev
```

### 步骤 5: 访问应用

打开浏览器访问: http://localhost:5173/agent/poetry-painting

---

## 📝 第一次使用

1. **输入创作主题**: 例如"春江花月夜"、"秋日登高"
2. **选择风格**: 
   - 诗词风格: 豪放/婉约/田园/边塞/山水
   - 诗词格式: 五绝/七绝/五律/七律/词
   - 绘画风格: 水墨/工笔/油画/水彩/现代
3. **点击"开始创作"**: 等待 AI 生成诗词和画作
4. **查看结果**: 欣赏诗词、画作和赏析
5. **优化作品**: 如果不满意，输入优化建议进行迭代

---

## 🎯 示例主题

### 推荐主题
- 春江花月夜
- 秋日登高远望
- 梅花傲雪
- 江南水乡
- 塞外孤烟
- 月下独酌
- 山间竹林
- 雨后初霁

### 风格搭配建议

| 主题 | 诗词风格 | 绘画风格 |
|------|---------|---------|
| 春江花月夜 | 婉约 | 水墨画 |
| 秋日登高 | 豪放 | 水墨画 |
| 梅花傲雪 | 山水 | 工笔画 |
| 塞外孤烟 | 边塞 | 油画风格 |
| 江南水乡 | 田园 | 水彩风格 |

---

## 🔍 API 测试

### 使用 curl 测试

```bash
# 创作作品
curl -X POST http://localhost:8000/api/v1/agent/poetry-painting/create-work/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "春江花月夜",
    "poetry_style": "婉约",
    "poetry_format": "seven_jueju",
    "painting_style": "chinese_ink"
  }'
```

### 使用 Python 测试

```python
import requests

# 登录获取 token
login_response = requests.post(
    'http://localhost:8000/api/v1/auth/login/',
    json={'username': 'your_username', 'password': 'your_password'}
)
token = login_response.json()['access']

# 创作诗词画作
response = requests.post(
    'http://localhost:8000/api/v1/agent/poetry-painting/create-work/',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'input': '春江花月夜',
        'poetry_style': '婉约',
        'poetry_format': 'seven_jueju',
        'painting_style': 'chinese_ink'
    }
)

print(response.json())
```

---

## 🐛 常见问题

### Q: 创作失败，提示 API 错误
**A**: 检查 DASHSCOPE_API_KEY 是否正确配置

### Q: 图片无法显示
**A**: 
1. 检查 `MEDIA_ROOT` 和 `MEDIA_URL` 配置
2. 确保目录有写入权限
3. 查看后端日志获取详细错误

### Q: 诗词格式不符合要求
**A**: 调整提示词温度参数或多次生成选择最佳结果

### Q: 前端显示空白
**A**: 
1. 检查前端控制台错误
2. 确认后端 CORS 配置
3. 检查路由配置是否正确

---

## 📊 性能建议

### 开发环境
- 诗词生成: ~5-10秒
- 图像生成: ~10-15秒
- 总耗时: ~15-25秒

### 优化建议
1. **使用异步处理**: 考虑使用 Celery
2. **添加缓存**: Redis 缓存常用结果
3. **批量生成**: 支持一次生成多个作品

---

## 🎨 功能清单

### ✅ 已实现
- [x] 诗词创作（5种风格，5种格式）
- [x] 意境绘画（5种绘画风格）
- [x] 诗词赏析（意象、情感、修辞、典故）
- [x] 迭代优化
- [x] 作品评分
- [x] 作品画廊
- [x] 对话管理
- [x] 图片下载

### 🔜 计划中
- [ ] 图生诗功能
- [ ] 诗词朗诵（TTS）
- [ ] 作品分享卡片
- [ ] 社区展示墙
- [ ] 收藏功能

---

## 📚 相关文档

- [完整使用说明](backend/agent/poetry_painting/README.md)
- [实现总结](POETRY_PAINTING_IMPLEMENTATION_SUMMARY.md)
- [开发指导](开发指导.md)

---

## 🎉 开始创作吧！

访问: http://localhost:5173/agent/poetry-painting

让 AI 为您创作美妙的诗词和画作！🎨✨

---

**更新时间**: 2025-10-21

