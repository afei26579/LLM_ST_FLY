"""
文字转语音功能测试脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from services import ai_audio_service

User = get_user_model()


def test_text_to_speech():
    """测试文字转语音功能"""
    print("=" * 50)
    print("文字转语音功能测试")
    print("=" * 50)
    
    # 获取第一个用户（或创建测试用户）
    try:
        user = User.objects.first()
        if not user:
            print("❌ 没有找到用户，请先创建用户")
            return
        
        print(f"✓ 使用用户: {user.username}")
        
        # 测试文本
        test_text = "你好，这是一个文字转语音的测试。"
        test_voice = "Cherry"
        test_language = "Chinese"
        
        print(f"\n测试参数:")
        print(f"  - 文本: {test_text}")
        print(f"  - 音色: {test_voice}")
        print(f"  - 语言: {test_language}")
        
        # 调用服务
        print("\n正在调用 DashScope API...")
        result = ai_audio_service.text_to_speech(
            user_id=user.id,
            text=test_text,
            voice=test_voice,
            language_type=test_language,
            format='wav'
        )
        
        # 显示结果
        print("\n✓ 生成成功!")
        print(f"  - 任务ID: {result['task_id']}")
        print(f"  - 音频URL: {result['audio_url']}")
        print(f"  - 音频ID: {result.get('audio_id', 'N/A')}")
        print(f"  - 过期时间: {result.get('expires_at', 'N/A')}")
        print(f"  - 状态: {result['status']}")
        print(f"  - 使用量: {result.get('usage', {})}")
        
        print("\n" + "=" * 50)
        print("测试完成!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_text_to_speech()

