"""
基于 LangGraph 的文档分析智能体
用于分析知识库文档，生成总结和推荐问题
"""
import logging
from typing import TypedDict, List, Dict, Any
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from django.conf import settings

logger = logging.getLogger(__name__)


class DocumentAnalysisState(TypedDict):
    """文档分析状态定义"""
    documents: List[str]  # 文档内容列表
    chunks: List[Dict[str, Any]]  # 文档切片
    summary: str  # 总结
    key_points: List[str]  # 核心要点
    keywords: List[str]  # 关键词
    suggested_questions: List[str]  # 推荐问题
    domain: str  # 领域/主题
    intent_prompt: str  # 生成的意图识别提示词


class DocumentAnalyzerGraph:
    """文档分析 LangGraph 工作流"""
    
    def __init__(self, api_key: str = None, model: str = "qwen-plus"):
        """
        初始化文档分析图
        
        Args:
            api_key: DashScope API Key
            model: 使用的模型名称
        """
        self.api_key = api_key or settings.DASHSCOPE_API_KEY
        
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=self.api_key,
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            temperature=0.7,
            max_tokens=2000,
        )
        
        # 构建工作流图
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图"""
        workflow = StateGraph(DocumentAnalysisState)
        
        # 添加节点
        workflow.add_node("extract_domain", self.extract_domain)
        workflow.add_node("generate_summary", self.generate_summary)
        workflow.add_node("extract_keywords", self.extract_keywords)
        workflow.add_node("generate_questions", self.generate_questions)
        workflow.add_node("build_intent_prompt", self.build_intent_prompt)
        
        # 设置入口点
        workflow.set_entry_point("extract_domain")
        
        # 添加边：按顺序执行
        workflow.add_edge("extract_domain", "generate_summary")
        workflow.add_edge("generate_summary", "extract_keywords")
        workflow.add_edge("extract_keywords", "generate_questions")
        workflow.add_edge("generate_questions", "build_intent_prompt")
        workflow.add_edge("build_intent_prompt", END)
        
        return workflow.compile()
    
    def extract_domain(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """提取文档领域/主题"""
        logger.info("提取文档领域")
        
        # 获取前几个切片作为样本
        sample_chunks = state["chunks"][:5]
        sample_text = "\n\n".join([chunk.get("content", "") for chunk in sample_chunks])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是专业的文档分析专家。分析文档内容，判断其所属领域和主题。

只返回一个简短的领域描述（5-15字），例如：
- 产品使用手册
- 技术开发文档
- 公司政策规章
- 客户服务指南
- 业务流程说明

直接返回领域描述，不要其他内容。"""),
            ("user", "文档内容样本：\n{sample}\n\n这份文档的领域/主题是：")
        ])
        
        try:
            result = self.llm.invoke(prompt.format_messages(sample=sample_text[:2000]))
            state["domain"] = result.content.strip()
            logger.info(f"识别领域: {state['domain']}")
        except Exception as e:
            logger.error(f"领域提取失败: {e}")
            state["domain"] = "通用知识文档"
        
        return state
    
    def generate_summary(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """生成文档总结"""
        logger.info("生成文档总结")
        
        # 取前10个切片生成总结
        sample_chunks = state["chunks"][:10]
        combined_text = "\n\n".join([
            f"切片 {i+1}:\n{chunk.get('content', '')}" 
            for i, chunk in enumerate(sample_chunks)
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是专业的文档分析专家。阅读文档内容，生成简洁的总结。

要求：
1. 总结文档的核心内容和主要信息
2. 字数控制在150-300字
3. 语言简洁、专业
4. 突出重点内容

直接返回总结内容，不要标题或其他说明。"""),
            ("user", "文档内容：\n{content}\n\n请生成总结：")
        ])
        
        try:
            result = self.llm.invoke(prompt.format_messages(content=combined_text[:4000]))
            state["summary"] = result.content.strip()
            
            # 同时提取核心要点
            state["key_points"] = self._extract_key_points(state["summary"])
            
            logger.info("文档总结生成完成")
        except Exception as e:
            logger.error(f"总结生成失败: {e}")
            state["summary"] = f"本知识库包含关于{state['domain']}的相关内容。"
            state["key_points"] = []
        
        return state
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """从总结中提取核心要点"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """从文档总结中提取3-5个核心要点。

要求：
1. 每个要点一句话，15-30字
2. 要点之间用换行分隔
3. 只返回要点内容，不要编号或其他格式

格式示例：
文档详细介绍了产品的主要功能和特性
提供了完整的操作步骤和使用方法
包含常见问题的解决方案和技巧"""),
            ("user", "总结内容：\n{summary}\n\n核心要点：")
        ])
        
        try:
            result = self.llm.invoke(prompt.format_messages(summary=summary))
            points = [p.strip() for p in result.content.strip().split('\n') if p.strip()]
            return points[:5]  # 最多5个要点
        except Exception as e:
            logger.error(f"要点提取失败: {e}")
            return []
    
    def extract_keywords(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """提取关键词"""
        logger.info("提取关键词")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """从文档总结中提取5-10个关键词。

要求：
1. 关键词应该是名词或专业术语
2. 每个关键词2-6个字
3. 用逗号分隔
4. 只返回关键词，不要其他内容

格式示例：产品功能,使用教程,故障排查,配置参数,安全设置"""),
            ("user", "文档领域：{domain}\n文档总结：\n{summary}\n\n关键词：")
        ])
        
        try:
            result = self.llm.invoke(prompt.format_messages(
                domain=state["domain"],
                summary=state["summary"]
            ))
            keywords = [kw.strip() for kw in result.content.strip().split(',')]
            state["keywords"] = keywords[:10]  # 最多10个
            logger.info(f"提取到 {len(state['keywords'])} 个关键词")
        except Exception as e:
            logger.error(f"关键词提取失败: {e}")
            state["keywords"] = []
        
        return state
    
    def generate_questions(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """生成推荐问题"""
        logger.info("生成推荐问题")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """基于文档内容，生成5-8个用户可能会问的问题。

要求：
1. 问题应该具体、实用
2. 每个问题10-30字
3. 涵盖不同方面的内容
4. 用换行分隔
5. 问题以"？"结尾
6. 只返回问题，不要编号

格式示例：
如何快速开始使用这个产品？
产品有哪些主要功能和特性？
遇到问题时如何进行故障排查？
如何配置和优化系统参数？"""),
            ("user", """文档领域：{domain}
文档总结：{summary}
关键词：{keywords}

请生成推荐问题：""")
        ])
        
        try:
            result = self.llm.invoke(prompt.format_messages(
                domain=state["domain"],
                summary=state["summary"],
                keywords="、".join(state["keywords"][:5])
            ))
            questions = [q.strip() for q in result.content.strip().split('\n') if q.strip() and '？' in q]
            state["suggested_questions"] = questions[:8]  # 最多8个
            logger.info(f"生成 {len(state['suggested_questions'])} 个推荐问题")
        except Exception as e:
            logger.error(f"推荐问题生成失败: {e}")
            state["suggested_questions"] = [
                "这份文档的主要内容是什么？",
                "有哪些重要的知识点？",
                "如何快速找到需要的信息？"
            ]
        
        return state
    
    def build_intent_prompt(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """构建意图识别提示词"""
        logger.info("构建意图识别提示词")
        
        # 基于文档分析结果构建更精准的意图识别提示词
        intent_prompt = f"""你是专业的意图分类专家。判断用户消息是否为知识检索需求。

当前知识库领域：{state["domain"]}
知识库内容概述：{state["summary"][:200]}

知识检索需求包括：
- 询问关于【{state["domain"]}】的相关问题
- 涉及以下关键词的咨询：{", ".join(state["keywords"][:8])}
- 寻求该领域的具体问题解答或建议
- 与文档内容相关的任何专业咨询

非知识检索需求包括：
- 闲聊、问候、寒暄（如"你好"、"在吗"）
- 完全不相关的话题（天气、新闻、娱乐等）
- 情感表达（如"谢谢"、"再见"）
- 与【{state["domain"]}】无关的问题

只返回 "retrieval" 或 "reject"，不要解释。
- retrieval: 是知识检索需求
- reject: 不是知识检索需求"""
        
        state["intent_prompt"] = intent_prompt
        logger.info("意图识别提示词构建完成")
        
        return state
    
    def run(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        运行文档分析工作流
        
        Args:
            chunks: 文档切片列表
            
        Returns:
            分析结果字典
        """
        logger.info(f"开始分析文档，共 {len(chunks)} 个切片")
        
        try:
            # 初始化状态
            initial_state = {
                "documents": [],
                "chunks": chunks,
                "summary": "",
                "key_points": [],
                "keywords": [],
                "suggested_questions": [],
                "domain": "",
                "intent_prompt": ""
            }
            
            # 运行工作流
            final_state = self.graph.invoke(initial_state)
            
            result = {
                "domain": final_state["domain"],
                "summary": final_state["summary"],
                "key_points": final_state["key_points"],
                "keywords": final_state["keywords"],
                "suggested_questions": final_state["suggested_questions"],
                "intent_prompt": final_state["intent_prompt"],
                "analyzed_at": datetime.now().isoformat()
            }
            
            logger.info("文档分析完成")
            logger.info(f"领域: {result['domain']}")
            logger.info(f"关键词数: {len(result['keywords'])}")
            logger.info(f"推荐问题数: {len(result['suggested_questions'])}")
            
            return result
            
        except Exception as e:
            logger.error(f"文档分析失败: {e}", exc_info=True)
            return {
                "domain": "通用知识文档",
                "summary": "文档分析过程中遇到问题，请稍后重试。",
                "key_points": [],
                "keywords": [],
                "suggested_questions": [
                    "这份文档的主要内容是什么？",
                    "有哪些重要信息？"
                ],
                "intent_prompt": "",
                "error": str(e)
            }

