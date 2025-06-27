from twilio.rest import Client as Twilio_client
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from core.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

# 测试发送手机验证码
def test_send_sms_code():
    # 创建Twilio客户端
    client = Twilio_client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    # 发送短信
    message = client.messages.create(
        body="【米粒】你好，验证码是：123456",
        from_=TWILIO_PHONE_NUMBER,
        to="+8615678100175"
    )
    print(message)


if __name__ == "__main__":
    test_send_sms_code()