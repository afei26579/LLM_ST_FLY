# 音频文件存储说明

## 📁 存储架构

### 存储位置
```
backend/media/ai-audio/{user_id}/{date}/{task_id}.{format}
```

### 目录结构示例
```
backend/media/
└── ai-audio/
    ├── 1/                    # 用户1的音频
    │   ├── 20251016/
    │   │   ├── task-123.wav
    │   │   └── task-456.wav
    │   └── 20251017/
    │       └── task-789.wav
    └── 2/                    # 用户2的音频
        └── 20251016/
            └── task-abc.wav
```

## 🔄 工作流程

### 1. 用户请求生成语音
```
用户提交文本
   ↓
创建 AudioTask 和 TextToSpeechTask 记录
   ↓
调用 DashScope API
   ↓
获得临时音频 URL
```

### 2. 下载并保存
```
下载 DashScope 临时 URL 的音频文件
   ↓
保存到 media/ai-audio/{user_id}/{date}/{task_id}.{format}
   ↓
生成本地访问 URL
   ↓
更新数据库记录
```

### 3. 数据库存储

**AudioTask 表字段**：
- `output_audio_url` - DashScope 原始临时 URL（会过期）
- `output_audio_file` - 本地保存路径（永久有效）

**返回给前端**：
```json
{
  "audio_url": "http://localhost:8000/media/ai-audio/1/20251016/task-123.wav",
  "original_url": "https://dashscope-result.oss-cn-shanghai.aliyuncs.com/...",
  "saved_path": "ai-audio/1/20251016/task-123.wav",
  "file_size": 245678,
  "task_id": "task-123"
}
```

## 📊 文件管理

### 命名规则
- **格式**: `{task_id}.{format}`
- **task_id**: UUID 格式的唯一标识符
- **format**: wav, mp3, pcm

### 访问方式

**通过 Django Media URL**:
```
http://localhost:8000/media/ai-audio/1/20251016/task-123.wav
```

**通过数据库查询**:
```python
task = AudioTask.objects.get(task_id='task-123')
audio_file_path = task.output_audio_file
audio_url = default_storage.url(audio_file_path)
```

## 🧹 存储管理建议

### 定期清理
建议创建定时任务清理过期文件：

```python
# 示例：清理30天前的音频文件
from datetime import timedelta
from django.utils import timezone

cutoff_date = timezone.now() - timedelta(days=30)
old_tasks = AudioTask.objects.filter(
    created_at__lt=cutoff_date,
    task_type='text_to_speech'
)

for task in old_tasks:
    if task.output_audio_file:
        default_storage.delete(task.output_audio_file)
    task.delete()
```

### 存储限制
- 单个音频文件通常在 100KB - 5MB
- 建议为每个用户设置存储配额
- 定期监控磁盘使用情况

## 🔒 安全考虑

1. **用户隔离**: 每个用户的音频存储在独立目录
2. **访问控制**: 建议添加权限检查，确保用户只能访问自己的音频
3. **文件验证**: 下载时验证文件类型和大小

## 📈 监控指标

### 统计信息（UserAudioStats）
- `total_storage_used` - 总存储使用量（字节）
- `total_audio_duration` - 总音频时长（秒）
- `total_text_to_speech` - 文字转语音次数

### 日志记录
所有下载和保存操作都会记录详细日志：
```
INFO: 准备下载音频: URL=..., 保存路径=...
INFO: 音频下载成功: 大小=245678 bytes
INFO: 音频文件已保存: 路径=ai-audio/1/20251016/task-123.wav
```

## 🛠️ 相关代码

### 服务层（services.py）
- `text_to_speech()` - 主要入口
- `_call_speech_synthesis_api()` - 调用 DashScope API
- `_download_and_save_audio()` - 下载并保存音频文件

### 模型（models.py）
- `AudioTask.output_audio_file` - 存储文件路径
- `TextToSpeechTask.file_size` - 存储文件大小

## ✅ 优势

1. **永久存储** - 不依赖 DashScope 的临时 URL
2. **用户体验** - 音频文件可以随时访问，不会过期
3. **数据完整** - 完整保留用户生成的所有音频
4. **可追溯** - 按日期组织，便于查找和管理

---

**更新时间**: 2025-10-16  
**功能状态**: ✅ 已实现并启用

