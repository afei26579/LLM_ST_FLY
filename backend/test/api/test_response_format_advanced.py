#!/usr/bin/env python
"""
高级响应格式测试脚本
"""
import os
import sys
import django
import json
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.response import StandardResponse
from core.validators import ResponseValidator, ResponseHelper
from core.monitoring import ResponseMonitor
from django.http import HttpRequest
from django.contrib.auth import get_user_model

User = get_user_model()


def test_response_validation():
    """测试响应格式验证"""
    print("🔍 测试响应格式验证...")
    print("=" * 50)
    
    # 测试有效响应
    valid_response = {
        "code": 200,
        "message": "操作成功",
        "data": {"name": "测试"},
        "timestamp": datetime.now().isoformat(),
        "request_id": "test-12345"
    }
    
    result = ResponseValidator.validate_response_format(valid_response)
    print(f"✅ 有效响应验证: {result['is_valid']}")
    if not result['is_valid']:
        print(f"   错误: {result['errors']}")
    
    # 测试无效响应
    invalid_response = {
        "code": "200",  # 错误：应该是整数
        "message": 123,  # 错误：应该是字符串
        "data": {"name": "测试"},
        # 缺少timestamp和request_id
    }
    
    result = ResponseValidator.validate_response_format(invalid_response)
    print(f"❌ 无效响应验证: {result['is_valid']}")
    print(f"   错误: {result['errors']}")
    
    # 测试分页响应
    paginated_response = {
        "code": 200,
        "message": "获取数据成功",
        "data": {
            "list": [{"id": 1, "name": "项目1"}],
            "total": 1,
            "page": 1,
            "page_size": 20
        },
        "timestamp": datetime.now().isoformat(),
        "request_id": "test-12345"
    }
    
    result = ResponseValidator.validate_paginated_response(paginated_response)
    print(f"📄 分页响应验证: {result['is_valid']}")
    if not result['is_valid']:
        print(f"   错误: {result['errors']}")
    
    print()


def test_response_helper():
    """测试响应辅助工具"""
    print("🛠️ 测试响应辅助工具...")
    print("=" * 50)
    
    # 成功响应
    success_response = {
        "code": 200,
        "message": "操作成功",
        "data": {"result": "success"},
        "timestamp": datetime.now().isoformat(),
        "request_id": "test-12345"
    }
    
    print(f"✅ 是否成功响应: {ResponseHelper.is_success_response(success_response)}")
    print(f"📊 响应数据: {ResponseHelper.get_response_data(success_response)}")
    print(f"❌ 错误信息: {ResponseHelper.extract_error_info(success_response)}")
    
    # 错误响应
    error_response = {
        "code": 400,
        "message": "请求参数错误",
        "data": {"field": "username", "error": "用户名不能为空"},
        "timestamp": datetime.now().isoformat(),
        "request_id": "test-12345"
    }
    
    print(f"❌ 是否成功响应: {ResponseHelper.is_success_response(error_response)}")
    error_info = ResponseHelper.extract_error_info(error_response)
    print(f"🚨 错误信息: {error_info}")
    
    # 格式化错误消息
    formatted_message = ResponseHelper.format_error_message(
        400, "请求参数错误", "test-12345"
    )
    print(f"📝 格式化错误消息: {formatted_message}")
    
    print()


def test_response_monitoring():
    """测试响应监控"""
    print("📊 测试响应监控...")
    print("=" * 50)
    
    # 重置统计
    ResponseMonitor.reset_stats()
    
    # 记录一些响应
    responses = [
        {"code": 200, "message": "成功", "data": {}, "timestamp": datetime.now().isoformat(), "request_id": "req-1"},
        {"code": 200, "message": "成功", "data": {}, "timestamp": datetime.now().isoformat(), "request_id": "req-2"},
        {"code": 400, "message": "错误", "data": {}, "timestamp": datetime.now().isoformat(), "request_id": "req-3"},
        {"code": 500, "message": "服务器错误", "data": {}, "timestamp": datetime.now().isoformat(), "request_id": "req-4"},
    ]
    
    endpoints = ["/api/users/", "/api/users/", "/api/login/", "/api/data/"]
    
    for i, response in enumerate(responses):
        ResponseMonitor.record_response(
            response_data=response,
            endpoint=endpoints[i],
            user_id=1,
            duration=100 + i * 50
        )
    
    # 获取统计信息
    stats = ResponseMonitor.get_stats()
    print(f"📈 总响应数: {stats['total_responses']}")
    print(f"✅ 成功响应数: {stats['success_responses']}")
    print(f"❌ 错误响应数: {stats['error_responses']}")
    print(f"🚨 格式错误数: {stats['format_errors']}")
    print(f"⏱️ 平均响应时间: {stats['avg_response_time']:.2f}ms")
    
    # 获取健康状态
    health = ResponseMonitor.get_health_status()
    print(f"🏥 系统状态: {health['status']}")
    print(f"📊 成功率: {health['success_rate']:.2f}%")
    print(f"⚠️ 错误率: {health['error_rate']:.2f}%")
    
    print()


def test_standard_response_methods():
    """测试StandardResponse的所有方法"""
    print("🧪 测试StandardResponse方法...")
    print("=" * 50)
    
    # 测试成功响应
    success_resp = StandardResponse.success(
        data={"user_id": 1, "username": "admin"},
        message="获取用户信息成功",
        request_id="test-success"
    )
    print(f"✅ 成功响应状态码: {success_resp.status_code}")
    print(f"   响应数据: {success_resp.data}")
    
    # 测试错误响应
    error_resp = StandardResponse.error(
        message="用户不存在",
        code=404,
        data={"user_id": 999},
        request_id="test-error"
    )
    print(f"❌ 错误响应状态码: {error_resp.status_code}")
    print(f"   响应数据: {error_resp.data}")
    
    # 创建模拟序列化器
    class MockSerializer:
        def __init__(self, data, many=False, context=None):
            if many:
                self.data = data
            else:
                self.data = data
    
    # 测试分页响应
    paginated_resp = StandardResponse.paginated_success(
        queryset_or_page=[{"id": 1, "name": "项目1"}, {"id": 2, "name": "项目2"}],
        serializer_class=MockSerializer,
        message="获取项目列表成功",
        request_id="test-paginated"
    )
    print(f"📄 分页响应状态码: {paginated_resp.status_code}")
    print(f"   响应数据: {paginated_resp.data}")
    
    # 测试单对象响应
    single_resp = StandardResponse.single_success(
        instance={"id": 1, "name": "项目1"},
        serializer_class=MockSerializer,
        message="获取项目详情成功",
        request_id="test-single"
    )
    print(f"📋 单对象响应状态码: {single_resp.status_code}")
    print(f"   响应数据: {single_resp.data}")
    
    print()


def test_error_scenarios():
    """测试各种错误场景"""
    print("🚨 测试错误场景...")
    print("=" * 50)
    
    error_scenarios = [
        {"code": 400, "message": "请求参数错误", "data": {"field": "username"}},
        {"code": 401, "message": "未授权访问", "data": None},
        {"code": 403, "message": "权限不足", "data": {"required_permission": "admin"}},
        {"code": 404, "message": "资源不存在", "data": {"resource_id": 123}},
        {"code": 500, "message": "服务器内部错误", "data": {"error_id": "ERR_001"}},
    ]
    
    for scenario in error_scenarios:
        resp = StandardResponse.error(
            message=scenario["message"],
            code=scenario["code"],
            data=scenario["data"],
            request_id=f"test-{scenario['code']}"
        )
        print(f"[{scenario['code']}] {scenario['message']}")
        print(f"   HTTP状态码: {resp.status_code}")
        print(f"   响应格式验证: {ResponseValidator.validate_response_format(resp.data)['is_valid']}")
    
    print()


def run_comprehensive_tests():
    """运行综合测试"""
    print("🎯 运行综合响应格式测试套件")
    print("=" * 80)
    
    test_response_validation()
    test_response_helper()
    test_response_monitoring()
    test_standard_response_methods()
    test_error_scenarios()
    
    print("🎉 所有测试完成！")
    print("=" * 80)


if __name__ == "__main__":
    run_comprehensive_tests()