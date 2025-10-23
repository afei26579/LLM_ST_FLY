# 智能客服知识库系统实现方案

## 📋 功能概述

已实现完整的知识库管理和客服助手自定义功能：

### 1. 知识库管理
- ✅ 创建/编辑/删除知识库
- ✅ 上传多种格式文档（TXT、PDF、DOCX、MD）
- ✅ 智能文档切片
- ✅ 智能文档清洗
- ✅ 向量化存储（PostgreSQL + pgvector）

### 2. 文档处理功能

#### 切片策略
- **智能切片 (auto)**: 自动分析文档结构选择最佳策略
- **固定长度 (fixed)**: 按指定字符数切片，支持重叠
- **语义切片 (semantic)**: 基于段落和语义边界切片

#### 清洗策略
- **智能清洗 (auto)**: 自动识别并清理无用内容
  - 移除页码、页眉页脚
  - 移除URL、邮箱
  - 标准化空白字符
  - 保留有意义的标点
- **基础清洗 (basic)**: 基本格式化
- **自定义清洗**: 支持正则表达式规则

### 3. 客服助手配置
- ✅ 创建多个自定义助手
- ✅ 自定义名称和头像
- ✅ 设置开场白
- ✅ 配置系统提示词
- ✅ 选择关联知识库
- ✅ 调整AI参数（模型、温度、检索数量）
- ✅ 启用/禁用功能模块

### 4. 向量检索
- ✅ 向量相似度搜索（余弦相似度）
- ✅ 关键词全文搜索
- ✅ 混合检索（向量+关键词）
- ✅ pgvector索引优化

---

## 🗄️ 数据库设计

### 表结构

#### 1. KnowledgeBase (cs_knowledge_base)
```sql
- id: 主键
- user_id: 用户ID
- name: 知识库名称
- description: 描述
- status: 状态 (creating/processing/ready/error)
- document_count: 文档数量
- chunk_count: 切片数量
- total_tokens: 总token数
- created_at, updated_at
```

#### 2. KnowledgeDocument (cs_knowledge_document)
```sql
- id: 主键
- knowledge_base_id: 关联知识库
- filename: 文件名
- file_type: 文件类型
- file_size: 文件大小
- file_path: 存储路径
- status: 处理状态
- chunk_strategy: 切片策略
- chunk_size: 切片大小
- chunk_overlap: 切片重叠
- clean_strategy: 清洗策略
- chunk_count: 切片数量
- token_count: token数量
- metadata: 元数据(JSON)
- created_at, updated_at, processed_at
```

#### 3. DocumentChunk (cs_document_chunk)
```sql
- id: 主键
- document_id: 关联文档
- knowledge_base_id: 关联知识库
- content: 切片内容
- chunk_index: 切片索引
- embedding: 向量嵌入 (vector[1536])
- metadata: 元数据(JSON)
- token_count: token数量
- created_at
```

#### 4. CustomerServiceAssistant (cs_assistant)
```sql
- id: 主键
- user_id: 用户ID
- name: 助手名称
- description: 描述
- avatar: 头像emoji
- greeting_message: 开场白
- system_prompt: 系统提示词
- model: AI模型
- temperature: 温度参数
- top_k: 检索数量
- enable_knowledge_base: 启用知识库
- enable_order_query: 启用订单查询
- enable_human_handoff: 启用人工转接
- is_active: 是否启用
- is_default: 是否默认
- total_conversations: 总对话数
- total_messages: 总消息数
- avg_satisfaction: 平均满意度
- created_at, updated_at
```

#### 5. CustomerServiceSession (更新)
添加字段：
```sql
- assistant_id: 关联助手
```

---

## 🔧 核心服务

### 1. DocumentProcessor (document_processor.py)

#### 文档清洗器 (DocumentCleaner)
```python
# 智能清洗
text = DocumentCleaner.auto_clean(text)

# 基础清洗
text = DocumentCleaner.basic_clean(text)

# 自定义清洗
rules = [
    {"pattern": r"\d+页", "replacement": ""},
    {"pattern": r"http[s]?://\S+", "replacement": ""}
]
text = DocumentCleaner.custom_clean(text, rules)
```

#### 文档切片器 (DocumentChunker)
```python
# 固定长度切片
chunks = DocumentChunker.chunk_by_fixed_size(
    text, 
    chunk_size=500, 
    overlap=50
)

# 语义切片
chunks = DocumentChunker.chunk_by_semantic(
    text,
    max_chunk_size=500,
    min_chunk_size=100
)

# 智能切片
chunks = DocumentChunker.chunk_auto(text)
```

### 2. VectorService (vector_service.py)

#### 向量化
```python
vector_service = VectorService()

# 单文本
embedding = vector_service.get_embedding("查询文本")

# 批量
embeddings = vector_service.get_embeddings_batch([
    "文本1", "文本2", "文本3"
])
```

#### 检索
```python
retriever = VectorRetriever()

# 向量检索
results = retriever.search_similar_chunks(
    query="如何退货",
    knowledge_base_ids=[1, 2],
    top_k=5,
    similarity_threshold=0.7
)

# 混合检索（推荐）
results = retriever.search_hybrid(
    query="如何退货",
    knowledge_base_ids=[1, 2],
    top_k=5,
    vector_weight=0.7,
    keyword_weight=0.3
)
```

---

## 📡 API 接口

### 知识库管理

#### 创建知识库
```http
POST /api/v1/agent/customer-service/knowledge-bases/
{
  "name": "产品知识库",
  "description": "包含所有产品相关信息"
}
```

#### 上传文档
```http
POST /api/v1/agent/customer-service/documents/upload/
Content-Type: multipart/form-data

{
  "knowledge_base_id": 1,
  "file": <文件>,
  "chunk_strategy": "auto",    # auto/fixed/semantic
  "chunk_size": 500,
  "chunk_overlap": 50,
  "clean_strategy": "auto"     # auto/basic/none
}
```

#### 搜索知识库
```http
POST /api/v1/agent/customer-service/knowledge-bases/search/
{
  "query": "如何退货",
  "knowledge_base_ids": [1, 2],
  "top_k": 5,
  "search_type": "hybrid"      # vector/keyword/hybrid
}
```

### 助手配置

#### 创建助手
```http
POST /api/v1/agent/customer-service/assistants/
{
  "name": "售后客服",
  "description": "专门处理售后问题",
  "avatar": "🛠️",
  "greeting_message": "您好！我是售后客服，请问有什么可以帮您？",
  "system_prompt": "你是专业的售后客服，要耐心解答问题...",
  "knowledge_bases": [1, 2],
  "model": "qwen-plus",
  "temperature": 0.7,
  "top_k": 3,
  "enable_knowledge_base": true,
  "is_default": false
}
```

#### 使用指定助手对话
```http
POST /api/v1/agent/customer-service/chat/
{
  "message": "我想退货",
  "session_id": "uuid",
  "assistant_id": 1    # 指定使用的助手
}
```

---

## 🚀 部署步骤

### 1. 安装依赖
```bash
pip install pgvector
pip install openai
pip install PyPDF2
pip install python-docx
```

更新 `requirements.txt`:
```
pgvector==0.2.4
openai>=1.0.0
PyPDF2==3.0.1
python-docx==1.1.0
```

### 2. 配置PostgreSQL

启用pgvector扩展:
```sql
CREATE EXTENSION vector;
```

或在Django中自动初始化:
```python
from agent.customer_service.vector_service import init_pgvector
init_pgvector()
```

### 3. 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 配置环境变量
```python
# settings.py
DASHSCOPE_API_KEY = 'your_api_key'

# 文件上传配置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
```

---

## 💡 使用流程

### 场景1: 创建知识库助手

1. **创建知识库**
```python
knowledge_base = KnowledgeBase.objects.create(
    user=request.user,
    name="产品手册",
    description="所有产品使用手册"
)
```

2. **上传文档**
```python
# 通过API上传PDF/DOCX/TXT文档
# 系统自动: 提取文本 → 清洗 → 切片 → 向量化
```

3. **创建助手**
```python
assistant = CustomerServiceAssistant.objects.create(
    user=request.user,
    name="产品客服",
    greeting_message="您好！关于产品使用有什么疑问吗？",
    is_default=True
)
assistant.knowledge_bases.add(knowledge_base)
```

4. **开始对话**
```python
# 用户对话时自动使用知识库检索
# LangGraph服务会调用向量检索找到相关信息
```

### 场景2: 文档处理示例

```python
from agent.customer_service.document_processor import DocumentProcessor

processor = DocumentProcessor()

# 处理文档
chunks = processor.process_document(
    text=document_text,
    chunk_strategy='semantic',  # 语义切片
    chunk_size=500,
    chunk_overlap=50,
    clean_strategy='auto'  # 智能清洗
)

# 向量化并存储
from agent.customer_service.vector_service import VectorService

vector_service = VectorService()
for chunk in chunks:
    embedding = vector_service.get_embedding(chunk.content)
    DocumentChunk.objects.create(
        document=document,
        knowledge_base=kb,
        content=chunk.content,
        chunk_index=chunk.index,
        embedding=embedding,
        metadata=chunk.metadata
    )
```

---

## 🎯 性能优化

### 1. 向量索引
```sql
-- IVFFlat索引 - 加速向量搜索
CREATE INDEX cs_chunk_embedding_idx 
ON cs_document_chunk 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 2. 批量向量化
```python
# 批量处理，减少API调用
texts = [chunk.content for chunk in chunks]
embeddings = vector_service.get_embeddings_batch(texts)
```

### 3. 缓存常用查询
```python
# Redis缓存检索结果
cache_key = f"search:{query}:{kb_ids}"
cached_result = cache.get(cache_key)
if cached_result:
    return cached_result
```

---

## 📊 监控指标

### 关键指标
- 知识库数量和大小
- 文档处理成功率
- 向量检索响应时间
- 检索准确率（通过满意度反馈）
- token使用量

### 日志记录
```python
ChunkProcessingLog.objects.create(
    document=doc,
    step='chunking',
    status='success',
    message=f'生成{len(chunks)}个切片',
    details={'chunk_count': len(chunks)}
)
```

---

## 🔍 故障排查

### Q: pgvector扩展未安装？
```bash
# PostgreSQL 需要先安装pgvector
# Ubuntu/Debian:
apt-get install postgresql-14-pgvector

# 然后在数据库中:
CREATE EXTENSION vector;
```

### Q: 向量检索很慢？
```sql
-- 确保创建了向量索引
SELECT indexname FROM pg_indexes 
WHERE tablename = 'cs_document_chunk';
```

### Q: 文档处理失败？
```python
# 检查日志
ChunkProcessingLog.objects.filter(
    document=doc, 
    status='failed'
)
```

---

## 📚 参考资料

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [DashScope文档](https://help.aliyun.com/zh/dashscope/)

---

**实现状态**: ✅ 核心功能完成  
**下一步**: 创建前端管理界面

**更新日期**: 2025-10-22

