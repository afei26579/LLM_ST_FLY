import os
import requests
import time
from http import HTTPStatus

# 从环境变量获取阿里云百炼API Key，或直接在代码中赋值
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")


"""注意：
图片分辨率：分辨率不小于256*256，不超过5760*3240，长宽比不超过2:1。
图片格式：JPEG，PNG，JPG，BMP，WEBP
图片大小：不超过10M。
图片格式：支持公网可访问的 HTTP/HTTPS 地址，URL 中不能包含中文字符；
支持传入Base64编码字符串。

支持对于本地文件，
"""
def submit_task():
    """提交一个风格重绘任务"""
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image-generation/generation"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-DashScope-Async": "enable"  # 异步调用
    }

    # --- 使用预置风格 ---
    # style_index: 0=复古漫画, 1=3D童话, 2=二次元, 3=小清新, 4=未来科技...
    body = {
        "model": "wanx-style-repaint-v1",
        "input": {
            "image_url": "https://vigen-video.oss-cn-shanghai.aliyuncs.com/demo_image/image_demo_input.png",
            "style_index": 3  # 示例：选择“小清新”风格
        }
    }

    # --- 使用自定义风格 ---
    # body = {
    #     "model": "wanx-style-repaint-v1",
    #     "input": {
    #         "image_url": "https://vigen-video.oss-cn-shanghai.aliyuncs.com/demo_image/input_example.png",
    #         "style_ref_url": "https://vigen-video.oss-cn-shanghai.aliyuncs.com/demo_image/style_example.png",
    #         "style_index": -1
    #     }
    # }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == HTTPStatus.OK:
        task_id = response.json().get('output', {}).get('task_id')
        print(f"任务提交成功，任务ID为: {task_id}")
        return task_id
    else:
        print(f"任务提交失败，状态码: {response.status_code}, 响应: {response.text}")
        return None


def query_task_result(task_id):
    """根据任务ID轮询查询结果"""
    if not task_id:
        return

    url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    print("开始查询任务状态...")
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code != HTTPStatus.OK:
            print(f"查询失败，状态码: {response.status_code}, 响应: {response.text}")
            break

        response_data = response.json()
        task_status = response_data.get('output', {}).get('task_status')

        if task_status == 'SUCCEEDED':
            print("任务成功完成！")
            print(f"任务成功响应数据: {response_data}")
            results = response_data.get('output', {}).get('results', [])
            for i, result in enumerate(results):
                print(f"生成图片_{i + 1} URL: {result.get('url')}")
            break
        elif task_status == 'FAILED':
            print(f"任务失败。错误信息: {response_data}")
            break
        else:
            print(f"任务正在处理中，当前状态: {task_status}...")
            time.sleep(5)  # 等待5秒后再次查询


if __name__ == '__main__':
    task_id = submit_task()
    if task_id:
        query_task_result(task_id)