# 🚀 知识库功能快速启动指南

## 第一步：安装依赖

```bash
cd backend
pip install -r agent/customer_service/requirements_extended.txt
```

主要新增依赖：
- `pgvector` - PostgreSQL向量扩展
- `openai` - OpenAI SDK（兼容DashScope）
- `PyPDF2` - PDF处理
- `python-docx` - Word文档处理

---

## 第二步：配置PostgreSQL

### 1. 安装pgvector扩展

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-14-pgvector
```

**Mac (Homebrew):**
```bash
brew install pgvector
```

**Windows:**
下载并安装: https://github.com/pgvector/pgvector/releases

### 2. 启用扩展

连接到PostgreSQL数据库：
```bash
psql -U your_user -d your_database
```

执行：
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

验证：
```sql
SELECT * FROM pg_extension WHERE extname = 'vector';
```

---

## 第三步：更新Django配置

### 1. 在 `settings.py` 中添加：

```python
# agent/customer_service 扩展配置
INSTALLED_APPS = [
    ...
    'pgvector',  # 添加pgvector应用
]

# 文件上传配置
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/knowledge_base')
MEDIA_URL = '/media/'
MAX_UPLOAD_SIZE = 20 * 1024 * 1024  # 20MB

# DashScope API配置（如果还没有）
DASHSCOPE_API_KEY = env('DASHSCOPE_API_KEY', default='your_api_key')
```

### 2. 更新 `models.py`

在 `agent/customer_service/models.py` 中的 `CustomerServiceSession` 添加：

```python
from .models_extended import CustomerServiceAssistant

class CustomerServiceSession(models.Model):
    ...
    # 添加这个字段
    assistant = models.ForeignKey(
        'CustomerServiceAssistant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions',
        verbose_name='使用的助手'
    )
```

---

## 第四步：数据库迁移

```bash
cd backend

# 生成迁移文件
python manage.py makemigrations agent

# 执行迁移
python manage.py migrate

# 初始化pgvector索引
python manage.py shell
```

在Python shell中：
```python
from agent.customer_service.vector_service import init_pgvector
init_pgvector()
```

---

## 第五步：创建默认助手和知识库

### 方式1: 通过Django Admin

```bash
python manage.py createsuperuser  # 如果还没有
python manage.py runserver
```

访问：http://localhost:8000/admin

创建：
1. Knowledge Base（知识库）
2. Customer Service Assistant（客服助手）

### 方式2: 通过API

启动服务器：
```bash
python manage.py runserver
```

#### 创建知识库：
```bash
curl -X POST http://localhost:8000/api/v1/agent/customer-service/knowledge-bases/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "产品知识库",
    "description": "包含所有产品相关信息"
  }'
```

#### 上传文档：
```bash
curl -X POST http://localhost:8000/api/v1/agent/customer-service/documents/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "knowledge_base_id=1" \
  -F "file=@产品手册.pdf" \
  -F "chunk_strategy=auto" \
  -F "clean_strategy=auto"
```

#### 创建助手：
```bash
curl -X POST http://localhost:8000/api/v1/agent/customer-service/assistants/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "产品客服",
    "greeting_message": "您好！我是产品客服助手，有什么可以帮您？",
    "knowledge_bases": [1],
    "is_default": true
  }'
```

---

## 第六步：测试功能

### 测试文档处理：

```python
python manage.py shell
```

```python
from agent.customer_service.document_processor import DocumentProcessor

# 创建处理器
processor = DocumentProcessor()

# 测试文本
test_text = """
产品使用说明

第一章：产品介绍
本产品是一款智能设备...

第二章：使用方法
1. 开机：长按电源键3秒
2. 配置：打开手机APP进行配对
"""

# 处理文档
chunks = processor.process_document(
    text=test_text,
    chunk_strategy='auto',
    clean_strategy='auto'
)

print(f"生成 {len(chunks)} 个切片")
for chunk in chunks:
    print(f"切片 {chunk.index}: {chunk.content[:50]}...")
```

### 测试向量检索：

```python
from agent.customer_service.vector_service import VectorService, VectorRetriever
from agent.customer_service.models_extended import KnowledgeBase

# 向量化
vector_service = VectorService()
embedding = vector_service.get_embedding("如何开机")
print(f"向量维度: {len(embedding)}")

# 检索（需要先有数据）
retriever = VectorRetriever()
results = retriever.search_similar_chunks(
    query="如何使用产品",
    knowledge_base_ids=[1],
    top_k=3
)
print(f"找到 {len(results)} 个相关结果")
```

### 测试对话（使用知识库）：

```bash
curl -X POST http://localhost:8000/api/v1/agent/customer-service/chat/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "如何开机",
    "assistant_id": 1
  }'
```

---

## 第七步：前端集成（可选）

如果需要管理界面，继续创建前端页面。

---

## 常见问题

### Q1: pgvector扩展安装失败？

**检查PostgreSQL版本：**
```bash
psql --version  # 需要11+
```

**手动编译安装：**
```bash
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Q2: 向量检索无结果？

**检查数据：**
```python
from agent.customer_service.models_extended import DocumentChunk
print(DocumentChunk.objects.filter(embedding__isnull=False).count())
```

**重新生成向量：**
```python
from agent.customer_service.vector_service import VectorService

vector_service = VectorService()
for chunk in DocumentChunk.objects.filter(embedding__isnull=True):
    embedding = vector_service.get_embedding(chunk.content)
    chunk.embedding = embedding
    chunk.save()
```

### Q3: API Key配置问题？

**检查环境变量：**
```bash
echo $DASHSCOPE_API_KEY
```

**在Django settings中设置：**
```python
DASHSCOPE_API_KEY = 'sk-xxx'
```

### Q4: 文档上传失败？

**检查文件大小限制：**
```python
# settings.py
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB
```

**检查文件权限：**
```bash
chmod 755 backend/media/knowledge_base
```

---

## 性能优化建议

### 1. 批量处理文档

```python
# 批量向量化
texts = [chunk.content for chunk in chunks]
embeddings = vector_service.get_embeddings_batch(texts)

# 批量创建
DocumentChunk.objects.bulk_create([
    DocumentChunk(
        content=chunk.content,
        embedding=embedding,
        ...
    )
    for chunk, embedding in zip(chunks, embeddings)
])
```

### 2. 使用异步任务（Celery）

```python
# tasks.py
@shared_task
def process_document_async(document_id):
    # 处理文档逻辑
    pass
```

### 3. 缓存检索结果

```python
from django.core.cache import cache

cache_key = f"search:{query}:{kb_ids}"
results = cache.get(cache_key)
if not results:
    results = retriever.search_similar_chunks(...)
    cache.set(cache_key, results, timeout=3600)
```

---

## 下一步

- ✅ 基础功能已就绪
- 📝 创建知识库管理前端界面
- 📝 创建助手配置前端界面
- 📝 添加文档预览功能
- 📝 添加检索结果高亮

---

**🎉 恭喜！知识库功能已配置完成！**

现在您可以：
1. 创建多个知识库
2. 上传各种格式文档
3. 自动切片和向量化
4. 创建自定义客服助手
5. 使用知识库增强对话

需要帮助？查看完整文档：`KNOWLEDGE_BASE_IMPLEMENTATION.md`

