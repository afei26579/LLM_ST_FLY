"""
文档处理服务 - 切片和清洗
"""
import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """文档切片数据类"""
    content: str
    index: int
    metadata: Dict[str, Any]
    token_count: int = 0


class DocumentCleaner:
    """文档清洗器"""
    
    @staticmethod
    def auto_clean(text: str) -> str:
        """智能清洗 - 自动识别并清理"""
        text = DocumentCleaner.basic_clean(text)
        text = DocumentCleaner.remove_special_patterns(text)
        text = DocumentCleaner.normalize_whitespace(text)
        return text
    
    @staticmethod
    def basic_clean(text: str) -> str:
        """基础清洗"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符（保留中英文、数字、基本标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fff。，、；：？！""''（）《》【】…—\-\.,;:?!()\[\]\'\"]+', '', text)
        # 去除首尾空格
        text = text.strip()
        return text
    
    @staticmethod
    def remove_special_patterns(text: str) -> str:
        """移除特殊模式"""
        # 移除页码
        text = re.sub(r'第?\s*\d+\s*页', '', text)
        text = re.sub(r'Page\s*\d+', '', text, flags=re.IGNORECASE)
        
        # 移除页眉页脚常见格式
        text = re.sub(r'^[-=_]{3,}.*?[-=_]{3,}$', '', text, flags=re.MULTILINE)
        
        # 移除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # 移除邮箱
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """标准化空白字符"""
        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 移除多余空行（保留最多2个连续换行）
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 移除行首行尾空格
        text = '\n'.join(line.strip() for line in text.split('\n'))
        
        return text
    
    @staticmethod
    def custom_clean(text: str, rules: List[Dict[str, str]]) -> str:
        """自定义清洗 - 根据用户规则"""
        for rule in rules:
            pattern = rule.get('pattern', '')
            replacement = rule.get('replacement', '')
            if pattern:
                try:
                    text = re.sub(pattern, replacement, text)
                except Exception as e:
                    logger.warning(f"自定义清洗规则失败: {pattern}, {e}")
        return text


class DocumentChunker:
    """文档切片器"""
    
    @staticmethod
    def chunk_by_fixed_size(
        text: str, 
        chunk_size: int = 500, 
        overlap: int = 50,
        separator: str = '\n'
    ) -> List[DocumentChunk]:
        """固定长度切片"""
        chunks = []
        paragraphs = text.split(separator)
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_size = len(para)
            
            # 如果当前段落加上累积大小超过chunk_size
            if current_size + para_size > chunk_size and current_chunk:
                # 保存当前chunk
                chunk_text = separator.join(current_chunk)
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    index=chunk_index,
                    metadata={'paragraphs': len(current_chunk)},
                    token_count=len(chunk_text) // 4  # 粗略估计
                ))
                chunk_index += 1
                
                # 处理重叠
                if overlap > 0:
                    # 保留最后几个段落作为重叠
                    overlap_text = separator.join(current_chunk[-2:])
                    current_chunk = current_chunk[-2:] if len(current_chunk) > 2 else []
                    current_size = len(overlap_text)
                else:
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(para)
            current_size += para_size
        
        # 处理剩余内容
        if current_chunk:
            chunk_text = separator.join(current_chunk)
            chunks.append(DocumentChunk(
                content=chunk_text,
                index=chunk_index,
                metadata={'paragraphs': len(current_chunk)},
                token_count=len(chunk_text) // 4
            ))
        
        return chunks
    
    @staticmethod
    def chunk_by_semantic(
        text: str,
        max_chunk_size: int = 500,
        min_chunk_size: int = 100
    ) -> List[DocumentChunk]:
        """语义切片 - 基于段落和语义边界"""
        chunks = []
        
        # 首先按段落分割
        paragraphs = text.split('\n\n')
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_size = len(para)
            
            # 如果单个段落太长，需要进一步分割
            if para_size > max_chunk_size:
                # 如果已有内容，先保存
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunks.append(DocumentChunk(
                        content=chunk_text,
                        index=chunk_index,
                        metadata={'type': 'semantic', 'paragraphs': len(current_chunk)},
                        token_count=len(chunk_text) // 4
                    ))
                    chunk_index += 1
                    current_chunk = []
                    current_size = 0
                
                # 按句子分割长段落
                sentences = DocumentChunker._split_sentences(para)
                temp_chunk = []
                temp_size = 0
                
                for sent in sentences:
                    sent_size = len(sent)
                    if temp_size + sent_size > max_chunk_size and temp_chunk:
                        chunk_text = ''.join(temp_chunk)
                        chunks.append(DocumentChunk(
                            content=chunk_text,
                            index=chunk_index,
                            metadata={'type': 'sentence_split', 'sentences': len(temp_chunk)},
                            token_count=len(chunk_text) // 4
                        ))
                        chunk_index += 1
                        temp_chunk = []
                        temp_size = 0
                    
                    temp_chunk.append(sent)
                    temp_size += sent_size
                
                if temp_chunk:
                    chunk_text = ''.join(temp_chunk)
                    chunks.append(DocumentChunk(
                        content=chunk_text,
                        index=chunk_index,
                        metadata={'type': 'sentence_split', 'sentences': len(temp_chunk)},
                        token_count=len(chunk_text) // 4
                    ))
                    chunk_index += 1
                
                continue
            
            # 正常段落处理
            if current_size + para_size > max_chunk_size and current_size >= min_chunk_size:
                # 保存当前chunk
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    index=chunk_index,
                    metadata={'type': 'semantic', 'paragraphs': len(current_chunk)},
                    token_count=len(chunk_text) // 4
                ))
                chunk_index += 1
                current_chunk = []
                current_size = 0
            
            current_chunk.append(para)
            current_size += para_size
        
        # 处理剩余内容
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(DocumentChunk(
                content=chunk_text,
                index=chunk_index,
                metadata={'type': 'semantic', 'paragraphs': len(current_chunk)},
                token_count=len(chunk_text) // 4
            ))
        
        return chunks
    
    @staticmethod
    def chunk_auto(text: str, **kwargs) -> List[DocumentChunk]:
        """智能切片 - 自动选择最佳策略"""
        # 分析文本特征
        has_paragraphs = '\n\n' in text
        avg_para_length = len(text) / (text.count('\n\n') + 1)
        
        chunk_size = kwargs.get('chunk_size', 500)
        overlap = kwargs.get('overlap', 50)
        
        # 根据特征选择策略
        if has_paragraphs and avg_para_length < 600:
            # 文本有明确段落结构，使用语义切片
            return DocumentChunker.chunk_by_semantic(
                text, 
                max_chunk_size=chunk_size,
                min_chunk_size=100
            )
        else:
            # 文本结构不明确，使用固定长度
            return DocumentChunker.chunk_by_fixed_size(text, chunk_size, overlap)
    
    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        """分割句子"""
        # 中文句子分隔符
        cn_pattern = r'([。！？；]+)'
        
        # 先按中文分割
        parts = re.split(cn_pattern, text)
        sentences = []
        temp = ''
        
        for i, part in enumerate(parts):
            temp += part
            if i % 2 == 1 or i == len(parts) - 1:  # 分隔符或最后一部分
                if temp.strip():
                    sentences.append(temp)
                temp = ''
        
        return sentences if sentences else [text]


class DocumentProcessor:
    """文档处理主类"""
    
    def __init__(self):
        self.cleaner = DocumentCleaner()
        self.chunker = DocumentChunker()
    
    def process_document(
        self,
        file_path: str,
        file_type: str,
        kb_format: str,
        chunk_strategy: str = 'auto',
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        remove_spaces: bool = True,
        remove_urls: bool = False,
        separator: str = '\n'
    ) -> List[Dict[str, Any]]:
        """
        处理文档 - 根据格式选择不同的处理方式
        
        Args:
            file_path: 文件路径
            file_type: 文件类型 (txt, pdf, docx, csv等)
            kb_format: 知识库格式 (text, structured, image)
            chunk_strategy: 切片策略
            chunk_size: 切片大小
            chunk_overlap: 切片重叠
            remove_spaces: 是否移除多余空格
            remove_urls: 是否移除URL
            separator: 分段标识符
        
        Returns:
            切片列表，每个切片包含content和metadata
        """
        logger.info(f"开始处理文档: {file_path}, 类型={file_type}, 格式={kb_format}")
        
        # 根据知识库格式选择处理方式
        if kb_format == 'text':
            return self._process_text_document(
                file_path, file_type, chunk_strategy, chunk_size, chunk_overlap, 
                remove_spaces, remove_urls, separator
            )
        elif kb_format == 'structured':
            return self._process_structured_document(
                file_path, file_type, chunk_size
            )
        elif kb_format == 'image':
            return self._process_image_document(
                file_path, file_type, chunk_size
            )
        else:
            raise ValueError(f"不支持的知识库格式: {kb_format}")
    
    def _process_text_document(
        self, file_path: str, file_type: str, chunk_strategy: str,
        chunk_size: int, chunk_overlap: int, remove_spaces: bool, 
        remove_urls: bool, separator: str
    ) -> List[Dict[str, Any]]:
        """处理文本类文档 - 使用unstructured或基础处理"""
        try:
            # 提取文本
            text = self.extract_text_from_file(file_path, file_type)
            
            # 清洗
            if remove_spaces:
                text = self.cleaner.normalize_whitespace(text)
            if remove_urls:
                text = self.cleaner.remove_special_patterns(text)
            
            # 切片
            if chunk_strategy == 'custom':
                chunks = self.chunker.chunk_by_fixed_size(text, chunk_size, chunk_overlap, separator)
            elif chunk_strategy == 'auto':
                chunks = self.chunker.chunk_auto(text, chunk_size=chunk_size, overlap=chunk_overlap)
            else:
                chunks = self.chunker.chunk_by_fixed_size(text, chunk_size, chunk_overlap)
            
            # 转换为字典格式
            return [
                {
                    'content': chunk.content,
                    'metadata': {
                        'chunk_index': chunk.index,
                        'token_count': chunk.token_count,
                        'file_type': file_type,
                        **chunk.metadata
                    }
                }
                for chunk in chunks
            ]
            
        except Exception as e:
            logger.error(f"处理文本文档失败: {str(e)}", exc_info=True)
            raise
    
    def _process_structured_document(
        self, file_path: str, file_type: str, chunk_size: int
    ) -> List[Dict[str, Any]]:
        """处理结构化文档 - 使用pandas"""
        try:
            import pandas as pd
            
            chunks = []
            
            if file_type == 'csv':
                df = pd.read_csv(file_path)
                metadata_base = {'file_type': 'csv', 'columns': list(df.columns)}
                
                # 按行切片，每chunk_size行一个切片
                rows_per_chunk = max(1, chunk_size // 200)  # 假设每行约200字符
                
                for i in range(0, len(df), rows_per_chunk):
                    chunk_df = df.iloc[i:i+rows_per_chunk]
                    content = chunk_df.to_string(index=False)
                    
                    chunks.append({
                        'content': content,
                        'metadata': {
                            **metadata_base,
                            'chunk_index': i // rows_per_chunk,
                            'row_start': i,
                            'row_end': min(i + rows_per_chunk, len(df)),
                            'row_count': len(chunk_df),
                            'token_count': len(content) // 4
                        }
                    })
            
            elif file_type in ['xlsx', 'xls']:
                df = pd.read_excel(file_path)
                metadata_base = {'file_type': file_type, 'columns': list(df.columns)}
                
                rows_per_chunk = max(1, chunk_size // 200)
                
                for i in range(0, len(df), rows_per_chunk):
                    chunk_df = df.iloc[i:i+rows_per_chunk]
                    content = chunk_df.to_string(index=False)
                    
                    chunks.append({
                        'content': content,
                        'metadata': {
                            **metadata_base,
                            'chunk_index': i // rows_per_chunk,
                            'row_start': i,
                            'row_end': min(i + rows_per_chunk, len(df)),
                            'row_count': len(chunk_df),
                            'token_count': len(content) // 4
                        }
                    })
            
            elif file_type == 'json':
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 将JSON转换为可读文本
                content = json.dumps(data, ensure_ascii=False, indent=2)
                
                # 简单切片
                text_chunks = self.chunker.chunk_by_fixed_size(content, chunk_size, 0)
                
                for chunk in text_chunks:
                    chunks.append({
                        'content': chunk.content,
                        'metadata': {
                            'file_type': 'json',
                            'chunk_index': chunk.index,
                            'token_count': chunk.token_count
                        }
                    })
            
            elif file_type in ['xml', 'html']:
                # 读取为文本处理
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 移除标签
                import re
                text = re.sub(r'<[^>]+>', '', content)
                text_chunks = self.chunker.chunk_by_fixed_size(text, chunk_size, 0)
                
                for chunk in text_chunks:
                    chunks.append({
                        'content': chunk.content,
                        'metadata': {
                            'file_type': file_type,
                            'chunk_index': chunk.index,
                            'token_count': chunk.token_count
                        }
                    })
            
            return chunks
            
        except Exception as e:
            logger.error(f"处理结构化文档失败: {str(e)}", exc_info=True)
            raise
    
    def _process_image_document(
        self, file_path: str, file_type: str, chunk_size: int
    ) -> List[Dict[str, Any]]:
        """处理图片文档 - 使用OCR识别"""
        try:
            # 尝试使用OCR识别图片文字
            try:
                from PIL import Image
                import pytesseract
                
                image = Image.open(file_path)
                text = pytesseract.image_to_string(image, lang='chi_sim+eng')
                
                # 获取图片信息
                width, height = image.size
                
                metadata_base = {
                    'file_type': file_type,
                    'image_width': width,
                    'image_height': height,
                    'ocr_processed': True
                }
                
            except ImportError:
                logger.warning("OCR库未安装，使用文件名作为内容")
                text = f"图片文件: {file_path}"
                metadata_base = {
                    'file_type': file_type,
                    'ocr_processed': False
                }
            
            # 切片识别的文本
            if text and len(text) > chunk_size:
                text_chunks = self.chunker.chunk_by_fixed_size(text, chunk_size, 0)
                
                return [
                    {
                        'content': chunk.content,
                        'metadata': {
                            **metadata_base,
                            'chunk_index': chunk.index,
                            'token_count': chunk.token_count
                        }
                    }
                    for chunk in text_chunks
                ]
            else:
                # 整个图片作为一个切片
                return [
                    {
                        'content': text if text else f"图片文件: {file_path}",
                        'metadata': {
                            **metadata_base,
                            'chunk_index': 0,
                            'token_count': len(text) // 4 if text else 10
                        }
                    }
                ]
                
        except Exception as e:
            logger.error(f"处理图片文档失败: {str(e)}", exc_info=True)
            raise
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> str:
        """从文件中提取文本"""
        try:
            if file_type in ['txt', 'md']:
                return self._read_text_file(file_path)
            elif file_type == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type in ['doc', 'docx']:
                return self._extract_from_docx(file_path)
            else:
                logger.warning(f"不支持的文件类型: {file_type}")
                return ""
        except Exception as e:
            logger.error(f"文件提取失败: {e}")
            raise
    
    def _read_text_file(self, file_path: str) -> str:
        """读取文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """从PDF提取文本"""
        try:
            import PyPDF2
            text = []
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
            return '\n\n'.join(text)
        except ImportError:
            logger.error("PyPDF2未安装")
            return ""
    
    def _extract_from_docx(self, file_path: str) -> str:
        """从DOCX提取文本"""
        try:
            from docx import Document
            doc = Document(file_path)
            return '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
        except ImportError:
            logger.error("python-docx未安装")
            return ""

