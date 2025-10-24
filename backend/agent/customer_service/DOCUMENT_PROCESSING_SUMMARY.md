# 文档切片处理能力总结

## 当前支持的文档格式

### 📝 文本格式 (kb_format='text')

| 格式 | 工具/库 | 状态 | 说明 |
|------|---------|------|------|
| **TXT** | Python 内置 | ✅ 已支持 | 直接读取文本文件 |
| **MD** | Python 内置 | ✅ 已支持 | Markdown 文件作为纯文本读取 |
| **PDF** | PyPDF2 | ❌ 未安装 | 需要安装: `pip install PyPDF2` |
| **DOCX** | python-docx | ❌ 未安装 | 需要安装: `pip install python-docx` |

### 📊 结构化格式 (kb_format='structured')

| 格式 | 工具/库 | 状态 | 说明 |
|------|---------|------|------|
| **CSV** | pandas | ❌ 未安装 | 需要安装: `pip install pandas` |
| **XLSX/XLS** | pandas + openpyxl | ❌ 未安装 | 需要安装: `pip install pandas openpyxl` |
| **JSON** | Python 内置 | ✅ 已支持 | 直接解析JSON文件 |
| **XML** | Python 内置 | ✅ 已支持 | 正则移除标签后处理 |
| **HTML** | Python 内置 | ✅ 已支持 | 正则移除标签后处理 |

### 🖼️ 图片格式 (kb_format='image')

| 格式 | 工具/库 | 状态 | 说明 |
|------|---------|------|------|
| **PNG** | DashScope OCR + Pillow | ✅ 已支持 | 使用阿里云 DashScope OCR，中英文识别效果好 |
| **JPG/JPEG** | DashScope OCR + Pillow | ✅ 已支持 | 无需额外系统依赖 |
| **GIF** | DashScope OCR + Pillow | ✅ 已支持 | 通过图像理解服务统一调用 |
| **WEBP** | DashScope OCR + Pillow | ✅ 已支持 | 高置信度识别结果 |

## 切片策略

### 1. 智能切片 (strategy='auto') ✅
**特点**：
- 自动分析文本结构
- 根据段落特征选择最佳策略
- 适用于大多数场景

**逻辑**：
- 如果有明确段落结构 → 使用语义切片
- 如果结构不明确 → 使用固定长度切片

### 2. 固定长度切片 (strategy='custom') ✅
**参数**：
- `chunk_size`: 切片大小（默认500字符）
- `chunk_overlap`: 重叠度（默认50字符）
- `separator`: 分段标识符（默认换行符）

**特点**：
- 按固定字符数切片
- 支持重叠避免语义断裂
- 自定义分段符

### 3. 语义切片 (内部使用) ✅
**特点**：
- 基于段落边界
- 保持语义完整性
- 长段落自动按句子分割

## 文本清洗功能

### 基础清洗 ✅
- 移除多余空白字符
- 统一换行符
- 去除特殊符号

### 高级清洗 ✅
- 移除页码（中英文）
- 移除页眉页脚
- 移除URL（可选）
- 移除邮箱地址（可选）
- 标准化空白字符

### 自定义清洗 ✅
- 支持正则表达式规则
- 用户自定义替换规则

## 实际可用格式

### ✅ 完全支持（已在 requirements.txt 中，安装后即可使用）

**文本格式**：
1. **TXT** - 纯文本文件（Python 内置）
2. **MD** - Markdown 文件（Python 内置）
3. **PDF** - PDF 文档（PyPDF2==3.0.1）
4. **DOCX** - Word 文档（python-docx==1.1.0）

**结构化格式**：
1. **JSON** - JSON 数据（Python 内置）
2. **XML** - XML 配置（Python 内置）
3. **HTML** - HTML 网页（Python 内置）
4. **CSV** - CSV 表格（pandas==2.2.0）
5. **XLSX/XLS** - Excel 表格（pandas + openpyxl==3.1.2）

**图片格式（DashScope OCR）**：
1. **PNG** - PNG 图片（通过 AI 图像理解服务）
2. **JPG/JPEG** - JPEG 图片（通过 AI 图像理解服务）
3. **GIF** - GIF 图片（通过 AI 图像理解服务）
4. **WEBP** - WEBP 图片（通过 AI 图像理解服务）

**总计支持：13 种文档格式**

## DashScope OCR 优势

使用阿里云 DashScope 图像理解服务进行 OCR，具有以下优势：

1. **✅ 云端 API** - 调用云端服务，无需本地部署
2. **✅ 中文识别准确** - 专门优化的中文识别模型
3. **✅ 中英文混合** - 同时支持中英文混合文本
4. **✅ 高准确率** - 阿里云企业级 OCR 引擎
5. **✅ 零维护成本** - 无需管理模型更新和优化
6. **✅ 统一服务** - 复用现有的 AI 图像理解服务

## 安装依赖

运行以下命令安装所有文档处理依赖：

```bash
cd backend
D:\workspace\llm_st_fly\venv\Scripts\pip.exe install -r requirements.txt
```

**注意**：
- PDF、Word、Excel 处理依赖安装较快
- 图片 OCR 功能复用现有的 DashScope 图像理解服务，无需额外安装

## 代码位置

- **文档处理器**: `backend/agent/customer_service/document_processor.py`
- **切片接口**: `backend/agent/customer_service/views_extended.py::chunk_documents`
- **文档分析**: `backend/agent/customer_service/document_analyzer.py` (LangGraph)

## 各格式处理流程详解

### 📝 文本格式处理：
```
上传 → 文本提取 → 清洗 → 切片 → 向量化 → 异步分析
```
- **TXT/MD**: 直接读取
- **PDF**: PyPDF2 逐页提取 → 合并
- **DOCX**: python-docx 提取段落 → 合并

### 📊 结构化格式处理：
```
上传 → 解析 → 转文本 → 切片 → 向量化 → 异步分析
```
- **CSV/Excel**: pandas 读取 → 按行切片
- **JSON**: 解析 → 格式化为文本 → 切片
- **XML/HTML**: 正则移除标签 → 切片

### 🖼️ 图片格式处理（DashScope OCR）：
```
上传 → DashScope OCR识别 → 文本提取 → 切片 → 向量化 → 异步分析
```

**详细步骤**：
1. **准备图片文件**
   - 读取图片二进制内容
   - 创建 Django UploadedFile 对象

2. **调用 DashScope 多模态 API**
   ```python
   import dashscope
   
   # 构建消息
   messages = [{
       'role': 'user',
       'content': [
           {'image': f'file://{file_path}'},
           {'text': 'OCR识别提示词'}
       ]
   }]
   
   # 调用API
   response = dashscope.MultiModalConversation.call(
       model='qwen-vl-plus',
       messages=messages
   )
   ```

3. **文本提取**
   - 从 `response.output.choices[0].message.content` 提取文本
   - 处理识别结果
   - 保持原有格式和换行

4. **元数据记录**
   - 图片尺寸（宽x高）
   - OCR 引擎: DashScope-QwenVL
   - 识别状态和置信度（0.9）
   - 错误信息（如有）

5. **文本切片**
   - 如果文本 > chunk_size → 固定长度切片
   - 如果文本 ≤ chunk_size → 整体作为一个切片

## 使用示例

### 创建知识库并上传图片：
1. 选择格式: **图片格式** 📷
2. 上传: PNG、JPG、JPEG、GIF、WEBP
3. 切片策略: **智能分段**（推荐）
4. 点击"下一步" → 自动 OCR 识别
5. 预览识别结果 → 确认切片
6. 向量化 → 完成
7. **后台自动**: 文档分析智能体生成总结、问题等

### 安装后即可使用所有格式：
```bash
cd backend
D:\workspace\llm_st_fly\venv\Scripts\pip.exe install -r requirements.txt
```

