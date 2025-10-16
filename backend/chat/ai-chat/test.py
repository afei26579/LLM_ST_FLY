#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
流式聊天API测试脚本
测试接口: /api/v1/chat/ai-chat/stream-chat/
"""

import requests
import json
import sys
import time

# 配置
API_BASE_URL = "http://localhost:8000"
STREAM_CHAT_URL = f"{API_BASE_URL}/api/v1/chat/ai-chat/stream-chat/"

# 认证token (需要替换为真实token)
# 可以通过登录接口获取，或者从浏览器开发者工具复制
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYwMzQzMTY3LCJpYXQiOjE3NjAyNTY3NjcsImp0aSI6ImU3Yzk3NTg0ZjZjMjRkYWJhZTI0YWFhNmFiN2UwYzQ3IiwidXNlcl9pZCI6MX0.gviIsh7_-TPzZRo48-RZjFFxOawqvrDwM9GnZO7rRWk"


def login_and_get_token(username="admin", password="admin"):
    """登录并获取token"""
    login_url = f"{API_BASE_URL}/api/v1/auth/login/"
    
    try:
        response = requests.post(login_url, json={
            "username": username,
            "password": password
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200 and 'data' in data:
                token = data['data'].get('access')
                print(f"✅ 登录成功，获取到token")
                return token
            else:
                print(f"❌ 登录失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 登录异常: {e}")
    
    return None


def test_stream_chat(token, question="你好，请介绍一下你自己", deep_thinking=False, web_search=False):
    """测试流式聊天API"""
    
    # 请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    # 请求数据
    data = {
        "messages": [
            {"role": "user", "content": question}
        ],
        "stream": True,
        "deep_thinking": deep_thinking,
        "web_search": web_search
    }
    
    print("=" * 80)
    print(f"📤 发送请求到: {STREAM_CHAT_URL}")
    print(f"📝 问题: {question}")
    print(f"🧠 深度思考: {deep_thinking}")
    print(f"🌐 联网搜索: {web_search}")
    print("=" * 80)
    print()
    
    try:
        # 发送流式请求
        response = requests.post(
            STREAM_CHAT_URL, 
            headers=headers, 
            json=data, 
            stream=True,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return
        
        print("🚀 开始接收流式响应...\n")
        
        # 用于收集完整内容
        full_content = ""
        thinking_content = ""
        conversation_id = None
        
        # 处理流式响应
        for line in response.iter_lines():
            if not line:
                continue
            
            line = line.decode('utf-8')
            
            # 解析SSE数据
            if line.startswith('data: '):
                data_str = line[6:].strip()
                
                if not data_str:
                    continue
                
                try:
                    chunk = json.loads(data_str)
                    chunk_type = chunk.get('type')
                    
                    if chunk_type == 'conversation_id':
                        conversation_id = chunk.get('conversation_id')
                        print(f"🆔 对话ID: {conversation_id}\n")
                    
                    elif chunk_type == 'thinking':
                        # 思考过程
                        thinking_content = chunk.get('full_thinking', '')
                        content_chunk = chunk.get('content', '')
                        if content_chunk:
                            print(f"🤔 思考: {content_chunk}", end='', flush=True)
                    
                    elif chunk_type == 'content':
                        # 内容片段
                        content_chunk = chunk.get('content', '')
                        if content_chunk:
                            # 实时打印，模拟打字机效果
                            print(content_chunk, end='', flush=True)
                            full_content += content_chunk
                            # 添加小延迟，更好地展示流式效果
                            time.sleep(0.01)
                    
                    elif chunk_type == 'final':
                        # 最终结果
                        print("\n")
                        print("-" * 80)
                        print("✅ 流式响应完成")
                        print(f"📊 完整内容长度: {len(chunk.get('content', ''))} 字符")
                        if chunk.get('usage'):
                            usage = chunk.get('usage')
                            print(f"📈 Token使用: 输入={usage.get('input_tokens')}, 输出={usage.get('output_tokens')}")
                        print("-" * 80)
                    
                    elif chunk_type == 'done':
                        print("\n🏁 响应流结束")
                        break
                    
                    elif chunk_type == 'error':
                        print(f"\n❌ 错误: {chunk.get('error')}")
                        break
                
                except json.JSONDecodeError as e:
                    print(f"\n⚠️ JSON解析错误: {e}")
                    print(f"原始数据: {data_str}")
        
        print()
        print("=" * 80)
        print("📦 测试完成")
        if full_content:
            print(f"📝 收集到的完整内容长度: {len(full_content)} 字符")
        if thinking_content:
            print(f"🤔 思考过程长度: {len(thinking_content)} 字符")
        print("=" * 80)
        
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print("=" * 80)
    print("🧪 流式聊天API测试工具")
    print("=" * 80)
    print()
    
    # 方式1: 使用全局TOKEN变量（需要手动设置）
    token = TOKEN
    
    # 方式2: 自动登录获取token（推荐）
    if token == "your_token_here":
        print("📋 未设置TOKEN，尝试自动登录...")
        username = input("请输入用户名 (默认: admin): ").strip() or "admin"
        password = input("请输入密码 (默认: admin): ").strip() or "admin"
        token = login_and_get_token(username, password)
        
        if not token:
            print("\n❌ 无法获取token，测试中止")
            return
    
    print()
    
    # 测试问题
    while True:
        print("\n" + "=" * 80)
        print("请选择测试场景:")
        print("  1. 简单问答 (默认)")
        print("  2. 深度思考模式")
        print("  3. 联网搜索模式")
        print("  4. 自定义问题")
        print("  0. 退出")
        print("=" * 80)
        
        choice = input("\n请输入选项 (1-4, 0退出): ").strip()
        
        if choice == '0':
            print("👋 退出测试")
            break
        elif choice == '2':
            question = "请深入分析一下人工智能的未来发展趋势"
            test_stream_chat(token, question, deep_thinking=True)
        elif choice == '3':
            question = "今天杭州的天气怎么样"
            test_stream_chat(token, question, web_search=True)
        elif choice == '4':
            question = input("请输入你的问题: ").strip()
            if question:
                deep_thinking = input("是否启用深度思考? (y/N): ").strip().lower() == 'y'
                web_search = input("是否启用联网搜索? (y/N): ").strip().lower() == 'y'
                test_stream_chat(token, question, deep_thinking, web_search)
        else:  # 默认选项1
            question = "你好，请介绍一下你自己"
            test_stream_chat(token, question)
        
        # 询问是否继续
        continue_test = input("\n是否继续测试? (Y/n): ").strip().lower()
        if continue_test == 'n':
            print("👋 退出测试")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，测试结束")
        sys.exit(0)

