# 音频保存功能 - 完整检查清单

## ✅ 功能实现状态

### 后端实现 ✅

#### 1. API 调用（已完成）
- ✅ 使用您调整好的 API 调用方法
- ✅ 调用 `dashscope.audio.qwen_tts.SpeechSynthesizer.call()`
- ✅ 获取音频 URL、ID、过期时间

#### 2. 音频下载（已完成）
```python
# services.py 第 205-215 行
if result.get('audio_url'):
    saved_info = self._download_and_save_audio(
        result['audio_url'],
        audio_task.task_id,
        user_id,
        format
    )
    result.update(saved_info)
```

#### 3. 文件保存（已完成）
```python
# services.py 第 480-546 行
def _download_and_save_audio():
    # 生成路径：ai-audio/{user_id}/{date}/{task_id}.{format}
    save_path = f"ai-audio/{user_id}/{date_str}/{filename}"
    
    # 下载文件
    response = requests.get(audio_url, timeout=60)
    audio_content = response.content
    
    # 保存到本地
    saved_path = default_storage.save(save_path, ContentFile(audio_content))
    
    # 生成访问URL
    saved_url = default_storage.url(saved_path)
```

#### 4. 数据库记录（已完成）
```python
# services.py 第 217-224 行
audio_task.output_audio_url = result.get('audio_url', '')      # DashScope 原始URL
audio_task.output_audio_file = result.get('saved_path', '')    # 本地文件路径
tts_task.file_size = result.get('file_size', 0)                # 文件大小
```

#### 5. 返回数据（已完成）
```python
# services.py 第 236-247 行
return {
    'audio_url': result.get('saved_url', result.get('audio_url', '')),  # 优先返回本地URL
    'original_url': result.get('audio_url', ''),                        # 原始URL
    'saved_path': result.get('saved_path', ''),                         # 保存路径
    'file_size': result.get('file_size', 0),                            # 文件大小
    'status': 'completed'
}
```

## 📂 存储结构（已完成）

### 目录创建 ✅
- ✅ `backend/media/ai-audio/` 目录已创建
- ✅ `.gitkeep` 文件已添加

### 路径规则 ✅
```
media/ai-audio/{user_id}/{YYYYMMDD}/{task_id}.{format}
```

### 示例
```
media/
└── ai-audio/
    ├── 1/
    │   └── 20251016/
    │       ├── uuid-123.wav
    │       └── uuid-456.wav
    └── 2/
        └── 20251016/
            └── uuid-789.wav
```

## 🔄 完整工作流程

```
1. 用户提交文本
   ↓
2. 调用 DashScope API
   ↓ 
3. 获取临时音频 URL
   ↓
4. 下载音频文件 ✅
   └─ requests.get(audio_url, timeout=60)
   └─ 获取文件内容和大小
   ↓
5. 保存到本地目录 ✅
   └─ 路径: media/ai-audio/{user_id}/{date}/{task_id}.wav
   └─ 使用 Django default_storage.save()
   ↓
6. 生成本地访问 URL ✅
   └─ default_storage.url(saved_path)
   ↓
7. 更新数据库 ✅
   └─ output_audio_url: DashScope URL
   └─ output_audio_file: 本地路径
   └─ file_size: 文件大小
   ↓
8. 返回本地 URL 给前端 ✅
   └─ audio_url: 本地永久URL
```

## 📊 数据库字段使用

### AudioTask 表
| 字段 | 值示例 | 说明 |
|-----|--------|------|
| `output_audio_url` | `https://dashscope-result...` | DashScope 临时 URL（会过期） |
| `output_audio_file` | `ai-audio/1/20251016/uuid.wav` | 本地保存路径（永久有效） |
| `api_request_id` | `request-id-123` | API 请求ID |
| `api_usage` | `{"characters": 10}` | API 使用统计 |

### TextToSpeechTask 表
| 字段 | 值示例 | 说明 |
|-----|--------|------|
| `voice` | `Cherry` | 音色 |
| `language_type` | `Chinese` | 语言类型 |
| `format` | `wav` | 输出格式 |
| `file_size` | `245678` | 文件大小（字节） |

## 🔍 日志输出

### 成功流程日志
```
INFO: 开始文字转语音任务: uuid-123
INFO: TTS API调用成功: audio_id=audio_xxx, url=https://dashscope-result...
INFO: 开始下载音频文件: https://dashscope-result...
INFO: 准备下载音频 - URL: https://dashscope-result...
INFO: 保存路径: media/ai-audio/1/20251016/uuid-123.wav
INFO: 音频下载成功 - 大小: 245678 bytes (239.92 KB)
INFO: 音频保存成功 - 文件路径: ai-audio/1/20251016/uuid-123.wav
INFO: 访问URL: /media/ai-audio/1/20251016/uuid-123.wav
INFO: 音频文件已保存到: ai-audio/1/20251016/uuid-123.wav
INFO: 文字转语音完成: uuid-123
```

## 🧪 测试验证

### 1. 功能测试
```bash
cd backend\chat\ai-audio
..\..\..\venv\Scripts\activate
python test_tts.py
```

### 2. 检查文件保存
```bash
cd backend\media\ai-audio
dir /s
# 应该看到按用户ID和日期组织的音频文件
```

### 3. 检查数据库
```python
from chat.models import AudioTask
task = AudioTask.objects.latest('created_at')

print(f"原始URL: {task.output_audio_url}")
print(f"本地路径: {task.output_audio_file}")
print(f"文件大小: {task.texttospeechtask.file_size} bytes")
```

### 4. 访问音频
```
http://localhost:8000/media/ai-audio/1/20251016/uuid-123.wav
```

## ⚠️ 注意事项

### 1. 环境配置
- ✅ DASHSCOPE_API_KEY 已配置
- ✅ MEDIA_ROOT 已设置
- ✅ MEDIA_URL 已配置

### 2. 文件权限
- 确保 Django 进程有权限写入 `media/ai-audio/` 目录
- 确保目录存在（已创建）

### 3. 存储空间
- WAV 格式文件通常较大（100KB - 5MB）
- 建议监控磁盘使用情况
- 考虑定期清理旧文件

### 4. 网络超时
- 下载超时设置为 60 秒
- 如果网络慢，可能需要调整

## 📝 关键代码位置

| 功能 | 文件 | 行号 |
|-----|------|-----|
| 启用保存 | services.py | 205-215 |
| 下载函数 | services.py | 480-546 |
| 数据库更新 | services.py | 217-224 |
| 返回数据 | services.py | 236-247 |
| API 调用 | services.py | 384-429 |

## ✅ 功能状态总结

### 已完成 ✅
1. ✅ API 调用（保持您调整的方法）
2. ✅ 音频下载（真实下载逻辑）
3. ✅ 文件保存（media/ai-audio/目录）
4. ✅ 数据库记录（双重URL保存）
5. ✅ 错误处理（完整的异常捕获）
6. ✅ 日志记录（详细的操作日志）
7. ✅ 返回本地URL（优先使用本地URL）

### 测试建议
- 🧪 运行 test_tts.py 测试
- 🧪 检查 media/ai-audio/ 目录是否有文件生成
- 🧪 验证数据库中的路径是否正确
- 🧪 确认前端能正常播放本地URL的音频

---

**检查日期**: 2025-10-16  
**功能状态**: ✅ **完整实现，已启用**  
**保存目录**: `backend/media/ai-audio/`  
**API 调用**: 保持您调整的方法（不修改）

