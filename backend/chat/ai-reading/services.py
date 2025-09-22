import os
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Document, DocumentAnalysis, QAHistory, DocumentAccess

User = get_user_model()


class AIReadingService:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
    
    def calculate_file_hash(self, file_content: bytes) -> str:
        """计算文件哈希值"""
        return hashlib.sha256(file_content).hexdigest()
    
    def find_existing_document(self, user: User, name: str, size: int, last_modified: int, file_hash: str = None) -> Optional[Document]:
        """查找已存在的相同文档"""
        try:
            # 首先按基本信息查找
            document = Document.objects.filter(
                user=user,
                name=name,
                size=size,
                last_modified=last_modified
            ).first()
            
            if document:
                print(f"找到相同文档（基于基本信息）: {document.name}")
                return document
            
            # 如果有文件哈希，按哈希查找
            if file_hash:
                document = Document.objects.filter(
                    user=user,
                    name=name,
                    size=size,
                    file_hash=file_hash
                ).first()
                
                if document:
                    print(f"找到相同文档（基于哈希）: {document.name}")
                    return document
            
            return None
        except Exception as e:
            print(f"查找文档时出错: {e}")
            return None
    
    def upload_file_to_ai_service(self, file_content: bytes, filename: str) -> str:
        """上传文件到AI服务"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as temp_file:
                temp_file.write(file_content)
                temp_file.flush()
                
                with open(temp_file.name, 'rb') as f:
                    file_object = self.client.files.create(
                        file=f,
                        purpose="file-extract"
                    )
                
                os.unlink(temp_file.name)
                return file_object.id
        except Exception as e:
            print(f"上传文件到AI服务失败: {e}")
            raise
    
    @transaction.atomic
    def save_or_get_document(self, user: User, file_content: bytes, filename: str, 
                           file_size: int, file_type: str, last_modified: int) -> Tuple[Document, bool]:
        """保存或获取文档，返回(文档对象, 是否为新创建)"""
        file_hash = self.calculate_file_hash(file_content)
        
        # 查找已存在的文档
        existing_doc = self.find_existing_document(user, filename, file_size, last_modified, file_hash)
        
        if existing_doc:
            # 记录访问
            DocumentAccess.objects.create(
                document=existing_doc,
                user=user,
                access_type='view'
            )
            print(f"使用已存在的文档: {existing_doc.name}, file_object_id: {existing_doc.file_object_id}")
            return existing_doc, False
        
        # 上传到AI服务
        file_object_id = self.upload_file_to_ai_service(file_content, filename)
        
        # 创建新文档记录
        document = Document.objects.create(
            user=user,
            name=filename,
            size=file_size,
            file_type=file_type,
            file_object_id=file_object_id,
            file_hash=file_hash,
            last_modified=last_modified
        )
        
        # 记录上传访问
        DocumentAccess.objects.create(
            document=document,
            user=user,
            access_type='upload'
        )
        
        print(f"创建新文档: {document.name}, file_object_id: {file_object_id}")
        return document, True
    
    def analyze_document_content(self, file_object_id: str) -> Dict[str, Any]:
        """分析文档内容"""
        try:
            response = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的文档分析助手。请对上传的文档进行全面分析，并按以下JSON格式返回结果：

{
    "summary": "文档的详细总结",
    "keyPoints": ["要点1", "要点2", "要点3"],
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "entities": [{"text": "实体名", "type": "实体类型"}],
    "suggestedQuestions": ["问题1", "问题2", "问题3", "问题4", "问题5"]
}

请确保：
1. summary 是对文档内容的详细总结
2. keyPoints 是文档的核心要点，3-5个
3. keywords 是关键词列表，5-10个
4. entities 是识别出的重要实体
5. suggestedQuestions 是基于文档内容的5个推荐问题
"""
                    },
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "file", 
                                "file_url": {
                                    "url": f"fileid://{file_object_id}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "请分析这个文档并返回JSON格式的分析结果。"
                            }
                        ]
                    }
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            import json
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # 如果不是标准JSON，尝试提取内容
                return {
                    "summary": content[:500] + "..." if len(content) > 500 else content,
                    "keyPoints": ["文档分析完成", "内容已提取", "可进行问答"],
                    "keywords": ["文档", "分析", "AI"],
                    "entities": [],
                    "suggestedQuestions": [
                        "这份文档的主要内容是什么？",
                        "文档中的关键信息有哪些？",
                        "作者想要表达什么观点？",
                        "文档的结论是什么？",
                        "有什么重要的数据或统计信息？"
                    ]
                }
                
        except Exception as e:
            print(f"分析文档失败: {e}")
            raise
    
    @transaction.atomic
    def save_analysis_result(self, document: Document, analysis_result: Dict[str, Any]) -> DocumentAnalysis:
        """保存分析结果"""
        try:
            # 删除已存在的分析结果（如果有）
            DocumentAnalysis.objects.filter(document=document).delete()
            
            # 创建新的分析结果
            analysis = DocumentAnalysis.objects.create(
                document=document,
                summary=analysis_result.get('summary', ''),
                key_points=analysis_result.get('keyPoints', []),
                keywords=analysis_result.get('keywords', []),
                entities=analysis_result.get('entities', []),
                suggested_questions=analysis_result.get('suggestedQuestions', [])
            )
            
            # 记录分析访问
            DocumentAccess.objects.create(
                document=document,
                user=document.user,
                access_type='analyze'
            )
            
            print(f"分析结果已保存: {document.name}")
            return analysis
            
        except Exception as e:
            print(f"保存分析结果失败: {e}")
            raise
    
    def get_document_analysis(self, document: Document) -> Optional[DocumentAnalysis]:
        """获取文档分析结果"""
        try:
            return DocumentAnalysis.objects.filter(document=document).first()
        except Exception as e:
            print(f"获取分析结果失败: {e}")
            return None
    
    def ask_question_about_document(self, file_object_id: str, question: str) -> str:
        """基于文档回答问题"""
        try:
            response = self.client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的文档问答助手。请基于上传的文档内容回答用户的问题。回答要准确、详细，并且要基于文档内容。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "file",
                                "file_url": {
                                    "url": f"fileid://{file_object_id}"
                                }
                            },
                            {
                                "type": "text",
                                "text": f"问题：{question}"
                            }
                        ]
                    }
                ],
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"问答失败: {e}")
            raise
    
    @transaction.atomic
    def save_qa_history(self, document: Document, question: str, answer: str) -> QAHistory:
        """保存问答历史"""
        try:
            qa = QAHistory.objects.create(
                document=document,
                question=question,
                answer=answer
            )
            
            # 记录问答访问
            DocumentAccess.objects.create(
                document=document,
                user=document.user,
                access_type='question'
            )
            
            print(f"问答历史已保存: {document.name}")
            return qa
            
        except Exception as e:
            print(f"保存问答历史失败: {e}")
            raise
    
    def get_qa_history(self, document: Document, limit: int = 20) -> List[QAHistory]:
        """获取问答历史"""
        try:
            return list(QAHistory.objects.filter(document=document).order_by('-created_time')[:limit])
        except Exception as e:
            print(f"获取问答历史失败: {e}")
            return []
    
    def get_user_documents(self, user: User, limit: int = 50) -> List[Document]:
        """获取用户的文档列表"""
        try:
            return list(Document.objects.filter(user=user).order_by('-upload_time')[:limit])
        except Exception as e:
            print(f"获取用户文档失败: {e}")
            return []
    
    def get_document_stats(self, user: User) -> Dict[str, Any]:
        """获取用户的文档统计信息"""
        try:
            documents = Document.objects.filter(user=user)
            total_documents = documents.count()
            total_size = sum(doc.size for doc in documents)
            
            qa_count = QAHistory.objects.filter(document__user=user).count()
            
            return {
                'total_documents': total_documents,
                'total_size': total_size,
                'total_questions': qa_count,
                'recent_documents': list(documents.order_by('-upload_time')[:5].values('name', 'upload_time'))
            }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {
                'total_documents': 0,
                'total_size': 0,
                'total_questions': 0,
                'recent_documents': []
            }


# 创建服务实例
ai_reading_service = AIReadingService()