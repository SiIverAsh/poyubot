import json
import os
import re
import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage

file_path = "./resource/scrapy/tweets/latest_tweet.txt"
username_list_path = "./resource/scrapy/tweets/username_list.txt"

log_file_path = "logs/bot_log.txt"
log_dir = os.path.dirname(log_file_path)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
_log = logging.get_logger()

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None

def read_username_list():
    try:
        with open(username_list_path, 'r', encoding='utf-8') as file:
            usernames = file.readlines()
            return [username.strip() for username in usernames]
    except Exception as e:
        print(f" {e}")
        return []

def remove_invalid_control_chars(text):
    return re.sub(r'[\x00-\x1F\x7F]', '', text)

def process_tweets_content(tweets_content):
    tweets = json.loads(tweets_content)
    for tweet in tweets:
        if "内容" in tweet:
            tweet["内容"] = re.sub(r'http[s]?://\S+', '', tweet["内容"])
        if "推文链接" in tweet:
            del tweet["推文链接"]
        if "图片链接" in tweet:
            del tweet["图片链接"]
    return json.dumps(tweets, ensure_ascii=False, indent=4)

def filter_tweets_by_author(tweets_content, author_name):
    tweets_content = remove_invalid_control_chars(tweets_content)
    try:
        tweets = json.loads(tweets_content)
    except json.JSONDecodeError as e:
        return f"JSON 解析错误: {str(e)}"

    pattern = re.compile(re.escape(author_name), re.IGNORECASE)
    filtered_tweets = [tweet for tweet in tweets if "作者" in tweet and pattern.search(tweet["作者"])]

    if not filtered_tweets:
        return f"没有找到关于'{author_name}'的推文。"

    return json.dumps(filtered_tweets, ensure_ascii=False, indent=4)

test_config = read(os.path.join(os.path.dirname(__file__), "E:/python/bottest/bot_test/config/config.yaml"))

class MyClient(botpy.Client):
    async def on_group_at_message_create(self, message: GroupMessage):
        content = message.content.strip()
        _log.info(f"收到消息: {content}")

        if content == "发送推文":
            _log.info("收到 '发送推文' 指令，开始读取博主用户名列表...")
            usernames = read_username_list()

            if usernames:
                options = "\n".join([f"{i + 1}. {username}" for i, username in enumerate(usernames)])
                prompt = f"请选择：\n{options}"
                await self.api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    msg_id=message.id,
                    content=prompt
                )
        elif content.isdigit():
            choice = int(content.strip()) - 1
            usernames = read_username_list()
            if 0 <= choice < len(usernames):
                author_name = usernames[choice]
                _log.info(f"{author_name}")

                message_content = read_file(file_path)
                if message_content:
                    filtered_content = filter_tweets_by_author(message_content, author_name)

                    if "没有找到" in filtered_content:
                        await self.api.post_group_message(
                            group_openid=message.group_openid,
                            msg_type=0,
                            msg_id=message.id,
                            content=filtered_content
                        )
                    else:
                        filtered_content = process_tweets_content(filtered_content)
                        await self.api.post_group_message(
                            group_openid=message.group_openid,
                            msg_type=0,
                            msg_id=message.id,
                            content=filtered_content
                        )
                    _log.info(f"已发送 '{author_name}' 的推文！")
                else:
                    await self.api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=0,
                        msg_id=message.id,
                        content="无法读取推文文件"
                    )
            else:
                await self.api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0,
                    msg_id=message.id,
                    content="无效的博主选择！"
                )
        else:
            _log.info("未进行选择。")

if __name__ == "__main__":
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
