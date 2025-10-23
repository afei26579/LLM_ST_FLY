# 异步视频生成实现说明

## 🎯 为什么使用异步模式

### 问题
- ❌ 视频生成耗时长（通常 30-120 秒）
- ❌ HTTP 请求超时（默认 30 秒）
- ❌ 用户体验差（长时间等待无响应）

### 解决方案
- ✅ 使用异步 API（`async_call`）
- ✅ 立即返回任务 ID
- ✅ 前端轮询任务状态
- ✅ 后台处理，前端可交互

## 🔄 异步流程

```
用户点击"生成视频"
    ↓
前端发送请求
    ↓
后端立即响应（<1秒）
    ├─ 任务已提交
    ├─ 返回 task_id
    └─ 状态: processing
    ↓
前端开始轮询（每3秒）
    ↓
后端查询 DashScope 任务状态
    ├─ PENDING: 等待中
    ├─ RUNNING: 生成中
    ├─ SUCCEEDED: 完成 → 下载视频
    └─ FAILED: 失败
    ↓
前端更新 UI
    ├─ 显示进度
    ├─ 显示视频（完成时）
    └─ 显示错误（失败时）
```

## 📝 代码实现

### 1. 异步调用 API

```python
def _call_text_to_video_api_async(self, task: VideoGenerationTask):
    """调用DashScope文生视频API（异步模式）"""
    
    # 构建参数
    api_params = {
        'api_key': self.api_key,
        'model': task.model,
        'prompt': task.prompt,
        'size': task.resolution,
        'duration': task.duration,
        'audio': True,
        'prompt_extend': True,
        'watermark': False
    }
    
    # 添加随机种子（可选）
    if task.seed is not None:
        api_params['seed'] = int(task.seed)
    
    # 异步调用（立即返回）
    response = VideoSynthesis.async_call(**api_params)
    
    if response.status_code == HTTPStatus.OK:
        api_task_id = response.output.task_id
        
        return {
            'status': 'SUBMITTED',
            'api_task_id': api_task_id,
            'request_id': response.request_id
        }
```

### 2. 查询任务状态

```python
def fetch_video_task_status(self, api_task_id: str):
    """查询视频生成任务状态"""
    
    # 使用 fetch 查询
    response = VideoSynthesis.fetch(
        api_key=self.api_key, 
        task_id=api_task_id
    )
    
    if response.status_code == HTTPStatus.OK:
        output = response.output
        task_status = output.task_status
        
        result = {
            'task_id': api_task_id,
            'task_status': task_status  # PENDING/RUNNING/SUCCEEDED/FAILED
        }
        
        # 如果完成，返回视频URL
        if task_status == 'SUCCEEDED':
            result['video_url'] = output.video_url
            result['actual_prompt'] = output.get('actual_prompt', '')
        
        return result
```

### 3. 轮询逻辑（在 get_task_status 中）

```python
def get_task_status(self, task_id: str):
    """获取任务状态（支持异步任务轮询）"""
    
    task = VideoGenerationTask.objects.get(task_id=task_id)
    
    # 如果任务在处理中，查询 DashScope 状态
    if task.status == 'processing' and task.api_task_id:
        api_result = self.fetch_video_task_status(task.api_task_id)
        
        if api_result['task_status'] == 'SUCCEEDED':
            # 下载视频
            video_url = api_result['video_url']
            saved_info = self._download_and_save_video(video_url, task.task_id, task.user_id)
            
            # 更新数据库
            task.status = 'completed'
            task.output_video_url = video_url
            task.saved_video_path = saved_info['saved_path']
            task.save()
        
        elif api_result['task_status'] == 'FAILED':
            # 标记失败
            task.status = 'failed'
            task.error_message = api_result.get('error', '')
            task.save()
    
    # 返回当前状态
    return {
        'task_id': task.task_id,
        'status': task.status,
        'result_url': task.output_video_url if task.status == 'completed' else None
    }
```

## 🎨 前端轮询（已实现）

```typescript
// AIVideoView.vue 中的轮询逻辑
const pollVideoTaskStatus = async (taskId: string, type: 't2v' | 'i2v') => {
  const maxAttempts = 60  // 最多轮询60次
  let attempts = 0
  
  const poll = async () => {
    attempts++
    const response = await apiService.getVideoTaskStatus(taskId)
    
    if (response.data.status === 'completed') {
      // 任务完成
      t2vResult.value = response.data
      toast.success('视频生成完成！')
      loadUserStats()
      return
    } else if (response.data.status === 'failed') {
      // 任务失败
      toast.error('视频生成失败')
      return
    } else if (attempts < maxAttempts) {
      // 继续轮询
      setTimeout(poll, 3000)  // 3秒后再次查询
    }
  }
  
  setTimeout(poll, 3000)  // 3秒后开始轮询
}
```

## 📊 任务状态流转

### DashScope 任务状态
```
PENDING   → 等待调度
    ↓
RUNNING   → 正在生成
    ↓
SUCCEEDED → 生成成功
    ↓
（自动下载视频）
    ↓
本地状态: completed
```

### 失败流程
```
PENDING/RUNNING
    ↓
FAILED → 生成失败
    ↓
本地状态: failed
```

## 🕐 时间线

```
T=0s:    用户点击"生成视频"
T=0.5s:  后端提交异步任务，返回 task_id
T=0.5s:  前端收到响应，显示"处理中..."
T=3s:    前端第1次轮询 → 状态: PENDING
T=6s:    前端第2次轮询 → 状态: RUNNING
T=9s:    前端第3次轮询 → 状态: RUNNING
...
T=60s:   前端第20次轮询 → 状态: SUCCEEDED
T=60s:   后端下载视频
T=63s:   前端收到完成状态，显示视频
```

## 🔍 日志输出

### 提交阶段
```
INFO: 开始文生视频任务: uuid-123
INFO: 调用文生视频API（异步）: uuid-123, duration=5, seed=1234567
INFO: 使用随机种子: 1234567
INFO: 异步API响应状态: 200
INFO: 异步任务已提交: task_id=uuid-123, api_task_id=ds-task-456
```

### 轮询阶段
```
INFO: 轮询异步任务状态: task_id=uuid-123, api_task_id=ds-task-456
INFO: 查询视频任务状态: api_task_id=ds-task-456
INFO: 任务状态: RUNNING
（等待3秒...）

INFO: 轮询异步任务状态: task_id=uuid-123, api_task_id=ds-task-456
INFO: 查询视频任务状态: api_task_id=ds-task-456
INFO: 任务状态: SUCCEEDED
INFO: 视频生成完成: uuid-123
INFO: 开始下载视频: https://dashscope-result...
INFO: 视频保存成功: ai-videos/1/20251016/uuid-123.mp4
INFO: 视频记录保存成功: uuid-123
```

## 📦 API 方法对比

| 方法 | 说明 | 返回时间 | 适用场景 |
|-----|------|---------|---------|
| `VideoSynthesis.call()` | 同步调用 | 30-120秒 | ❌ 容易超时 |
| `VideoSynthesis.async_call()` | 异步调用 | <1秒 | ✅ 立即返回 |
| `VideoSynthesis.fetch()` | 查询状态 | <1秒 | ✅ 轮询使用 |
| `VideoSynthesis.wait()` | 等待完成 | 30-120秒 | ⚠️ 阻塞调用 |

## 🎯 优势

### 异步模式优势
- ✅ **快速响应**: 1秒内返回
- ✅ **避免超时**: 不会HTTP超时
- ✅ **用户体验好**: 可以查看进度
- ✅ **资源高效**: 不占用HTTP连接
- ✅ **可扩展**: 支持批量任务

### 同步模式劣势
- ❌ 响应慢（30-120秒）
- ❌ 容易超时
- ❌ 连接占用
- ❌ 无法查看进度

## 🔧 完整流程示例

### 提交任务
```python
# 1. 异步调用
response = VideoSynthesis.async_call(
    api_key=api_key,
    model='wan2.5-t2v-preview',
    prompt='一只小猫在花园里玩耍',
    size='1280*720',
    duration=5,
    seed=123456,
    audio=True
)

# 2. 立即返回任务ID
api_task_id = response.output.task_id

# 3. 保存到数据库
task.api_task_id = api_task_id
task.status = 'processing'
task.save()

# 4. 返回给前端
return {'task_id': task.task_id, 'status': 'processing'}
```

### 轮询状态
```python
# 前端每3秒调用一次
GET /api/v1/chat/ai-video/task/{task_id}/status/

# 后端查询 DashScope
response = VideoSynthesis.fetch(api_key=api_key, task_id=api_task_id)
task_status = response.output.task_status

# 返回状态
if task_status == 'SUCCEEDED':
    # 下载视频，更新数据库
    video_url = response.output.video_url
    # ... 下载和保存
    return {'status': 'completed', 'result_url': video_url}
else:
    return {'status': 'processing'}
```

## 📋 任务状态映射

| DashScope 状态 | 本地状态 | 前端显示 |
|---------------|---------|---------|
| PENDING | processing | 等待中... |
| RUNNING | processing | 生成中... |
| SUCCEEDED | completed | ✅ 完成 |
| FAILED | failed | ❌ 失败 |

## ⚙️ 配置参数

### 前端轮询配置
```typescript
const maxAttempts = 60      // 最多轮询60次
const pollInterval = 3000   // 每3秒轮询一次
// 最长等待时间 = 60 * 3 = 180秒
```

### 后端超时配置
```python
timeout = 60  # 下载视频超时60秒
```

## ⚠️ 注意事项

### 1. API 参数差异
```python
# 异步调用需要明确传递 api_key
VideoSynthesis.async_call(api_key=self.api_key, ...)

# fetch 也需要 api_key
VideoSynthesis.fetch(api_key=self.api_key, task_id=api_task_id)
```

### 2. 任务状态检查
- 只有 `status='processing'` 且有 `api_task_id` 时才查询
- 避免重复查询已完成的任务
- 失败任务不再查询

### 3. 数据库字段
```python
task.api_task_id      # DashScope 返回的任务ID（用于查询）
task.task_id          # 本地任务ID（用户查询）
task.status           # 本地状态（processing/completed/failed）
```

## 🧪 测试场景

### 正常流程
1. 提交任务 → 返回 processing
2. 轮询1次 → PENDING
3. 轮询2次 → RUNNING
4. 轮询N次 → SUCCEEDED
5. 自动下载视频
6. 返回 completed + video_url

### 失败流程
1. 提交任务 → 返回 processing
2. 轮询N次 → FAILED
3. 返回 failed + error_message

### 超时处理
1. 前端轮询60次（180秒）
2. 仍未完成 → 提示"处理时间较长，请稍后查看历史记录"
3. 后台继续处理，用户可刷新查看

## ✅ 完成清单

- ✅ 使用 `async_call()` 异步提交
- ✅ 使用 `fetch()` 查询状态
- ✅ 立即返回 task_id
- ✅ 前端轮询机制（已有）
- ✅ 后端智能轮询查询
- ✅ 自动下载视频
- ✅ 状态更新到数据库
- ✅ 传递 duration 和 seed 参数
- ✅ 完整的错误处理
- ✅ 详细的日志记录

## 📊 性能对比

| 模式 | 响应时间 | 超时风险 | 用户体验 |
|-----|---------|---------|---------|
| 同步 | 30-120秒 | ❌ 高 | ❌ 差 |
| 异步 | <1秒 | ✅ 无 | ✅ 好 |

## 🎉 优势总结

1. **快速响应** - 1秒内返回，不阻塞
2. **避免超时** - 不会HTTP超时
3. **实时进度** - 用户可看到处理状态
4. **可扩展** - 支持多任务并行
5. **资源高效** - 不占用HTTP连接
6. **容错性好** - 轮询失败不影响生成

---

**实现日期**: 2025-10-16  
**模式**: 异步（async_call + fetch 轮询）  
**状态**: ✅ 完成  
**响应时间**: <1秒

