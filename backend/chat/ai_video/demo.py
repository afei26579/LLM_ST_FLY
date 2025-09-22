import base64
import os
from http import HTTPStatus
from dashscope import VideoSynthesis
import mimetypes

"""
环境要求：
    dashscope python SDK >= 1.23.8
安装/升级SDK:
    pip install -U dashscope
"""

# --- 准备工作：确保 API Key 已设置 ---
api_key = os.getenv("DASHSCOPE_API_KEY")

# --- 辅助函数：用于 Base64 编码 ---
# 格式为 data:{MIME_type};base64,{base64_data}
def encode_file(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type or not mime_type.startswith("image/"):
        raise ValueError("不支持或无法识别的图像格式")
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:{mime_type};base64,{encoded_string}"

"""
图像输入方式说明：
以下提供了三种图片输入方式，三选一即可

1. 使用公网URL - 适合已有公开可访问的图片
2. 使用本地文件 - 适合本地开发测试
3. 使用Base64编码 - 适合私有图片或需要加密传输的场景
"""

# 【方式一】使用公网可访问的图片URL
# 示例：使用一个公开的图片URL
img_url = "https://cdn.translate.alibaba.com/r/wanx-demo-1.png"

# 【方式二】使用本地文件（支持绝对路径和相对路径）
# 格式要求：file:// + 文件路径
# 示例（绝对路径）：
# img_url = "file://" + "/path/to/your/img.png"    # Linux/macOS
# img_url = "file://" + "C:/path/to/your/img.png"  # Windows
# 示例（相对路径）：
# img_url = "file://" + "./img.png"                # 相对当前执行文件的路径

# 【方式三】使用Base64编码的图片
# img_url = encode_file("./img.png")
# 图生视频
def sample_call_i2v():
    # 同步调用，直接返回结果
    print('please wait...')
    rsp = VideoSynthesis.call(api_key=api_key,
                              model='wan2.2-i2v-plus',
                              prompt='一只猫在草地上奔跑',
                              resolution="1080P",
                              img_url=img_url)
    print(rsp)
    if rsp.status_code == HTTPStatus.OK:
        print("video_url:", rsp.output.video_url)
    else:
        print('Failed, status_code: %s, code: %s, message: %s' %
              (rsp.status_code, rsp.code, rsp.message))

# 返回结果示例
{
    "status_code": 200,
    "request_id": "a77bde74-d20a-97cb-8384-xxxxxx",
    "code": null,
    "message": "",
    "output": {
        "task_id": "66ca2804-1e64-468f-b554-xxxxxx",
        "task_status": "SUCCEEDED",
        "video_url": "https://dashscope-result-wlcb.oss-cn-wulanchabu.aliyuncs.com/xxx.mp4?xxxxxx",
        "submit_time": "2025-07-27 21:15:19.582",
        "scheduled_time": "2025-07-27 21:15:19.613",
        "end_time": "2025-07-27 21:18:00.047",
        "orig_prompt": "一只猫在草地上奔跑",
        "actual_prompt": "一只白猫在草地上奔跑，尾巴高高扬起，步伐轻快。"
    },
    "usage": {
        "video_count": 1,
        "video_duration": 0,
        "video_ratio": "",
        "duration": 5,
        "SR": 1080
    }
}



if __name__ == '__main__':
    sample_call_i2v()