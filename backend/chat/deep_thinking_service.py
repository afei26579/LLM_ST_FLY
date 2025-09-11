"""
深度思考服务模块
处理深度思考模式的特殊逻辑
"""
import re
import logging

logger = logging.getLogger(__name__)

class DeepThinkingService:
    """深度思考服务类"""
    
    @staticmethod
    def build_deep_thinking_prompt():
        """构建深度思考模式的系统提示词"""
        return """你是一个智能助手，请根据用户的问题提供有帮助的回答。

深度思考模式已启用：
请按照以下格式回答，在回答中明确展示你的思考过程：

<思考过程>
[在这里详细展示你的分析思路，包括：
1. 问题理解和分解
2. 相关知识点梳理
3. 多角度分析
4. 逻辑推理过程
5. 可能的解决方案对比]
</思考过程>

<最终回答>
[基于上述思考过程，给出完整、准确的最终答案]
</最终回答>

要求：
- 思考过程要详细、有逻辑性
- 考虑问题的多个角度和层面
- 包含相关的背景知识和延伸思考
- 最终回答要全面、深入且有条理"""
    
    @staticmethod
    def parse_deep_thinking_response(content):
        """
        解析深度思考模式的回复，提取思考过程和最终回答
        
        Args:
            content: AI回复的完整内容
            
        Returns:
            dict: 包含thinking_process和final_answer的字典
        """
        try:
            # 使用正则表达式提取思考过程和最终回答
            thinking_pattern = r'<思考过程>(.*?)</思考过程>'
            answer_pattern = r'<最终回答>(.*?)</最终回答>'
            
            thinking_match = re.search(thinking_pattern, content, re.DOTALL)
            answer_match = re.search(answer_pattern, content, re.DOTALL)
            
            thinking_process = ""
            final_answer = content  # 默认使用完整内容作为最终回答
            
            if thinking_match:
                thinking_process = thinking_match.group(1).strip()
                
            if answer_match:
                final_answer = answer_match.group(1).strip()
            elif thinking_match:
                # 如果有思考过程但没有最终回答标签，则移除思考过程部分
                final_answer = re.sub(thinking_pattern, '', content, flags=re.DOTALL).strip()
                # 清理可能残留的标签
                final_answer = re.sub(r'</?最终回答>', '', final_answer).strip()
            
            return {
                'thinking_process': thinking_process,
                'final_answer': final_answer,
                'has_structured_response': bool(thinking_match or answer_match)
            }
            
        except Exception as e:
            logger.error(f"解析深度思考回复失败: {str(e)}")
            return {
                'thinking_process': "",
                'final_answer': content,
                'has_structured_response': False
            }
    
    @staticmethod
    def build_web_search_prompt():
        """构建联网搜索模式的系统提示词"""
        return """你是一个智能助手，请根据用户的问题提供有帮助的回答。

联网搜索模式已启用：
- 如果问题涉及最新信息、实时数据或时事，请明确说明需要联网搜索
- 对于可能过时的信息，请提醒用户信息的时效性
- 建议用户查询最新的官方资源或权威网站
- 可以提供相关的搜索关键词或信息源建议"""
    
    @staticmethod
    def build_combined_prompt():
        """构建深度思考+联网搜索的组合提示词"""
        return """你是一个智能助手，请根据用户的问题提供有帮助的回答。

深度思考模式和联网搜索模式已启用：

请按照以下格式回答：

<思考过程>
[详细展示分析思路，包括：
1. 问题理解和分解
2. 相关知识点梳理
3. 多角度分析
4. 是否需要最新信息的判断
5. 逻辑推理过程]
</思考过程>

<最终回答>
[基于思考过程给出完整答案，如需最新信息请明确说明]
</最终回答>

要求：
- 思考过程要详细、有逻辑性
- 如涉及时效性信息，请在思考过程中说明
- 提供权威信息源建议
- 最终回答要全面、准确"""