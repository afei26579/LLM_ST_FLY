#!/usr/bin/env python
"""
调试用户管理API的响应
查看实际的API响应内容
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

def debug_user_api():
    """调试用户管理API"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== 调试用户管理API响应 ===\n")
    
    # 获取管理员用户和token
    admin_user = User.objects.filter(is_superuser=True).first()
    token, created = Token.objects.get_or_create(user=admin_user)
    headers = {'Authorization': f'Token {token.key}'}
    
    # 测试用户列表API
    print("1. 原始API响应:")
    response = requests.get(f"{base_url}/api/v1/auth/user-management/", headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应头: {dict(response.headers)}")
    print(f"原始响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    print("\n" + "="*50)
    
    # 检查数据库中的用户信息
    print("\n2. 数据库中的用户信息:")
    for user in User.objects.all():
        print(f"用户: {user.username}")
        print(f"  - ID: {user.id}")
        print(f"  - is_active: {user.is_active}")
        print(f"  - date_joined: {user.date_joined}")
        print(f"  - user_role: {user.user_role}")
        if user.user_role:
            print(f"    - 角色ID: {user.user_role.id}")
            print(f"    - 角色名称: {user.user_role.name}")
            print(f"    - 角色描述: {user.user_role.description}")
        print()

if __name__ == "__main__":
    debug_user_api()