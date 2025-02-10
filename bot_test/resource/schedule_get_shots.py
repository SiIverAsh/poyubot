import json
import time
import logging
import schedule
from scrapy.get_local_tweets_shots import TweetScreenshotRetriever


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='E:/python/bottest/bot_test/logs/auto_tweet_screenshot.log',
    filemode='a',
    encoding='utf-8'
)

def schedule_task(tweet_file_path, captured_tweets_file, cookies_path):
    tweet_screenshot_retriever = TweetScreenshotRetriever()
    logging.info("开始爬取推文截图")
    tweet_screenshot_retriever.create_driver()
    logging.info("WebDriver successfully created with proxy 127.0.0.1:4962")
    tweet_screenshot_retriever.capture_tweets_screenshots(tweet_file_path, captured_tweets_file)
    logging.info("爬取任务完成")
    tweet_screenshot_retriever.close_driver()

def get_shots():
    tweet_file_path = "E:/python/bottest/bot_test/resource/scrapy/tweets/latest_tweet.txt"
    captured_tweets_file = "E:/python/bottest/bot_test/resource/scrapy/tweets/captured_tweets.txt"
    cookies_path = "E:/python/bottest/bot_test/config/cookie.json"
    logging.info("开始运行爬取任务")
    schedule_task(tweet_file_path, captured_tweets_file, cookies_path)

#test
get_shots()

# schedule.every(30).minutes.do(get_shots)
# logging.info("定时任务启动，每 30 分钟运行一次...")

# while True:
#     schedule.run_pending()
#     time.sleep(1)
