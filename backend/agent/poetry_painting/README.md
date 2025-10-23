# 诗词绘画智能体 - 使用说明

基于 LangGraph 的多模态 AI 创作助手

---

## 📋 功能概述

诗词绘画智能体是一个创新的多模态 AI 应用，能够：

- 🖋️ **诗词创作**: 根据用户主题创作各种格式的古诗词（五言/七言绝句、律诗、词牌）
- 🎨 **意境绘画**: 将诗词意境转化为视觉图像（使用 qwen-image-plus 模型）
- 📖 **诗词鉴赏**: 深入解析诗词的意象、典故、修辞手法
- 🔄 **迭代优化**: 支持基于用户反馈的诗词和画作优化

---

## 🏗️ 技术架构

### 核心技术栈

- **LangGraph**: 状态机工作流管理
- **通义千问 (qwen-max)**: 诗词创作和分析
- **通义万相 (qwen-image-plus)**: 图像生成
- **Django + DRF**: 后端 API
- **Vue 3 + TypeScript**: 前端界面

### LangGraph 工作流

```
用户输入
   ↓
意图识别节点
   ↓
诗词创作节点
   ↓
诗词分析节点
   ↓
绘画生成节点
   ↓
结果整合节点
   ↓
用户反馈？
   ├─ 满意 → 完成
   └─ 不满意 → 迭代优化节点 → 重新生成
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 后端依赖
pip install langgraph langchain dashscope

# 确保已安装其他依赖
pip install -r backend/requirements.txt
```

### 2. 数据库迁移

```bash
cd backend
python manage.py makemigrations agent
python manage.py migrate
```

### 3. 配置 API 密钥

在 `backend/.env` 中配置：

```env
DASHSCOPE_API_KEY=your_dashscope_api_key
```

### 4. 启动服务

```bash
# 后端
cd backend
python manage.py runserver

# 前端
cd frontend
pnpm dev
```

### 5. 访问应用

访问: http://localhost:5173/agent/poetry-painting

---

## 📡 API 接口

### 创作诗词画作

**POST** `/api/v1/agent/poetry-painting/create-work/`

**请求参数:**
```json
{
  "input": "春江花月夜",
  "poetry_style": "婉约",
  "poetry_format": "seven_jueju",
  "painting_style": "chinese_ink",
  "conversation_id": null
}
```

**响应示例:**
```json
{
  "success": true,
  "message": "创作成功！",
  "data": {
    "work_id": 1,
    "conversation_id": 1,
    "result": {
      "poetry": {
        "title": "春江花月夜",
        "content": "春江潮水连海平，\n海上明月共潮生。\n滟滟随波千万里，\n何处春江无月明。",
        "style": "婉约",
        "format": "seven_jueju",
        "analysis": {
          "imagery": [...],
          "emotion": "柔美静谧",
          "rhetoric": ["对仗", "比喻"]
        }
      },
      "painting": {
        "url": "https://...",
        "style": "chinese_ink",
        "description": "春江夜景，月光如水..."
      }
    }
  }
}
```

### 迭代优化作品

**POST** `/api/v1/agent/poetry-painting/{work_id}/iterate/`

**请求参数:**
```json
{
  "feedback": "希望诗词风格更豪放一些",
  "type": "both"
}
```

### 获取作品列表

**GET** `/api/v1/agent/poetry-painting/works/`

### 评分作品

**POST** `/api/v1/agent/poetry-painting/{work_id}/rate/`

**请求参数:**
```json
{
  "rating": 5
}
```

---

## 🎯 使用示例

### 示例 1: 创作山水诗词

```
输入主题: "秋日登高远望"
诗词风格: 豪放
诗词格式: 七言律诗
绘画风格: 水墨画

结果:
- 生成豪放风格的七言律诗
- 分析诗词意境、意象、修辞
- 生成水墨风格的山水画
```

### 示例 2: 迭代优化

```
原作品: "春江花月夜"（婉约风格）
优化反馈: "画面色彩更淡雅，增加月光效果"

结果:
- 保持原诗词内容
- 重新生成优化后的画作
```

---

## 🎨 风格选项

### 诗词风格

- **豪放**: 气势磅礴，意境开阔
- **婉约**: 细腻柔美，含蓄隽永
- **田园**: 清新自然，恬淡闲适
- **边塞**: 雄浑壮阔，慷慨悲壮
- **山水**: 描绘自然，意境清幽

### 诗词格式

- **五言绝句**: 4句，每句5字
- **七言绝句**: 4句，每句7字
- **五言律诗**: 8句，每句5字
- **七言律诗**: 8句，每句7字
- **词**: 长短句，讲究韵律

### 绘画风格

- **水墨画**: 淡雅飘逸，留白艺术
- **工笔画**: 细腻精致，色彩典雅
- **油画风格**: 色彩浓郁，笔触明显
- **水彩风格**: 清新淡雅，水色交融
- **现代艺术**: 抽象表现，构图创新

---

## 📊 数据模型

### PoetryPaintingConversation (对话)

- `user`: 用户
- `title`: 对话标题
- `created_at`: 创建时间
- `updated_at`: 更新时间

### PoetryPaintingWork (作品)

- `conversation`: 所属对话
- `poetry_theme`: 诗词主题
- `poetry_format`: 诗词格式
- `poetry_style`: 诗词风格
- `poetry_content`: 诗词内容
- `poetry_title`: 诗词标题
- `poetry_analysis`: 诗词分析(JSON)
- `painting_prompt`: 绘画提示词
- `painting_style`: 绘画风格
- `painting_url`: 画作URL
- `painting_local_path`: 本地路径
- `langgraph_state`: LangGraph状态(JSON)
- `iteration_count`: 迭代次数
- `user_rating`: 用户评分

### PoetryPaintingMessage (消息)

- `conversation`: 所属对话
- `role`: 角色(user/assistant/system)
- `content`: 消息内容
- `work`: 关联作品
- `created_at`: 创建时间

---

## 🔧 开发指南

### 添加新的诗词风格

1. 在 `prompts.py` 中添加风格描述
2. 更新前端 `types.ts` 中的 `POETRY_STYLES`
3. 优化 `PoetryService` 中的风格处理逻辑

### 添加新的绘画风格

1. 在 `prompts.py` 中的 `PAINTING_STYLE_DESCRIPTIONS` 添加描述
2. 更新前端 `types.ts` 中的 `PAINTING_STYLES`
3. 在 `PaintingService` 中实现风格特定处理

### 扩展 LangGraph 工作流

在 `langgraph_service.py` 中：

1. 定义新节点函数
2. 使用 `workflow.add_node()` 添加节点
3. 使用 `workflow.add_edge()` 或 `workflow.add_conditional_edges()` 连接节点

---

## 🐛 故障排查

### 问题: 诗词生成失败

**原因**: API 密钥未配置或无效

**解决**: 检查 `.env` 文件中的 `DASHSCOPE_API_KEY`

### 问题: 图像生成失败

**原因**: 模型 `qwen-image-plus` 调用失败

**解决**: 
1. 确认 API 密钥有权限使用该模型
2. 检查网络连接
3. 查看 `backend/logs/django.log` 获取详细错误

### 问题: 图片无法显示

**原因**: 图片保存路径问题

**解决**: 
1. 确保 `MEDIA_ROOT` 和 `MEDIA_URL` 正确配置
2. 检查目录权限
3. 使用绝对 URL 访问图片

---

## 📈 性能优化建议

1. **异步处理**: 使用 Celery 异步生成诗词和画作
2. **缓存策略**: 缓存常用诗词主题的分析结果
3. **图片优化**: 生成缩略图，按需加载高清图
4. **数据库索引**: 为常用查询字段添加索引

---

## 🎯 后续规划

- [ ] 支持用户上传图片生成诗词（图生诗）
- [ ] 添加诗词朗诵功能（TTS）
- [ ] 支持多人协作创作
- [ ] 添加诗词收藏和分享功能
- [ ] 支持导出为精美的图文卡片

---

## 📝 许可证

本项目遵循 MIT 许可证

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**最后更新**: 2025-10-21
**版本**: v1.0.0

