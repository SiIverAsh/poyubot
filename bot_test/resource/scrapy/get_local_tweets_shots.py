import json
import time
import os
import logging
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image


class TweetScreenshotRetriever:
    def __init__(self, proxy_address="127.0.0.1:4962", cookies_path="E:/python/bottest/bot_test/config/cookie.json", log_dir="E:/python/bottest/bot_test/logs"):
        self.proxy_address = proxy_address
        self.cookies_path = cookies_path
        self.driver = None
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = os.path.join(log_dir, "get_local_shots.log")
        logging.basicConfig(filename=log_file, level=logging.DEBUG,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()


    def create_driver(self):
        chrome_options = Options()
        chrome_options.add_argument(f"--proxy-server={self.proxy_address}")
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.logger.info("WebDriver successfully created with proxy %s", self.proxy_address)


    def get_screenshot_of_tweet(self, url, wait_time=3):
        if not self.driver:
            self.create_driver()

        self.driver.get(url)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logger.info("开始爬取推文 %s 的截图", url)
        try:
            with open(self.cookies_path, "r", encoding="utf-8") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    if 'sameSite' in cookie:
                        cookie['sameSite'] = {'Strict': 'Strict', 'Lax': 'Lax', 'None': 'None'}.get(cookie['sameSite'], None)
                        if cookie['sameSite'] is None:
                            del cookie['sameSite']
                    self.driver.add_cookie(cookie)
        except Exception as e:
            self.logger.error("加载cookies时发生错误: %s", e)
            self.driver.quit()
            return
        self.driver.refresh()

        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article'))
            )
        except Exception as e:
            self.logger.error("等待页面加载时发生错误: %s", e)
            self.driver.quit()
            return

        time.sleep(wait_time)
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(BytesIO(screenshot))
        image_path = f'./image/{url.split("/")[-1]}.jpg'
        image.save(image_path)

    def read_tweet_data(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tweet_data = json.load(file)
                return tweet_data
        except Exception as e:
            self.logger.error("读取推文数据文件时出错: %s", e)
            return []

    def read_captured_tweets(self, captured_tweets_file):
        try:
            if not os.path.exists(captured_tweets_file):
                with open(captured_tweets_file, 'w', encoding='utf-8') as file:
                    pass
            with open(captured_tweets_file, 'r', encoding='utf-8') as file:
                captured_tweets = file.read().splitlines()
            return set(captured_tweets)
        except Exception as e:
            self.logger.error("读取已爬取推文记录时出错: %s", e)
            return set()

    def capture_tweets_screenshots(self, tweet_file_path, captured_tweets_file):
        tweet_data = self.read_tweet_data(tweet_file_path)
        captured_tweets = self.read_captured_tweets(captured_tweets_file)

        for tweet in tweet_data:
            tweet_url = tweet.get("推文链接")
            if tweet_url and tweet_url not in captured_tweets:
                self.get_screenshot_of_tweet(tweet_url)
                with open(captured_tweets_file, 'a', encoding='utf-8') as f:
                    f.write(tweet_url + '\n')

    def close_driver(self):
        if self.driver:
            self.driver.quit()
