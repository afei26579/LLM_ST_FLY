"""
AI图像生成服务
处理图像生成的业务逻辑
"""

import os
import uuid
import logging
import requests
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from http import HTTPStatus
from datetime import datetime, timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

import dashscope
from dashscope import ImageSynthesis
from django.db import transaction

from .models import ImageGenerationTask, GeneratedImage, UserImageStats

logger = logging.getLogger(__name__)


class ImageGenerationError(Exception):
    """图像生成异常"""
    pass


class ImageDownloadError(Exception):
    """图像下载异常"""
    pass


class AIImageService:
    """AI图像生成服务类"""
    
    def __init__(self):
        # 设置API密钥
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        
        # 检查API密钥是否配置
        if not settings.DASHSCOPE_API_KEY:
            raise ImageGenerationError("DashScope API密钥未配置")
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        size: str = "1328*1328",
        prompt_extend: bool = True,
        watermark: bool = True,
        style: Optional[str] = None,
        shot_type: Optional[str] = None,
        angle: Optional[str] = None,
        shooting_technique: Optional[str] = None,
        lighting: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            prompt: 正向提示词
            negative_prompt: 反向提示词
            size: 图像尺寸
            prompt_extend: 是否启用智能改写
            watermark: 是否添加水印
            user_id: 用户ID
            
        Returns:
            生成结果字典（固定生成1张图片）
        """
        task = None
        try:
            logger.info(f"开始生成图像，用户ID: {user_id}, 提示词: {prompt[:100]}...")
            
            # 生成任务ID
            task_id = str(uuid.uuid4())
            
            # 创建数据库记录
            if user_id:
                task = self._create_task_record(
                    user_id=user_id,
                    task_id=task_id,
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    size=size,
                    n=1,  # 固定生成1张图片
                    prompt_extend=prompt_extend,
                    watermark=watermark,
                    style=style,
                    shot_type=shot_type,
                    angle=angle,
                    shooting_technique=shooting_technique,
                    lighting=lighting
                )
            
            # 构建请求参数
            params = {
                'model': 'qwen-image',
                'prompt': prompt,
                'n': 1,  # 固定生成1张图片
                'size': size,
                'prompt_extend': prompt_extend,
                'watermark': watermark
            }
            
            # 添加反向提示词
            if negative_prompt and negative_prompt.strip():
                params['negative_prompt'] = negative_prompt.strip()
            
            # 更新任务状态为处理中
            if task:
                task.status = 'processing'
                task.save(update_fields=['status'])
            
            # 调用DashScope API
            logger.info(f"调用DashScope API，参数: {params}")
            response = ImageSynthesis.call(
                api_key=settings.DASHSCOPE_API_KEY,
                **params
            )
            
            logger.info(f"API响应状态: {response.status_code}")
            
            if response.status_code == HTTPStatus.OK:
                # 处理成功响应
                result = self._process_success_response(response, task, user_id)
                logger.info(f"图像生成成功，任务ID: {result.get('task_id')}")
                
                # 更新任务状态为完成
                if task:
                    try:
                        task.status = 'completed'
                        task.completed_at = timezone.now()
                        task.api_request_id = result.get('request_id', '')
                        
                        # 安全地提取usage数据，确保是纯字典类型
                        usage_data = result.get('usage', {})
                        if usage_data and not isinstance(usage_data, dict):
                            try:
                                # 如果不是字典，尝试转换
                                if hasattr(usage_data, '__dict__'):
                                    usage_data = dict(usage_data.__dict__)
                                else:
                                    usage_data = {'raw_data': str(usage_data)}
                            except Exception:
                                usage_data = {}
                        task.api_usage = usage_data
                        
                        task.enhanced_prompt = result.get('enhanced_prompt', prompt)
                        task.save()
                        logger.info(f"任务状态更新为完成: {task.task_id}")
                    except Exception as e:
                        logger.error(f"更新任务状态为完成失败: {str(e)}")
                        logger.error(f"错误详情: {repr(e)}")
                        import traceback
                        logger.error(f"错误堆栈: {traceback.format_exc()}")
                        
                    # 更新用户统计
                    self._update_user_stats(user_id)
                
                return result
            else:
                # 处理失败响应
                error_msg = f"图像生成失败: status_code={response.status_code}, code={response.code}, message={response.message}"
                logger.error(error_msg)
                
                # 更新任务状态为失败
                if task:
                    task.status = 'failed'
                    task.error_message = error_msg
                    task.completed_at = timezone.now()
                    task.save()
                    
                    # 更新用户统计
                    self._update_user_stats(user_id)
                
                raise ImageGenerationError(error_msg)
                
        except Exception as e:
            logger.error(f"图像生成异常: {str(e)}")
            
            # 更新任务状态为失败
            if task:
                task.status = 'failed'
                task.error_message = str(e)
                task.completed_at = timezone.now()
                task.save()
                
                # 更新用户统计
                if user_id:
                    self._update_user_stats(user_id)
            
            if isinstance(e, ImageGenerationError):
                raise
            else:
                raise ImageGenerationError(f"图像生成过程中发生错误: {str(e)}")
    
    def _process_success_response(self, response, task: Optional['ImageGenerationTask'] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        处理成功响应
        
        Args:
            response: API响应
            user_id: 用户ID
            
        Returns:
            处理后的结果
        """
        output = response.output
        task_id = task.task_id if task else output.get('task_id', str(uuid.uuid4()))
        
        # 处理生成的图像
        images = []
        if output.get('results'):
            for result in output['results']:
                try:
                    # 下载并保存图像
                    image_info = self._download_and_save_image(
                        result['url'], 
                        task_id, 
                        user_id
                    )
                    
                    # 添加额外信息
                    image_info.update({
                        'orig_prompt': result.get('orig_prompt', ''),
                        'actual_prompt': result.get('actual_prompt', ''),
                    })
                    
                    images.append(image_info)
                    
                except Exception as e:
                    logger.error(f"处理图像失败: {str(e)}")
                    # 继续处理其他图像，不要因为一张图像失败就整体失败
                    continue
            
            # 如果有任务对象，保存图像记录到数据库
            if task and images:
                try:
                    self._save_generated_images(task, images)
                except Exception as e:
                    logger.error(f"保存图像记录到数据库失败: {str(e)}")
        
        # 安全地提取DashScope响应数据，避免对象类型冲突
        usage_data = {}
        if hasattr(response, 'usage') and response.usage:
            try:
                # 将DashScope usage对象转换为字典
                if hasattr(response.usage, '__dict__'):
                    usage_data = dict(response.usage.__dict__)
                elif isinstance(response.usage, dict):
                    usage_data = dict(response.usage)
                else:
                    usage_data = {'raw_usage': str(response.usage)}
            except Exception as e:
                logger.warning(f"提取usage信息失败: {str(e)}")
                usage_data = {}
        
        request_id = ''
        if hasattr(response, 'request_id'):
            try:
                request_id = str(getattr(response, 'request_id', ''))
            except Exception as e:
                logger.warning(f"提取request_id失败: {str(e)}")
                request_id = ''
        
        return {
            'task_id': task_id,
            'status': output.get('task_status', 'SUCCEEDED'),
            'images': images,
            'usage': usage_data,
            'request_id': request_id,
            'submit_time': output.get('submit_time'),
            'end_time': output.get('end_time'),
        }
    
    def _download_and_save_image(
        self, 
        image_url: str, 
        task_id: str, 
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        下载并保存图像
        
        Args:
            image_url: 图像URL
            task_id: 任务ID
            user_id: 用户ID
            
        Returns:
            图像信息字典
        """
        try:
            logger.info(f"开始下载图像: {image_url}")
            
            # 下载图像
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 获取文件名
            original_filename = PurePosixPath(unquote(urlparse(image_url).path)).parts[-1]
            if not original_filename:
                original_filename = f"{task_id}_{uuid.uuid4().hex[:8]}.png"
            
            # 构建保存路径 - 保存到MEDIA_ROOT/ai-images目录下
            timestamp = datetime.now().strftime('%Y%m%d')
            if user_id:
                save_path = f"ai-images/{user_id}/{timestamp}/{original_filename}"
            else:
                save_path = f"ai-images/anonymous/{timestamp}/{original_filename}"
            
            # 保存图像到存储
            saved_path = default_storage.save(
                save_path, 
                ContentFile(response.content)
            )
            
            # 生成访问URL - 返回完整URL
            if hasattr(default_storage, 'url'):
                saved_url = default_storage.url(saved_path)
            else:
                saved_url = f"/media/{saved_path}"
            
            # 确保返回完整URL（包含域名和端口）
            from django.contrib.sites.shortcuts import get_current_site
            from django.http import HttpRequest
            
            # 如果是相对路径，转换为绝对路径
            if saved_url.startswith('/'):
                # 使用配置的BASE_URL或默认localhost
                base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                saved_url = f"{base_url}{saved_url}"
            
            logger.info(f"图像保存成功: {saved_path}")
            logger.info(f"图像访问URL: {saved_url}")
            
            return {
                'original_url': image_url,
                'saved_path': saved_path,
                'saved_url': saved_url,
                'filename': original_filename,
                'size': len(response.content),
                'download_time': timezone.now().isoformat(),
            }
            
        except requests.RequestException as e:
            error_msg = f"下载图像失败: {str(e)}"
            logger.error(error_msg)
            raise ImageDownloadError(error_msg)
        except Exception as e:
            error_msg = f"保存图像失败: {str(e)}"
            logger.error(error_msg)
            raise ImageDownloadError(error_msg)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态（异步任务）
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        try:
            # 注意：这里假设DashScope支持任务状态查询
            # 实际使用时需要根据API文档调整
            response = ImageSynthesis.fetch(task_id)
            
            if response.status_code == HTTPStatus.OK:
                return {
                    'task_id': task_id,
                    'status': response.output.get('task_status', 'UNKNOWN'),
                    'results': response.output.get('results', []),
                    'submit_time': response.output.get('submit_time'),
                    'end_time': response.output.get('end_time'),
                }
            else:
                raise ImageGenerationError(f"查询任务状态失败: {response.message}")
                
        except Exception as e:
            logger.error(f"查询任务状态异常: {str(e)}")
            raise ImageGenerationError(f"查询任务状态失败: {str(e)}")
    
    def validate_image_params(self, params: Dict[str, Any]) -> None:
        """
        验证图像生成参数
        
        Args:
            params: 参数字典
        """
        # 验证尺寸
        valid_sizes = [
            '1328*1328', '1664*928', '928*1664', 
            '1472*1140', '1140*1472'
        ]
        if params.get('size') not in valid_sizes:
            raise ImageGenerationError(f"不支持的图像尺寸: {params.get('size')}")
        
        # 验证数量
        n = params.get('n', 1)
        if not isinstance(n, int) or n < 1 or n > 4:
            raise ImageGenerationError("图像生成数量必须在1-4之间")
        
        # 验证提示词长度
        prompt = params.get('prompt', '')
        if len(prompt) > 2000:
            raise ImageGenerationError("正向提示词长度不能超过2000字符")
        
        negative_prompt = params.get('negative_prompt', '')
        if negative_prompt and len(negative_prompt) > 1000:
            raise ImageGenerationError("反向提示词长度不能超过1000字符")
    
    def cleanup_expired_images(self, days: int = 30) -> int:
        """
        清理过期图像
        
        Args:
            days: 保留天数
            
        Returns:
            清理的文件数量
        """
        try:
            # 这里可以实现清理逻辑
            # 例如删除超过指定天数的图像文件
            logger.info(f"开始清理{days}天前的图像文件")
            
            # 实际实现时需要遍历存储目录并删除过期文件
            # 这里只是示例
            cleanup_count = 0
            
            logger.info(f"清理完成，共清理{cleanup_count}个文件")
            return cleanup_count
            
        except Exception as e:
            logger.error(f"清理过期图像失败: {str(e)}")
            return 0
    
    def get_user_image_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        获取用户图像生成统计
        
        Args:
            user_id: 用户ID
            days: 统计天数
            
        Returns:
            统计信息
        """
        try:
            # 这里可以实现统计逻辑
            # 例如查询数据库获取用户的生成记录
            
            return {
                'user_id': user_id,
                'total_images': 0,
                'success_count': 0,
                'failed_count': 0,
                'total_size': 0,
                'period_days': days,
            }
            
        except Exception as e:
            logger.error(f"获取用户统计失败: {str(e)}")
            return {}
    
    def _create_task_record(self, user_id: int, task_id: str, **kwargs) -> 'ImageGenerationTask':
        """创建任务记录"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            task = ImageGenerationTask.objects.create(
                user=user,
                task_id=task_id,
                **kwargs
            )
            logger.info(f"创建任务记录成功: {task_id}")
            return task
        except Exception as e:
            logger.error(f"创建任务记录失败: {str(e)}")
            raise
    
    def _save_generated_images(self, task: 'ImageGenerationTask', images_data: List[Dict]) -> List['GeneratedImage']:
        """保存生成的图像记录"""
        saved_images = []
        
        for image_data in images_data:
            try:
                image_record = GeneratedImage.objects.create(
                    task=task,
                    original_url=image_data.get('original_url', ''),
                    saved_path=image_data.get('saved_path', ''),
                    saved_url=image_data.get('saved_url', ''),
                    filename=image_data.get('filename', ''),
                    file_size=image_data.get('size', 0),
                    orig_prompt=image_data.get('orig_prompt', ''),
                    actual_prompt=image_data.get('actual_prompt', ''),
                    download_time=timezone.now(),
                    is_downloaded=True
                )
                saved_images.append(image_record)
                logger.info(f"保存图像记录成功: {image_record.filename}")
                
            except Exception as e:
                logger.error(f"保存图像记录失败: {str(e)}")
                continue
        
        return saved_images
    
    def _update_user_stats(self, user_id: int):
        """更新用户统计数据"""
        if not user_id:
            return
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            user = User.objects.get(id=user_id)
            stats, created = UserImageStats.objects.get_or_create(user=user)
            stats.update_stats()
            logger.info(f"更新用户统计成功: {user.username}")
            
        except Exception as e:
            logger.error(f"更新用户统计失败: {str(e)}")


    def understand_image(self, user, image_file, analyze_type='description') -> Dict[str, Any]:
        """
        图像理解功能
        上传图片，AI分析并描述图像内容
        """
        import tempfile
        import os
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from datetime import datetime
        temp_path = None
        saved_path = None
        
        try:
            logger.info(f"开始图像理解，用户: {user.username}, 文件: {image_file.name}, 分析类型: {analyze_type}")
            
            # 先保存文件到media目录，获得稳定的本地路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_filename = f"temp_understand_{user.id}_{timestamp}_{analyze_type}.jpg"
            save_path = f"temp/{save_filename}"
            
            # 保存到media目录
            saved_path = default_storage.save(save_path, ContentFile(image_file.read()))
            local_path = default_storage.path(saved_path)
            
            logger.info(f"图片已保存到本地: {local_path}")
            
            # 根据分析类型构建不同的提示词
            if analyze_type == 'question':
                text_prompt = '这是一道题目，请仔细分析图片中的问题，请你分步骤解答这道题，输出对这道题的思考判断过程。'
            elif analyze_type == 'ocr':
                text_prompt = '你是一个专门用于识别和提取图像中文本的AI。你的任务是分析图像文档，并使用指定的标签以QwenVL文档解析器的HTML格式生成结果，同时确保用户隐私和数据完整性。'
            else:  # description
                text_prompt = '图中描绘的是什么景象？请详细描述图片的内容，包括主要物体、场景、颜色、构图等信息。'
            
            # 按您建议的格式调用API
            image_path = f"file://{local_path}"
            messages = [
                {
                    'role': 'user',
                    'content': [
                        {'image': image_path},
                        {'text': text_prompt}
                    ]
                }
            ]
            
            # 调用DashScope多模态对话API
            from http import HTTPStatus
            response = dashscope.MultiModalConversation.call(
                model='qwen-vl-plus',
                messages=messages
            )
            
            logger.info(f"DashScope API调用完成，状态码: {response.status_code}")
            
            # 清理临时文件
            if saved_path and default_storage.exists(saved_path):
                default_storage.delete(saved_path)
                logger.info(f"临时文件已清理: {saved_path}")
            
            if response.status_code == HTTPStatus.OK:
                description = response.output.choices[0].message.content
                logger.info(f"图像理解成功({analyze_type})，描述长度: {len(description)}")
                return {
                    'description': description,
                    'confidence': 0.9,
                    'analyze_type': analyze_type
                }
            else:
                error_msg = f"DashScope API调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                # 使用默认描述而不是抛出异常
                return {
                    'description': f'这是一张图片。API调用遇到问题：{response.message}',
                    'confidence': 0.1,
                    'analyze_type': analyze_type
                }
                
        except Exception as e:
            logger.error(f"图像理解失败: {str(e)}")
            
            # 清理临时文件
            if saved_path:
                try:
                    if default_storage.exists(saved_path):
                        default_storage.delete(saved_path)
                        logger.info(f"异常时临时文件已清理: {saved_path}")
                except Exception as cleanup_error:
                    logger.error(f"清理临时文件失败: {cleanup_error}")
            
            # 返回默认描述而不是抛出异常，确保前端不报错
            logger.warning(f"使用默认描述替代API结果")
            return {
                'description': f'这是一张图片，由于技术限制暂时无法提供详细{analyze_type}。错误信息：{str(e)}',
                'confidence': 0.1,
                'analyze_type': analyze_type
            }
    
    def detect_objects(self, user, image_file, detection_prompt) -> Dict[str, Any]:
        """
        物体检测和定位功能
        用户上传图片+提示词，返回标注后的图片
        使用qwen-image-edit模型检测并标注图像中的指定物体
        """
        import os
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from datetime import datetime
        import requests
        import uuid
        saved_path = None
        
        try:
            logger.info(f"=== 开始物体定位 ===")
            logger.info(f"用户: {user.username}")
            logger.info(f"文件: {image_file.name}")
            logger.info(f"提示词: {detection_prompt}")
            
            # 1. 临时保存上传的图片
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_filename = f"temp_detect_{user.id}_{timestamp}.jpg"
            save_path = f"temp/{save_filename}"
            
            saved_path = default_storage.save(save_path, ContentFile(image_file.read()))
            local_path = default_storage.path(saved_path)
            logger.info(f"步骤1: 图片已临时保存到 {local_path}")
            
            # 2. 调用qwen-image-edit模型
            image_path = f"file://{local_path}"
            messages = [
                {
                    'role': 'user',
                    'content': [
                        {'image': image_path},
                        {'text': detection_prompt}  # 直接使用用户的提示词
                    ]
                }
            ]
            
            logger.info(f"步骤2: 调用qwen-image-edit API, 提示词: {detection_prompt}")
            
            from http import HTTPStatus
            response = dashscope.MultiModalConversation.call(
                model='qwen-image-edit',
                messages=messages,
                stream=False
            )
            
            logger.info(f"步骤3: API调用完成，状态码: {response.status_code}")
            
            # 清理上传的临时文件
            if saved_path and default_storage.exists(saved_path):
                default_storage.delete(saved_path)
                logger.info(f"上传临时文件已清理")
            
            if response.status_code == HTTPStatus.OK:
                # 3. 查询qwen-image-edit返回的已标注的图片
                if hasattr(response.output, 'choices') and len(response.output.choices) > 0:
                    content = response.output.choices[0].message.content
                    logger.info(f"API返回内容类型: {type(content)}")
                    
                    annotated_image_url = None
                    description_text = ""
                    
                    # 解析返回内容
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                # 提取标注后的图像URL
                                if 'image' in item:
                                    annotated_image_url = item['image']
                                    logger.info(f"找到标注图像URL: {annotated_image_url}")
                                # 提取文本描述
                                if 'text' in item:
                                    description_text += item['text']
                    elif isinstance(content, str):
                        description_text = content
                    
                    # 4. 下载并保存标注后的图片
                    saved_annotated_url = None
                    if annotated_image_url:
                        try:
                            logger.info(f"步骤4: 开始下载标注图像")
                            
                            # 下载标注图像
                            img_response = requests.get(annotated_image_url, timeout=30)
                            img_response.raise_for_status()
                            
                            # 保存到用户的ai-images目录
                            annotated_filename = f"annotated_{uuid.uuid4().hex[:12]}.jpg"
                            today = datetime.now().strftime('%Y%m%d')
                            annotated_save_path = f"ai-images/{user.id}/{today}/{annotated_filename}"
                            
                            annotated_saved_path = default_storage.save(
                                annotated_save_path,
                                ContentFile(img_response.content)
                            )
                            
                            # 生成可访问的URL
                            saved_annotated_url = default_storage.url(annotated_saved_path)
                            
                            # 确保URL是完整的绝对路径
                            if saved_annotated_url.startswith('/'):
                                # 如果是相对路径，需要加上服务器地址
                                from django.conf import settings
                                base_url = getattr(settings, 'MEDIA_URL_BASE', 'http://localhost:8000')
                                saved_annotated_url = base_url + saved_annotated_url
                            
                            logger.info(f"标注图像已保存: {annotated_saved_path}")
                            logger.info(f"完整访问URL: {saved_annotated_url}")
                            
                        except Exception as download_error:
                            logger.warning(f"下载标注图像失败: {download_error}，使用原始URL")
                            saved_annotated_url = annotated_image_url
                    
                    # 返回给前端渲染
                    logger.info(f"=== 物体定位完成 ===")
                    return {
                        'annotated_image_url': saved_annotated_url or annotated_image_url,  # 标注后的图片
                        'description': description_text or f"已完成{detection_prompt}的物体定位标注",
                        'confidence': 0.9
                    }
                else:
                    logger.warning("API返回内容中没有choices")
                    return {
                        'annotated_image_url': None,
                        'description': f'物体定位完成，但未能生成标注图像',
                        'confidence': 0.5
                    }
            else:
                error_msg = f"qwen-image-edit API调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                return {
                    'annotated_image_url': None,
                    'description': f'物体定位遇到问题：{response.message}',
                    'confidence': 0.1
                }
                
        except Exception as e:
            logger.error(f"物体检测失败: {str(e)}")
            
            # 清理临时文件
            if saved_path:
                try:
                    if default_storage.exists(saved_path):
                        default_storage.delete(saved_path)
                        logger.info(f"异常时临时文件已清理: {saved_path}")
                except Exception as cleanup_error:
                    logger.error(f"清理临时文件失败: {cleanup_error}")
            
            # 返回错误信息
            return {
                'annotated_image_url': None,
                'description': f'物体定位失败: {str(e)}',
                'confidence': 0.1
            }
    
    def _extract_coordinates_from_text(self, text: str, target_object: str) -> List[str]:
        """
        从AI返回的文本中提取坐标信息
        """
        import re
        coordinates = []
        
        try:
            # 多种位置描述模式匹配
            location_patterns = [
                # 坐标格式: "坐标: (x, y)" 或 "位置: (x, y)"
                r'(?:坐标|位置)[：:]\s*\(([^)]+)\)',
                # 百分比位置: "位于图像左上角约25%处"
                r'位于图像([^，。！？\s]+)约?(\d+%?[^，。！？\s]*)',
                # 相对位置: "在图像的左上角" "位于中央" "处于右下方"
                r'(?:在图像的|位于|处于|在)([左右上下中央部]{1,4}[^，。！？\s]*)',
                # 具体物体位置
                fr'{re.escape(target_object)}(?:位于|在|处于)([^，。！？\s]+)',
                # 像素坐标
                r'(?:坐标|位置).*?(\d+,\s*\d+)',
                # 区域描述
                r'(?:左上角|右上角|左下角|右下角|中央|中心|顶部|底部|左侧|右侧)'
            ]
            
            for pattern in location_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    coord_text = match.group(1) if match.groups() else match.group(0)
                    if coord_text and coord_text.strip():
                        coordinates.append(coord_text.strip())
            
            # 如果没有找到具体坐标，但找到了目标物体，提取相关描述
            if not coordinates and target_object in text:
                sentences = re.split(r'[。！？\n]', text)
                for sentence in sentences:
                    if target_object in sentence and len(sentence.strip()) > 0:
                        coordinates.append(sentence.strip())
            
            # 去重
            coordinates = list(dict.fromkeys(coordinates))
            
        except Exception as e:
            logger.error(f"坐标提取失败: {e}")
        
        return coordinates
    
    def edit_image(self, user, image_file, prompt: str, edit_type: str = 'prompt', style: str = '') -> Dict[str, Any]:
        """
        图像编辑功能
        根据提示词对上传的图片进行编辑
        """
        import tempfile
        import os
        temp_path = None
        
        try:
            logger.info(f"开始图像编辑，用户: {user.username}, 编辑类型: {edit_type}")
            
            # 使用tempfile创建临时文件（跨平台兼容）
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # 根据编辑类型构建不同的提示词
            if edit_type == 'background':
                final_prompt = f"保持主体不变，将背景修改为：{prompt}"
            elif edit_type == 'style':
                final_prompt = f"保持主体和场景不变，将整体风格转换为：{style}风格"
            else:  # prompt
                final_prompt = prompt
            
            logger.info(f"最终提示词: {final_prompt}")
            
            # 调用DashScope图像编辑API
            from http import HTTPStatus
            response = dashscope.ImageSynthesis.call(
                model='wanx-v1',
                prompt=final_prompt,
                reference_image=f'file://{temp_path}',
                size='1024*1024',
                n=1
            )
            
            # 清理临时文件
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            
            if response.status_code == HTTPStatus.OK:
                # 处理编辑结果
                output = response.output
                if output.results:
                    edited_url = output.results[0].url
                    
                    logger.info(f"图像编辑成功，原始URL: {edited_url}")
                    
                    # 下载并保存编辑后的图像
                    try:
                        saved_info = self._download_and_save_image(edited_url, response.output.task_id, user.id)
                        logger.info(f"编辑图像已保存: {saved_info['saved_path']}")
                        return {
                            'edited_image_url': saved_info['saved_url'],
                            'task_id': response.output.task_id
                        }
                    except Exception as save_error:
                        logger.warning(f"保存编辑后图像失败: {save_error}")
                        return {
                            'edited_image_url': edited_url,
                            'task_id': response.output.task_id
                        }
                else:
                    raise Exception("编辑结果为空")
            else:
                error_msg = f"DashScope API调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"图像编辑失败: {str(e)}")
            
            # 清理临时文件
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    logger.info(f"异常时临时文件已清理: {temp_path}")
                except Exception as cleanup_error:
                    logger.error(f"清理临时文件失败: {cleanup_error}")
            
            raise Exception(f"图像编辑失败: {str(e)}")


# 创建服务实例
ai_image_service = AIImageService()
