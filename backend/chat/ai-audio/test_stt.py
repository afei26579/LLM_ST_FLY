"""
语音转文字功能测试脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from services import ai_audio_service

User = get_user_model()


def test_speech_to_text():
    """测试语音转文字功能"""
    print("=" * 50)
    print("语音转文字功能测试")
    print("=" * 50)
    
    # 获取第一个用户
    try:
        user = User.objects.first()
        if not user:
            print("❌ 没有找到用户，请先创建用户")
            return
        
        print(f"✓ 使用用户: {user.username}")
        
        # 检查是否有测试音频文件
        test_audio_path = os.path.join(os.path.dirname(__file__), 'test_audio.mp3')
        if not os.path.exists(test_audio_path):
            print(f"\n⚠️  未找到测试音频文件: {test_audio_path}")
            print("请准备一个测试音频文件（MP3、WAV等格式）并命名为 test_audio.mp3")
            print("\n您也可以修改代码中的 test_audio_path 变量指向您的音频文件。")
            return
        
        # 读取音频文件
        with open(test_audio_path, 'rb') as f:
            audio_content = f.read()
        
        # 创建上传文件对象
        audio_file = SimpleUploadedFile(
            name="test_audio.mp3",
            content=audio_content,
            content_type="audio/mpeg"
        )
        
        print(f"\n测试音频文件:")
        print(f"  - 路径: {test_audio_path}")
        print(f"  - 大小: {len(audio_content)} bytes ({len(audio_content)/1024:.2f} KB)")
        
        # 调用服务
        print("\n正在调用 DashScope 语音识别 API...")
        result = ai_audio_service.speech_to_text(
            user_id=user.id,
            audio_file=audio_file,
            language='zh-cn',
            model='qwen-audio-turbo-latest'
        )
        
        # 显示结果
        print("\n✓ 识别成功!")
        print(f"  - 任务ID: {result['task_id']}")
        print(f"  - 识别文本: {result.get('result_text', result.get('text', ''))}")
        print(f"  - 置信度: {result.get('confidence', 0.0)}")
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
    test_speech_to_text()

