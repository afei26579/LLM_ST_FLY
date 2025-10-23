# 图生视频功能实现总结

## ✅ 完成的工作

### 1️⃣ 后端实现（参照 demo2.py）

#### 更新模型（models.py）
- ✅ fps 字段已存在，默认24

#### 更新序列化器（serializers.py）
```python
class ImageToVideoSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=False, allow_blank=True)  # 可选
    input_image = serializers.ImageField(required=False)
    model = serializers.CharField(default='wan2.5-i2v-preview')
    resolution = serializers.ChoiceField(
        choices=['480P', '720P', '1080P', '854*480', '1280*720', '1920*1080'],
        default='1280*720'
    )
    duration = serializers.IntegerField(default=5, min_value=5, max_value=10)
    fps = serializers.IntegerField(default=24)
```

#### 更新服务层（services.py）

**方法签名**：
```python
def image_to_video(
    self,
    user_id: int,
    prompt: str = '',           # 可选提示词
    input_image=None,
    model: str = 'wan2.5-i2v-preview',
    resolution: str = '1280*720',
    duration: int = 5,
    fps: int = 24               # 新增
) -> Dict[str, Any]:
```

**异步API调用**（参照 demo2.py）：
```python
def _call_image_to_video_api_async(self, task, img_url):
    # 构建参数
    api_params = {
        'api_key': self.api_key,
        'model': task.model,                              # wan2.5-i2v-preview
        'prompt': task.prompt if task.prompt else '让图片动起来',  # 默认提示词
        'resolution': task.resolution,                    # 1280*720
        'duration': task.duration,                        # 5
        'img_url': img_url                                # file://路径
    }
    
    # 异步调用（参照 demo2.py）
    response = VideoSynthesis.async_call(**api_params)
    
    # 立即返回任务ID
    return {
        'status': 'SUBMITTED',
        'api_task_id': response.output.task_id,
        'response': response  # 保存响应对象供fetch使用
    }
```

**图片路径处理**：
```python
def _prepare_image_input(self, task):
    if task.input_image:
        file_path = task.input_image.path
        # 添加 file:// 前缀（参照 demo2.py）
        img_url = f"file://{file_path}"
        return img_url
```

#### 更新视图层（views.py）
```python
result = ai_video_service.image_to_video(
    user_id=request.user.id,
    prompt=validated_data.get('prompt', ''),
    input_image=validated_data.get('input_image'),
    model=validated_data.get('model', 'wan2.5-i2v-preview'),
    resolution=validated_data.get('resolution', '1280*720'),
    duration=validated_data.get('duration', 5),
    fps=validated_data.get('fps', 24)
)
```

### 2️⃣ 前端实现

#### 页面布局（AIVideoView.vue）

**未上传图片时**：
```vue
<div class="upload-section" v-if="!selectedImage">
  <div class="upload-area" @click="triggerImageInput">
    🖼️ 点击或拖拽图片上传
  </div>
</div>
```

**上传图片后**：
```vue
<div class="i2v-content-wrapper" v-if="selectedImage">
  <!-- 左侧：图片预览 -->
  <div class="i2v-left-panel">
    <div class="image-preview-card" @click="triggerImageInput">
      <img :src="imagePreview" />
      <div class="change-image-hint">点击更换图片</div>
    </div>
  </div>
  
  <!-- 右侧：设置区域 -->
  <div class="i2v-right-panel">
    <!-- 动态描述（8行，高度180px+） -->
    <textarea rows="8" class="i2v-prompt-textarea">...</textarea>
    
    <!-- 配置选项 -->
    <div class="settings-section-horizontal">
      <CustomSelect v-model="resolution" :options="i2vResolutionOptions" />
      <CustomSelect v-model="duration" :options="i2vDurationOptions" />
    </div>
    
    <!-- 生成按钮（底部对齐） -->
    <button class="generate-btn">生成视频</button>
  </div>
</div>
```

#### 表单数据
```typescript
const imageToVideoForm = reactive({
  prompt: '',
  model: 'wan2.5-i2v-preview',  // 固定模型
  resolution: '1280*720',        // 默认720P
  duration: 5,                   // 默认5秒
  fps: 24                        // 固定24fps
})
```

#### 选项配置
```typescript
// 分辨率选项（与文生视频一致）
const i2vResolutionOptions = [
  { value: '854*480', label: '480P' },
  { value: '1280*720', label: '720P' },
  { value: '1920*1080', label: '1080P' }
]

// 时长选项（与文生视频一致）
const i2vDurationOptions = [
  { value: 5, label: '5秒' },
  { value: 10, label: '10秒' }
]
```

## 🔄 完整流程

```
1. 用户上传图片
   ↓
2. 图片保存到 media/video-inputs/
   ↓
3. 显示图片预览 + 设置选项
   ↓
4. 用户配置参数（可选填写动态描述）
   ↓
5. 点击"生成视频"
   ↓
6. 后端异步调用 VideoSynthesis.async_call()
   - model: wan2.5-i2v-preview
   - prompt: 用户输入或默认"让图片动起来"
   - resolution: 1280*720
   - duration: 5
   - img_url: file://本地路径
   ↓
7. 立即返回 task_id（status: processing）
   ↓
8. 前端开始轮询（每3秒）
   ↓
9. 后端调用 VideoSynthesis.fetch(response)
   - PENDING → 等待中
   - RUNNING → 生成中
   - SUCCEEDED → 下载视频
   - FAILED → 标记失败
   ↓
10. 视频下载到 media/ai-videos/
   ↓
11. 前端显示视频播放器
```

## 📊 参数对比（demo2.py vs 实现）

| 参数 | demo2.py | 实现 | 说明 |
|-----|---------|------|------|
| model | wan2.5-i2v-preview | wan2.5-i2v-preview | ✅ 一致 |
| prompt | 一只猫在草地上奔跑 | 用户输入或默认 | ✅ 支持 |
| resolution | 1080P | 1280*720 | ✅ 支持 |
| duration | 5 | 5 | ✅ 一致 |
| img_url | file://路径 | file://路径 | ✅ 一致 |

## 🎨 前端布局效果

### 桌面端布局
```
┌──────────────────────────────────────────────────┐
│ 图生视频                                          │
├────────────────┬─────────────────────────────────┤
│ 【图片】400px   │ 【设置】剩余空间                 │
│ ┌────────────┐ │ 动态描述：                       │
│ │            │ │ ┌─────────────────────────────┐ │
│ │            │ │ │                             │ │
│ │  图片预览   │ │ │   （8行，180px+）          │ │
│ │            │ │ │                             │ │
│ │            │ │ └─────────────────────────────┘ │
│ │            │ │                                 │
│ └────────────┘ │ 分辨率：[720P] 时长：[5秒]       │
│ 点击更换图片    │                                 │
│                │      [生成视频] ← 底部对齐       │
└────────────────┴─────────────────────────────────┘
```

### 关键样式
```css
.i2v-content-wrapper {
  grid-template-columns: 400px 1fr;
  align-items: end;  /* 底部对齐 */
}

.i2v-prompt-textarea {
  rows: 8
  min-height: 180px;
  flex: 1;
}
```

## 🔧 关键技术点

### 1. 异步模式
- 使用 `async_call()` 立即返回
- 前端轮询状态
- 避免HTTP超时

### 2. 图片处理
- 使用 `file://` 本地路径
- 不需要Base64编码
- 更高效

### 3. 提示词可选
- 允许空提示词
- 提供默认值"让图片动起来"

### 4. 响应对象缓存
- 保存 async_call 返回的响应
- 供 fetch 方法使用

## ✅ 完成清单

- ✅ 更新模型默认值
- ✅ 更新序列化器（prompt可选，添加fps）
- ✅ 实现异步API调用
- ✅ 使用 file:// 路径
- ✅ 更新视图层传参
- ✅ 前端布局优化
- ✅ 底部对齐
- ✅ 动态描述高度增加
- ✅ 统一分辨率和时长选项

---

**实现日期**: 2025-10-16  
**模型**: wan2.5-i2v-preview  
**模式**: 异步（async_call + fetch）  
**状态**: ✅ 完成

