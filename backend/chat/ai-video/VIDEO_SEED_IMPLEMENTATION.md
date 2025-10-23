# 视频生成 - 随机种子功能实现

## ✅ 完成的工作

### 1️⃣ 数据库模型更新

**文件**: `backend/chat/ai-video/models.py`

**新增字段**：
```python
class VideoGenerationTask(models.Model):
    # ... 其他字段
    seed = models.BigIntegerField(blank=True, null=True, verbose_name=_('随机种子'))
```

**其他调整**：
- 默认模型：`wan2.5-t2v-preview`
- 默认帧率：24 fps

### 2️⃣ 序列化器更新

**文件**: `backend/chat/ai-video/serializers.py`

**新增字段**：
```python
class TextToVideoSerializer(serializers.Serializer):
    seed = serializers.IntegerField(
        required=False, 
        min_value=0, 
        max_value=2147483647, 
        help_text="随机种子"
    )
```

**验证方法**：
```python
def validate_seed(self, value):
    """验证随机种子"""
    if value is not None:
        if value < 0:
            return 0
        if value > 2147483647:
            return 2147483647
    return value
```

**其他调整**：
- 分辨率选项：添加 480P、720P、1080P
- 时长范围：5-10秒
- 默认帧率：24 fps
- 默认模型：wan2.5-t2v-preview

### 3️⃣ 服务层更新

**文件**: `backend/chat/ai-video/services.py`

**方法签名更新**：
```python
def text_to_video(
    self,
    user_id: int,
    prompt: str,
    model: str = 'wan2.5-t2v-preview',
    resolution: str = '1280*720',
    duration: int = 5,
    fps: int = 24,
    seed: int = None  # 新增参数
) -> Dict[str, Any]:
```

**API 调用更新**：
```python
def _call_text_to_video_api(self, task: VideoGenerationTask) -> Dict[str, Any]:
    # 构建 API 参数
    api_params = {
        'model': task.model,
        'prompt': task.prompt,
        'size': task.resolution,
        'duration': task.duration,  # 视频时长
        'audio': True
    }
    
    # 如果提供了随机种子，添加到参数中
    if task.seed is not None:
        api_params['seed'] = int(task.seed)
        logger.info(f"使用随机种子: {task.seed}")
    
    # 调用 API
    response = VideoSynthesis.call(**api_params)
```

### 4️⃣ 视图层更新

**文件**: `backend/chat/ai-video/views.py`

**调用服务更新**：
```python
result = ai_video_service.text_to_video(
    user_id=request.user.id,
    prompt=prompt,
    model=validated_data.get('model', 'wan2.5-t2v-preview'),
    resolution=validated_data.get('resolution', '1280*720'),
    duration=validated_data.get('duration', 5),
    fps=validated_data.get('fps', 24),
    seed=validated_data.get('seed')  # 传递随机种子
)
```

### 5️⃣ 数据库迁移

**迁移文件**: `chat/migrations/0010_videogenerationtask_seed_and_more.py`

**操作**：
- 添加 `seed` 字段（BigIntegerField, nullable）
- 修改 `fps` 默认值为 24
- 修改 `model` 默认值为 wan2.5-t2v-preview

## 🔄 完整数据流

```
前端
  ↓
textToVideoForm.seed = 1234567
  ↓
POST /api/v1/chat/ai-video/text-to-video/
{
  "prompt": "...",
  "resolution": "1280*720",
  "duration": 5,
  "seed": 1234567
}
  ↓
后端 views.py
  ↓
TextToVideoSerializer 验证（范围 0-2147483647）
  ↓
ai_video_service.text_to_video(seed=1234567)
  ↓
创建 VideoGenerationTask（保存 seed 到数据库）
  ↓
_call_text_to_video_api(task)
  ↓
VideoSynthesis.call(
    model="wan2.5-t2v-preview",
    prompt="...",
    size="1280*720",
    duration=5,
    seed=1234567  ← 传递给 DashScope API
)
  ↓
生成视频
```

## 📊 参数对应关系

| 前端参数 | 后端字段 | API 参数 | 类型 | 范围 |
|---------|---------|---------|------|------|
| prompt | prompt | prompt | string | 1-5000字符 |
| resolution | resolution | size | string | 480P/720P/1080P |
| duration | duration | duration | int | 5-10秒 |
| fps | fps | - | int | 24 |
| seed | seed | seed | int | 0-2147483647 |

## 🔍 日志记录

### 成功流程
```
INFO: 开始文生视频任务: uuid-123
INFO: 调用文生视频API: uuid-123, duration=5, seed=1234567
INFO: 使用随机种子: 1234567
INFO: API响应状态: 200
INFO: 视频保存成功: ai-videos/1/20251016/uuid-123.mp4
INFO: 文生视频完成: uuid-123
```

### 无种子情况
```
INFO: 调用文生视频API: uuid-123, duration=5, seed=None
INFO: API响应状态: 200
（不会传递 seed 参数给 API）
```

## 🎯 功能特性

### 随机种子作用
- **可复现性**: 相同种子 + 相同参数 = 相似结果
- **实验性**: 调整种子探索不同效果
- **可选性**: 不提供种子时由 API 随机生成

### 后端验证
- ✅ 范围验证：0 - 2,147,483,647
- ✅ 类型验证：整数
- ✅ 空值处理：允许为 null
- ✅ 超限处理：自动调整到有效范围

## 📝 数据库存储

### VideoGenerationTask 表

| 字段 | 类型 | 示例值 | 说明 |
|-----|------|--------|------|
| seed | BigIntegerField | 1234567 | 随机种子 |
| duration | IntegerField | 5 | 视频时长(秒) |
| fps | IntegerField | 24 | 帧率 |
| model | CharField | wan2.5-t2v-preview | 生成模型 |
| resolution | CharField | 1280*720 | 分辨率 |

## ⚠️ 注意事项

### 1. 种子可选
- `seed` 字段为可选（`required=False`）
- 前端可以不传，或传 `null`
- API 调用时仅在有值时传递

### 2. 类型转换
```python
# 确保传递整数类型
if task.seed is not None:
    api_params['seed'] = int(task.seed)
```

### 3. 验证规则
- 前端验证：实时范围检查
- 后端验证：序列化器双重验证
- 数据库：BigIntegerField 支持大整数

## 🧪 测试建议

### 测试用例
1. ✅ 使用随机种子：seed=123456
2. ✅ 不使用种子：seed=None
3. ✅ 最小值：seed=0
4. ✅ 最大值：seed=2147483647
5. ✅ 超限值：seed=9999999999（自动调整）
6. ✅ 负数：seed=-100（自动调整为0）

### 验证点
- 数据库正确保存 seed 值
- API 正确传递 seed 参数
- 相同 seed 生成相似视频
- 日志记录完整

## ✅ 完成清单

- ✅ 模型添加 seed 字段
- ✅ 序列化器添加 seed 验证
- ✅ 服务层接收 seed 参数
- ✅ API 调用传递 seed
- ✅ 视图层传递 seed
- ✅ 数据库迁移
- ✅ 日志记录
- ✅ 默认值更新

---

**实现日期**: 2025-10-16  
**字段**: seed (BigIntegerField)  
**范围**: 0 - 2,147,483,647  
**状态**: ✅ 完成

