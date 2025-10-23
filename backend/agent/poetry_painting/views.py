"""
诗词绘画智能体视图
"""
import logging
import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.response import StandardResponse

from .models import PoetryPaintingConversation, PoetryPaintingWork, PoetryPaintingMessage
from .serializers import (
    PoetryPaintingConversationSerializer,
    PoetryPaintingWorkSerializer,
    PoetryPaintingMessageSerializer,
    CreateWorkRequestSerializer,
    IterateWorkRequestSerializer,
    RateWorkRequestSerializer
)
from .langgraph_service import PoetryPaintingLangGraphService

logger = logging.getLogger(__name__)


@csrf_exempt
def create_work_stream(request):
    """
    创作诗词画作（流式返回）
    
    POST /api/v1/agent/poetry-painting/create-work-stream/
    """
    if request.method != 'POST':
        return JsonResponse({'error': '方法不允许'}, status=405)
    
    # 手动进行JWT认证
    try:
        jwt_auth = JWTAuthentication()
        user_auth_tuple = jwt_auth.authenticate(request)
        if user_auth_tuple is None:
            return JsonResponse({'error': '未授权'}, status=401)
        user, token = user_auth_tuple
        request.user = user
    except Exception as e:
        logger.error(f"认证失败: {e}")
        return JsonResponse({'error': '认证失败'}, status=401)
    
    def event_stream():
        try:
            import json as json_module
            # 验证请求数据
            from .serializers import CreateWorkRequestSerializer
            
            # 解析JSON请求体
            try:
                request_data = json_module.loads(request.body)
            except:
                request_data = {}
            
            serializer = CreateWorkRequestSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            
            user_input = serializer.validated_data['input']
            poetry_style = serializer.validated_data.get('poetry_style')
            poetry_format = serializer.validated_data.get('poetry_format')
            painting_style = serializer.validated_data.get('painting_style')
            image_size = serializer.validated_data.get('image_size')
            conversation_id = serializer.validated_data.get('conversation_id')
            
            # 获取或创建对话
            if conversation_id:
                conversation = get_object_or_404(
                    PoetryPaintingConversation,
                    id=conversation_id,
                    user=request.user
                )
            else:
                conversation = PoetryPaintingConversation.objects.create(
                    user=request.user,
                    title=user_input[:50]
                )
            
            # 发送对话ID
            yield f"data: {json.dumps({'type': 'conversation_id', 'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"
            
            # 保存用户消息
            PoetryPaintingMessage.objects.create(
                conversation=conversation,
                role='user',
                content=user_input
            )
            
            # 运行 LangGraph（逐步执行并流式输出）
            service = PoetryPaintingLangGraphService()
            
            # 1. 意图识别
            yield f"data: {json.dumps({'type': 'step', 'step': 'intent_recognizing', 'message': '正在理解您的创作意图...'}, ensure_ascii=False)}\n\n"
            
            # 初始化状态
            from .langgraph_service import PoetryPaintingState
            
            # 获取对话历史的辅助函数
            def get_conversation_history(conv):
                messages = conv.messages.order_by('created_at')[:10]
                history = []
                for msg in messages:
                    history.append({"role": msg.role, "content": msg.content})
                return history
            
            state: PoetryPaintingState = {
                "user_input": user_input,
                "intent": None,
                "poetry_theme": None,
                "poetry_style": poetry_style,
                "poetry_format": poetry_format,
                "poetry_content": None,
                "poetry_title": None,
                "poetry_analysis": None,
                "painting_description": None,
                "painting_style": painting_style,
                "painting_prompt": None,
                "painting_url": None,
                "painting_local_path": None,
                "image_size": image_size or "1328*1328",
                "current_step": "start",
                "iteration_count": 1,
                "user_feedback": None,
                "conversation_history": get_conversation_history(conversation),
                "final_output": None,
                "error": None
            }
            
            # 意图识别
            state = service.recognize_intent(state)
            yield f"data: {json.dumps({'type': 'intent', 'theme': state.get('poetry_theme', ''), 'poetry_style': state.get('poetry_style', ''), 'painting_style': state.get('painting_style', '')}, ensure_ascii=False)}\n\n"
            
            # 2. 诗词创作
            yield f"data: {json.dumps({'type': 'step', 'step': 'poetry_creating', 'message': '正在创作诗词...'}, ensure_ascii=False)}\n\n"
            state = service.create_poetry(state)
            yield f"data: {json.dumps({'type': 'poetry', 'title': state.get('poetry_title', ''), 'content': state.get('poetry_content', ''), 'style': state.get('poetry_style', ''), 'format': state.get('poetry_format', '')}, ensure_ascii=False)}\n\n"
            
            # 3. 诗词分析
            yield f"data: {json.dumps({'type': 'step', 'step': 'analyzing', 'message': '正在分析诗词意境...'}, ensure_ascii=False)}\n\n"
            state = service.analyze_poetry(state)
            yield f"data: {json.dumps({'type': 'analysis', 'analysis': state.get('poetry_analysis', {}), 'imagery_description': state.get('painting_description', '')}, ensure_ascii=False)}\n\n"
            
            # 4. 绘画生成
            yield f"data: {json.dumps({'type': 'step', 'step': 'painting_generating', 'message': '正在绘制意境画作...'}, ensure_ascii=False)}\n\n"
            state = service.generate_painting(state)
            yield f"data: {json.dumps({'type': 'painting', 'url': state.get('painting_url', ''), 'local_path': state.get('painting_local_path', ''), 'prompt': state.get('painting_prompt', '')}, ensure_ascii=False)}\n\n"
            
            # 5. 整合结果
            state = service.integrate_result(state)
            result = state
            
            # 保存作品
            final_output = result.get("final_output", {})
            poetry_data = final_output.get("poetry", {})
            painting_data = final_output.get("painting", {})
            
            work = PoetryPaintingWork.objects.create(
                conversation=conversation,
                poetry_content=poetry_data.get("content", ""),
                poetry_title=poetry_data.get("title", ""),
                poetry_theme=poetry_data.get("theme", user_input),
                poetry_format=poetry_data.get("format", "seven_jueju"),
                poetry_style=poetry_data.get("style", "婉约"),
                poetry_analysis=poetry_data.get("analysis", {}),
                painting_url=painting_data.get("url", ""),
                painting_local_path=painting_data.get("local_path", ""),
                painting_prompt=painting_data.get("prompt", ""),
                painting_style=painting_data.get("style", "chinese_ink"),
                langgraph_state=result,
                iteration_count=result.get("iteration_count", 1)
            )
            
            # 保存助手消息
            def format_response_content(result_data):
                poetry = result_data.get("poetry", {})
                painting = result_data.get("painting", {})
                
                content = f"""📜 **{poetry.get('title', '诗词作品')}**

{poetry.get('content', '')}

---

🎨 **意境画作**

画作已生成，展现了诗词中的意境。

**风格**: {painting.get('style', '')}
"""
                return content
            
            response_content = format_response_content(final_output)
            PoetryPaintingMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=response_content,
                work=work
            )
            
            # 发送完成信息
            yield f"data: {json.dumps({'type': 'complete', 'work_id': work.id, 'conversation_id': conversation.id}, ensure_ascii=False)}\n\n"
            
        except Exception as e:
            logger.error(f"流式创作异常: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }
    )


class PoetryPaintingViewSet(viewsets.ViewSet):
    """诗词绘画智能体视图集"""
    
    permission_classes = [IsAuthenticated]
    
    def _get_conversation_history(self, conversation: PoetryPaintingConversation) -> list:
        """获取对话历史"""
        messages = conversation.messages.order_by('created_at')[:10]  # 最近10条
        history = []
        for msg in messages:
            history.append({
                "role": msg.role,
                "content": msg.content
            })
        return history
    
    def _format_response_content(self, result: dict) -> str:
        """格式化响应内容"""
        poetry = result.get("poetry", {})
        painting = result.get("painting", {})
        
        content = f"""📜 **{poetry.get('title', '诗词作品')}**

{poetry.get('content', '')}

---

🎨 **意境画作**

画作已生成，展现了诗词中的意境：{painting.get('description', '')}

**风格**: {painting.get('style', '')}
**提示词**: {painting.get('prompt', '')[:100]}...

---

💡 **赏析**

"""
        
        analysis = poetry.get('analysis', {})
        if analysis:
            content += f"""
**意象**: {', '.join([img.get('name', '') for img in analysis.get('imagery', [])])}
**情感**: {analysis.get('emotion', '')}
**修辞**: {', '.join(analysis.get('rhetoric', []))}
"""
        
        return content
    
    @action(detail=False, methods=['post'], url_path='create-work')
    def create_work(self, request):
        """
        创作诗词画作
        
        POST /api/v1/agent/poetry-painting/create-work/
        """
        try:
            # 验证请求数据
            serializer = CreateWorkRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user_input = serializer.validated_data['input']
            # 空字符串转为None，让AI智能选择
            poetry_style = serializer.validated_data.get('poetry_style') or None
            poetry_format = serializer.validated_data.get('poetry_format') or None
            painting_style = serializer.validated_data.get('painting_style') or None
            image_size = serializer.validated_data.get('image_size')
            conversation_id = serializer.validated_data.get('conversation_id')
            
            # 日志记录接收到的参数
            logger.info(f"接收到的参数 - 诗词风格: {poetry_style or '智能选择'}, 诗词格式: {poetry_format or '智能选择'}, 绘画风格: {painting_style or '智能选择'}, 图像尺寸: {image_size}")
            
            # 获取或创建对话
            if conversation_id:
                conversation = get_object_or_404(
                    PoetryPaintingConversation,
                    id=conversation_id,
                    user=request.user
                )
            else:
                conversation = PoetryPaintingConversation.objects.create(
                    user=request.user,
                    title=user_input[:50]
                )
            
            # 保存用户消息
            PoetryPaintingMessage.objects.create(
                conversation=conversation,
                role='user',
                content=user_input
            )
            
            # 运行 LangGraph
            logger.info(f"用户 {request.user.username} 开始创作 - 主题: {user_input[:30]}")
            
            service = PoetryPaintingLangGraphService()
            result = service.run(
                user_input=user_input,
                poetry_style=poetry_style,
                poetry_format=poetry_format,
                painting_style=painting_style,
                image_size=image_size,
                history=self._get_conversation_history(conversation)
            )
            
            # 检查是否有错误
            if result.get("error"):
                logger.error(f"创作失败: {result['error']}")
                return StandardResponse.error(
                    message=f"创作失败: {result['error']}",
                    code=500
                )
            
            # 保存作品
            final_output = result.get("final_output", {})
            poetry_data = final_output.get("poetry", {})
            painting_data = final_output.get("painting", {})
            
            work = PoetryPaintingWork.objects.create(
                conversation=conversation,
                poetry_content=poetry_data.get("content", ""),
                poetry_title=poetry_data.get("title", ""),
                poetry_theme=poetry_data.get("theme", user_input),
                poetry_format=poetry_data.get("format", "seven_jueju"),
                poetry_style=poetry_data.get("style", "婉约"),
                poetry_analysis=poetry_data.get("analysis", {}),
                painting_url=painting_data.get("url", ""),
                painting_local_path=painting_data.get("local_path", ""),
                painting_prompt=painting_data.get("prompt", ""),
                painting_style=painting_data.get("style", "chinese_ink"),
                langgraph_state=result,
                iteration_count=result.get("iteration_count", 1)
            )
            
            # 保存助手消息
            response_content = self._format_response_content(final_output)
            PoetryPaintingMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=response_content,
                work=work
            )
            
            # 序列化返回
            work_serializer = PoetryPaintingWorkSerializer(
                work, 
                context={'request': request}
            )
            
            logger.info(f"创作完成 - 作品ID: {work.id}")
            
            return StandardResponse.success(
                data={
                    "work_id": work.id,
                    "conversation_id": conversation.id,
                    "work": work_serializer.data,
                    "result": final_output
                },
                message="创作成功！"
            )
            
        except Exception as e:
            logger.error(f"创作作品异常: {e}", exc_info=True)
            return StandardResponse.error(
                message=f"创作失败: {str(e)}",
                code=500
            )
    
    @action(detail=True, methods=['post'], url_path='iterate')
    def iterate_work(self, request, pk=None):
        """
        迭代优化作品
        
        POST /api/v1/agent/poetry-painting/{id}/iterate/
        """
        try:
            # 验证请求数据
            serializer = IterateWorkRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            feedback = serializer.validated_data['feedback']
            optimize_type = serializer.validated_data.get('type', 'both')
            
            # 获取原作品
            work = get_object_or_404(
                PoetryPaintingWork,
                id=pk,
                conversation__user=request.user
            )
            
            logger.info(f"迭代优化作品 {work.id} - 反馈: {feedback[:50]}")
            
            # 保存用户反馈消息
            PoetryPaintingMessage.objects.create(
                conversation=work.conversation,
                role='user',
                content=f"优化建议: {feedback}"
            )
            
            # 基于反馈重新生成（保持原有尺寸）
            original_size = work.langgraph_state.get("image_size", "1328*1328") if work.langgraph_state else "1328*1328"
            
            service = PoetryPaintingLangGraphService()
            result = service.run(
                user_input=work.poetry_theme,
                poetry_style=work.poetry_style,
                poetry_format=work.poetry_format,
                painting_style=work.painting_style,
                image_size=original_size,
                user_feedback=feedback,
                iteration_count=work.iteration_count + 1,
                history=self._get_conversation_history(work.conversation)
            )
            
            # 检查错误
            if result.get("error"):
                return StandardResponse.error(
                    message=f"优化失败: {result['error']}",
                    code=500
                )
            
            # 创建新版本作品
            final_output = result.get("final_output", {})
            poetry_data = final_output.get("poetry", {})
            painting_data = final_output.get("painting", {})
            
            new_work = PoetryPaintingWork.objects.create(
                conversation=work.conversation,
                poetry_content=poetry_data.get("content", ""),
                poetry_title=poetry_data.get("title", ""),
                poetry_theme=work.poetry_theme,
                poetry_format=work.poetry_format,
                poetry_style=work.poetry_style,
                poetry_analysis=poetry_data.get("analysis", {}),
                painting_url=painting_data.get("url", ""),
                painting_local_path=painting_data.get("local_path", ""),
                painting_prompt=painting_data.get("prompt", ""),
                painting_style=work.painting_style,
                langgraph_state=result,
                iteration_count=work.iteration_count + 1
            )
            
            # 保存助手消息
            response_content = self._format_response_content(final_output)
            PoetryPaintingMessage.objects.create(
                conversation=work.conversation,
                role='assistant',
                content=response_content,
                work=new_work
            )
            
            # 序列化返回
            work_serializer = PoetryPaintingWorkSerializer(
                new_work,
                context={'request': request}
            )
            
            logger.info(f"优化完成 - 新作品ID: {new_work.id}")
            
            return StandardResponse.success(
                data={
                    "work_id": new_work.id,
                    "work": work_serializer.data,
                    "result": final_output
                },
                message="优化成功！"
            )
            
        except Exception as e:
            logger.error(f"迭代优化异常: {e}", exc_info=True)
            return StandardResponse.error(
                message=f"优化失败: {str(e)}",
                code=500
            )
    
    @action(detail=False, methods=['get'], url_path='works')
    def list_works(self, request):
        """
        获取作品列表
        
        GET /api/v1/agent/poetry-painting/works/
        """
        try:
            works = PoetryPaintingWork.objects.filter(
                conversation__user=request.user
            ).order_by('-created_at')[:20]  # 最近20个作品
            
            logger.info(f"查询到 {works.count()} 个作品")
            
            serializer = PoetryPaintingWorkSerializer(
                works, 
                many=True,
                context={'request': request}
            )
            
            logger.info(f"序列化后数据: {len(serializer.data)} 条记录")
            
            return StandardResponse.success(data=serializer.data)
            
        except Exception as e:
            logger.error(f"获取作品列表异常: {e}")
            return StandardResponse.error(message=f"获取失败: {str(e)}")
    
    @action(detail=True, methods=['get'])
    def retrieve_work(self, request, pk=None):
        """获取作品详情"""
        try:
            work = get_object_or_404(
                PoetryPaintingWork,
                id=pk,
                conversation__user=request.user
            )
            
            serializer = PoetryPaintingWorkSerializer(
                work,
                context={'request': request}
            )
            return StandardResponse.success(data=serializer.data)
            
        except Exception as e:
            logger.error(f"获取作品详情异常: {e}")
            return StandardResponse.error(message=f"获取失败: {str(e)}")
    
    @action(detail=True, methods=['post'], url_path='rate')
    def rate_work(self, request, pk=None):
        """评分作品"""
        try:
            serializer = RateWorkRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            rating = serializer.validated_data['rating']
            
            work = get_object_or_404(
                PoetryPaintingWork,
                id=pk,
                conversation__user=request.user
            )
            
            work.user_rating = rating
            work.save()
            
            return StandardResponse.success(
                data={"rating": rating},
                message="评分成功"
            )
            
        except Exception as e:
            logger.error(f"评分异常: {e}")
            return StandardResponse.error(message=f"评分失败: {str(e)}")
    
    @action(detail=False, methods=['get'], url_path='conversations')
    def list_conversations(self, request):
        """获取对话列表"""
        try:
            conversations = PoetryPaintingConversation.objects.filter(
                user=request.user
            ).order_by('-updated_at')
            
            logger.info(f"查询到 {conversations.count()} 个对话")
            
            serializer = PoetryPaintingConversationSerializer(
                conversations,
                many=True,
                context={'request': request}
            )
            
            logger.info(f"序列化后数据: {len(serializer.data)} 条记录")
            if serializer.data:
                logger.info(f"第一条数据: {serializer.data[0]}")
            
            return StandardResponse.success(data=serializer.data)
            
        except Exception as e:
            logger.error(f"获取对话列表异常: {e}", exc_info=True)
            return StandardResponse.error(message=f"获取失败: {str(e)}")

