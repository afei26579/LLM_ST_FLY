"""
诗词分析服务
"""
import logging
import json
from typing import Dict, Any
from django.conf import settings
import dashscope
from .prompts import ANALYSIS_SYSTEM_PROMPT, POETRY_ANALYSIS_TEMPLATE

logger = logging.getLogger(__name__)


class AnalysisService:
    """诗词分析服务"""
    
    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY
        dashscope.api_key = self.api_key
    
    def analyze_poetry(self, poetry_content: str, poetry_title: str = "") -> Dict[str, Any]:
        """
        分析诗词的意境、意象、修辞等
        
        Args:
            poetry_content: 诗词内容
            poetry_title: 诗词标题
            
        Returns:
            分析结果字典
        """
        try:
            # 构建分析提示词
            prompt = POETRY_ANALYSIS_TEMPLATE.format(
                title=poetry_title or "无题",
                content=poetry_content
            )
            
            logger.info(f"开始分析诗词: {poetry_title or poetry_content[:20]}")
            
            # 调用API进行分析
            response = dashscope.Generation.call(
                model='qwen-max',
                messages=[
                    {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 较低温度确保分析准确性
                result_format='message'
            )
            
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                
                # 解析JSON响应
                analysis_result = self._parse_analysis_response(content)
                
                logger.info(f"诗词分析完成 - 意象数量: {len(analysis_result.get('imagery', []))}")
                
                return analysis_result
            else:
                error_msg = f"诗词分析失败: {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"诗词分析异常: {e}")
            # 返回默认分析结果
            return self._get_default_analysis(poetry_content)
    
    def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """
        解析分析响应
        
        Args:
            content: AI返回的内容
            
        Returns:
            结构化的分析结果
        """
        try:
            # 尝试提取JSON内容
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            
            if json_match:
                json_str = json_match.group(0)
                analysis = json.loads(json_str)
                
                # 确保所有必需字段存在
                result = {
                    "imagery": analysis.get("imagery", []),
                    "emotion": analysis.get("emotion", "未知"),
                    "rhetoric": analysis.get("rhetoric", []),
                    "allusion": analysis.get("allusion", []),
                    "imagery_description": analysis.get("imagery_description", "")
                }
                
                return result
            else:
                # 如果没有JSON格式，尝试从文本中提取
                return self._extract_from_text(content)
                
        except json.JSONDecodeError as e:
            logger.warning(f"JSON解析失败，尝试文本提取: {e}")
            return self._extract_from_text(content)
        except Exception as e:
            logger.error(f"解析分析响应异常: {e}")
            return self._get_default_analysis("")
    
    def _extract_from_text(self, content: str) -> Dict[str, Any]:
        """
        从文本中提取分析内容
        
        Args:
            content: 文本内容
            
        Returns:
            分析结果
        """
        result = {
            "imagery": [],
            "emotion": "",
            "rhetoric": [],
            "allusion": [],
            "imagery_description": ""
        }
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 提取意象
            if '意象' in line:
                result["imagery"].append({"name": line, "meaning": ""})
            
            # 提取情感
            if '情感' in line or '基调' in line:
                result["emotion"] = line
            
            # 提取修辞
            if '修辞' in line or '手法' in line:
                result["rhetoric"].append(line)
            
            # 提取画面描述
            if '画面' in line or '描述' in line:
                result["imagery_description"] += line + " "
        
        # 如果没有提取到画面描述，使用整个内容
        if not result["imagery_description"]:
            result["imagery_description"] = content
        
        return result
    
    def _get_default_analysis(self, poetry_content: str) -> Dict[str, Any]:
        """
        获取默认分析结果
        
        Args:
            poetry_content: 诗词内容
            
        Returns:
            默认分析结果
        """
        return {
            "imagery": [
                {"name": "诗词意象", "meaning": "待分析"}
            ],
            "emotion": "意境深远",
            "rhetoric": ["对仗", "用典"],
            "allusion": [],
            "imagery_description": f"诗词描绘的意境画面：{poetry_content[:50]}..."
        }
    
    def generate_painting_description(
        self, 
        poetry_content: str, 
        analysis: Dict[str, Any],
        painting_style: str
    ) -> str:
        """
        基于诗词分析生成绘画描述
        
        Args:
            poetry_content: 诗词内容
            analysis: 诗词分析结果
            painting_style: 绘画风格
            
        Returns:
            适合AI绘画的提示词
        """
        # 提取关键意象
        imagery_names = [img.get("name", "") for img in analysis.get("imagery", [])]
        imagery_str = "、".join(imagery_names) if imagery_names else "诗词意境"
        
        # 情感基调
        emotion = analysis.get("emotion", "意境深远")
        
        # 基础画面描述
        base_description = analysis.get("imagery_description", poetry_content)
        
        # 构建完整描述
        description = f"{base_description}。主要元素：{imagery_str}。情感氛围：{emotion}。"
        
        return description

