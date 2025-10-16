# 文字转语音功能开发说明

## 📋 功能概述

本次开发完成了基于 DashScope API (qwen3-tts-flash 模型) 的文字转语音功能。

## ✨ 主要特性

### 1. 音色支持
根据 `audio_style_list.csv` 配置，支持以下 16 种音色：

| 音色代码 | 音色名 | 描述 |
|---------|-------|------|
| Cherry | 芊悦 | 阳光积极、亲切自然小姐姐 |
| Ethan | 晨煦 | 阳光、温暖、活力、朝气 |
| Nofish | 不吃鱼 | 不会翘舌音的设计师 |
| Jennifer | 詹妮弗 | 品牌级、电影质感般美语女声 |
| Ryan | 甜茶 | 节奏拉满，戏感炸裂 |
| Katerina | 卡捷琳娜 | 御姐音色，韵律回味十足 |
| Elias | 墨讲师 | 学科严谨性与叙事技巧 |
| Jada | 上海-阿珍 | 风风火火的沪上阿姐 |
| Dylan | 北京-晓东 | 北京胡同里长大的少年 |
| Sunny | 四川-晴儿 | 甜到你心里的川妹子 |
| Li | 南京-老李 | 耐心的瑜伽老师 |
| Marcus | 陕西-秦川 | 面宽话短，心实声沉 |
| Roy | 闽南-阿杰 | 诙谐直爽、市井活泼 |
| Peter | 天津-李彼得 | 天津相声，专业捧人 |
| Rocky | 粤语-阿强 | 幽默风趣的阿强 |
| Kiki | 粤语-阿清 | 甜美的港妹闺蜜 |

### 2. 语言支持
支持 10 种语言类型：
- 中文 (Chinese)
- 英语 (English)
- 法语 (French)
- 德语 (German)
- 俄语 (Russian)
- 意大利语 (Italian)
- 西班牙语 (Spanish)
- 葡萄牙语 (Portuguese)
- 日语 (Japanese)
- 韩语 (Korean)

### 3. 输出格式
支持 3 种音频格式：
- WAV (默认)
- MP3
- PCM

## 🔧 技术实现

### 后端修改

#### 1. 模型更新 (`models.py`)
- 移除字段：`speed`, `volume`, `pitch`
- 新增字段：`language_type`
- 更新默认值：`voice='Cherry'`

#### 2. 序列化器更新 (`serializers.py`)
```python
class TextToSpeechSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=5000)
    voice = serializers.CharField(default='Cherry')
    language_type = serializers.CharField(default='Chinese')
    format = serializers.ChoiceField(choices=['mp3', 'wav', 'pcm'], default='wav')
```

#### 3. 服务层实现 (`services.py`)
使用 DashScope API 的 `MultiModalConversation.call` 方法：
```python
response = dashscope.MultiModalConversation.call(
    model="qwen3-tts-flash",
    api_key=self.api_key,
    text=audio_task.input_text,
    voice=tts_task.voice,
    language_type=tts_task.language_type,
    stream=False
)
```

#### 4. 视图更新 (`views.py`)
更新参数传递，移除 `speed`, `volume`, `pitch`，添加 `language_type`

### 前端修改

#### 1. 类型定义更新 (`api.ts`)
```typescript
export interface TextToSpeechRequest {
  text: string;
  voice?: string;
  language_type?: string;
  format?: string;
}

export interface UserAudioStats {
  total_speech_to_text: number;
  total_text_to_speech: number;
  total_voice_clone: number;
  total_audio_duration: number;
  total_storage_used: number;
  last_audio_at?: string;
}
```

#### 2. 页面更新 (`AIAudioView.vue`)
- 添加音色下拉选择列表（16个音色选项）
- 添加语言类型选择（10种语言）
- 添加输出格式选择
- 移除语速、音量、音调滑块控件
- 更新统计数据显示

### 数据库迁移

迁移文件：`0009_remove_texttospeechtask_pitch_and_more.py`

操作：
1. 移除字段：`pitch`, `speed`, `volume`
2. 新增字段：`language_type` (默认值: 'Chinese')
3. 修改字段：`voice` (默认值改为 'Cherry')

## 📝 API 使用示例

### 请求
```bash
POST /api/v1/chat/ai-audio/text-to-speech/
Content-Type: application/json
Authorization: Bearer <token>

{
  "text": "你好，这是一个测试。",
  "voice": "Cherry",
  "language_type": "Chinese",
  "format": "wav"
}
```

### 响应
```json
{
  "code": 200,
  "message": "文字转语音成功",
  "data": {
    "task_id": "uuid-string",
    "audio_url": "https://dashscope-result.oss-cn-shanghai.aliyuncs.com/...",
    "audio_id": "audio_xxx",
    "expires_at": 1759229218,
    "status": "completed",
    "usage": {
      "characters": 10
    }
  }
}
```

## 🧪 测试

运行测试脚本：
```bash
cd backend/chat/ai-audio
python test_tts.py
```

## 📌 注意事项

1. **API 密钥配置**：确保在环境变量或配置文件中正确设置 `DASHSCOPE_API_KEY`

2. **音频 URL 有效期**：DashScope 返回的音频 URL 是临时的，有过期时间（expires_at）。如需永久保存，可启用下载功能。

3. **字符限制**：单次请求文本不超过 5000 字符

4. **前端主题兼容**：下拉选择框已适配 light、dark、future 三种主题

5. **错误处理**：
   - 后端异常会更新任务状态为 'failed' 并记录错误信息
   - 前端通过 toast 提示用户错误信息

## 🔄 扩展功能建议

1. **音频下载保存**：可启用 `_download_and_save_audio` 方法将临时 URL 的音频下载到服务器永久保存

2. **批量转换**：支持多段文本批量转换

3. **历史记录**：前端添加历史记录查看功能，可重复播放或下载

4. **音频编辑**：添加音频剪辑、拼接等后处理功能

## 📚 相关文档

- [DashScope 文本转语音 API 文档](https://help.aliyun.com/zh/dashscope/)
- [项目开发指导文档](../../../开发指导.md)
- [API 响应格式文档](../../docs/api_response_format.md)

## ✅ 完成清单

- [x] 后端模型修改
- [x] 后端序列化器更新
- [x] 后端服务层实现
- [x] 后端视图更新
- [x] 前端类型定义
- [x] 前端 API 服务
- [x] 前端页面更新
- [x] 数据库迁移
- [x] 测试脚本

---

**开发完成时间**: 2025-10-16  
**开发者**: AI Assistant  
**版本**: v1.0

