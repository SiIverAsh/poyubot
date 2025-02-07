import json
import os
import re
import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage
from datetime import datetime

file_path = "./resource/scrapy/tweets/latest_tweet.txt"
username_list_path = "./resource/scrapy/tweets/username_list.txt"
image_directory = './resource/scrapy/image'
image_url_base = " "
log_file_path = "./logs/bot"
_log = logging.get_logger(log_file_path)


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
        print(f"读取用户名列表时出错: {e}")
        return []


def remove_invalid_control_chars(text):
    return re.sub(r'[\x00-\x1F\x7F]', '', text)


def filter_tweets_by_author(tweets_content, author_name):
    tweets_content = remove_invalid_control_chars(tweets_content)
    try:
        tweets = json.loads(tweets_content)
    except json.JSONDecodeError as e:
        return f"JSON 解析错误: {str(e)}"
    pattern = re.compile(re.escape(author_name.split('(')[0].strip()), re.IGNORECASE)
    filtered_tweets = []
    for tweet in tweets:
        if "作者" in tweet:
            author = tweet["作者"].split("(")[0].strip()
            if pattern.search(author):
                filtered_tweets.append(tweet)
    if not filtered_tweets:
        return f"没有找到关于'{author_name}'的推文。"
    sorted_tweets = sorted(filtered_tweets, key=lambda x: x.get('发送时间', datetime.min), reverse=True)
    return sorted_tweets


test_config = read(os.path.join(os.path.dirname(__file__), "E:/python/bottest/bot_test/config/config.yaml"))


class MyClient(botpy.Client):
    async def on_group_at_message_create(self, message: GroupMessage):
        content = message.content.strip()
        _log.info(f"收到消息: {content}")

        if "最新推文" in content:
            _log.info("收到 '最新推文' 指令，开始读取博主用户名列表...")
            usernames = read_username_list()
            if usernames:
                options = "\n".join([f"{i + 1}. {username}" for i, username in enumerate(usernames)])
                prompt = f"请选择博主:\n{options}"
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
                _log.info(f"选择的博主: {author_name}")
                message_content = read_file(file_path)

                if message_content:
                    sorted_tweets = filter_tweets_by_author(message_content, author_name)
                    if isinstance(sorted_tweets, list) and sorted_tweets:
                        # 获取最新的推文（排在最前面的推文）
                        tweet = sorted_tweets[0]
                        tweet_id = tweet.get('推文ID')
                        image_filename = f"{tweet_id}.jpg"
                        local_image_path = os.path.join(image_directory, image_filename)

                        if os.path.exists(local_image_path):
                            file_url = f"{image_url_base}/{image_filename}"
                            uploadMedia = await message._api.post_group_file(
                                group_openid=message.group_openid,
                                file_type=1,
                                url=file_url
                            )
                            await message._api.post_group_message(
                                group_openid=message.group_openid,
                                msg_type=7,
                                msg_id=message.id,
                                media=uploadMedia
                            )
                            _log.info(f"成功发送图片: {file_url}")
                        else:
                            _log.info(f"未找到图片: {local_image_path}")
                    else:
                        await self.api.post_group_message(
                            group_openid=message.group_openid,
                            msg_type=0,
                            msg_id=message.id,
                            content="没有找到关于此博主的推文或图片"
                        )
                        _log.info(f"没有找到 {author_name} 的推文或图片！")

        else:
            _log.info("未进行选择。")


if __name__ == "__main__":
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])
