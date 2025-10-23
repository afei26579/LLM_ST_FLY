"""
API测试脚本 - 测试知识库和助手管理API
"""
import requests
import json

# API基础URL
BASE_URL = 'http://localhost:8000/api/v1/agent/customer-service'

# 测试用的token（需要先登录获取）
TOKEN = None  # 替换为实际token

headers = {}
if TOKEN:
    headers['Authorization'] = f'Bearer {TOKEN}'


def test_knowledge_bases():
    """测试知识库API"""
    print("\n========== 测试知识库API ==========")
    
    # 获取知识库列表
    print("\n1. 获取知识库列表...")
    url = f'{BASE_URL}/knowledge-bases/'
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 创建知识库
    if TOKEN:
        print("\n2. 创建知识库...")
        data = {
            'name': '测试知识库',
            'description': '这是一个测试知识库'
        }
        response = requests.post(url, json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


def test_assistants():
    """测试助手API"""
    print("\n========== 测试助手API ==========")
    
    # 获取助手列表
    print("\n1. 获取助手列表...")
    url = f'{BASE_URL}/assistants/'
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    
    # 创建助手
    if TOKEN:
        print("\n2. 创建助手...")
        data = {
            'name': '测试助手',
            'description': '这是一个测试助手',
            'greeting_message': '您好！有什么可以帮您的吗？'
        }
        response = requests.post(url, json=data, headers=headers)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")


def test_urls():
    """测试URL是否可访问"""
    print("\n========== 测试URL可访问性 ==========")
    
    urls = [
        f'{BASE_URL}/knowledge-bases/',
        f'{BASE_URL}/assistants/',
        f'{BASE_URL}/documents/',
        f'{BASE_URL}/assistants/default/',
    ]
    
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=5)
            status = "✅" if response.status_code in [200, 401, 403] else "❌"
            print(f"{status} {url} - 状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - 错误: {str(e)}")


if __name__ == '__main__':
    print("=" * 60)
    print("客服系统 API 测试")
    print("=" * 60)
    print(f"BASE_URL: {BASE_URL}")
    print(f"TOKEN: {'已设置' if TOKEN else '未设置（部分API需要认证）'}")
    
    # 测试URL可访问性
    test_urls()
    
    # 测试知识库API
    test_knowledge_bases()
    
    # 测试助手API
    test_assistants()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

