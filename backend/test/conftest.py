"""
测试配置文件
"""
import os
import sys
import django

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"已添加项目根目录到PYTHONPATH: {project_root}")

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
print(f"设置DJANGO_SETTINGS_MODULE为: {os.environ.get('DJANGO_SETTINGS_MODULE')}")

# 初始化Django
try:
    django.setup()
    print("Django环境初始化成功")
except Exception as e:
    print(f"Django环境初始化失败: {str(e)}")
    raise

print(f"当前Python路径: {sys.path}") 