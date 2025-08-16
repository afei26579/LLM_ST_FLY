"""
AI服务模块
处理不同的AI功能模式
"""
import dashscope
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class AIService:
    """AI服务类"""
    
    def __init__(self):
        # 设置API密钥
        dashscope.api_key = settings.DASHSCOPE_API_KEY
    
    def generate_response(self, messages, deep_thinking=False, web_search=False):
        """
        生成AI回复
        
        Args:
            messages: 对话历史消息列表
            deep_thinking: 是否启用深度思考模式
            web_search: 是否启用联网搜索模式
        
        Returns:
            AI回复内容
        """
        try:
            # 构建系统提示
            system_prompt = self._build_system_prompt(deep_thinking, web_search)
            
            # 构建完整的消息列表
            full_messages = [
                {"role": "system", "content": system_prompt}
            ] + messages
            
            # 选择合适的模型
            model = self._select_model(deep_thinking, web_search)
            
            # 调用API
            response = dashscope.Generation.call(
                model=model,
                messages=full_messages,
                result_format='message',
                temperature=0.7 if deep_thinking else 0.5,
                max_tokens=2000 if deep_thinking else 1500
            )
            
            if response.status_code == 200:
                return response.output.choices[0].message.content
            else:
                logger.error(f"DashScope API调用失败: {response}")
                return "抱歉，我现在无法回答您的问题，请稍后再试。"
                
        except Exception as e:
            logger.error(f"AI服务调用异常: {str(e)}")
            return "抱歉，服务暂时不可用，请稍后再试。"
    
    def _build_system_prompt(self, deep_thinking=False, web_search=False):
        """构建系统提示词"""
        base_prompt = "你是一个智能助手，请根据用户的问题提供有帮助的回答。"
        
        if deep_thinking:
            base_prompt += """
            
深度思考模式已启用：
- 请对问题进行深入分析，考虑多个角度和层面
- 提供更全面、更深入的回答
- 可以包含相关的背景知识和延伸思考
- 回答要有逻辑性和条理性
- 适当时可以提出进一步的思考方向"""
        
        if web_search:
            base_prompt += """
            
联网搜索模式已启用：
- 如果问题涉及最新信息、实时数据或时事，请明确说明需要联网搜索
- 对于可能过时的信息，请提醒用户信息的时效性
- 建议用户查询最新的官方资源或权威网站
- 可以提供相关的搜索关键词或信息源建议"""
        
        return base_prompt
    
    def _select_model(self, deep_thinking=False, web_search=False):
        """根据功能模式选择合适的模型"""
        if deep_thinking:
            # 深度思考模式使用更强的模型
            return 'qwen-plus'
        elif web_search:
            # 联网搜索模式使用标准模型
            return 'qwen-turbo'
        else:
            # 默认模式
            return 'qwen-turbo'
    
    def simulate_web_search(self, query):
        """
        模拟联网搜索功能
        注意：这是一个模拟实现，实际项目中需要集成真实的搜索API
        """
        return f"[模拟搜索结果] 关于'{query}'的搜索结果将在这里显示。实际部署时需要集成真实的搜索API。"