# Chat API 测试

这个目录包含针对聊天功能相关API的测试用例。

## 测试文件说明

- `test_conversations.py`: 测试对话管理相关的API
- `test_chat_completion.py`: 测试大模型聊天功能的API
- `run_tests.py`: 运行所有测试的脚本

## 如何运行测试

### 方法1：使用Django测试命令

在项目根目录下运行：

```bash
# 运行所有聊天相关测试
python manage.py test test_chats

# 运行特定测试文件
python manage.py test test_chats.test_conversations
python manage.py test test_chats.test_chat_completion

# 运行特定测试类
python manage.py test test_chats.test_conversations.ConversationAPITestCase

# 运行特定测试方法
python manage.py test test_chats.test_conversations.ConversationAPITestCase.test_list_conversations
```

### 方法2：使用提供的运行脚本

在当前目录下运行：

```bash
python run_tests.py
```

## 注意事项

1. 测试会在测试数据库中创建临时数据，不会影响生产数据库
2. 对于大模型调用相关的测试，使用了mock技术避免实际调用外部API
3. 确保已安装所有必要的依赖：`pip install -r requirements.txt`
4. 如果要单独运行某个测试文件，需要先设置好Django环境(可以参考运行脚本中的设置)

## 测试覆盖的API端点

1. `/api/v1/chat/conversations/` - GET：获取对话列表
2. `/api/v1/chat/conversations/` - POST：创建新对话
3. `/api/v1/chat/conversations/{id}/` - GET：获取单个对话详情
4. `/api/v1/chat/conversations/{id}/` - DELETE：删除对话
5. `/api/v1/chat/conversations/{id}/clear_messages/` - DELETE：清空对话消息
6. `/api/v1/chat/completion/` - POST：发送聊天请求获取AI回复

## 测试设计原则

1. 每个API端点都有对应的测试方法
2. 测试包括成功场景和失败场景
3. 验证响应格式和状态码
4. 验证数据库状态变化
5. 测试权限控制 