#!/usr/bin/env python
"""
测试统一返回格式的脚本
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.response import StandardResponse
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from users.serializers import UserSerializer

User = get_user_model()

def test_response_formats():
    """测试不同类型的响应格式"""
    print("🧪 测试统一返回格式...")
    print("=" * 50)
    
    # 创建模拟请求
    request = HttpRequest()
    request.request_id = "test-12345"
    
    # 1. 测试成功响应
    print("1️⃣ 测试成功响应:")
    success_response = StandardResponse.success(
        data={"name": "张三", "age": 25},
        message="获取用户信息成功",
        request_id="test-12345"
    )
    print(f"状态码: {success_response.status_code}")
    print(f"响应数据: {success_response.data}")
    print()
    
    # 2. 测试错误响应
    print("2️⃣ 测试错误响应:")
    error_response = StandardResponse.error(
        message="用户不存在",
        code=404,
        data={"field": "user_id", "message": "用户ID无效"},
        request_id="test-12345"
    )
    print(f"状态码: {error_response.status_code}")
    print(f"响应数据: {error_response.data}")
    print()
    
    # 3. 测试分页响应
    print("3️⃣ 测试分页响应:")
    
    # 创建模拟序列化器
    class MockSerializer:
        def __init__(self, data, many=False, context=None):
            self.data = data if many else [data]
    
    # 模拟分页数据
    mock_data = [{"id": 1, "name": "用户1"}, {"id": 2, "name": "用户2"}]
    
    paginated_response = StandardResponse.paginated_success(
        queryset_or_page=mock_data,
        serializer_class=MockSerializer,
        message="获取用户列表成功",
        request_id="test-12345"
    )
    print(f"状态码: {paginated_response.status_code}")
    print(f"响应数据: {paginated_response.data}")
    print()
    
    # 4. 测试单对象响应
    print("4️⃣ 测试单对象响应:")
    
    # 模拟单个对象数据
    mock_user = {"id": 1, "username": "admin", "email": "admin@example.com"}
    
    single_response = StandardResponse.single_success(
        instance=mock_user,
        serializer_class=MockSerializer,
        message="获取用户详情成功",
        request_id="test-12345"
    )
    print(f"状态码: {single_response.status_code}")
    print(f"响应数据: {single_response.data}")
    print()
    
    print("✅ 所有测试完成！")

if __name__ == "__main__":
    test_response_formats()