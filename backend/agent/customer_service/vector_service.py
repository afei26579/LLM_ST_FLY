"""
向量化和检索服务 - 使用 ChromaDB
"""
import logging
import os
from typing import List, Dict, Any, Optional
from django.conf import settings
import openai
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)


class VectorService:
    """向量化服务"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化向量服务
        
        Args:
            api_key: OpenAI API Key (或DashScope Key)
        """
        self.api_key = api_key or settings.DASHSCOPE_API_KEY
        # 配置为DashScope
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        self.embedding_model = "text-embedding-v4"  # DashScope最新embedding模型
        self.embedding_dim = 1536  # 嵌入维度
        
        # 初始化ChromaDB
        self._init_chromadb()
    
    def _init_chromadb(self):
        """初始化ChromaDB"""
        try:
            # ChromaDB数据目录
            chroma_data_path = os.path.join(settings.MEDIA_ROOT, 'chromadb')
            os.makedirs(chroma_data_path, exist_ok=True)
            
            # 创建ChromaDB客户端
            self.chroma_client = chromadb.PersistentClient(
                path=chroma_data_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            logger.info(f"ChromaDB初始化成功: {chroma_data_path}")
        except Exception as e:
            logger.error(f"ChromaDB初始化失败: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量嵌入
        
        Args:
            text: 输入文本
        
        Returns:
            向量列表
        """
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            embedding = response.data[0].embedding
            return embedding
        except Exception as e:
            logger.error(f"获取嵌入失败: {e}")
            raise
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取向量嵌入
        
        Args:
            texts: 文本列表
        
        Returns:
            向量列表的列表
        """
        try:
            # 分批处理，每批最多10个（DashScope限制）
            batch_size = 10
            all_embeddings = []
            
            total_batches = (len(texts) + batch_size - 1) // batch_size
            logger.info(f"开始批量向量化: 总数={len(texts)}, 批次数={total_batches}, 每批={batch_size}")
            
            for batch_num, i in enumerate(range(0, len(texts), batch_size), 1):
                batch = texts[i:i + batch_size]
                logger.info(f"处理批次 {batch_num}/{total_batches}: {len(batch)} 个文本")
                
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(embeddings)
            
            logger.info(f"批量向量化完成: 共生成 {len(all_embeddings)} 个向量")
            return all_embeddings
        except Exception as e:
            logger.error(f"批量获取嵌入失败: {e}")
            raise
    
    def get_or_create_collection(self, kb_id: int, kb_name: str):
        """获取或创建ChromaDB集合"""
        try:
            collection_name = f"kb_{kb_id}"
            
            # 尝试获取已存在的集合
            try:
                collection = self.chroma_client.get_collection(name=collection_name)
                logger.info(f"使用已存在的集合: {collection_name}")
            except:
                # 创建新集合
                collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"kb_name": kb_name, "kb_id": kb_id}
                )
                logger.info(f"创建新集合: {collection_name}")
            
            return collection
        except Exception as e:
            logger.error(f"获取/创建集合失败: {e}")
            raise
    
    def add_chunks_to_collection(
        self, 
        kb_id: int, 
        kb_name: str,
        chunks: List[Dict[str, Any]]
    ) -> int:
        """
        添加切片到ChromaDB集合
        
        Args:
            kb_id: 知识库ID
            kb_name: 知识库名称
            chunks: 切片列表
        
        Returns:
            添加的切片数量
        """
        try:
            collection = self.get_or_create_collection(kb_id, kb_name)
            
            # 准备数据
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for chunk in chunks:
                chunk_id = chunk.get('id') or f"{kb_id}_{chunk['metadata']['document_id']}_{chunk['index']}"
                ids.append(str(chunk_id))
                embeddings.append(chunk['embedding'])
                documents.append(chunk['content'])
                metadatas.append(chunk['metadata'])
            
            # 添加到集合
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            logger.info(f"已添加 {len(chunks)} 个切片到集合 kb_{kb_id}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"添加切片到集合失败: {e}")
            raise


class VectorRetriever:
    """向量检索器 - 使用ChromaDB"""
    
    def __init__(self):
        self.vector_service = VectorService()
    
    def search_similar_chunks(
        self,
        query: str,
        knowledge_base_ids: List[int],
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        搜索相似的文档切片
        
        Args:
            query: 查询文本
            knowledge_base_ids: 知识库ID列表
            top_k: 返回结果数量
            similarity_threshold: 相似度阈值
        
        Returns:
            相似切片列表，包含content和score
        """
        try:
            # 1. 获取查询向量
            logger.info(f"生成查询向量: {query[:50]}...")
            query_embedding = self.vector_service.get_embedding(query)
            logger.info(f"查询向量生成成功，维度: {len(query_embedding)}")
            
            all_results = []
            
            # 2. 在每个知识库中搜索
            for kb_id in knowledge_base_ids:
                try:
                    collection_name = f"kb_{kb_id}"
                    logger.info(f"查询集合: {collection_name}")
                    
                    collection = self.vector_service.chroma_client.get_collection(
                        name=collection_name
                    )
                    
                    # 检查集合中的文档数量
                    collection_count = collection.count()
                    logger.info(f"  集合 {collection_name} 包含 {collection_count} 个文档")
                    
                    if collection_count == 0:
                        logger.warning(f"  集合 {collection_name} 为空，跳过")
                        continue
                    
                    # 使用ChromaDB查询
                    results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(top_k, collection_count)  # 不要超过集合中的文档数
                    )
                    
                    logger.info(f"  ChromaDB 查询结果: {len(results.get('ids', [[]])[0])} 条")
                    
                    # 处理结果
                    if results and results['ids'] and len(results['ids'][0]) > 0:
                        for i in range(len(results['ids'][0])):
                            distance = results['distances'][0][i]
                            similarity = 1 - distance  # ChromaDB返回的是距离，转换为相似度
                            
                            logger.info(f"    [{i+1}] 相似度: {similarity:.3f}, 距离: {distance:.3f}")
                            
                            if similarity >= similarity_threshold:
                                all_results.append({
                                    'id': results['ids'][0][i],
                                    'content': results['documents'][0][i],
                                    'metadata': results['metadatas'][0][i],
                                    'similarity': similarity,
                                    'kb_id': kb_id
                                })
                                logger.info(f"      ✅ 通过阈值 {similarity_threshold}")
                            else:
                                logger.info(f"      ❌ 未通过阈值 {similarity_threshold}")
                    else:
                        logger.warning(f"  集合 {collection_name} 查询无结果")
                    
                except Exception as e:
                    logger.error(f"在知识库 {kb_id} 中搜索失败: {e}", exc_info=True)
                    continue
            
            # 按相似度排序
            all_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            logger.info(f"✅ 向量检索完成: 找到 {len(all_results)} 个相似切片（阈值 {similarity_threshold}）")
            
            final_results = all_results[:top_k]
            for i, result in enumerate(final_results, 1):
                logger.info(f"  [{i}] KB{result['kb_id']}, 相似度: {result['similarity']:.3f}, 内容: {result['content'][:50]}...")
            
            return final_results
            
        except Exception as e:
            logger.error(f"向量检索失败: {e}", exc_info=True)
            return []
    
    def search_hybrid(
        self,
        query: str,
        knowledge_base_ids: List[int],
        top_k: int = 5,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        混合检索 - 向量检索 + 关键词检索
        
        Args:
            query: 查询文本
            knowledge_base_ids: 知识库ID列表
            top_k: 返回结果数量
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
        
        Returns:
            混合检索结果
        """
        # 1. 向量检索
        vector_results = self.search_similar_chunks(
            query,
            knowledge_base_ids,
            top_k * 2  # 多取一些用于融合
        )
        
        # 2. 关键词检索（使用PostgreSQL全文搜索）
        keyword_results = self._keyword_search(query, knowledge_base_ids, top_k * 2)
        
        # 3. 融合结果
        merged_results = self._merge_results(
            vector_results,
            keyword_results,
            vector_weight,
            keyword_weight,
            top_k
        )
        
        return merged_results
    
    def _keyword_search(
        self,
        query: str,
        knowledge_base_ids: List[int],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """关键词搜索"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        c.id,
                        c.content,
                        c.metadata,
                        c.chunk_index,
                        d.filename,
                        k.name as kb_name,
                        ts_rank(
                            to_tsvector('simple', c.content),
                            plainto_tsquery('simple', %s)
                        ) as rank
                    FROM cs_document_chunk c
                    JOIN cs_knowledge_document d ON c.document_id = d.id
                    JOIN cs_knowledge_base k ON c.knowledge_base_id = k.id
                    WHERE c.knowledge_base_id = ANY(%s)
                        AND to_tsvector('simple', c.content) @@ plainto_tsquery('simple', %s)
                    ORDER BY rank DESC
                    LIMIT %s
                """, [query, knowledge_base_ids, query, top_k])
                
                columns = [col[0] for col in cursor.description]
                results = []
                for row in cursor.fetchall():
                    result = dict(zip(columns, row))
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"关键词检索失败: {e}")
            return []
    
    def _merge_results(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict],
        vector_weight: float,
        keyword_weight: float,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """融合检索结果"""
        # 创建分数字典
        scores = {}
        
        # 添加向量检索分数
        for i, result in enumerate(vector_results):
            chunk_id = result['id']
            # 向量相似度已经是0-1之间
            vector_score = result.get('similarity', 0) * vector_weight
            scores[chunk_id] = {
                'vector_score': vector_score,
                'keyword_score': 0,
                'data': result
            }
        
        # 添加关键词检索分数
        max_rank = max([r.get('rank', 0) for r in keyword_results], default=1)
        for i, result in enumerate(keyword_results):
            chunk_id = result['id']
            # 归一化rank分数
            keyword_score = (result.get('rank', 0) / max_rank if max_rank > 0 else 0) * keyword_weight
            
            if chunk_id in scores:
                scores[chunk_id]['keyword_score'] = keyword_score
            else:
                scores[chunk_id] = {
                    'vector_score': 0,
                    'keyword_score': keyword_score,
                    'data': result
                }
        
        # 计算最终分数并排序
        merged = []
        for chunk_id, score_data in scores.items():
            final_score = score_data['vector_score'] + score_data['keyword_score']
            data = score_data['data']
            data['final_score'] = final_score
            data['vector_score'] = score_data['vector_score']
            data['keyword_score'] = score_data['keyword_score']
            merged.append(data)
        
        # 按最终分数排序
        merged.sort(key=lambda x: x['final_score'], reverse=True)
        
        return merged[:top_k]
    
    def rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        重排序结果（可选功能）
        使用更复杂的模型对初步检索结果进行重排序
        
        Args:
            query: 查询文本
            results: 初步检索结果
            top_k: 返回结果数量
        
        Returns:
            重排序后的结果
        """
        # TODO: 可以接入专门的rerank模型
        # 目前直接返回原结果
        return results[:top_k]


def init_chromadb():
    """初始化ChromaDB"""
    try:
        vector_service = VectorService()
        logger.info("ChromaDB初始化完成")
        return vector_service
    except Exception as e:
        logger.error(f"初始化ChromaDB失败: {e}")
        raise

