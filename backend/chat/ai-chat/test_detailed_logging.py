#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Chat 详细日志功能测试脚本

专门用于测试新增的详细日志记录功能
"""

import os
import sys
import django

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from chat.models import Conversation, Message

# 由于目录名包含连字符，需要使用相对导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services import AIChatService

User = get_user_model()


def test_detailed_logging():
    """测试详细日志记录功能"""
    print("🚀 开始 AI Chat 详细日志测试")
    print("=" * 60)
    
    # 创建测试用户和对话
    user, created = User.objects.get_or_create(
        username='detailed_log_test_user',
        defaults={'email': 'test@example.com', 'is_active': True}
    )
    
    conversation, created = Conversation.objects.get_or_create(
        user=user,
        title="详细日志测试对话"
    )
    
    # 创建AI Chat服务实例
    service = AIChatService()
    
    print(f"✅ 测试环境准备完成")
    print(f"   用户: {user.username}")
    print(f"   对话ID: {conversation.id}")
    print()
    
    # 测试1: 基础聊天（观察详细日志）
    print("🧪 测试1: 基础聊天功能（观察详细日志）")
    print("-" * 50)
    
    test_message = "请简单介绍一下你自己，不需要太长"
    print(f"📤 发送消息: {test_message}")
    print()
    
    try:
        result = service.process_message(
            conversation=conversation,
            user_message=test_message,
            user=user,
            deep_thinking=False,
            web_search=False
        )
        
        print(f"✅ 测试1 完成")
        print(f"   AI回复长度: {len(result['ai_message']['content'])} 字符")
        print(f"   处理时间: {result['processing_time']} 秒")
        print()
        
    except Exception as e:
        print(f"❌ 测试1 失败: {str(e)}")
        print()
    
    # 测试2: 深度思考模式（观察更详细的日志）
    print("🧪 测试2: 深度思考模式（观察更详细的日志）")
    print("-" * 50)
    
    deep_test_message = "请分析一下编程语言的发展趋势"
    print(f"📤 发送消息: {deep_test_message}")
    print()
    
    try:
        result = service.process_message(
            conversation=conversation,
            user_message=deep_test_message,
            user=user,
            deep_thinking=True,
            web_search=False
        )
        
        print(f"✅ 测试2 完成")
        print(f"   AI回复长度: {len(result['ai_message']['content'])} 字符")
        print(f"   处理时间: {result['processing_time']} 秒")
        print()
        
    except Exception as e:
        print(f"❌ 测试2 失败: {str(e)}")
        print()
    
    # 清理测试数据
    try:
        print("🧹 清理测试数据...")
        Message.objects.filter(conversation=conversation).delete()
        conversation.delete()
        user.delete()
        print("✅ 测试数据清理完成")
    except Exception as e:
        print(f"⚠️ 清理测试数据时出错: {str(e)}")
    
    print()
    print("🏁 详细日志测试完成！")
    print("💡 注意观察上面的详细日志输出，包括:")
    print("   - 方法调用的开始和结束")
    print("   - 输入参数的详细信息")
    print("   - AI模型选择和参数配置")
    print("   - 消息历史的构建过程")
    print("   - AI服务调用的详细过程")
    print("   - AI回复的完整内容")
    print("   - 数据库操作的详细记录")
    print("   - 错误处理和重试机制")


if __name__ == "__main__":
    test_detailed_logging()
