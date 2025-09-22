import os
from http import HTTPStatus
import dashscope
from dashscope import Generation

# 1. 准备工作：配置API Key
# 建议通过环境变量配置API Key，避免硬编码。
try:
    dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]
except KeyError:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")

# 2. 发起流式请求
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "请介绍一下自己"},
]
api_params = {'api_key': 'sk-6773f83a2894476bbac38c4f1a6735c3', 'model': 'qwen-flash', 'messages': [{'role': 'user', 'content': '你叫什么呢'}], 'result_format': 'message', 'stream': True, 'incremental_output': True, 'enable_thinking': False}
try:
    responses = Generation.call(**api_params)

    # 3. 处理流式响应
    content_parts = []
    print("AI: ", end="", flush=True)

    for resp in responses:
        if resp.status_code == HTTPStatus.OK:
            content = resp.output.choices[0].message.content
            print(content, end="", flush=True)
            content_parts.append(content)

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

    full_response = "".join(content_parts)
    # print(f"\n--- 完整回复 ---\n{full_response}")

except Exception as e:
    print(f"发生未知错误: {e}")
