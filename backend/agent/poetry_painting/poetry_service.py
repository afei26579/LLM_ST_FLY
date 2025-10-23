"""
诗词生成服务
"""
import logging
import json
import re
from typing import Dict, Any, Optional
from django.conf import settings
import dashscope
from .prompts import (
    POETRY_SYSTEM_PROMPT,
    POETRY_CREATION_TEMPLATE,
    POETRY_FORMAT_DESCRIPTIONS
)

logger = logging.getLogger(__name__)


class PoetryService:
    """诗词生成服务"""
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        dashscope.api_key = self.api_key
    
    def generate_poetry(
        self, 
        theme: str, 
        style: str = "婉约", 
        format_type: str = "seven_jueju",
        additional_requirements: str = ""
    ) -> Dict[str, Any]:
        """
        生成诗词
        
        Args:
            theme: 主题
            style: 风格（豪放/婉约/田园/边塞/山水）
            format_type: 格式类型
            additional_requirements: 额外要求
            
        Returns:
            包含诗词内容、标题等的字典
        """
        try:
            # 构建提示词
            format_desc = POETRY_FORMAT_DESCRIPTIONS.get(format_type, "")
            prompt = POETRY_CREATION_TEMPLATE.format(
                theme=theme,
                style=style,
                format_type=format_desc,
                additional_requirements=additional_requirements or "无特殊要求"
            )
            
            logger.info(f"开始生成诗词 - 主题: {theme}, 风格: {style}, 格式: {format_type}")
            
            # 调用通义千问API
            response = dashscope.Generation.call(
                model='qwen-max',
                messages=[
                    {"role": "system", "content": POETRY_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                top_p=0.9,
                result_format='message'
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                
                # 解析响应
                parsed_result = self._parse_poetry_response(content)
                
                logger.info(f"诗词生成成功 - 标题: {parsed_result.get('title', '无标题')}")
                
                return {
                    "content": parsed_result["content"],
                    "title": parsed_result.get("title", ""),
                    "format": format_type,
                    "style": style,
                    "theme": theme,
                    "creation_note": parsed_result.get("note", "")
                }
            else:
                error_msg = f"诗词生成失败: {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"诗词生成异常: {e}")
            raise
    
    def _parse_poetry_response(self, content: str) -> Dict[str, str]:
        """
        解析诗词响应内容
        
        Args:
            content: AI返回的原始内容
            
        Returns:
            解析后的结构化数据
        """
        result = {
            "title": "",
            "content": "",
            "note": ""
        }
        
        # 尝试提取标题
        title_match = re.search(r'标题[：:]\s*([^\n]+)', content)
        if title_match:
            result["title"] = title_match.group(1).strip()
        else:
            # 尝试提取《》中的标题
            title_match = re.search(r'《([^》]+)》', content)
            if title_match:
                result["title"] = title_match.group(1).strip()
        
        # 提取诗词正文
        # 移除标题行、创作说明等，只保留诗句
        lines = content.split('\n')
        poetry_lines = []
        
        in_poetry = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 跳过标题行
            if '标题' in line or line.startswith('《'):
                continue
            
            # 跳过创作说明
            if '创作说明' in line or '说明' in line:
                # 提取说明内容
                note_match = re.search(r'[创作]*说明[：:]\s*(.+)', line)
                if note_match:
                    result["note"] = note_match.group(1).strip()
                break
            
            # 判断是否为诗句（一般包含标点符号或纯中文）
            if re.search(r'[\u4e00-\u9fff，。、；！？]', line):
                poetry_lines.append(line)
        
        result["content"] = '\n'.join(poetry_lines)
        
        # 如果没有提取到内容，使用原始内容
        if not result["content"]:
            result["content"] = content.strip()
        
        return result
    
    def refine_poetry(
        self, 
        original_content: str, 
        feedback: str,
        original_title: str = ""
    ) -> Dict[str, Any]:
        """
        根据反馈优化诗词
        
        Args:
            original_content: 原诗词内容
            feedback: 用户反馈
            original_title: 原标题
            
        Returns:
            优化后的诗词
        """
        try:
            prompt = f"""请根据用户反馈优化以下诗词：

原作品：
标题：{original_title or "无题"}
{original_content}

用户反馈：{feedback}

请保持原有风格和格式，根据反馈进行针对性优化。
输出优化后的作品（包含标题和正文）。"""

            response = dashscope.Generation.call(
                model='qwen-max',
                messages=[
                    {"role": "system", "content": POETRY_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                result_format='message'
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                parsed_result = self._parse_poetry_response(content)
                
                return {
                    "content": parsed_result["content"],
                    "title": parsed_result.get("title", original_title),
                    "note": parsed_result.get("note", "")
                }
            else:
                raise Exception(f"诗词优化失败: {response.message}")
                
        except Exception as e:
            logger.error(f"诗词优化异常: {e}")
            raise

