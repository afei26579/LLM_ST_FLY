#!/usr/bin/env python
"""
测试用户管理API的字段命名
验证前端需要的驼峰命名字段是否正确返回
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

def test_user_api():
    """测试用户管理API"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== 用户管理API字段测试 ===\n")
    
    # 1. 获取管理员用户和token
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            print("❌ 没有找到超级用户")
            return
        
        token, created = Token.objects.get_or_create(user=admin_user)
        headers = {'Authorization': f'Token {token.key}'}
        print(f"✅ 使用管理员用户: {admin_user.username}")
        print(f"✅ Token: {token.key}\n")
        
    except Exception as e:
        print(f"❌ Token创建失败: {e}")
        return
    
    # 2. 测试用户列表API
    print("2. 测试用户列表API")
    try:
        response = requests.get(f"{base_url}/api/v1/auth/user-management/", headers=headers)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功获取用户列表")
            
            if 'data' in data and 'list' in data['data']:
                users = data['data']['list']
                print(f"用户数量: {len(users)}")
                
                if users:
                    user = users[0]
                    print(f"\n📋 第一个用户的字段:")
                    print(f"  - id: {user.get('id')}")
                    print(f"  - username: {user.get('username')}")
                    print(f"  - email: {user.get('email')}")
                    print(f"  - is_active (下划线): {user.get('is_active')}")
                    print(f"  - isActive (驼峰): {user.get('isActive')}")
                    print(f"  - date_joined (下划线): {user.get('date_joined')}")
                    print(f"  - createdAt (驼峰): {user.get('createdAt')}")
                    print(f"  - role (角色信息): {user.get('role')}")
                    
                    # 检查关键字段
                    if 'isActive' in user:
                        print(f"✅ 驼峰命名字段 'isActive' 存在: {user['isActive']}")
                    else:
                        print(f"❌ 驼峰命名字段 'isActive' 不存在")
                    
                    if 'createdAt' in user:
                        print(f"✅ 驼峰命名字段 'createdAt' 存在: {user['createdAt']}")
                    else:
                        print(f"❌ 驼峰命名字段 'createdAt' 不存在")
                    
                    if 'role' in user and user['role']:
                        print(f"✅ 角色信息存在: {user['role']}")
                    else:
                        print(f"❌ 角色信息不存在或为空")
                        
            else:
                print("❌ 响应格式不正确，缺少data.list字段")
        else:
            print(f"❌ 请求失败: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 用户列表API测试失败: {e}")
    
    print("\n" + "="*50)
    
    # 3. 测试用户状态更新API
    print("\n3. 测试用户状态更新API")
    try:
        # 获取一个非管理员用户进行测试
        test_user = User.objects.filter(is_superuser=False).first()
        if test_user:
            original_status = test_user.is_active
            new_status = not original_status
            
            print(f"测试用户: {test_user.username}")
            print(f"原始状态: {original_status}")
            print(f"新状态: {new_status}")
            
            # 使用驼峰命名发送请求
            response = requests.patch(
                f"{base_url}/api/v1/auth/user-management/{test_user.id}/status/",
                headers=headers,
                json={'isActive': new_status}
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 状态更新成功")
                
                if 'data' in data:
                    user_data = data['data']
                    print(f"返回的is_active: {user_data.get('is_active')}")
                    print(f"返回的isActive: {user_data.get('isActive')}")
                    
                    if user_data.get('isActive') == new_status:
                        print(f"✅ 驼峰命名字段更新正确")
                    else:
                        print(f"❌ 驼峰命名字段更新错误")
                
                # 恢复原始状态
                requests.patch(
                    f"{base_url}/api/v1/auth/user-management/{test_user.id}/status/",
                    headers=headers,
                    json={'isActive': original_status}
                )
                print(f"✅ 已恢复原始状态")
                
            else:
                print(f"❌ 状态更新失败: {response.text[:200]}...")
        else:
            print("❌ 没有找到测试用户")
            
    except Exception as e:
        print(f"❌ 用户状态更新API测试失败: {e}")

if __name__ == "__main__":
    test_user_api()