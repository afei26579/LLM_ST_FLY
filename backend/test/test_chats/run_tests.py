#!/usr/bin/env python
import os
import sys
import django
from django.test.runner import DiscoverRunner

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)
print(f"添加项目根目录到PYTHONPATH: {project_root}")

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
print(f"设置DJANGO_SETTINGS_MODULE为: {os.environ['DJANGO_SETTINGS_MODULE']}")

try:
    django.setup()
    print("Django环境初始化成功")
except Exception as e:
    print(f"Django环境初始化失败: {str(e)}")
    sys.exit(1)

def run_tests():
    """
    运行聊天相关的测试用例
    """
    print("开始运行聊天模块测试用例...")
    
    # 运行指定的测试用例
    test_runner = DiscoverRunner(verbosity=2)
    failures = test_runner.run_tests([
        'test_chats.test_conversations',
        'test_chats.test_chat_completion'
    ])
    
    if failures:
        print(f"测试失败! {failures}个测试用例未通过.")
        sys.exit(1)
    else:
        print("所有测试用例通过!")
        sys.exit(0)

if __name__ == '__main__':
    run_tests() 