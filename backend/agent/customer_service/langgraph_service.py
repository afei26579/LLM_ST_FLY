"""
基于 LangGraph 的智能客服系统核心服务
"""
import json
import logging
from typing import TypedDict, List, Dict, Any, Annotated
import operator
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate

from django.conf import settings
from django.db import models as django_models
from .models import CustomerServiceKnowledgeBase

logger = logging.getLogger(__name__)


class CustomerServiceState(TypedDict):
    """客服系统状态定义"""
    messages: Annotated[List[BaseMessage], operator.add]
    intent: str
    entities: Dict[str, Any]
    user_id: int
    session_id: str
    context: Dict[str, Any]
    tools_result: Dict[str, Any]
    need_human: bool
    confidence: float
    response: str


class CustomerServiceGraph:
    """智能客服 LangGraph 工作流"""
    
    def __init__(self, api_key: str = None, model: str = "qwen-plus", knowledge_bases: list = None):
        """
        初始化客服图
        
        Args:
            api_key: DashScope API Key
            model: 使用的模型名称
            knowledge_bases: 助手关联的知识库列表
        """
        self.api_key = api_key or settings.DASHSCOPE_API_KEY
        self.knowledge_bases = knowledge_bases or []
        
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
        """构建 LangGraph 状态图 - 简化版：只做知识库检索"""
        workflow = StateGraph(CustomerServiceState)
        
        # 添加节点
        workflow.add_node("intent_classifier", self.classify_intent)
        workflow.add_node("knowledge_retrieval", self.retrieve_knowledge)
        workflow.add_node("response_generator", self.generate_response)
        
        # 设置入口点
        workflow.set_entry_point("intent_classifier")
        
        # 意图分类后，根据是否需要检索进行路由
        workflow.add_conditional_edges(
            "intent_classifier",
            self.route_to_handler,
            {
                "retrieval": "knowledge_retrieval",
                "reject": "response_generator",
            }
        )
        
        # 知识库检索后生成响应
        workflow.add_edge("knowledge_retrieval", "response_generator")
        
        # 响应生成后结束
        workflow.add_edge("response_generator", END)
        
        return workflow.compile()
    
    def classify_intent(self, state: CustomerServiceState) -> CustomerServiceState:
        """意图分类节点 - 使用知识库分析结果判断"""
        logger.info("开始意图分类")
        
        # 构建意图识别提示词
        system_prompt = self._build_intent_prompt()
        print(system_prompt, 'system_prompt')
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{message}")
        ])
        
        try:
            last_message = state["messages"][-1].content
            result = self.llm.invoke(prompt.format_messages(message=last_message))
            intent = result.content.strip().lower()
            
            # 验证意图是否有效
            if intent not in ["retrieval", "reject"]:
                # 默认当作检索需求
                intent = "retrieval"
            
            state["intent"] = intent
            state["confidence"] = 0.9
            logger.info(f"意图分类结果: {intent}")
            
        except Exception as e:
            logger.error(f"意图分类失败: {e}")
            state["intent"] = "reject"
            state["confidence"] = 0.3
        
        return state
    
    def _build_intent_prompt(self) -> str:
        """构建意图识别提示词（基于知识库分析结果）"""
        # 如果有知识库且有自定义的 intent_prompt，使用它
        if self.knowledge_bases:
            for kb in self.knowledge_bases:
                if kb.intent_prompt:
                    logger.info(f"使用知识库 {kb.name} 的自定义意图提示词")
                    return kb.intent_prompt
        
        # 否则使用通用提示词
        return """你是专业的意图分类专家。判断用户消息是否为知识检索需求。

知识检索需求包括：
- 询问产品信息、功能、特性、使用方法
- 询问技术问题、故障排查、配置说明
- 询问公司政策、规章制度、流程说明
- 询问业务相关的专业知识
- 寻求具体问题的解答或建议

非知识检索需求包括：
- 闲聊、问候、寒暄（如"你好"、"在吗"）
- 无关话题（天气、新闻、娱乐等）
- 情感表达（如"谢谢"、"再见"）
- 与业务无关的问题

只返回 "retrieval" 或 "reject"，不要解释。
- retrieval: 是知识检索需求
- reject: 不是知识检索需求"""
    
    def route_to_handler(self, state: CustomerServiceState) -> str:
        """路由到具体处理器 - 简化版"""
        intent = state["intent"]
        
        if intent == "retrieval":
            route = "retrieval"
        else:
            route = "reject"
        
        logger.info(f"路由到: {route}")
        return route
    
    def retrieve_knowledge(self, state: CustomerServiceState) -> CustomerServiceState:
        """知识库检索 - 从向量数据库搜索"""
        logger.info("检索知识库")
        
        query = state["messages"][-1].content
        
        # 从知识库搜索（不限制分类，搜索所有相关内容）
        knowledge = self._search_knowledge_base(query, category=None)
        state["tools_result"]["knowledge"] = knowledge
        
        logger.info(f"知识库检索完成: {len(knowledge)} 条结果")
        return state
    
    def generate_response(self, state: CustomerServiceState) -> CustomerServiceState:
        """生成最终响应 - 简化版"""
        logger.info("生成响应")
        
        intent = state["intent"]
        
        # 如果不是检索需求，直接返回拒绝消息
        if intent == "reject":
            state["response"] = "抱歉，我无法回答这个问题。我是专业的知识库助手，只能回答与业务相关的专业问题。"
            logger.info("非检索需求，返回拒绝消息")
            return state
        
        # 检索需求：基于知识库内容生成回复
        knowledge_results = state["tools_result"].get("knowledge", [])
        
        if not knowledge_results:
            state["response"] = "抱歉，我在知识库中没有找到相关信息。请您换个方式描述问题，或提供更多细节。"
            logger.info("知识库无结果")
            return state
        
        # 构建对话历史
        history_text = "\n".join([
            f"{msg.type}: {msg.content}"
            for msg in state["messages"][:-1]
        ]) if len(state["messages"]) > 1 else "无历史对话"
        
        # 构建知识库内容（支持向量检索格式）
        knowledge_text = "\n\n".join([
            f"【来源：{item.get('category', '知识库')} - {item.get('title', '文档')}】\n{item['content']}"
            for item in knowledge_results
        ])
        
        logger.info(f"构建知识库上下文，共 {len(knowledge_results)} 条结果")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是专业的知识库助手。基于检索到的知识库内容回答用户问题。

知识库内容：
{knowledge}

对话历史：
{history}

回复要求：
1. 严格基于知识库内容回答，不要编造信息
2. 如果知识库内容不完全匹配问题，选择最相关的内容回答
3. 语气专业、准确、简洁
4. 回复控制在200字以内
5. 如果需要补充说明，可以适当展开

请直接生成回复内容，不要包含其他说明。"""),
            ("user", "用户问题：{current_message}")
        ])
        
        try:
            result = self.llm.invoke(prompt.format_messages(
                knowledge=knowledge_text,
                history=history_text,
                current_message=state["messages"][-1].content
            ))
            
            state["response"] = result.content.strip()
            logger.info("响应生成成功")
            
        except Exception as e:
            logger.error(f"响应生成失败: {e}")
            state["response"] = "抱歉，我遇到了一些问题。请稍后再试。"
        
        return state
    
    # ==================== 工具方法 ====================
    
    def _query_order_system(self, order_number: str) -> Dict[str, Any]:
        """查询订单系统（模拟）"""
        # TODO: 实际对接订单系统API
        logger.info(f"查询订单: {order_number}")
        
        # 模拟数据
        return {
            "order_number": order_number,
            "status": "配送中",
            "status_desc": "您的订单正在配送中",
            "tracking_number": "ZT1234567890",
            "estimated_delivery": "2025-10-23",
            "products": [
                {"name": "智能手表", "quantity": 1, "price": 999}
            ],
            "total_amount": 999,
            "create_time": "2025-10-20 10:30:00"
        }
    
    def _search_product_knowledge(self, query: str) -> Dict[str, Any]:
        """检索产品知识"""
        logger.info(f"检索产品知识: {query}")
        
        # 从知识库查询
        knowledge_items = CustomerServiceKnowledgeBase.objects.filter(
            category='product',
            is_active=True
        ).filter(
            django_models.Q(question__icontains=query) | 
            django_models.Q(answer__icontains=query)
        )[:3]
        
        if knowledge_items.exists():
            return {
                "found": True,
                "items": [
                    {
                        "question": item.question,
                        "answer": item.answer,
                        "keywords": item.keywords
                    }
                    for item in knowledge_items
                ]
            }
        
        # 模拟数据
        return {
            "found": False,
            "suggestion": "智能手表系列",
            "products": [
                {
                    "name": "智能手表 Pro",
                    "price": "¥999",
                    "features": ["50米防水", "7天续航", "健康监测"],
                    "stock": "有货"
                },
                {
                    "name": "智能手表 Air",
                    "price": "¥599",
                    "features": ["轻薄设计", "5天续航", "运动追踪"],
                    "stock": "有货"
                }
            ]
        }
    
    def _search_tech_docs(self, query: str) -> List[Dict[str, str]]:
        """检索技术文档"""
        logger.info(f"检索技术文档: {query}")
        
        # 从知识库查询
        from django.db.models import Q
        knowledge_items = CustomerServiceKnowledgeBase.objects.filter(
            category='technical',
            is_active=True
        ).filter(
            Q(question__icontains=query) | 
            Q(answer__icontains=query)
        )[:3]
        
        if knowledge_items.exists():
            return [
                {
                    "title": item.question,
                    "content": item.answer,
                    "category": "技术支持"
                }
                for item in knowledge_items
            ]
        
        # 模拟数据
        return [
            {
                "title": "设备无法开机解决方案",
                "content": "1. 长按电源键10秒重启\n2. 检查电量是否充足\n3. 尝试充电30分钟后再开机",
                "category": "故障排查"
            },
            {
                "title": "如何连接手机配对",
                "content": "1. 打开手机蓝牙\n2. 在APP中选择添加设备\n3. 按照提示完成配对",
                "category": "使用教程"
            }
        ]
    
    def _search_knowledge_base(self, query: str, category: str = None) -> List[Dict[str, str]]:
        """通用知识库检索 - 从 ChromaDB 向量数据库检索"""
        logger.info(f"检索知识库: {query}, category: {category}")
        
        # 检查是否有关联的知识库
        if not self.knowledge_bases:
            logger.warning("助手未关联任何知识库")
            return []
        
        # 获取知识库 IDs
        kb_ids = [kb.id for kb in self.knowledge_bases]
        logger.info(f"从 {len(kb_ids)} 个知识库中检索: {kb_ids}")
        
        try:
            # 使用向量检索服务
            from .vector_service import VectorRetriever
            
            retriever = VectorRetriever()
            results = retriever.search_similar_chunks(
                query=query,
                knowledge_base_ids=kb_ids,
                top_k=5,
                similarity_threshold=0.5  # 降低阈值，提高召回率
            )
            
            logger.info(f"向量检索完成: 找到 {len(results)} 条相似结果")
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get('metadata', {}).get('document_name', '未知文档'),
                    "content": result['content'],
                    "category": result.get('metadata', {}).get('kb_name', '知识库'),
                    "similarity": f"{result['similarity']:.2f}"
                })
                logger.info(f"  - {result.get('metadata', {}).get('document_name', '未知')}: 相似度 {result['similarity']:.2f}")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"向量检索失败: {e}", exc_info=True)
            return []
    
    def run(self, user_message: str, user_id: int, session_id: str, 
            history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        运行工作流
        
        Args:
            user_message: 用户消息
            user_id: 用户ID
            session_id: 会话ID
            history: 历史对话（可选）
        
        Returns:
            包含响应和元数据的字典
        """
        logger.info(f"开始处理用户消息: session_id={session_id}, user_id={user_id}")
        
        # 构建消息历史
        messages = []
        if history:
            for msg in history[-5:]:  # 只保留最近5轮
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=user_message))
        
        # 初始化状态
        initial_state = CustomerServiceState(
            messages=messages,
            intent="",
            entities={},
            user_id=user_id,
            session_id=session_id,
            context={},
            tools_result={},
            need_human=False,
            confidence=0.0,
            response=""
        )
        
        try:
            # 运行图
            final_state = self.graph.invoke(initial_state)
            
            logger.info("工作流执行成功")
            
            return {
                "success": True,
                "response": final_state["response"],
                "intent": final_state["intent"],
                "entities": final_state["entities"],
                "need_human": final_state["need_human"],
                "confidence": final_state["confidence"],
                "tools_result": final_state["tools_result"],
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"工作流执行失败: {e}", exc_info=True)
            return {
                "success": False,
                "response": "抱歉，系统遇到了一些问题。让我为您转接人工客服。",
                "intent": "error",
                "entities": {},
                "need_human": True,
                "confidence": 0.0,
                "tools_result": {},
                "session_id": session_id,
                "error": str(e)
            }

