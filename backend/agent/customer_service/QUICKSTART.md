# 智能客服系统 - 快速启动指南

## 🚀 5分钟快速上手

### 步骤 1: 确认环境

```bash
# 检查 Python 版本 (需要 3.10+)
python --version

# 检查虚拟环境已激活
which python  # Linux/Mac
where python  # Windows
```

### 步骤 2: 安装依赖（如果还没安装）

```bash
pip install langgraph langchain langchain-openai
```

### 步骤 3: 配置 API Key

在 `backend/core/settings.py` 或环境变量中设置：

```python
# settings.py
DASHSCOPE_API_KEY = 'your_dashscope_api_key'
```

或使用环境变量：
```bash
export DASHSCOPE_API_KEY=your_api_key
```

### 步骤 4: 数据库迁移（已完成）

```bash
cd backend
python manage.py makemigrations agent
python manage.py migrate
```

### 步骤 5: 启动后端服务

```bash
cd backend
python manage.py runserver
```

看到以下信息表示成功：
```
Starting development server at http://127.0.0.1:8000/
```

### 步骤 6: 启动前端

新开一个终端：
```bash
cd frontend
pnpm dev
```

看到：
```
➜  Local:   http://localhost:5173/
```

### 步骤 7: 访问系统

1. 打开浏览器访问：`http://localhost:5173/`
2. 登录系统
3. 点击左侧菜单 **智能体 → 客服助手**
4. 开始对话！

---

## 💬 测试对话示例

### 示例 1: 订单查询
```
用户: 我想查询订单 202510210001
AI: 正在为您查询订单信息...
   订单号：202510210001
   状态：配送中
   物流单号：ZT1234567890
   预计送达：2025-10-23
```

### 示例 2: 产品咨询
```
用户: 智能手表有什么功能？
AI: 我们的智能手表系列包括以下产品：
   
   智能手表 Pro - ¥999
   - 50米防水
   - 7天续航
   - 健康监测
   
   智能手表 Air - ¥599
   - 轻薄设计
   - 5天续航
   - 运动追踪
```

### 示例 3: 技术支持
```
用户: 我的手表无法开机
AI: 请尝试以下解决方案：
   1. 长按电源键10秒重启
   2. 检查电量是否充足
   3. 尝试充电30分钟后再开机
   
   如果问题仍未解决，我可以为您转接人工客服。
```

### 示例 4: 转人工
```
用户: 我要投诉
AI: 非常抱歉给您带来不便，正在为您转接人工客服，请稍候...
```

---

## 🔧 常用功能

### 新建会话
点击页面右上角 "➕ 新会话" 按钮

### 查看历史
点击 "📋 历史会话" 查看所有对话记录

### 满意度评价
对话结束后，点击星星图标进行评分

### 查看统计
右侧面板显示您的使用统计信息

---

## 🎯 开发调试

### 查看日志
```bash
# Django日志
tail -f backend/logs/django.log

# 或查看控制台输出
```

### 测试 API
使用 Postman 或 curl：

```bash
# 获取欢迎语
curl -X GET http://localhost:8000/api/v1/agent/customer-service/greeting/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# 发送消息
curl -X POST http://localhost:8000/api/v1/agent/customer-service/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "message": "我想查询订单",
    "session_id": ""
  }'
```

### 调试 LangGraph
在 `langgraph_service.py` 中添加日志：

```python
logger.info(f"当前状态: {state}")
logger.info(f"意图识别结果: {state['intent']}")
```

---

## 📚 下一步

- 📖 阅读完整文档：[README.md](./README.md)
- 🔨 添加自定义知识库
- 🎨 自定义意图和处理器
- 📊 对接真实的订单系统

---

## ❓ 遇到问题？

### 后端无法启动
- 检查虚拟环境是否激活
- 确认所有依赖已安装
- 检查数据库配置

### 前端无法访问
- 确认后端已启动
- 检查 CORS 配置
- 清除浏览器缓存

### AI 不响应
- 检查 DASHSCOPE_API_KEY 是否正确
- 查看后端日志错误信息
- 确认网络可以访问阿里云服务

### 意图识别不准
- 优化意图分类提示词
- 增加更多示例
- 调整 temperature 参数

---

## 📞 获取帮助

- 查看项目文档
- 提交 Issue
- 联系开发团队

---

**祝您使用愉快！** 🎉

