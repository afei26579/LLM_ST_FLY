#!/usr/bin/env python
"""
测试用户状态更新功能
验证前端发送的字段名是否与后端匹配
"""

import os
import sys
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_user_status_update():
    """测试用户状态更新"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== 用户状态更新测试 ===\n")
    
    # 获取管理员用户和token
    admin_user = User.objects.filter(is_superuser=True).first()
    token, created = Token.objects.get_or_create(user=admin_user)
    headers = {'Authorization': f'Token {token.key}'}
    
    # 创建一个测试用户
    test_user = User.objects.create_user(
        username='test_status_user',
        email='test@example.com',
        password='testpass123',
        is_active=True
    )
    
    print(f"✅ 创建测试用户: {test_user.username} (ID: {test_user.id})")
    print(f"初始状态: is_active = {test_user.is_active}")
    
    try:
        # 测试状态更新 - 停用用户
        print("\n1. 测试停用用户")
        response = requests.patch(
            f"{base_url}/api/v1/auth/user-management/{test_user.id}/status/",
            headers=headers,
            json={'is_active': False}
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 停用成功")
            print(f"返回数据中的is_active: {data.get('data', {}).get('is_active')}")
            
            # 验证数据库中的状态
            test_user.refresh_from_db()
            print(f"数据库中的is_active: {test_user.is_active}")
            
            if test_user.is_active == False:
                print("✅ 数据库状态更新正确")
            else:
                print("❌ 数据库状态更新错误")
        else:
            print(f"❌ 停用失败: {response.text}")
        
        # 测试状态更新 - 激活用户
        print("\n2. 测试激活用户")
        response = requests.patch(
            f"{base_url}/api/v1/auth/user-management/{test_user.id}/status/",
            headers=headers,
            json={'is_active': True}
        )
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 激活成功")
            print(f"返回数据中的is_active: {data.get('data', {}).get('is_active')}")
            
            # 验证数据库中的状态
            test_user.refresh_from_db()
            print(f"数据库中的is_active: {test_user.is_active}")
            
            if test_user.is_active == True:
                print("✅ 数据库状态更新正确")
            else:
                print("❌ 数据库状态更新错误")
        else:
            print(f"❌ 激活失败: {response.text}")
            
    finally:
        # 清理测试用户
        test_user.delete()
        print(f"\n🧹 已删除测试用户: {test_user.username}")

if __name__ == "__main__":
    test_user_status_update()