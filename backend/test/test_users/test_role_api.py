#!/usr/bin/env python
"""
角色管理API测试脚本
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
from users.models import Role
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_role_management():
    """测试角色管理功能"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== 角色管理API测试 ===\n")
    
    # 1. 测试数据库中的角色数据
    print("1. 数据库中的角色数据")
    try:
        roles = Role.objects.all()
        print(f"数据库中角色数量: {roles.count()}")
        for role in roles:
            users_count = role.users.count()
            print(f"  - {role.code}: {role.name} (用户数: {users_count}, 系统角色: {role.is_system})")
    except Exception as e:
        print(f"数据库查询失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 测试用户角色关系
    print("2. 用户角色关系")
    try:
        users = User.objects.all()
        print(f"用户总数: {users.count()}")
        for user in users:
            role_name = user.user_role.name if user.user_role else "未分配"
            old_role = getattr(user, 'role_str', '无')
            print(f"  - {user.username}: 新角色={role_name}, 旧角色字段={old_role}")
    except Exception as e:
        print(f"用户查询失败: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 创建测试token并测试认证API
    print("3. 创建测试token并测试认证API")
    try:
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            token, created = Token.objects.get_or_create(user=admin_user)
            print(f"管理员用户: {admin_user.username}")
            print(f"Token: {token.key}")
            
            # 使用token测试角色API
            headers = {'Authorization': f'Token {token.key}'}
            response = requests.get(f"{base_url}/api/v1/auth/roles/", headers=headers)
            print(f"带认证的角色API状态码: {response.status_code}")
            if response.status_code == 200:
                response_data = response.json()
                print(f"API响应数据: {response_data}")
                
                # 检查响应格式
                if isinstance(response_data, dict) and 'data' in response_data:
                    data = response_data['data']
                    if isinstance(data, dict) and 'list' in data:
                        # 标准分页响应格式
                        roles = data['list']
                        print(f"分页信息: 总数={data.get('total', '未知')}, 当前页={data.get('page', '未知')}")
                    elif isinstance(data, list):
                        # 数据直接是列表
                        roles = data
                    else:
                        roles = data
                elif isinstance(response_data, dict) and 'results' in response_data:
                    # DRF分页响应格式
                    roles = response_data['results']
                elif isinstance(response_data, list):
                    # 直接列表格式
                    roles = response_data
                else:
                    roles = response_data
                
                print(f"成功获取角色列表，数量: {len(roles) if isinstance(roles, list) else '未知'}")
                
                if isinstance(roles, list):
                    for role in roles:
                        if isinstance(role, dict):
                            print(f"  - {role.get('code', '未知')}: {role.get('name', '未知')} (系统角色: {role.get('is_system', '未知')})")
                        else:
                            print(f"  - 角色数据格式异常: {role}")
                else:
                    print(f"角色数据不是列表格式: {type(roles)}")
            else:
                print(f"认证后仍然失败: {response.text[:200]}...")
        else:
            print("没有找到超级用户")
    except Exception as e:
        print(f"Token测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_role_management()