# 使用示例

## 📚 知识库功能示例

### 示例1: 创建产品知识库

```python
from agent.customer_service.models_extended import KnowledgeBase, KnowledgeDocument
from agent.customer_service.document_processor import DocumentProcessor
from agent.customer_service.vector_service import VectorService
from django.contrib.auth import get_user_model

User = get_user_model()

# 1. 创建知识库
user = User.objects.get(username='admin')
kb = KnowledgeBase.objects.create(
    user=user,
    name="产品使用手册",
    description="包含所有产品的使用说明和常见问题"
)

# 2. 准备文档内容
document_text = """
产品使用手册

第一章：快速开始
1. 开机：长按电源键3秒
2. 配置：打开手机APP进行蓝牙配对
3. 使用：通过APP控制所有功能

第二章：常见问题
Q: 如何充电？
A: 使用附带的磁吸充电线，连接设备背面的充电触点。

Q: 续航时间多久？
A: 正常使用可续航7天，重度使用约3天。

第三章：售后服务
保修期：12个月
联系方式：400-xxx-xxxx
"""

# 3. 处理文档
processor = DocumentProcessor()
chunks = processor.process_document(
    text=document_text,
    chunk_strategy='semantic',    # 语义切片
    chunk_size=500,
    clean_strategy='auto'         # 智能清洗
)

print(f"生成了 {len(chunks)} 个切片")

# 4. 向量化并存储
vector_service = VectorService()

# 批量获取向量
texts = [chunk.content for chunk in chunks]
embeddings = vector_service.get_embeddings_batch(texts)

# 创建文档记录
doc = KnowledgeDocument.objects.create(
    knowledge_base=kb,
    filename="产品使用手册.txt",
    file_type="txt",
    file_size=len(document_text),
    file_path="/path/to/file",
    chunk_strategy='semantic',
    clean_strategy='auto',
    status='completed'
)

# 批量创建切片
from agent.customer_service.models_extended import DocumentChunk

chunk_objects = []
for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    chunk_objects.append(DocumentChunk(
        document=doc,
        knowledge_base=kb,
        content=chunk.content,
        chunk_index=i,
        embedding=embedding,
        metadata=chunk.metadata,
        token_count=chunk.token_count
    ))

DocumentChunk.objects.bulk_create(chunk_objects)

# 5. 更新统计
kb.document_count = 1
kb.chunk_count = len(chunks)
kb.total_tokens = sum(c.token_count for c in chunks)
kb.status = 'ready'
kb.save()

print(f"✅ 知识库创建成功！")
print(f"  - 文档数: {kb.document_count}")
print(f"  - 切片数: {kb.chunk_count}")
print(f"  - Token数: {kb.total_tokens}")
```

### 示例2: 测试向量检索

```python
from agent.customer_service.vector_service import VectorRetriever

retriever = VectorRetriever()

# 向量检索
results = retriever.search_similar_chunks(
    query="如何充电？",
    knowledge_base_ids=[kb.id],
    top_k=3,
    similarity_threshold=0.7
)

print(f"找到 {len(results)} 个相关结果：")
for i, result in enumerate(results, 1):
    print(f"\n结果 {i}:")
    print(f"  内容: {result['content'][:100]}...")
    print(f"  相似度: {result['similarity']:.2%}")
    print(f"  来源: {result['filename']}")

# 混合检索（推荐）
hybrid_results = retriever.search_hybrid(
    query="续航时间",
    knowledge_base_ids=[kb.id],
    top_k=3,
    vector_weight=0.7,
    keyword_weight=0.3
)

print(f"\n混合检索找到 {len(hybrid_results)} 个结果：")
for result in hybrid_results:
    print(f"  - {result['content'][:80]}...")
    print(f"    最终得分: {result['final_score']:.3f}")
```

### 示例3: 创建自定义助手

```python
from agent.customer_service.models_extended import CustomerServiceAssistant

# 创建售后客服助手
售后助手 = CustomerServiceAssistant.objects.create(
    user=user,
    name="售后客服小王",
    description="专门处理售后问题的客服助手",
    avatar="🛠️",
    greeting_message="您好！我是售后客服小王，请问遇到什么问题了？",
    system_prompt="""你是一个专业、耐心的售后客服。

你的职责：
1. 帮助用户解决产品使用问题
2. 处理退换货申请
3. 解答保修政策
4. 提供技术支持

你的特点：
- 语气友好、富有同理心
- 专业、准确地回答问题
- 主动提供解决方案
- 遇到复杂问题及时转人工

请始终保持耐心和专业。""",
    model='qwen-plus',
    temperature=0.7,
    top_k=3,
    enable_knowledge_base=True,
    enable_order_query=True,
    enable_human_handoff=True,
    is_active=True,
    is_default=True
)

# 关联知识库
售后助手.knowledge_bases.add(kb)

print(f"✅ 助手创建成功: {售后助手.name}")
```

### 示例4: 使用助手进行对话

```python
from agent.customer_service.langgraph_service import CustomerServiceGraph

# 初始化服务
graph = CustomerServiceGraph()

# 模拟对话
result = graph.run(
    user_message="我的手表充不进电",
    user_id=user.id,
    session_id="test-session-001",
    history=[]
)

print("AI回复:", result['response'])
print("意图:", result['intent'])
print("实体:", result['entities'])
print("需要转人工:", result['need_human'])
```

---

## 🔧 文档处理策略对比

### 智能切片 vs 固定长度 vs 语义切片

```python
document_text = "..." # 你的文档内容

processor = DocumentProcessor()

# 方式1: 智能切片（推荐）
chunks_auto = processor.process_document(
    text=document_text,
    chunk_strategy='auto',  # 自动选择最佳策略
    clean_strategy='auto'
)

# 方式2: 固定长度
chunks_fixed = processor.process_document(
    text=document_text,
    chunk_strategy='fixed',
    chunk_size=500,         # 每个切片500字符
    chunk_overlap=50,       # 重叠50字符
    clean_strategy='auto'
)

# 方式3: 语义切片
chunks_semantic = processor.process_document(
    text=document_text,
    chunk_strategy='semantic',  # 基于段落和句子
    chunk_size=500,             # 最大切片大小
    clean_strategy='auto'
)

# 对比
print(f"智能切片: {len(chunks_auto)} 个")
print(f"固定长度: {len(chunks_fixed)} 个")
print(f"语义切片: {len(chunks_semantic)} 个")
```

### 清洗策略对比

```python
from agent.customer_service.document_processor import DocumentCleaner

dirty_text = """
第1页
产品介绍
http://example.com
联系邮箱: support@example.com


第2页
使用说明...
"""

# 方式1: 智能清洗
clean_auto = DocumentCleaner.auto_clean(dirty_text)
print("智能清洗结果:", clean_auto)

# 方式2: 基础清洗
clean_basic = DocumentCleaner.basic_clean(dirty_text)
print("基础清洗结果:", clean_basic)

# 方式3: 自定义清洗
rules = [
    {"pattern": r"第\d+页", "replacement": ""},
    {"pattern": r"http[s]?://\S+", "replacement": ""},
    {"pattern": r"\S+@\S+\.\S+", "replacement": ""}
]
clean_custom = DocumentCleaner.custom_clean(dirty_text, rules)
print("自定义清洗结果:", clean_custom)
```

---

## 🔍 检索策略对比

### 向量检索 vs 关键词检索 vs 混合检索

```python
retriever = VectorRetriever()

query = "如何退货"
kb_ids = [1, 2]

# 1. 纯向量检索
vector_results = retriever.search_similar_chunks(
    query=query,
    knowledge_base_ids=kb_ids,
    top_k=5
)
print(f"向量检索: {len(vector_results)} 个结果")

# 2. 关键词检索
keyword_results = retriever._keyword_search(
    query=query,
    knowledge_base_ids=kb_ids,
    top_k=5
)
print(f"关键词检索: {len(keyword_results)} 个结果")

# 3. 混合检索（推荐）
hybrid_results = retriever.search_hybrid(
    query=query,
    knowledge_base_ids=kb_ids,
    top_k=5,
    vector_weight=0.7,      # 向量权重70%
    keyword_weight=0.3      # 关键词权重30%
)
print(f"混合检索: {len(hybrid_results)} 个结果")

# 分析结果
for result in hybrid_results:
    print(f"\n内容: {result['content'][:80]}...")
    print(f"  向量分数: {result.get('vector_score', 0):.3f}")
    print(f"  关键词分数: {result.get('keyword_score', 0):.3f}")
    print(f"  最终分数: {result['final_score']:.3f}")
```

---

## 🎯 实际应用场景

### 场景1: 产品客服

```python
# 1. 创建产品知识库
产品库 = KnowledgeBase.objects.create(
    user=user,
    name="产品知识库",
    description="产品参数、功能说明、使用教程"
)

# 2. 上传产品手册（PDF）
# 通过API: POST /documents/upload/

# 3. 创建产品客服助手
产品客服 = CustomerServiceAssistant.objects.create(
    user=user,
    name="产品顾问小李",
    avatar="📱",
    greeting_message="您好！我是产品顾问，请问对哪款产品感兴趣？",
    system_prompt="你是专业的产品顾问，熟悉所有产品特性...",
    model='qwen-plus',
    is_default=True
)
产品客服.knowledge_bases.add(产品库)

# 4. 用户对话
# "这款手表防水吗？" → 自动从知识库检索相关信息并回答
```

### 场景2: 技术支持

```python
# 1. 创建技术知识库
技术库 = KnowledgeBase.objects.create(
    user=user,
    name="技术支持库",
    description="故障排查、配置教程、FAQ"
)

# 2. 上传技术文档（多个DOCX）
# 通过API批量上传

# 3. 创建技术支持助手
技术支持 = CustomerServiceAssistant.objects.create(
    user=user,
    name="技术支持工程师",
    avatar="🔧",
    greeting_message="您好！遇到技术问题了吗？我来帮您解决。",
    system_prompt="你是技术支持工程师，擅长故障诊断和问题解决...",
    model='qwen-max',  # 使用更强大的模型
    temperature=0.5,   # 更准确的回答
    top_k=5            # 检索更多参考
)
技术支持.knowledge_bases.add(技术库)
```

### 场景3: 多知识库综合助手

```python
# 创建综合客服助手，关联多个知识库
综合客服 = CustomerServiceAssistant.objects.create(
    user=user,
    name="全能客服",
    avatar="🌟",
    greeting_message="您好！我是全能客服，可以帮您解决各类问题。",
    system_prompt="你是全能客服，可以回答产品、售后、技术等各类问题..."
)

# 关联多个知识库
综合客服.knowledge_bases.add(产品库, 技术库, 售后库)

# 这样助手就能从多个知识库中检索信息
```

---

## 🧪 测试代码

### 测试文档处理

```python
def test_document_processing():
    """测试文档处理完整流程"""
    from agent.customer_service.document_processor import DocumentProcessor
    
    processor = DocumentProcessor()
    
    test_text = "这是一个测试文档。" * 100
    
    # 测试智能切片
    chunks = processor.process_document(
        text=test_text,
        chunk_strategy='auto',
        clean_strategy='auto'
    )
    
    assert len(chunks) > 0, "切片数量应大于0"
    assert all(chunk.content for chunk in chunks), "所有切片应有内容"
    
    print(f"✅ 文档处理测试通过: {len(chunks)} 个切片")
    return True

test_document_processing()
```

### 测试向量检索

```python
def test_vector_search():
    """测试向量检索"""
    from agent.customer_service.vector_service import VectorRetriever
    
    retriever = VectorRetriever()
    
    # 假设已有知识库数据
    results = retriever.search_similar_chunks(
        query="测试查询",
        knowledge_base_ids=[1],
        top_k=3
    )
    
    print(f"✅ 向量检索测试通过: {len(results)} 个结果")
    for r in results:
        print(f"  - 相似度: {r.get('similarity', 0):.2%}")
    
    return True

test_vector_search()
```

---

## 🌐 API调用示例

### 创建知识库

```bash
curl -X POST http://localhost:8000/api/v1/agent/customer-service/knowledge-bases/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "FAQ知识库",
    "description": "常见问题解答"
  }'
```

### 上传文档

```bash
curl -X POST http://localhost:8000/api/v1/agent/customer-service/documents/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "knowledge_base_id=1" \
  -F "file=@产品手册.pdf" \
  -F "chunk_strategy=semantic" \
  -F "chunk_size=500" \
  -F "chunk_overlap=50" \
  -F "clean_strategy=auto"
```

### 搜索知识库

```bash
curl -X POST http://localhost:8000/api/v1/agent/customer-service/knowledge-bases/search/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何退货",
    "knowledge_base_ids": [1, 2],
    "top_k": 5,
    "search_type": "hybrid"
  }'
```

### 创建助手

```bash
curl -X POST http://localhost:8000/api/v1/agent/customer-service/assistants/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "产品客服",
    "avatar": "📱",
    "greeting_message": "您好！关于产品有什么疑问吗？",
    "system_prompt": "你是产品客服，专业友好...",
    "knowledge_bases": [1],
    "model": "qwen-plus",
    "temperature": 0.7,
    "top_k": 3,
    "is_default": true
  }'
```

### 使用助手对话

```bash
curl -X POST http://localhost:8000/api/v1/agent/customer-service/chat/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "手表如何充电？",
    "assistant_id": 1
  }'
```

---

## 💡 实用技巧

### 技巧1: 批量处理文档

```python
import os
from pathlib import Path

def batch_upload_documents(kb_id, folder_path):
    """批量上传文件夹中的所有文档"""
    processor = DocumentProcessor()
    vector_service = VectorService()
    
    kb = KnowledgeBase.objects.get(id=kb_id)
    
    for file_path in Path(folder_path).glob('*.txt'):
        # 读取文本
        text = file_path.read_text(encoding='utf-8')
        
        # 处理文档
        chunks = processor.process_document(
            text=text,
            chunk_strategy='auto',
            clean_strategy='auto'
        )
        
        # 创建文档记录
        doc = KnowledgeDocument.objects.create(
            knowledge_base=kb,
            filename=file_path.name,
            file_type='txt',
            file_size=len(text),
            file_path=str(file_path),
            status='completed'
        )
        
        # 向量化并存储
        texts = [c.content for c in chunks]
        embeddings = vector_service.get_embeddings_batch(texts)
        
        DocumentChunk.objects.bulk_create([
            DocumentChunk(
                document=doc,
                knowledge_base=kb,
                content=c.content,
                chunk_index=i,
                embedding=emb,
                metadata=c.metadata
            )
            for i, (c, emb) in enumerate(zip(chunks, embeddings))
        ])
        
        print(f"✅ 已处理: {file_path.name}")
    
    # 更新知识库统计
    kb.document_count = kb.documents.count()
    kb.chunk_count = kb.chunks.count()
    kb.status = 'ready'
    kb.save()
```

### 技巧2: 自定义清洗规则

```python
# 定义自己的清洗规则
custom_rules = [
    # 移除页码
    {"pattern": r"第\s*\d+\s*页", "replacement": ""},
    {"pattern": r"Page\s*\d+", "replacement": ""},
    
    # 移除章节编号
    {"pattern": r"第[一二三四五六七八九十]+章", "replacement": ""},
    
    # 移除特定文本
    {"pattern": r"版权所有.*?保留", "replacement": ""},
    
    # 统一日期格式
    {"pattern": r"(\d{4})年(\d{1,2})月(\d{1,2})日", "replacement": r"\1-\2-\3"},
]

# 使用自定义规则
chunks = processor.process_document(
    text=document_text,
    chunk_strategy='auto',
    clean_strategy='custom',
    custom_clean_rules=custom_rules
)
```

### 技巧3: 优化检索参数

```python
# 根据不同场景调整检索参数

# 场景1: 需要高精度（如技术文档）
retriever.search_hybrid(
    query=query,
    knowledge_base_ids=kb_ids,
    top_k=3,
    vector_weight=0.8,      # 更依赖向量检索
    keyword_weight=0.2
)

# 场景2: 需要高召回（如FAQ）
retriever.search_hybrid(
    query=query,
    knowledge_base_ids=kb_ids,
    top_k=10,               # 返回更多结果
    vector_weight=0.5,
    keyword_weight=0.5      # 平衡两种方式
)

# 场景3: 专业术语检索
retriever.search_hybrid(
    query=query,
    knowledge_base_ids=kb_ids,
    top_k=5,
    vector_weight=0.3,
    keyword_weight=0.7      # 更依赖关键词匹配
)
```

---

## 🐛 调试技巧

### 查看切片内容

```python
# 查看某个文档的所有切片
doc = KnowledgeDocument.objects.get(id=1)
chunks = doc.chunks.all().order_by('chunk_index')

for chunk in chunks:
    print(f"\n切片 {chunk.chunk_index}:")
    print(f"  内容: {chunk.content[:100]}...")
    print(f"  Token数: {chunk.token_count}")
    print(f"  元数据: {chunk.metadata}")
```

### 测试相似度

```python
# 测试两个文本的相似度
from agent.customer_service.vector_service import VectorService

vector_service = VectorService()

text1 = "如何退货"
text2 = "退换货流程"

emb1 = vector_service.get_embedding(text1)
emb2 = vector_service.get_embedding(text2)

# 计算余弦相似度
import numpy as np
similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
print(f"相似度: {similarity:.2%}")
```

---

## 📚 更多资源

- [完整技术文档](./KNOWLEDGE_BASE_IMPLEMENTATION.md)
- [快速启动指南](./QUICK_SETUP.md)
- [故障排查指南](./README.md#故障排查)
- [pgvector官方文档](https://github.com/pgvector/pgvector)

---

**最后更新**: 2025-10-22  
**文档版本**: v1.0

