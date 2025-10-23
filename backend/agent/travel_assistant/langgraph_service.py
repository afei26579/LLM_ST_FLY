"""
基于 LangGraph 的旅游助手服务
"""

import os
import logging
from typing import TypedDict, Annotated, Sequence, List, Dict, Any
from operator import add
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from .gaode_tools import GAODE_TOOLS

logger = logging.getLogger(__name__)


# 定义状态
class TravelAgentState(TypedDict):
    """旅游助手状态"""
    messages: Annotated[Sequence[BaseMessage], add]
    user_preferences: Dict[str, Any]  # 用户偏好（预算、出行方式等）
    current_city: str  # 当前讨论的城市
    itinerary: List[Dict[str, Any]]  # 行程计划
    next_step: str  # 下一步动作


class TravelAssistantGraph:
    """旅游助手 LangGraph 服务"""
    
    def __init__(self):
        """初始化旅游助手图"""
        self.llm = self._create_llm()
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
    
    def _create_llm(self) -> ChatOpenAI:
        """创建 LLM 实例（使用 DashScope 的 OpenAI 兼容接口）"""
        api_key = os.getenv('DASHSCOPE_API_KEY', '')
        model = os.getenv('DASHSCOPE_MODEL', 'qwen-max')
        # DashScope 的 OpenAI 兼容接口
        base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
        
        if not api_key:
            logger.warning("未配置 DASHSCOPE_API_KEY，LLM 初始化可能失败")
        
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            streaming=True,
            top_p=0.8
        )
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图"""
        # 创建状态图
        workflow = StateGraph(TravelAgentState)
        
        # 绑定工具到 LLM
        llm_with_tools = self.llm.bind_tools(GAODE_TOOLS)
        
        # 创建工具节点
        tool_node = ToolNode(GAODE_TOOLS)
        
        # 添加节点
        workflow.add_node("agent", lambda state: self._agent_node(state, llm_with_tools))
        workflow.add_node("tools", tool_node)
        workflow.add_node("summarize", self._summarize_node)
        
        # 设置入口点
        workflow.set_entry_point("agent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "summarize": "summarize",
                "end": END
            }
        )
        
        # 工具执行后返回到 agent
        workflow.add_edge("tools", "agent")
        workflow.add_edge("summarize", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _agent_node(self, state: TravelAgentState, llm_with_tools) -> Dict[str, Any]:
        """智能体节点 - 决定下一步动作"""
        messages = state['messages']
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt(state)
        
        # 将系统提示词添加到消息列表开头（如果还没有）
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=system_prompt)] + list(messages)
        
        # 调用 LLM
        response = llm_with_tools.invoke(messages)
        
        return {
            "messages": [response],
            "next_step": "continue" if response.tool_calls else "end"
        }
    
    def _summarize_node(self, state: TravelAgentState) -> Dict[str, Any]:
        """总结节点 - 生成行程摘要"""
        messages = state['messages']
        
        # 构建总结提示
        summary_prompt = """
        请根据对话内容，总结用户的旅行计划，包括：
        1. 目的地城市
        2. 出行时间和天数
        3. 推荐的景点和活动
        4. 交通和住宿建议
        5. 预算估算
        
        请以清晰、结构化的方式呈现。
        """
        
        summary_messages = messages + [HumanMessage(content=summary_prompt)]
        response = self.llm.invoke(summary_messages)
        
        return {
            "messages": [response],
            "next_step": "end"
        }
    
    def _should_continue(self, state: TravelAgentState) -> str:
        """决定是否继续执行工具"""
        messages = state['messages']
        last_message = messages[-1]
        
        # 如果最后一条消息有工具调用，继续执行工具
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        
        # 检查是否需要总结
        if len(messages) > 10 and "总结" in str(messages[-1].content):
            return "summarize"
        
        return "end"
    
    def _build_system_prompt(self, state: TravelAgentState) -> str:
        """构建系统提示词"""
        base_prompt = """你是一个专业的旅游助手，具有以下能力：

1. **景点推荐**：使用 search_poi 工具搜索景点、餐厅、酒店等信息
2. **路线规划**：使用 calculate_route 工具计算两地之间的路线和时间
3. **天气查询**：使用 get_weather 工具查询目的地天气
4. **地址解析**：使用 geocode_address 工具获取地址的经纬度

你的任务是：
- 主动询问用户的旅行需求（出发点、目的地、时间、预算、偏好等）
- 使用工具搜索相关信息并给出专业建议
- 制定合理的行程计划，包括景点、交通、住宿安排
- 提供实用的旅游贴士和注意事项

注意事项：
- 调用工具前，确保参数准确（特别是城市名称）
- 根据工具返回的结果给出专业分析和建议
- 回答要具体、实用，包含必要的细节（价格、时间、距离等）
- 保持友好、专业的服务态度
"""
        
        # 添加上下文信息
        if state.get('current_city'):
            base_prompt += f"\n\n当前讨论的城市：{state['current_city']}"
        
        if state.get('user_preferences'):
            prefs = state['user_preferences']
            base_prompt += f"\n\n用户偏好：{prefs}"
        
        return base_prompt
    
    async def chat(
        self,
        user_message: str,
        thread_id: str,
        user_preferences: Dict[str, Any] = None,
        current_city: str = ""
    ) -> Dict[str, Any]:
        """
        处理聊天请求
        
        Args:
            user_message: 用户消息
            thread_id: 对话线程ID
            user_preferences: 用户偏好
            current_city: 当前城市
            
        Returns:
            响应字典
        """
        try:
            # 构建初始状态
            initial_state = {
                "messages": [HumanMessage(content=user_message)],
                "user_preferences": user_preferences or {},
                "current_city": current_city,
                "itinerary": [],
                "next_step": "continue"
            }
            
            # 配置（包含线程ID用于检查点）
            config = {"configurable": {"thread_id": thread_id}}
            
            # 执行图
            result = await self.graph.ainvoke(initial_state, config)
            
            # 提取最后的 AI 消息
            ai_messages = [
                msg for msg in result['messages'] 
                if isinstance(msg, AIMessage)
            ]
            
            if ai_messages:
                last_ai_message = ai_messages[-1]
                
                return {
                    "success": True,
                    "message": last_ai_message.content,
                    "tool_calls": getattr(last_ai_message, 'tool_calls', []),
                    "current_city": result.get('current_city', ''),
                    "itinerary": result.get('itinerary', [])
                }
            else:
                return {
                    "success": False,
                    "message": "抱歉，处理您的请求时遇到了问题。",
                    "error": "No AI response"
                }
                
        except Exception as e:
            logger.error(f"LangGraph 聊天处理失败: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"处理请求时出错: {str(e)}",
                "error": str(e)
            }
    
    def chat_stream(
        self,
        user_message: str,
        thread_id: str,
        user_preferences: Dict[str, Any] = None,
        current_city: str = ""
    ):
        """
        流式处理聊天请求（生成器）
        
        Args:
            user_message: 用户消息
            thread_id: 对话线程ID
            user_preferences: 用户偏好
            current_city: 当前城市
            
        Yields:
            消息块
        """
        try:
            # 构建初始状态
            initial_state = {
                "messages": [HumanMessage(content=user_message)],
                "user_preferences": user_preferences or {},
                "current_city": current_city,
                "itinerary": [],
                "next_step": "continue"
            }
            
            # 配置
            config = {"configurable": {"thread_id": thread_id}}
            
            # 流式执行图
            for event in self.graph.stream(initial_state, config):
                # 处理不同类型的事件
                if 'agent' in event:
                    agent_output = event['agent']
                    messages = agent_output.get('messages', [])
                    
                    for msg in messages:
                        if isinstance(msg, AIMessage):
                            # 流式输出内容
                            if msg.content:
                                # 提取工具调用信息（可序列化）
                                tool_calls_info = []
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    for tc in msg.tool_calls:
                                        tool_calls_info.append({
                                            'name': tc.get('name', '') if isinstance(tc, dict) else getattr(tc, 'name', ''),
                                            'args': tc.get('args', {}) if isinstance(tc, dict) else str(tc)
                                        })
                                
                                yield {
                                    "type": "message",
                                    "content": msg.content,
                                    "tool_calls": tool_calls_info
                                }
                
                elif 'tools' in event:
                    # 工具调用事件
                    yield {
                        "type": "tool",
                        "content": "🔧 正在调用工具获取信息..."
                    }
                
                elif 'summarize' in event:
                    summary_output = event['summarize']
                    messages = summary_output.get('messages', [])
                    
                    for msg in messages:
                        if isinstance(msg, AIMessage) and msg.content:
                            yield {
                                "type": "summary",
                                "content": msg.content
                            }
                            
        except Exception as e:
            logger.error(f"LangGraph 流式聊天失败: {e}", exc_info=True)
            yield {
                "type": "error",
                "content": f"处理请求时出错: {str(e)}",
                "error": str(e)
            }
    
    async def get_conversation_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """
        获取对话历史
        
        Args:
            thread_id: 对话线程ID
            
        Returns:
            对话历史列表
        """
        try:
            config = {"configurable": {"thread_id": thread_id}}
            state = await self.graph.aget_state(config)
            
            if state and state.values.get('messages'):
                messages = state.values['messages']
                return [
                    {
                        "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                        "content": msg.content
                    }
                    for msg in messages
                    if isinstance(msg, (HumanMessage, AIMessage))
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []


# 创建全局实例
travel_assistant_graph = TravelAssistantGraph()

