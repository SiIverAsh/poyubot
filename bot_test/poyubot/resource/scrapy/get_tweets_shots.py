import json
import time
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image

def get_screenshot_of_tweet(url, cookies_path="E:/python/bottest/bot_test/config/cookie.json", wait_time=3):
    chrome_options = Options()
    proxy_address = "127.0.0.1:4962"
    chrome_options.add_argument(f"--proxy-server={proxy_address}")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)


    with open(cookies_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
        for cookie in cookies:
            if 'sameSite' in cookie:
                cookie['sameSite'] = {'Strict': 'Strict', 'Lax': 'Lax', 'None': 'None'}.get(cookie['sameSite'], None)
                if cookie['sameSite'] is None:
                    del cookie['sameSite']
            driver.add_cookie(cookie)

    driver.refresh()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'article'))
    )
    time.sleep(wait_time)
    screenshot = driver.get_screenshot_as_png()

    image = Image.open(BytesIO(screenshot))
    image.save(f'./image/{url.split("/")[-1]}.jpg')

    driver.quit()


def read_tweet_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tweet_data = json.load(file)
            return tweet_data
    except Exception as e:
        print(f"读取推文数据文件时出错: {e}")
        return []


def capture_tweets_screenshots(tweet_file_path, cookies_path):
    tweet_data = read_tweet_data(tweet_file_path)

    for tweet in tweet_data:
        tweet_url = tweet.get("推文链接")
        if tweet_url:
            print(f"开始爬取推文 {tweet_url} 的截图...")
            get_screenshot_of_tweet(tweet_url, cookies_path)


tweet_file_path = "E:/python/bottest/bot_test/poyubot/resource/scrapy/tweets/latest_tweet.txt"
capture_tweets_screenshots(tweet_file_path, "E:/python/bottest/bot_test/config/cookie.json")
