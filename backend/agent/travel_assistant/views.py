"""
旅游助手 API 视图
"""

import logging
import json
from typing import Dict, Any
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import StreamingHttpResponse
from core.response import StandardResponse

from .langgraph_service import travel_assistant_graph

logger = logging.getLogger(__name__)


class TravelAssistantChatView(APIView):
    """旅游助手聊天视图"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        处理聊天请求
        
        请求体:
        {
            "message": "我想去北京旅游",
            "thread_id": "user_123_travel",
            "user_preferences": {
                "budget": "5000",
                "duration": "3天",
                "travel_style": "文化游"
            },
            "current_city": "北京",
            "stream": true
        }
        """
        try:
            data = request.data
            user_message = data.get('message', '').strip()
            thread_id = data.get('thread_id', f"user_{request.user.id}_travel")
            user_preferences = data.get('user_preferences', {})
            current_city = data.get('current_city', '')
            use_stream = data.get('stream', True)  # 默认使用流式
            
            if not user_message:
                return StandardResponse.error(message="消息内容不能为空", code=400)
            
            # 默认使用流式响应
            if use_stream:
                return self._stream_response(
                    user_message,
                    thread_id,
                    user_preferences,
                    current_city
                )
            
            # 非流式响应（同步调用）
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    travel_assistant_graph.chat(
                        user_message=user_message,
                        thread_id=thread_id,
                        user_preferences=user_preferences,
                        current_city=current_city
                    )
                )
            finally:
                loop.close()
            
            if result.get('success'):
                return StandardResponse.success(
                    data={
                        'message': result['message'],
                        'tool_calls': result.get('tool_calls', []),
                        'current_city': result.get('current_city', ''),
                        'itinerary': result.get('itinerary', []),
                        'thread_id': thread_id
                    },
                    message="处理成功"
                )
            else:
                return StandardResponse.error(
                    message=result.get('message', '处理失败'),
                    code=500
                )
                
        except Exception as e:
            logger.error(f"旅游助手聊天失败: {e}", exc_info=True)
            return StandardResponse.error(
                message=f"处理请求时出错: {str(e)}",
                code=500
            )
    
    def _stream_response(
        self,
        user_message: str,
        thread_id: str,
        user_preferences: Dict[str, Any],
        current_city: str
    ):
        """流式响应"""
        
        def event_generator():
            """SSE 事件生成器"""
            try:
                for chunk in travel_assistant_graph.chat_stream(
                    user_message=user_message,
                    thread_id=thread_id,
                    user_preferences=user_preferences,
                    current_city=current_city
                ):
                    # 确保 chunk 是可序列化的字典
                    if isinstance(chunk, dict):
                        # 检查是否包含不可序列化的对象
                        serializable_chunk = self._make_serializable(chunk)
                        data = json.dumps(serializable_chunk, ensure_ascii=False)
                        yield f"data: {data}\n\n"
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"流式响应失败: {e}", exc_info=True)
                error_data = json.dumps({
                    "type": "error",
                    "content": str(e)
                }, ensure_ascii=False)
                yield f"data: {error_data}\n\n"
        
        response = StreamingHttpResponse(
            event_generator(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
    
    def _make_serializable(self, obj: Any) -> Any:
        """将对象转换为可序列化的格式"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, '__dict__'):
            # 如果是自定义对象，转换为字符串
            return str(obj)
        else:
            return obj


class TravelAssistantHistoryView(APIView):
    """旅游助手对话历史视图"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取对话历史
        
        查询参数:
        - thread_id: 对话线程ID
        """
        try:
            thread_id = request.query_params.get('thread_id')
            
            if not thread_id:
                return StandardResponse.error(message="thread_id 参数缺失", code=400)
            
            # 获取对话历史（同步调用）
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                history = loop.run_until_complete(
                    travel_assistant_graph.get_conversation_history(thread_id)
                )
            finally:
                loop.close()
            
            return StandardResponse.success(
                data={
                    'thread_id': thread_id,
                    'messages': history,
                    'count': len(history)
                },
                message="获取成功"
            )
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}", exc_info=True)
            return StandardResponse.error(
                message=f"获取对话历史失败: {str(e)}",
                code=500
            )


class GaodeMapToolsView(APIView):
    """高德地图工具直接调用视图（用于测试）"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        直接调用高德地图工具
        
        请求体:
        {
            "tool": "search_poi",
            "params": {
                "city": "北京",
                "keywords": "景点",
                "page_size": 10
            }
        }
        """
        try:
            from .gaode_tools import search_poi, calculate_route, get_weather, geocode_address
            
            tool_name = request.data.get('tool')
            params = request.data.get('params', {})
            
            tool_map = {
                'search_poi': search_poi,
                'calculate_route': calculate_route,
                'get_weather': get_weather,
                'geocode_address': geocode_address
            }
            
            if tool_name not in tool_map:
                return StandardResponse.error(
                    message=f"未知的工具: {tool_name}",
                    code=400
                )
            
            # 调用工具
            tool_func = tool_map[tool_name]
            result = tool_func.invoke(params)
            
            return StandardResponse.success(
                data={
                    'tool': tool_name,
                    'result': result
                },
                message="调用成功"
            )
            
        except Exception as e:
            logger.error(f"工具调用失败: {e}", exc_info=True)
            return StandardResponse.error(
                message=f"工具调用失败: {str(e)}",
                code=500
            )

