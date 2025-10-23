import dashscope
audio_file_path = "file://D:/workspace/llm_st_fly/backend/media/audio-inputs/7ac10236-96cb-4299-b2bf-5cb6784f636b_6SjrPpA.wav"

messages = [
    {
        "role": "user",
        "content": [
            {"audio": audio_file_path},
        ]
    }
]
response = dashscope.MultiModalConversation.call(
    model="qwen-audio-asr",
    messages=messages,
    result_format="message")
print(response)