"""
绘画生成服务
使用 qwen-image-plus 模型（异步调用）
"""
import logging
import os
import time
import uuid
from http import HTTPStatus
from typing import Dict, Any
from django.conf import settings
import dashscope
from dashscope import ImageSynthesis
import requests
from .prompts import PAINTING_STYLE_DESCRIPTIONS, PAINTING_PROMPT_TEMPLATE, PAINTING_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class PaintingService:
    """绘画生成服务"""
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        dashscope.api_key = self.api_key
        self.media_root = settings.MEDIA_ROOT
        self.media_url = settings.MEDIA_URL
    
    def build_painting_prompt(
        self, 
        poetry_content: str, 
        imagery_description: str, 
        painting_style: str = "chinese_ink"
    ) -> str:
        """
        构建绘画提示词
        
        Args:
            poetry_content: 诗词内容
            imagery_description: 意境描述
            painting_style: 绘画风格
            
        Returns:
            绘画提示词
        """
        try:
            # 获取风格描述
            style_desc = PAINTING_STYLE_DESCRIPTIONS.get(
                painting_style, 
                PAINTING_STYLE_DESCRIPTIONS["chinese_ink"]
            )
            
            # 构建提示词生成请求
            prompt_request = PAINTING_PROMPT_TEMPLATE.format(
                poetry_content=poetry_content,
                imagery_description=imagery_description,
                painting_style=style_desc
            )
            
            logger.info(f"构建绘画提示词 - 风格: {painting_style}")
            
            # 使用AI优化提示词
            response = dashscope.Generation.call(
                model='qwen-max',
                messages=[
                    {"role": "system", "content": PAINTING_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_request}
                ],
                temperature=0.7,
                result_format='message'
            )
            
            if response.status_code == 200:
                optimized_prompt = response.output.choices[0].message.content.strip()
                
                # 添加风格描述
                final_prompt = f"{optimized_prompt}。{style_desc}"
                
                logger.info(f"绘画提示词生成成功: {final_prompt[:100]}...")
                return final_prompt
            else:
                # 如果优化失败，使用基础提示词
                logger.warning(f"提示词优化失败，使用基础提示词: {response.message}")
                return f"{imagery_description}。{style_desc}"
                
        except Exception as e:
            logger.error(f"构建绘画提示词异常: {e}")
            # 返回基础提示词
            return f"{imagery_description}。{PAINTING_STYLE_DESCRIPTIONS.get(painting_style, '')}"
    
    def generate_image(
        self, 
        prompt: str, 
        painting_style: str = "chinese_ink",
        size: str = "1024*1024"
    ) -> Dict[str, Any]:
        """
        生成图像（异步调用）
        使用 qwen-image-plus 模型
        
        Args:
            prompt: 绘画提示词
            painting_style: 绘画风格
            size: 图像尺寸
            
        Returns:
            包含图像URL和本地路径的字典
        """
        try:
            logger.info(f"开始生成图像（异步）- 模型: qwen-image-plus, 风格: {painting_style}")
            logger.info(f"提示词: {prompt[:200]}")
            
            # 创建异步任务 - 使用 async_call
            logger.info("创建异步图像生成任务...")
            logger.info(f"任务参数 - size: {size}, prompt长度: {len(prompt)}")
            
            task_response = ImageSynthesis.async_call(
                api_key=self.api_key,
                model='qwen-image-plus',
                prompt=prompt,
                size=size,
                n=1  # 生成1张图片
            )
            
            if task_response.status_code != HTTPStatus.OK:
                error_msg = f"创建异步任务失败: {task_response.code} - {task_response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            logger.info(f"异步任务已创建 - Task ID: {task_response.output.task_id}")
            
            # 等待异步任务完成
            logger.info("等待异步任务完成...")
            response = ImageSynthesis.wait(task_response)
            
            logger.info(f"任务完成 - 状态码: {response.status_code}")
            logger.info(f"完整响应: {response}")
            
            if response.status_code == HTTPStatus.OK:
                # 检查输出是否存在
                if not hasattr(response, 'output'):
                    error_msg = f"响应中没有output字段: {response}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                logger.info(f"响应输出类型: {type(response.output)}")
                logger.info(f"响应输出内容: {response.output}")
                
                # 检查task_status
                if hasattr(response.output, 'task_status'):
                    logger.info(f"任务状态: {response.output.task_status}")
                    if response.output.task_status != 'SUCCEEDED':
                        error_msg = f"任务未成功: {response.output.task_status}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                
                # 安全获取图像URL
                if not hasattr(response.output, 'results'):
                    error_msg = f"响应输出中没有results字段: {response.output}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                if not response.output.results or len(response.output.results) == 0:
                    error_msg = f"results列表为空: {response.output.results}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                
                # 获取图像URL
                logger.info(f"results数量: {len(response.output.results)}")
                image_url = response.output.results[0].url
                
                logger.info(f"图像生成成功 - URL: {image_url}")
                
                # 下载并保存图像
                local_path = self._download_and_save_image(image_url, painting_style)
                
                return {
                    "url": image_url,
                    "local_path": local_path,
                    "style": painting_style,
                    "size": size,
                    "task_id": task_response.output.task_id
                }
            else:
                error_msg = f"图像生成失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"图像生成异常: {e}")
            raise
    
    def _download_and_save_image(self, image_url: str, painting_style: str) -> str:
        """
        下载并保存图像到本地
        
        Args:
            image_url: 图像URL
            painting_style: 绘画风格
            
        Returns:
            本地相对路径
        """
        try:
            # 生成文件名
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())[:8]
            filename = f"poetry_painting_{painting_style}_{timestamp}_{unique_id}.png"
            
            # 构建保存路径
            relative_path = os.path.join('ai-images', 'poetry-painting', filename)
            full_path = os.path.join(self.media_root, relative_path)
            
            # 确保目录存在
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 下载图像
            logger.info(f"下载图像: {image_url}")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # 保存到本地
            with open(full_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图像保存成功: {relative_path}")
            
            return relative_path
            
        except Exception as e:
            logger.error(f"图像下载保存失败: {e}")
            # 返回空路径，使用远程URL
            return ""
    
    def refine_painting(
        self, 
        original_prompt: str, 
        feedback: str,
        painting_style: str = "chinese_ink",
        size: str = "1328*1328"
    ) -> Dict[str, Any]:
        """
        根据反馈优化绘画
        
        Args:
            original_prompt: 原始提示词
            feedback: 用户反馈
            painting_style: 绘画风格
            size: 图像尺寸
            
        Returns:
            新生成的图像信息
        """
        try:
            # 构建优化提示词
            refined_prompt = f"{original_prompt}。用户要求：{feedback}"
            
            logger.info(f"优化绘画 - 反馈: {feedback}, 尺寸: {size}")
            
            # 重新生成图像
            return self.generate_image(
                prompt=refined_prompt,
                painting_style=painting_style,
                size=size
            )
            
        except Exception as e:
            logger.error(f"绘画优化异常: {e}")
            raise

