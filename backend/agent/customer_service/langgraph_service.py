"""
基于 LangGraph 的智能客服系统核心服务
"""
import json
import logging
from typing import TypedDict, List, Dict, Any, Annotated
import operator
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate

from django.conf import settings
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
    
    def __init__(self, api_key: str = None, model: str = "qwen-plus"):
        """
        初始化客服图
        
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
        workflow = StateGraph(CustomerServiceState)
        
        # 添加节点
        workflow.add_node("intent_classifier", self.classify_intent)
        workflow.add_node("entity_extractor", self.extract_entities)
        workflow.add_node("knowledge_retrieval", self.retrieve_knowledge)
        workflow.add_node("order_handler", self.handle_order_query)
        workflow.add_node("product_advisor", self.advise_product)
        workflow.add_node("tech_support", self.provide_tech_support)
        workflow.add_node("response_generator", self.generate_response)
        workflow.add_node("human_handoff_check", self.check_human_handoff)
        
        # 设置入口点
        workflow.set_entry_point("intent_classifier")
        
        # 添加边
        workflow.add_edge("intent_classifier", "entity_extractor")
        
        # 添加条件路由：根据意图分发到不同处理器
        workflow.add_conditional_edges(
            "entity_extractor",
            self.route_to_handler,
            {
                "order": "order_handler",
                "product": "product_advisor",
                "technical": "tech_support",
                "general": "knowledge_retrieval",
                "complaint": "knowledge_retrieval",
            }
        )
        
        # 所有处理器都流向响应生成
        for node in ["order_handler", "product_advisor", "tech_support", "knowledge_retrieval"]:
            workflow.add_edge(node, "response_generator")
        
        # 响应生成后检查是否需要转人工
        workflow.add_edge("response_generator", "human_handoff_check")
        
        # 人工转接判断后结束
        workflow.add_edge("human_handoff_check", END)
        
        return workflow.compile()
    
    def classify_intent(self, state: CustomerServiceState) -> CustomerServiceState:
        """意图分类节点"""
        logger.info("开始意图分类")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是专业的意图分类专家。分析用户消息，返回以下类别之一：

分类规则：
- order_query: 订单查询、物流跟踪、退换货、订单状态
- product_consult: 产品咨询、价格查询、功能对比、产品推荐
- technical_issue: 技术问题、故障报修、使用教程、配置帮助
- complaint: 投诉建议、质量问题、服务不满
- general: 通用咨询、闲聊、问候、其他

只返回类别名称，不要解释。"""),
            ("user", "{message}")
        ])
        
        try:
            last_message = state["messages"][-1].content
            result = self.llm.invoke(prompt.format_messages(message=last_message))
            intent = result.content.strip().lower()
            
            # 验证意图是否有效
            valid_intents = ["order_query", "product_consult", "technical_issue", "complaint", "general"]
            if intent not in valid_intents:
                intent = "general"
            
            state["intent"] = intent
            state["confidence"] = 0.8
            logger.info(f"意图分类结果: {intent}")
            
        except Exception as e:
            logger.error(f"意图分类失败: {e}")
            state["intent"] = "general"
            state["confidence"] = 0.3
        
        return state
    
    def extract_entities(self, state: CustomerServiceState) -> CustomerServiceState:
        """实体提取节点"""
        logger.info("开始实体提取")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """从用户消息中提取关键实体信息，以JSON格式返回：

{{
    "order_number": "订单号（如：202510210001）",
    "product_name": "产品名称",
    "date": "日期（YYYY-MM-DD格式）",
    "amount": "金额（数字）",
    "phone": "手机号",
    "email": "邮箱",
    "issue_type": "问题类型"
}}

只返回提取到的实体，没有的字段不返回。确保返回有效的JSON格式。"""),
            ("user", "{message}")
        ])
        
        try:
            last_message = state["messages"][-1].content
            result = self.llm.invoke(prompt.format_messages(message=last_message))
            
            # 解析 JSON
            content = result.content.strip()
            # 移除可能的 markdown 代码块标记
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            entities = json.loads(content)
            state["entities"] = entities
            logger.info(f"实体提取结果: {entities}")
            
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            state["entities"] = {}
        
        return state
    
    def route_to_handler(self, state: CustomerServiceState) -> str:
        """路由到具体处理器"""
        intent_map = {
            "order_query": "order",
            "product_consult": "product",
            "technical_issue": "technical",
            "complaint": "general",
            "general": "general"
        }
        
        route = intent_map.get(state["intent"], "general")
        logger.info(f"路由到: {route}")
        return route
    
    def handle_order_query(self, state: CustomerServiceState) -> CustomerServiceState:
        """处理订单查询"""
        logger.info("处理订单查询")
        
        order_number = state["entities"].get("order_number")
        
        if order_number:
            # 模拟调用订单系统API
            order_info = self._query_order_system(order_number)
            state["tools_result"]["order"] = order_info
            logger.info(f"订单查询成功: {order_number}")
        else:
            state["tools_result"]["order"] = {
                "status": "need_order_number",
                "message": "未找到订单号，请提供您的订单号以便查询"
            }
            logger.info("未提供订单号")
        
        return state
    
    def advise_product(self, state: CustomerServiceState) -> CustomerServiceState:
        """产品咨询顾问"""
        logger.info("处理产品咨询")
        
        product_name = state["entities"].get("product_name", "")
        user_message = state["messages"][-1].content
        
        # 从知识库检索产品信息
        product_info = self._search_product_knowledge(product_name or user_message)
        state["tools_result"]["product"] = product_info
        
        logger.info(f"产品咨询处理完成: {product_name}")
        return state
    
    def provide_tech_support(self, state: CustomerServiceState) -> CustomerServiceState:
        """技术支持"""
        logger.info("提供技术支持")
        
        issue_type = state["entities"].get("issue_type", "")
        user_message = state["messages"][-1].content
        
        # 检索技术文档
        tech_docs = self._search_tech_docs(issue_type or user_message)
        state["tools_result"]["technical"] = tech_docs
        
        logger.info("技术支持处理完成")
        return state
    
    def retrieve_knowledge(self, state: CustomerServiceState) -> CustomerServiceState:
        """知识库检索"""
        logger.info("检索知识库")
        
        query = state["messages"][-1].content
        intent = state["intent"]
        
        # 根据意图选择知识库分类
        category_map = {
            "complaint": "policy",
            "general": "faq"
        }
        category = category_map.get(intent, "faq")
        
        knowledge = self._search_knowledge_base(query, category)
        state["tools_result"]["knowledge"] = knowledge
        
        logger.info(f"知识库检索完成: {len(knowledge)} 条结果")
        return state
    
    def generate_response(self, state: CustomerServiceState) -> CustomerServiceState:
        """生成最终响应"""
        logger.info("生成响应")
        
        # 构建对话历史
        history_text = "\n".join([
            f"{msg.type}: {msg.content}"
            for msg in state["messages"][:-1]
        ]) if len(state["messages"]) > 1 else "无历史对话"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是专业、友好的智能客服助手。基于以下信息生成回复：

意图：{intent}
提取的实体：{entities}
工具查询结果：{tools_result}
对话历史：
{history}

回复要求：
1. 语气友好、专业、有同理心
2. 针对性解答用户问题
3. 如信息不足，礼貌地询问具体细节
4. 提供后续建议或帮助
5. 如果是投诉，表达歉意并说明解决方案
6. 回复简洁明了，200字以内

请直接生成回复内容，不要包含其他说明。"""),
            ("user", "当前用户消息：{current_message}")
        ])
        
        try:
            result = self.llm.invoke(prompt.format_messages(
                intent=state["intent"],
                entities=json.dumps(state["entities"], ensure_ascii=False),
                tools_result=json.dumps(state["tools_result"], ensure_ascii=False, indent=2),
                history=history_text,
                current_message=state["messages"][-1].content
            ))
            
            state["response"] = result.content.strip()
            logger.info("响应生成成功")
            
        except Exception as e:
            logger.error(f"响应生成失败: {e}")
            state["response"] = "抱歉，我遇到了一些问题。请稍后再试，或者让我为您转接人工客服。"
        
        return state
    
    def check_human_handoff(self, state: CustomerServiceState) -> CustomerServiceState:
        """判断是否需要人工"""
        logger.info("检查是否需要转人工")
        
        user_message = state["messages"][-1].content.lower()
        
        # 判断条件
        needs_human = (
            state["intent"] == "complaint" or  # 投诉类自动转人工
            "人工" in user_message or
            "转接" in user_message or
            "客服" in user_message and "人" in user_message or
            state["confidence"] < 0.5  # 置信度低
        )
        
        state["need_human"] = needs_human
        
        if needs_human:
            logger.info("需要转人工")
            # 在响应中添加转人工提示
            if not any(keyword in state["response"] for keyword in ["转接", "人工客服"]):
                state["response"] += "\n\n正在为您转接人工客服，请稍候..."
        else:
            logger.info("无需转人工")
        
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
            models.Q(question__icontains=query) | 
            models.Q(answer__icontains=query)
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
        """通用知识库检索"""
        logger.info(f"检索知识库: {query}, category: {category}")
        
        from django.db.models import Q
        
        # 构建查询
        queryset = CustomerServiceKnowledgeBase.objects.filter(is_active=True)
        
        if category:
            queryset = queryset.filter(category=category)
        
        queryset = queryset.filter(
            Q(question__icontains=query) | 
            Q(answer__icontains=query)
        )[:5]
        
        if queryset.exists():
            # 更新使用次数
            for item in queryset:
                item.use_count += 1
                item.save(update_fields=['use_count'])
            
            return [
                {
                    "question": item.question,
                    "answer": item.answer,
                    "category": item.get_category_display()
                }
                for item in queryset
            ]
        
        # 返回空列表
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

