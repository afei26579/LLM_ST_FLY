# 语音转文字功能实现说明

## ✅ 实现概述

基于 DashScope 的 `MultiModalConversation.call()` API 实现了语音转文字功能，使用 `qwen-audio-turbo-latest` 模型。

## 🔧 技术实现

### API 调用方式

```python
import dashscope

# 1. 保存上传的音频文件到本地
audio_file_path = audio_task.input_audio_file.path

# 2. 添加 file:// 前缀
audio_file_url = f"file://{audio_file_path}"

# 3. 构建 messages
messages = [
    {
        "role": "system",
        "content": [{"text": "You are a helpful assistant."}]
    },
    {
        "role": "user",
        "content": [
            {"audio": audio_file_url},
            {"text": "请将音频内容转换为文字，只输出识别的文字内容，不需要额外说明。"}
        ]
    }
]

# 4. 调用 API
response = dashscope.MultiModalConversation.call(
    model="qwen-audio-turbo-latest",
    messages=messages
)

# 5. 提取识别文本
recognized_text = response.output.choices[0].message.content[0]["text"]
```

## 📋 关键要点

### 1. 文件路径格式
- ❗ **必须使用绝对路径**
- ❗ **必须添加 `file://` 前缀**
- ✅ 示例：`file:///d:/workspace/llm_st_fly/backend/media/audio-inputs/test.mp3`

### 2. API 响应结构
```python
response.output.choices[0].message.content[0]["text"]
```

### 3. 音频文件存储
- 上传的音频保存到：`media/audio-inputs/`
- Django 自动生成唯一文件名
- 使用 `audio_task.input_audio_file.path` 获取绝对路径

## 🔄 完整流程

```
1. 前端上传音频文件
   ↓
2. 后端保存到 media/audio-inputs/
   ↓
3. 创建 AudioTask 和 SpeechToTextTask 记录
   ↓
4. 获取文件绝对路径
   ↓
5. 添加 file:// 前缀
   ↓
6. 调用 MultiModalConversation API
   ↓
7. 提取识别文本
   ↓
8. 更新数据库记录
   ↓
9. 返回识别结果给前端
```

## 📁 文件结构

### 后端
```
backend/
├── chat/ai-audio/
│   ├── services.py               # 第 347-406 行：语音识别实现
│   └── test_stt.py               # 测试脚本
└── media/
    └── audio-inputs/             # 上传的音频存储目录
```

### 数据库字段
**AudioTask 表**：
- `input_audio_file` - 上传的音频文件路径
- `output_text` - 识别的文本结果

**SpeechToTextTask 表**：
- `language` - 识别语言（zh-cn、en-us等）
- `model` - 识别模型（qwen-audio-turbo-latest）
- `confidence` - 置信度（默认 0.95）

## 🎯 前端改进

### 1. 清空旧结果
```typescript
const recognizeSpeech = async () => {
  // 清空上一次的结果
  sttResult.value = null
  // ...
}
```

### 2. 强制重新渲染
```vue
<div v-if="sttResult" class="recognition-result" :key="sttResult.task_id">
  <!-- 通过 key 强制 Vue 重新渲染 -->
</div>
```

### 3. 自动刷新统计
```typescript
if (response.code === 200) {
  sttResult.value = response.data
  toast.success('语音识别成功！')
  loadUserStats()  // 刷新统计数据
}
```

## 🧪 测试方法

### 准备测试音频
1. 准备一个测试音频文件（MP3、WAV、M4A 等）
2. 重命名为 `test_audio.mp3`
3. 放到 `backend/chat/ai-audio/` 目录下

### 运行测试
```bash
cd backend\chat\ai-audio
..\..\..\venv\Scripts\activate
python test_stt.py
```

### 预期输出
```
==================================================
语音转文字功能测试
==================================================
✓ 使用用户: admin

测试音频文件:
  - 路径: D:\workspace\llm_st_fly\backend\chat\ai-audio\test_audio.mp3
  - 大小: 123456 bytes (120.56 KB)

正在调用 DashScope 语音识别 API...

✓ 识别成功!
  - 任务ID: uuid-string
  - 识别文本: 这是识别出来的文字内容
  - 置信度: 0.95
  - 状态: completed
  - 使用量: {...}

==================================================
测试完成!
==================================================
```

## 🔍 调试日志

### 成功日志
```
INFO: 开始语音转文字任务: uuid-123
INFO: 准备调用语音识别 API: 文件路径=D:/workspace/.../test.mp3
INFO: file:// URL: file://D:/workspace/.../test.mp3
INFO: 语音识别成功: text_length=50
INFO: 语音转文字完成: uuid-123
```

### 错误处理
- 文件路径错误 → 检查文件是否存在
- API 调用失败 → 检查 DASHSCOPE_API_KEY
- 路径格式错误 → 确保使用 file:// 前缀

## 📝 API 请求/响应

### 前端请求
```javascript
const formData = new FormData()
formData.append('audio_file', selectedAudioFile)
formData.append('language', 'zh-cn')
formData.append('model', 'qwen-audio-turbo-latest')

POST /api/v1/chat/ai-audio/speech-to-text/
```

### 后端响应
```json
{
  "code": 200,
  "message": "语音转文字成功",
  "data": {
    "task_id": "uuid-string",
    "result_text": "识别的文字内容",
    "text": "识别的文字内容",
    "confidence": 0.95,
    "status": "completed",
    "usage": {}
  }
}
```

## ⚠️ 注意事项

### 1. 文件路径
- Windows 路径示例：`file://D:/workspace/project/media/audio.mp3`
- Linux 路径示例：`file:///home/user/project/media/audio.mp3`
- 必须是绝对路径，不能是相对路径

### 2. 支持的音频格式
- MP3
- WAV
- M4A
- 其他常见音频格式

### 3. 文件大小限制
- 建议不超过 100MB
- 音频时长建议在 5 分钟以内

### 4. API 限制
- 需要有效的 DASHSCOPE_API_KEY
- 注意 API 调用频率限制
- 注意账户余额

## 🎉 完成清单

- ✅ 后端语音识别 API 调用实现
- ✅ 使用 file:// 前缀的本地文件路径
- ✅ 前端清空旧结果机制
- ✅ 前端强制重新渲染
- ✅ 自动刷新统计数据
- ✅ 测试脚本
- ✅ 文档说明

---

**实现日期**: 2025-10-16  
**模型**: qwen-audio-turbo-latest  
**状态**: ✅ 完成

