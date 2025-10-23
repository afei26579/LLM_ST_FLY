"""
诗词绘画 LangGraph 服务
基于 LangGraph 的状态机工作流
"""
import logging
import json
from typing import Dict, Any, TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
import dashscope
from django.conf import settings

from .poetry_service import PoetryService
from .painting_service import PaintingService
from .analysis_service import AnalysisService
from .prompts import INTENT_RECOGNITION_TEMPLATE

logger = logging.getLogger(__name__)


# 定义状态类型
class PoetryPaintingState(TypedDict):
    """诗词绘画智能体状态"""
    # 用户输入
    user_input: str
    intent: Optional[str]  # create_poetry, create_painting, both, analyze, iterate
    
    # 诗词相关
    poetry_theme: Optional[str]
    poetry_style: Optional[str]  # 豪放/婉约/田园/边塞/山水
    poetry_format: Optional[str]  # five_jueju/seven_jueju等
    poetry_content: Optional[str]
    poetry_title: Optional[str]
    poetry_analysis: Optional[dict]
    
    # 绘画相关
    painting_description: Optional[str]
    painting_style: Optional[str]  # chinese_ink/gongbi等
    painting_prompt: Optional[str]
    painting_url: Optional[str]
    painting_local_path: Optional[str]
    image_size: Optional[str]  # 图像尺寸
    
    # 流程控制
    current_step: str
    iteration_count: int
    user_feedback: Optional[str]
    conversation_history: list
    
    # 结果
    final_output: Optional[dict]
    error: Optional[str]


class PoetryPaintingLangGraphService:
    """诗词绘画 LangGraph 服务"""
    
    def __init__(self):
        self.poetry_service = PoetryService()
        self.painting_service = PaintingService()
        self.analysis_service = AnalysisService()
        self.api_key = settings.DASHSCOPE_API_KEY
        dashscope.api_key = self.api_key
        self.callback = None
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 状态图"""
        workflow = StateGraph(PoetryPaintingState)
        
        # 添加节点
        workflow.add_node("intent_recognition", self.recognize_intent)
        workflow.add_node("poetry_creation", self.create_poetry)
        workflow.add_node("poetry_analysis", self.analyze_poetry)
        workflow.add_node("painting_generation", self.generate_painting)
        workflow.add_node("result_integration", self.integrate_result)
        workflow.add_node("iteration_optimization", self.optimize_iteration)
        
        # 设置入口点
        workflow.set_entry_point("intent_recognition")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "intent_recognition",
            self.route_by_intent,
            {
                "create_both": "poetry_creation",
                "end": END
            }
        )
        
        # 创作流程
        workflow.add_edge("poetry_creation", "poetry_analysis")
        workflow.add_edge("poetry_analysis", "painting_generation")
        workflow.add_edge("painting_generation", "result_integration")
        
        # 结果处理
        workflow.add_conditional_edges(
            "result_integration",
            self.check_user_feedback,
            {
                "iterate": "iteration_optimization",
                "end": END
            }
        )
        
        # 迭代优化
        workflow.add_edge("iteration_optimization", "poetry_creation")
        
        return workflow.compile()
    
    # ==================== 节点实现 ====================
    
    def recognize_intent(self, state: PoetryPaintingState) -> PoetryPaintingState:
        """意图识别节点"""
        try:
            user_input = state["user_input"]
            
            logger.info(f"识别用户意图: {user_input[:50]}")
            
            # 使用 LLM 识别用户意图
            intent_prompt = INTENT_RECOGNITION_TEMPLATE.format(
                user_input=user_input
            )
            
            response = dashscope.Generation.call(
                model='qwen-max',
                messages=[
                    {"role": "user", "content": intent_prompt}
                ],
                temperature=0.3,
                result_format='message'
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                
                # 解析JSON响应
                result = self._parse_json_response(content)
                
                state["intent"] = result.get("intent", "both")
                state["poetry_theme"] = result.get("theme", user_input)
                
                # 只在用户未指定时使用AI推荐的参数
                if not state.get("poetry_style"):
                    state["poetry_style"] = result.get("poetry_style", "婉约")
                if not state.get("painting_style"):
                    state["painting_style"] = result.get("painting_style", "chinese_ink")
                if not state.get("poetry_format"):
                    state["poetry_format"] = result.get("poetry_format", "seven_jueju")
                
                logger.info(f"意图识别完成 - 意图: {state['intent']}, 主题: {state['poetry_theme']}")
                logger.info(f"使用参数 - 诗词风格: {state['poetry_style']}, 诗词格式: {state['poetry_format']}, 绘画风格: {state['painting_style']}")
            else:
                # 默认为创作模式
                logger.warning(f"意图识别失败，使用默认配置: {response.message}")
                state["intent"] = "both"
                state["poetry_theme"] = user_input
                
                # 只在用户未指定时使用默认值
                if not state.get("poetry_style"):
                    state["poetry_style"] = "婉约"
                if not state.get("painting_style"):
                    state["painting_style"] = "chinese_ink"
                if not state.get("poetry_format"):
                    state["poetry_format"] = "seven_jueju"
            
            state["current_step"] = "intent_recognized"
            
            # 回调发送意图识别结果
            if self.callback:
                self.callback('intent_recognized', state)
            
        except Exception as e:
            logger.error(f"意图识别异常: {e}")
            state["intent"] = "both"
            state["poetry_theme"] = state["user_input"]
            state["current_step"] = "intent_recognized"
        
        return state
    
    def create_poetry(self, state: PoetryPaintingState) -> PoetryPaintingState:
        """诗词创作节点"""
        try:
            theme = state.get("poetry_theme", "")
            style = state.get("poetry_style", "婉约")
            format_type = state.get("poetry_format", "seven_jueju")
            
            logger.info(f"开始创作诗词 - 主题: {theme}, 风格: {style}")
            
            # 如果是迭代，使用原有内容和反馈
            if state.get("user_feedback") and state.get("poetry_content"):
                poetry_result = self.poetry_service.refine_poetry(
                    original_content=state["poetry_content"],
                    feedback=state["user_feedback"],
                    original_title=state.get("poetry_title", "")
                )
            else:
                # 使用诗词生成服务
                poetry_result = self.poetry_service.generate_poetry(
                    theme=theme,
                    style=style,
                    format_type=format_type
                )
            
            state["poetry_content"] = poetry_result["content"]
            state["poetry_title"] = poetry_result.get("title", "")
            state["current_step"] = "poetry_created"
            
            logger.info(f"诗词创作完成 - 标题: {state['poetry_title']}")
            
            # 回调发送诗词创作结果
            if self.callback:
                self.callback('poetry_created', state)
            
        except Exception as e:
            logger.error(f"诗词创作异常: {e}")
            state["error"] = f"诗词创作失败: {str(e)}"
        
        return state
    
    def analyze_poetry(self, state: PoetryPaintingState) -> PoetryPaintingState:
        """诗词分析节点"""
        try:
            poetry_content = state.get("poetry_content", "")
            poetry_title = state.get("poetry_title", "")
            
            logger.info(f"开始分析诗词: {poetry_title or poetry_content[:20]}")
            
            # 分析诗词的意境、典故、修辞
            analysis = self.analysis_service.analyze_poetry(
                poetry_content=poetry_content,
                poetry_title=poetry_title
            )
            
            state["poetry_analysis"] = analysis
            
            # 生成绘画描述
            painting_description = self.analysis_service.generate_painting_description(
                poetry_content=poetry_content,
                analysis=analysis,
                painting_style=state.get("painting_style", "chinese_ink")
            )
            
            state["painting_description"] = painting_description
            state["current_step"] = "poetry_analyzed"
            
            logger.info(f"诗词分析完成 - 意象数: {len(analysis.get('imagery', []))}")
            
            # 回调发送诗词分析结果
            if self.callback:
                self.callback('poetry_analyzed', state)
            
        except Exception as e:
            logger.error(f"诗词分析异常: {e}")
            state["error"] = f"诗词分析失败: {str(e)}"
            # 使用基础描述
            state["painting_description"] = state.get("poetry_content", "")
        
        return state
    
    def generate_painting(self, state: PoetryPaintingState) -> PoetryPaintingState:
        """绘画生成节点"""
        try:
            poetry_content = state.get("poetry_content", "")
            painting_desc = state.get("painting_description", "")
            painting_style = state.get("painting_style", "chinese_ink")
            image_size = state.get("image_size", "1328*1328")
            
            logger.info(f"开始生成绘画 - 风格: {painting_style}, 尺寸: {image_size}")
            
            # 构建绘画提示词
            painting_prompt = self.painting_service.build_painting_prompt(
                poetry_content=poetry_content,
                imagery_description=painting_desc,
                painting_style=painting_style
            )
            
            state["painting_prompt"] = painting_prompt
            
            # 如果是迭代且有反馈，使用优化生成
            if state.get("user_feedback") and state.get("iteration_count", 1) > 1:
                painting_result = self.painting_service.refine_painting(
                    original_prompt=painting_prompt,
                    feedback=state["user_feedback"],
                    painting_style=painting_style,
                    size=image_size
                )
            else:
                # 生成图像
                painting_result = self.painting_service.generate_image(
                    prompt=painting_prompt,
                    painting_style=painting_style,
                    size=image_size
                )
            
            state["painting_url"] = painting_result["url"]
            state["painting_local_path"] = painting_result.get("local_path", "")
            state["current_step"] = "painting_generated"
            
            logger.info(f"绘画生成完成 - URL: {painting_result['url'][:50]}...")
            
            # 回调发送绘画生成结果
            if self.callback:
                self.callback('painting_generated', state)
            
        except Exception as e:
            logger.error(f"绘画生成异常: {e}")
            state["error"] = f"绘画生成失败: {str(e)}"
        
        return state
    
    def integrate_result(self, state: PoetryPaintingState) -> PoetryPaintingState:
        """整合结果节点"""
        try:
            logger.info("整合最终结果")
            
            state["final_output"] = {
                "poetry": {
                    "title": state.get("poetry_title", ""),
                    "content": state.get("poetry_content", ""),
                    "style": state.get("poetry_style", ""),
                    "format": state.get("poetry_format", ""),
                    "theme": state.get("poetry_theme", ""),
                    "analysis": state.get("poetry_analysis", {})
                },
                "painting": {
                    "url": state.get("painting_url", ""),
                    "local_path": state.get("painting_local_path", ""),
                    "prompt": state.get("painting_prompt", ""),
                    "style": state.get("painting_style", ""),
                    "description": state.get("painting_description", "")
                },
                "metadata": {
                    "iteration": state.get("iteration_count", 1),
                    "current_step": "completed"
                }
            }
            
            state["current_step"] = "completed"
            
            logger.info("结果整合完成")
            
        except Exception as e:
            logger.error(f"结果整合异常: {e}")
            state["error"] = f"结果整合失败: {str(e)}"
        
        return state
    
    def optimize_iteration(self, state: PoetryPaintingState) -> PoetryPaintingState:
        """迭代优化节点"""
        try:
            logger.info(f"开始迭代优化 - 迭代次数: {state.get('iteration_count', 1) + 1}")
            
            state["iteration_count"] = state.get("iteration_count", 1) + 1
            state["current_step"] = "iterating"
            
            # 重置当前步骤，准备重新生成
            # 保留用户反馈和迭代次数
            
        except Exception as e:
            logger.error(f"迭代优化异常: {e}")
            state["error"] = f"迭代优化失败: {str(e)}"
        
        return state
    
    # ==================== 路由函数 ====================
    
    def route_by_intent(self, state: PoetryPaintingState) -> str:
        """根据意图路由"""
        intent = state.get("intent", "both")
        
        # 目前支持创作模式
        if intent in ["create_poetry", "both"]:
            return "create_both"
        
        return "end"
    
    def check_user_feedback(self, state: PoetryPaintingState) -> str:
        """检查是否需要迭代"""
        # 如果有用户反馈且迭代次数未超限
        if state.get("user_feedback") and state.get("iteration_count", 1) < 3:
            return "iterate"
        
        return "end"
    
    # ==================== 辅助方法 ====================
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """解析JSON响应"""
        try:
            import re
            # 提取JSON内容
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                return {}
        except Exception as e:
            logger.warning(f"JSON解析失败: {e}")
            return {}
    
    # ==================== 公共方法 ====================
    
    def run(self, user_input: str, callback=None, **kwargs) -> Dict[str, Any]:
        """
        运行智能体
        
        Args:
            user_input: 用户输入
            callback: 回调函数，用于发送中间结果
            **kwargs: 其他参数
            
        Returns:
            最终状态
        """
        self.callback = callback
        initial_state: PoetryPaintingState = {
            "user_input": user_input,
            "intent": None,
            "poetry_theme": None,
            "poetry_style": kwargs.get("poetry_style"),
            "poetry_format": kwargs.get("poetry_format"),
            "poetry_content": None,
            "poetry_title": None,
            "poetry_analysis": None,
            "painting_description": None,
            "painting_style": kwargs.get("painting_style"),
            "painting_prompt": None,
            "painting_url": None,
            "painting_local_path": None,
            "image_size": kwargs.get("image_size", "1328*1328"),
            "current_step": "start",
            "iteration_count": kwargs.get("iteration_count", 1),
            "user_feedback": kwargs.get("user_feedback"),
            "conversation_history": kwargs.get("history", []),
            "final_output": None,
            "error": None
        }
        
        try:
            logger.info(f"开始运行 LangGraph - 输入: {user_input[:50]}")
            
            # 执行工作流
            final_state = self.graph.invoke(initial_state)
            
            logger.info(f"LangGraph 执行完成 - 状态: {final_state.get('current_step')}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"LangGraph 执行异常: {e}")
            raise

