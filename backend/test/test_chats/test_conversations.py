import os
import sys
import json

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

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)
print(f"添加项目根目录到PYTHONPATH: {project_root}")

from chat.models import Conversation, Message

User = get_user_model()

class ConversationAPITestCase(TestCase):
    """
    测试对话相关API
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
        
        # 创建几个测试对话
        self.conversation1 = Conversation.objects.create(
            user=self.user,
            title="测试对话1"
        )
        
        self.conversation2 = Conversation.objects.create(
            user=self.user,
            title="测试对话2"
        )
        
        # 添加消息到第一个对话
        Message.objects.create(
            conversation=self.conversation1,
            role="user",
            content="你好，这是一个测试消息"
        )
        
        Message.objects.create(
            conversation=self.conversation1,
            role="assistant",
            content="你好！我是AI助手，很高兴为你服务。",
            tokens_used=20
        )
        
        # 登录用户
        self.client.force_authenticate(user=self.user)
    
    def test_list_conversations(self):
        """
        测试获取对话列表
        """
        url = '/api/v1/chat/conversations/'
        response = self.client.get(url)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '成功')
        self.assertIn('data', data)
        
        # 检查返回的对话数量
        self.assertEqual(len(data['data']), 2)
        
        # 检查对话字段
        for conversation in data['data']:
            self.assertIn('id', conversation)
            self.assertIn('title', conversation)
            self.assertIn('created_at', conversation)
            self.assertIn('updated_at', conversation)
            self.assertIn('message_count', conversation)
    
    def test_create_conversation(self):
        """
        测试创建新对话
        """
        url = '/api/v1/chat/conversations/'
        data = {
            'title': '新创建的测试对话'
        }
        response = self.client.post(url, data, format='json')
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        data = response.json()
        self.assertEqual(data['code'], 201)  # 创建成功返回201
        self.assertEqual(data['message'], '对话创建成功')
        self.assertIn('data', data)
        
        # 检查创建的对话
        self.assertEqual(data['data']['title'], '新创建的测试对话')
        
        # 验证数据库中的对话数量
        self.assertEqual(Conversation.objects.count(), 3)
    
    def test_get_conversation_detail(self):
        """
        测试获取单个对话详情
        """
        url = f'/api/v1/chat/conversations/{self.conversation1.id}/'
        response = self.client.get(url)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '成功')
        self.assertIn('data', data)
        
        # 检查对话信息
        self.assertEqual(data['data']['id'], self.conversation1.id)
        self.assertEqual(data['data']['title'], '测试对话1')
        
        # 检查消息列表
        self.assertIn('messages', data['data'])
        self.assertEqual(len(data['data']['messages']), 2)
        
        # 检查消息内容
        messages = data['data']['messages']
        self.assertEqual(messages[0]['role'], 'user')
        self.assertEqual(messages[0]['content'], '你好，这是一个测试消息')
        self.assertEqual(messages[1]['role'], 'assistant')
        self.assertEqual(messages[1]['content'], '你好！我是AI助手，很高兴为你服务。')
    
    def test_delete_conversation(self):
        """
        测试删除对话
        """
        url = f'/api/v1/chat/conversations/{self.conversation2.id}/'
        response = self.client.delete(url)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertEqual(data['message'], '对话删除成功')
        
        # 验证数据库中的对话数量
        self.assertEqual(Conversation.objects.count(), 1)
        
        # 验证对话已被删除
        with self.assertRaises(Conversation.DoesNotExist):
            Conversation.objects.get(id=self.conversation2.id)
    
    def test_clear_conversation_messages(self):
        """
        测试清空对话消息
        """
        url = f'/api/v1/chat/conversations/{self.conversation1.id}/clear_messages/'
        response = self.client.delete(url)
        
        # 检查响应状态码
        self.assertEqual(response.status_code, 200)
        
        # 检查响应格式
        data = response.json()
        self.assertEqual(data['code'], 200)
        self.assertIn('对话消息已清空', data['message'])
        
        # 验证对话中的消息数量
        self.assertEqual(Message.objects.filter(conversation=self.conversation1).count(), 0)
    
    def test_unauthorized_access(self):
        """
        测试未授权访问
        """
        # 创建未登录客户端
        client = APIClient()
        
        url = '/api/v1/chat/conversations/'
        response = client.get(url)
        
        # 检查响应状态码是否为401未授权
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    #如果要单独运行此测试文件，取消以下注释并运行此脚本
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    from django.test.runner import DiscoverRunner
    test_runner = DiscoverRunner()
    test_runner.run_tests(['test_chats.test_conversations']) 