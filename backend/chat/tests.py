

import os
from http import HTTPStatus
import unittest
from unittest.mock import patch, MagicMock
import dashscope
from dashscope import Generation

class TestDashScopeStreaming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 配置API Key
        try:
            dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]
        except KeyError:
            raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")

    def test_streaming_response(self):
        # 测试数据
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "请介绍一下自己"},
        ]

        # 模拟Generation.call的返回值
        mock_responses = [
            MagicMock(status_code=HTTPStatus.OK, output=MagicMock(choices=[{
                'message': {'content': '我是一个AI助手，'},
                'finish_reason': None
            }])),
            MagicMock(status_code=HTTPStatus.OK, output=MagicMock(choices=[{
                'message': {'content': '可以回答各种问题。'},
                'finish_reason': 'stop'
            }])),
            # 可以添加更多模拟响应
        ]

        # 使用mock来模拟实际的API调用
        with patch('dashscope.Generation.call', side_effect=mock_responses):
            responses = Generation.call(
                model="qwen-plus",
                messages=messages,
                result_format="message",
                stream=True,
                incremental_output=True,
            )

            content_parts = []
            full_response = ""

            for resp in responses:
                if resp.status_code == HTTPStatus.OK:
                    content = resp.output.choices[0].message.content
                    content_parts.append(content)
                    full_response += content

                    # 检查是否是最后一个包
                    if resp.output.choices[0].finish_reason == "stop":
                        usage = resp.usage
                        print("\n--- 请求用量 ---")
                        print(f"输入 Tokens: {usage.input_tokens}")
                        print(f"输出 Tokens: {usage.output_tokens}")
                        print(f"总计 Tokens: {usage.total_tokens}")
                else:
                    # 处理错误情况
                    print(
                        f"\n请求失败: request_id={resp.request_id}, code={resp.code}, message={resp.message}"
                    )
                    break

            # 断言检查
            
            print(f"\n--- 完整回复 ---\n{full_response}")

if __name__ == '__main__':
    unittest.main()