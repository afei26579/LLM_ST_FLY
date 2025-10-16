from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .services import ai_reading_service
from .models import Document, DocumentAnalysis, QAHistory
import json


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_history(request):
    """获取用户的文档历史（仅返回已分析的文档）"""
    try:
        # 获取所有已分析的用户文档，按上传时间倒序
        # 使用 distinct() 去重，基于文档 ID（每个文档 ID 唯一）
        documents = Document.objects.filter(
            documentaccess__user=request.user,
            documentanalysis__isnull=False  # 只返回已分析的文档
        ).distinct().order_by('-upload_time')[:20]  # 最多返回20个文档
        
        document_list = []
        for doc in documents:
            # 获取该文档的分析结果（使用 document 对象直接查询，确保一一对应）
            try:
                analysis = doc.documentanalysis  # 使用反向关系，一对一关系
                
                document_list.append({
                    'id': doc.id,
                    'name': doc.name,
                    'size': doc.size,
                    'created_at': doc.upload_time.isoformat(),
                    'file_object_id': doc.file_object_id,
                    'has_analysis': True,  # 已过滤，全部都是已分析的
                    'summary': analysis.summary if analysis else None
                })
            except DocumentAnalysis.DoesNotExist:
                # 理论上不会发生，因为已经过滤了有分析的文档
                print(f"警告：文档 {doc.id} 没有分析结果")
                continue
        
        return Response({
            'success': True,
            'documents': document_list
        })
        
    except Exception as e:
        print(f"获取文档历史失败: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """上传文件并返回文档信息"""
    try:
        if 'file' not in request.FILES:
            return Response({'error': '没有上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        file_content = uploaded_file.read()
        
        # 获取文件信息
        file_info = {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.content_type or '',
            'last_modified': getattr(uploaded_file, 'last_modified', 0)
        }
        
        print(f"=== 文件上传请求 ===")
        print(f"用户: {request.user.username}")
        print(f"文件名: {file_info['name']}")
        print(f"文件大小: {file_info['size']}")
        print(f"文件类型: {file_info['type']}")
        print(f"==================")
        
        # 保存或获取文档
        document, is_new = ai_reading_service.save_or_get_document(
            user=request.user,
            file_content=file_content,
            filename=file_info['name'],
            file_size=file_info['size'],
            file_type=file_info['type'],
            last_modified=file_info['last_modified']
        )
        
        return Response({
            'file_id': document.file_object_id,
            'document_id': document.id,
            'is_new': is_new,
            'message': '文件上传成功' if is_new else '使用已存在的文档'
        })
        
    except Exception as e:
        print(f"文件上传失败: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_document(request):
    """分析文档"""
    try:
        data = json.loads(request.body)
        file_id = data.get('file_id')
        
        if not file_id:
            return Response({'error': '缺少file_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找文档
        try:
            document = Document.objects.get(file_object_id=file_id, user=request.user)
        except Document.DoesNotExist:
            return Response({'error': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        print(f"=== 开始分析文档 ===")
        print(f"用户: {request.user.username}")
        print(f"文档: {document.name}")
        print(f"file_object_id: {file_id}")
        
        # 检查是否已有分析结果
        existing_analysis = ai_reading_service.get_document_analysis(document)
        if existing_analysis:
            print("使用已存在的分析结果")
            return Response({
                'analysis': {
                    'summary': existing_analysis.summary,
                    'keyPoints': existing_analysis.key_points,
                    'keywords': existing_analysis.keywords,
                    'entities': existing_analysis.entities,
                    'suggestedQuestions': existing_analysis.suggested_questions
                },
                'message': '使用已存在的分析结果'
            })
        
        # 进行新的分析
        analysis_result = ai_reading_service.analyze_document_content(file_id)
        
        # 保存分析结果
        analysis = ai_reading_service.save_analysis_result(document, analysis_result)
        
        print("文档分析完成并保存")
        print(f"==================")
        
        return Response({
            'analysis': {
                'summary': analysis.summary,
                'keyPoints': analysis.key_points,
                'keywords': analysis.keywords,
                'entities': analysis.entities,
                'suggestedQuestions': analysis.suggested_questions
            },
            'message': '文档分析完成'
        })
        
    except Exception as e:
        print(f"文档分析失败: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_analysis(request):
    """完整分析（上传+分析一体化，但使用数据库存储）"""
    try:
        data = json.loads(request.body)
        file_id = data.get('file_id')
        
        if not file_id:
            return Response({'error': '缺少file_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找文档
        try:
            document = Document.objects.get(file_object_id=file_id, user=request.user)
        except Document.DoesNotExist:
            return Response({'error': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        print(f"=== 完整分析请求 ===")
        print(f"用户: {request.user.username}")
        print(f"文档: {document.name}")
        print(f"file_object_id: {file_id}")
        
        # 检查是否已有分析结果
        existing_analysis = ai_reading_service.get_document_analysis(document)
        if existing_analysis:
            print("使用已存在的分析结果")
            return Response({
                'analysis': {
                    'summary': existing_analysis.summary,
                    'keyPoints': existing_analysis.key_points,
                    'keywords': existing_analysis.keywords,
                    'entities': existing_analysis.entities,
                    'suggestedQuestions': existing_analysis.suggested_questions
                },
                'message': '使用已存在的分析结果'
            })
        
        # 进行新的分析
        analysis_result = ai_reading_service.analyze_document_content(file_id)
        
        # 保存分析结果
        analysis = ai_reading_service.save_analysis_result(document, analysis_result)
        
        print("完整分析完成并保存")
        print(f"==================")
        
        return Response({
            'analysis': {
                'summary': analysis.summary,
                'keyPoints': analysis.key_points,
                'keywords': analysis.keywords,
                'entities': analysis.entities,
                'suggestedQuestions': analysis.suggested_questions
            },
            'message': '完整分析完成'
        })
        
    except Exception as e:
        print(f"完整分析失败: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_question(request):
    """基于文档进行问答"""
    try:
        data = json.loads(request.body)
        file_id = data.get('file_id')
        question = data.get('question')
        
        if not file_id or not question:
            return Response({'error': '缺少file_id或question参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找文档
        try:
            document = Document.objects.get(file_object_id=file_id, user=request.user)
        except Document.DoesNotExist:
            return Response({'error': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        print(f"=== 问答请求 ===")
        print(f"用户: {request.user.username}")
        print(f"文档: {document.name}")
        print(f"问题: {question}")
        
        # 进行问答
        answer = ai_reading_service.ask_question_about_document(file_id, question)
        
        # 保存问答历史
        qa = ai_reading_service.save_qa_history(document, question, answer)
        
        print(f"问答完成并保存")
        print(f"===============")
        
        return Response({
            'answer': answer,
            'question': question,
            'timestamp': qa.created_time.isoformat(),
            'message': '问答完成'
        })
        
    except Exception as e:
        print(f"问答失败: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_qa_history(request):
    """获取问答历史"""
    try:
        file_id = request.GET.get('file_id')
        limit = int(request.GET.get('limit', 20))
        
        if not file_id:
            return Response({'error': '缺少file_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 查找文档
        try:
            document = Document.objects.get(file_object_id=file_id, user=request.user)
        except Document.DoesNotExist:
            return Response({'error': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取问答历史
        qa_history = ai_reading_service.get_qa_history(document, limit)
        
        history_data = [
            {
                'question': qa.question,
                'answer': qa.answer,
                'timestamp': qa.created_time.isoformat()
            }
            for qa in qa_history
        ]
        
        return Response({
            'history': history_data,
            'total': len(history_data)
        })
        
    except Exception as e:
        print(f"获取问答历史失败: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_documents(request):
    """获取用户的文档列表"""
    try:
        limit = int(request.GET.get('limit', 50))
        document_id = request.GET.get('document_id')  # 支持按 document_id 查询单个文档
        
        # 如果指定了 document_id，只返回该文档
        if document_id:
            try:
                doc = Document.objects.get(id=document_id, user=request.user)
                documents = [doc]
            except Document.DoesNotExist:
                return Response({
                    'error': '文档不存在或无权访问'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            documents = ai_reading_service.get_user_documents(request.user, limit)
        
        documents_data = []
        for doc in documents:
            # 直接通过反向关系获取分析结果，确保一一对应
            try:
                analysis = doc.documentanalysis  # 使用一对一反向关系
                has_analysis = True
                analysis_data = {
                    'summary': analysis.summary,
                    'keyPoints': analysis.key_points,
                    'keywords': analysis.keywords,
                    'entities': analysis.entities,
                    'suggestedQuestions': analysis.suggested_questions
                }
            except DocumentAnalysis.DoesNotExist:
                has_analysis = False
                analysis_data = None
            
            documents_data.append({
                'id': doc.id,
                'name': doc.name,
                'size': doc.size,
                'file_type': doc.file_type,
                'file_object_id': doc.file_object_id,
                'upload_time': doc.upload_time.isoformat(),
                'has_analysis': has_analysis,
                'analysis': analysis_data
            })
        
        return Response({
            'documents': documents_data,
            'total': len(documents_data)
        })
        
    except Exception as e:
        print(f"获取用户文档失败: {e}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_stats(request):
    """获取用户统计信息"""
    try:
        stats = ai_reading_service.get_document_stats(request.user)
        return Response(stats)
        
    except Exception as e:
        print(f"获取统计信息失败: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)