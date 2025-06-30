import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# 首先导入测试配置
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    import conftest
except ImportError:
    print("无法导入conftest模块")

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from chat.models import Conversation, Message

User = get_user_model()

class ChatCompletionAPITestCase(TestCase):
    """
    测试聊天完成API
    """
    
    def setUp(self):
        """
        测试前的准备工作
        """
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        
        # 创建测试客户端
        self.client = APIClient()
        
        # 创建测试对话
        self.conversation = Conversation.objects.create(
            user=self.user,
            title="测试对话"
        )
        
        # 登录用户
        self.client.force_authenticate(user=self.user)
    
    @patch('chat.views.ChatCompletionView.call_dashscope_api')
    def test_chat_completion_new_conversation(self, mock_api_call):
        """
        测试聊天完成API - 创建新对话
        """
        # 模拟API调用的返回值
        mock_api_call.return_value = {
            'content': '你好！我是AI助手，很高兴为你服务。',
            'usage': {
                'total_tokens': 20,
                'input_tokens': 10,
                'output_tokens': 10
            }
        }
        
        # 准备请求数据
        url = '/api/v1/chat/completion/'
        data = {
            'messages': [
                {
                    'role': 'user',
                    'content': '你好，这是一个测试消息'
                }
            ]
        }
        
        # 发送请求
        response = self.client.post(url, data, format='json')
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '成功')
        self.assertIn('data', data)
        
        # 检查返回的数据
        self.assertEqual(data['data']['content'], '你好！我是AI助手，很高兴为你服务。')
        self.assertIn('usage', data['data'])
        self.assertIn('conversation_id', data['data'])
        
        # 验证是否调用了AI API
        mock_api_call.assert_called_once()
        
        # 验证是否创建了新对话
        self.assertEqual(Conversation.objects.count(), 2)
        
        # 验证是否创建了新消息
        new_conversation = Conversation.objects.exclude(id=self.conversation.id).first()
        self.assertEqual(Message.objects.filter(conversation=new_conversation).count(), 2)
    
    @patch('chat.views.ChatCompletionView.call_dashscope_api')
    def test_chat_completion_existing_conversation(self, mock_api_call):
        """
        测试聊天完成API - 使用现有对话
        """
        # 模拟API调用的返回值
        mock_api_call.return_value = {
            'content': '这是AI的回复。',
            'usage': {
                'total_tokens': 15,
                'input_tokens': 5,
                'output_tokens': 10
            }
        }
        
        # 准备请求数据
        url = '/api/v1/chat/completion/'
        data = {
            'messages': [
                {
                    'role': 'user',
                    'content': '这是一个测试问题'
                }
            ],
            'conversation_id': self.conversation.id
        }
        
        # 发送请求
        response = self.client.post(url, data, format='json')
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '成功')
        
        # 检查返回的数据
        self.assertEqual(data['data']['content'], '这是AI的回复。')
        self.assertEqual(data['data']['conversation_id'], self.conversation.id)
        
        # 验证是否调用了AI API
        mock_api_call.assert_called_once()
        
        # 验证是否在现有对话中添加了消息
        self.assertEqual(Message.objects.filter(conversation=self.conversation).count(), 2)
    
    def test_chat_completion_invalid_request(self):
        """
        测试聊天完成API - 无效请求
        """
        # 准备请求数据 - 空消息列表
        url = '/api/v1/chat/completion/'
        data = {
            'messages': []
        }
        
        # 发送请求
        response = self.client.post(url, data, format='json')
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        data = response.json()
        self.assertEqual(data['code'], 400)
        self.assertEqual(data['message'], '消息不能为空')
    
    def test_chat_completion_nonexistent_conversation(self):
        """
        测试聊天完成API - 不存在的对话
        """
        # 准备请求数据 - 使用不存在的对话ID
        url = '/api/v1/chat/completion/'
        data = {
            'messages': [
                {
                    'role': 'user',
                    'content': '测试消息'
                }
            ],
            'conversation_id': 9999  # 不存在的对话ID
        }
        
        # 发送请求
        response = self.client.post(url, data, format='json')
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        data = response.json()
        self.assertEqual(data['code'], 404)
        self.assertIn('对话不存在', data['message'])
    
    def test_unauthorized_access(self):
        """
        测试未授权访问
        """
        # 创建未登录客户端
        client = APIClient()
        
        # 准备请求数据
        url = '/api/v1/chat/completion/'
        data = {
            'messages': [
                {
                    'role': 'user',
                    'content': '测试消息'
                }
            ]
        }
        
        # 发送请求
        response = client.post(url, data, format='json')
        
        # 检查响应状态码是否为401未授权
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    # 如果要单独运行此测试文件，取消以下注释并运行此脚本
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner()
    test_runner.run_tests(['test_chats.test_chat_completion']) 