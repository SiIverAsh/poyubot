import requests
import json

# 机器人凭证
bot_token = ""  # 你的 bot_token

# 目标频道 ID 和消息内容
channel_id = ""  # 你的频道 ID
message_content = "Hello, QQ Channel!"  # 你要发送的消息内容

# 沙箱环境请求的 URL
url = "https://sandbox.api.sgroup.qq.com/v1/message/send"

# 请求头，包含鉴权信息
headers = {
    "Authorization": f"Bot {bot_token}",
    "Content-Type": "application/json"
}

# 请求体，构造发送消息的内容
data = {
    "channel_id": channel_id,  # 频道 ID
    "content": message_content,  # 消息内容
    "msg_type": "text"  # 消息类型为文本消息
}

# 发送 POST 请求
response = requests.post(url, json=data, headers=headers)

# 输出响应内容
if response.status_code == 200:
    print("消息发送成功！")
else:
    print(f"消息发送失败，错误信息：{response.json()}")
