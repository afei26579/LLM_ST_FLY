#  DashScope SDK 版本不低于 1.24.6
import os
import requests
import dashscope

text = "那我来给大家推荐一款T恤，这款呢真的是超级好看，这个颜色呢很显气质，而且呢也是搭配的绝佳单品，大家可以闭眼入，真的是非常好看，对身材的包容性也很好，不管啥身材的宝宝呢，穿上去都是很好看的。推荐宝宝们下单哦。"
# SpeechSynthesizer接口使用方法：dashscope.audio.qwen_tts.SpeechSynthesizer.call(...)
response = dashscope.MultiModalConversation.call(
    model="qwen3-tts-flash",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    text=text,
    voice="Cherry",
    language_type="Chinese", # 建议与文本语种一致，以获得正确的发音和自然的语调。
    stream=False
)
audio_url = response.output.audio.url
save_path = "downloaded_audio.wav"  # 自定义保存路径

try:
    response = requests.get(audio_url)
    response.raise_for_status()  # 检查请求是否成功
    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"音频文件已保存至：{save_path}")
except Exception as e:
    print(f"下载失败：{str(e)}")


"返回示例："
{
  "status_code": 200,
  "request_id": "3c88b429-eb67-49de-b708-fe4c994fbfba",
  "code": "",
  "message": "",
  "output": {
    "text": null,
    "finish_reason": "stop",
    "choices": null,
    "audio": {
      "data": "",
      "url": "http://dashscope-result-sh.oss-cn-shanghai.aliyuncs.com/1d/08/20250929/ffcf3aa4/e6cf58c8-33bd-47b9-941b-9a0652868b8c.wav?Expires=1759229218&OSSAccessKeyId=LTAI5xxx&Signature=bSfyEcJ3wjeq15h2ABgSdo1L3Pw%3D",
      "id": "audio_3c88b429-eb67-49de-b708-fe4c994fbfba",
      "expires_at": 1759229218
    }
  },
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "characters": 195
  }
}

"实时语音播放"
#  DashScope SDK 版本不低于 1.24.6
# coding=utf-8
#
# Installation instructions for pyaudio:
# APPLE Mac OS X
#   brew install portaudio
#   pip install pyaudio
# Debian/Ubuntu
#   sudo apt-get install python-pyaudio python3-pyaudio
#   or
#   pip install pyaudio
# CentOS
#   sudo yum install -y portaudio portaudio-devel && pip install pyaudio
# Microsoft Windows
#   python -m pip install pyaudio

import os
import dashscope
import pyaudio
import time
import base64
import numpy as np

p = pyaudio.PyAudio()
# 创建音频流
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                output=True)


text = "你好啊，我是通义千问"
response = dashscope.MultiModalConversation.call(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model="qwen3-tts-flash",
    text=text,
    voice="Cherry",
    language_type="Chinese",  # 建议与文本语种一致，以获得正确的发音和自然的语调。
    stream=True
)

for chunk in response:
    audio = chunk.output.audio
    if audio.data is not None:
        wav_bytes = base64.b64decode(audio.data)
        audio_np = np.frombuffer(wav_bytes, dtype=np.int16)
        # 直接播放音频数据
        stream.write(audio_np.tobytes())
    if chunk.output.finish_reason == "stop":
        print("finish at: {} ", chunk.output.audio.expires_at)
time.sleep(0.8)
# 清理资源
stream.stop_stream()
stream.close()
p.terminate()




