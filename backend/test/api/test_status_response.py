"""
测试用户状态接口的统一响应格式
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import User

class UserStatusResponseTest(APITestCase):
    """测试用户状态接口响应格式"""
    
    def setUp(self):
        """设置测试数据"""
        # 创建管理员用户
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # 创建普通用户
        self.normal_user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # 登录管理员
        self.client.force_authenticate(user=self.admin_user)
    
    def test_user_status_update_response_format(self):
        """测试用户状态更新接口的响应格式"""
        url = f'/api/v1/auth/user-management/{self.normal_user.id}/status/'
        data = {'is_active': False}
        
        response = self.client.patch(url, data, format='json')
        
        # 检查HTTP状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 检查响应格式
        response_data = response.json()
        
        # 验证统一响应格式的字段
        self.assertIn('code', response_data)
        self.assertIn('message', response_data)
        self.assertIn('data', response_data)
        self.assertIn('timestamp', response_data)
        self.assertIn('request_id', response_data)
        
        # 验证具体值
        self.assertEqual(response_data['code'], 200)
        self.assertIn('禁用', response_data['message'])
        self.assertIsNotNone(response_data['data'])
        self.assertIsInstance(response_data['timestamp'], str)
        self.assertIsInstance(response_data['request_id'], str)
        
        # 验证用户数据
        user_data = response_data['data']
        self.assertEqual(user_data['id'], self.normal_user.id)
        self.assertEqual(user_data['is_active'], False)
    
    def test_user_status_update_error_response_format(self):
        """测试用户状态更新接口错误响应格式"""
        url = f'/api/v1/auth/user-management/{self.normal_user.id}/status/'
        data = {}  # 缺少is_active字段
        
        response = self.client.patch(url, data, format='json')
        
        # 检查HTTP状态码
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 检查响应格式
        response_data = response.json()
        
        # 验证统一响应格式的字段
        self.assertIn('code', response_data)
        self.assertIn('message', response_data)
        self.assertIn('data', response_data)
        self.assertIn('timestamp', response_data)
        self.assertIn('request_id', response_data)
        
        # 验证具体值
        self.assertEqual(response_data['code'], 400)
        self.assertIn('is_active', response_data['message'])
        self.assertIsInstance(response_data['timestamp'], str)
        self.assertIsInstance(response_data['request_id'], str)

    def test_response_format_consistency(self):
        """测试响应格式的一致性"""
        # 测试成功响应
        url = f'/api/v1/auth/user-management/{self.normal_user.id}/status/'
        data = {'is_active': True}
        
        response = self.client.patch(url, data, format='json')
        response_data = response.json()
        
        # 验证响应格式符合StandardResponse规范
        expected_keys = {'code', 'message', 'data', 'timestamp', 'request_id'}
        actual_keys = set(response_data.keys())
        
        self.assertEqual(expected_keys, actual_keys, 
                        f"响应格式不符合规范。期望: {expected_keys}, 实际: {actual_keys}")
        
        # 验证数据类型
        self.assertIsInstance(response_data['code'], int)
        self.assertIsInstance(response_data['message'], str)
        self.assertIsInstance(response_data['timestamp'], str)
        self.assertIsInstance(response_data['request_id'], str)

if __name__ == '__main__':
    print("用户状态接口响应格式测试")
    print("=" * 50)
    
    # 模拟响应格式示例
    success_response_example = {
        "code": 200,
        "message": "用户已禁用",
        "data": {
            "id": 1,
            "username": "testuser",
            "email": "test@test.com",
            "is_active": False,
            # ... 其他用户字段
        },
        "timestamp": "2024-01-01T12:00:00.000000",
        "request_id": "uuid-string"
    }
    
    error_response_example = {
        "code": 400,
        "message": "请提供is_active字段",
        "data": None,
        "timestamp": "2024-01-01T12:00:00.000000",
        "request_id": "uuid-string"
    }
    
    print("成功响应示例:")
    print(json.dumps(success_response_example, indent=2, ensure_ascii=False))
    print("\n错误响应示例:")
    print(json.dumps(error_response_example, indent=2, ensure_ascii=False))