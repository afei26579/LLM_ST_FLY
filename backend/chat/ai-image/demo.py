from http import HTTPStatus
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
import os

prompt = "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书“义本生知人机同道善思新”，右书“通云赋智乾坤启数高志远”， 横批“智启通义”，字体飘逸，中间挂在一着一副中国风的画作，内容是岳阳楼。"

# 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
api_key = os.getenv("DASHSCOPE_API_KEY")

print('----同步调用，请等待任务执行----')
rsp = ImageSynthesis.call(api_key=api_key,
                          model="qwen-image",
                          prompt=prompt,
                          n=1,
                          size='1328*1328',
                          prompt_extend=True,
                          watermark=True)
print('response: %s' % rsp)
if rsp.status_code == HTTPStatus.OK:
    # 在当前目录下保存图片
    for result in rsp.output.results:
        file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
        with open('./%s' % file_name, 'wb+') as f:
            f.write(requests.get(result.url).content)
else:
    print('同步调用失败, status_code: %s, code: %s, message: %s' %
          (rsp.status_code, rsp.code, rsp.message))


#响应示例
{
    "status_code": 200,
    "request_id": "03b1ef03-480d-4ea5-ba52-xxxxxx",
    "code": null,
    "message": "",
    "output": {
        "task_id": "3cefd9bc-fcb2-4de9-a8bc-xxxxxx",
        "task_status": "SUCCEEDED",
        "results": [
            {
                "url": "https://dashscope-result-sz.oss-cn-shenzhen.aliyuncs.com/xxx.png?Expires=xxxxxx",
                "orig_prompt": "一副典雅庄重的对联悬挂于厅堂之中，房间是个安静古典的中式布置，桌子上放着一些青花瓷，对联上左书“义本生知人机同道善思新”，右书“通云赋智乾坤启数高志远”， 横批“智启通义”，字体飘逸，中间挂在一着一副中国风的画作，内容是岳阳楼。",
                "actual_prompt": "一副典雅庄重的对联悬挂于中式厅堂正中，整体空间为安静、古色古香的中国传统布置。厅堂内木质家具沉稳大气，墙面为淡色仿古纸张质感，地面铺设深色木质地板，营造出宁静而庄重的氛围。对联以飘逸的书法字体书写，左侧上联为“义本生知人机同道善思新”，右侧下联为“通云赋智乾坤启数高志远”，横批“智启通义”，文字排列对称，墨色深邃，书法流畅有力，体现出浓厚的文化气息与哲思内涵。\n\n对联中央悬挂一幅中国风画作，内容为岳阳楼，楼阁依水而建，背景为浩渺洞庭湖，远处山峦起伏，云雾缭绕，画面采用传统水墨技法绘制，笔触细腻，意境悠远。画作下方为一张中式红木长桌，桌上错落摆放着几件青花瓷器，包括花瓶与茶具，瓷器釉色清透，纹饰典雅，与整体环境风格和谐统一。整体画面风格为中国古典水墨风，空间布局层次分明，氛围宁静雅致，展现出浓厚的东方文化底蕴。"
            }
        ],
        "submit_time": "2025-09-09 13:41:54.041",
        "scheduled_time": "2025-09-09 13:41:54.087",
        "end_time": "2025-09-09 13:42:22.596"
    },
    "usage": {
        "image_count": 1
    }
}

#参数说明
"""
1. 指令遵循（提示词）

参数：input.prompt（必选）、input.negative_prompt（可选）。

    prompt（正向提示词）：描述希望在画面中看到的内容、主体、场景、风格、光照和构图。文生图的核心控制参数。

    negative_prompt（反向提示词）：描述不希望在画面中出现的内容，如“模糊”、“多余的手指”等。仅用于辅助优化生成质量。

撰写技巧：一个结构化的 Prompt 通常能带来更好的效果，撰写技巧请参见文生图Prompt指南。
2. 开启prompt智能改写

参数: parameters.prompt_extend (bool, 默认为 true)。

此功能可自动扩展和优化较短的Prompt，提升出图效果。开启此功能额外耗时 3-5 秒。此耗时为使用大模型改写文本。

实践建议：

    建议开启：当输入 Prompt 较简洁或宽泛时，此功能可显著提升图像效果。

    建议关闭：若需控制画面细节、或已提供详细描述，或对响应延迟敏感。请将参数 prompt_extend 显式设为 false。

3. 设置输出图像分辨率

参数: parameters.size (string)，格式为 "宽*高"。

通义千问 Qwen-Image：仅支持以下 5 种固定的分辨率：

    1328*1328（默认值）：1:1。

    1664*928: 16:9。

    928*1664: 9:16。

    1472*1140: 4:3。

    1140*1472: 3:4。
"""

# 生产环境
"""
    容错策略

        处理限流：当 API 返回 Throttling 错误码或 HTTP 429 状态码时，表明已触发限流，限流处理请参见限流。

        异步任务轮询：轮询查询异步任务结果时，建议采用合理的轮询策略（如前30秒每3秒一次，之后拉长间隔），避免因过于频繁的请求而触发限流。为任务设置一个最终超时时间（如 2 分钟），超时后标记为失败。

    风险防范

        结果持久化：API 返回的图片 URL 有 24 小时有效期。生产系统必须在获取 URL 后立即下载图片，并转存至您自己的持久化存储服务中（如阿里云对象存储 OSS）。

        内容安全审核：所有 prompt 和 negative_prompt 都会经过内容安全审核。若输入内容不合规，请求将被拦截并返回 DataInspectionFailed 错误。

        生成内容的版权与合规风险：请确保您的提示词内容符合相关法律法规。生成包含品牌商标、名人肖像、受版权保护的 IP 形象等内容可能涉及侵权风险，请您自行评估并承担相应责任。

常见问题

Q: 图片 URL 多久会失效？我应该如何永久保存图片？

A: 图片 URL 的有效期为 24 小时。您必须在获取到 URL 后，立即通过程序下载图片，并将其保存到您自己的持久化存储中，例如本地服务器或阿里云对象存储 OSS。

Q: 调用API返回DataInspectionFailed错误，如何处理？

A: 该错误表示输入文本触发了内容安全审核。请检查并修改prompt或negative_prompt中的文本，移除可能违规的内容后重试。

Q: prompt_extend参数应该开启还是关闭？

A: 当输入的prompt比较简洁或希望模型发挥更多创意时，建议保持开启（默认）。当prompt已经非常详细、专业，或对API响应延迟有严格要求时，建议显式设置为false。

Q: 如何提升图像中文字的生成效果？

A: 如果业务强依赖于在图像中生成清晰、准确的文字，请使用qwen-image模型，它是为此类场景专门训练的。
"""