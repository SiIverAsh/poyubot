import os
import json
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def get_tweets(url, scroll_timeout=5):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    with open("cookie.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)
        driver.get(url)
        for cookie in cookies:
            if 'sameSite' in cookie:
                cookie['sameSite'] = {'Strict': 'Strict', 'Lax': 'Lax', 'None': 'None'}.get(cookie['sameSite'], None)
                if cookie['sameSite'] is None:
                    del cookie['sameSite']
            driver.add_cookie(cookie)
    driver.get(url)

    time.sleep(3)
    tweets = []
    total_tweets = 5
    fetched_tweets = 0
    last_scroll_time = time.time()

    while fetched_tweets < total_tweets:
        try:
            tweet_elements = driver.find_elements(By.CSS_SELECTOR, 'article')
            article_count = len(tweet_elements)

            for y in range(article_count):
                if fetched_tweets >= total_tweets:
                    break
                article = tweet_elements[y]
                soup = BeautifulSoup(article.get_attribute('outerHTML'), 'lxml')
                time_element = soup.find("time")
                publish_time = time_element.get("datetime")

                utc_time = datetime.strptime(publish_time, "%Y-%m-%dT%H:%M:%S.%fZ")
                beijing_time = utc_time + timedelta(hours=8)
                formatted_time = beijing_time.strftime("%Y年%m月%d日 %H:%M:%S")

                publish_url = "https://x.com" + time_element.find_parent().get("href")
                tweet_id = publish_url.split("/")[-1]

                tweet_text_div = soup.find("div", attrs={"data-testid": "tweetText"})
                publish_content = ""
                if tweet_text_div:
                    tweet_content_span = tweet_text_div.find("span")
                    if tweet_content_span:
                        publish_content = tweet_content_span.get_text(strip=True)
                else:
                    publish_content = "无正文"

                media_links = []
                media_elements = soup.find_all("img", attrs={"alt": "Image"})
                for img in media_elements:
                    media_links.append(img.get("src"))

                author = soup.find("div", attrs={"data-testid": "User-Name"})
                author_name = author.get_text() if author else "未知发布者"
                print(f"发布时间：", formatted_time)
                print(f"发布者：", author_name)
                print(f"推文地址：", publish_url)
                print(f"推文ID：", tweet_id)
                print(f"推文内容：", publish_content)
                print(f"图片链接：", media_links)
                tweets.append({
                    "作者": author_name,
                    "内容": publish_content,
                    "发送时间": formatted_time,
                    "推文链接": publish_url,
                    "推文ID": tweet_id,
                    "图片链接": media_links
                })
                fetched_tweets += 1
                if time.time() - last_scroll_time >= scroll_timeout:
                    driver.execute_script("window.scrollBy(0, 3000)")
                    last_scroll_time = time.time()
                    time.sleep(1)
        except Exception as e:
            print(f"推文获取失败：{str(e)}")
        if fetched_tweets < total_tweets:
            driver.execute_script("window.scrollBy(0, 4000)")
            last_scroll_time = time.time()
            time.sleep(3)
    with open("tweets/latest_tweet.txt", "w", encoding="utf-8") as f:
        json.dump(tweets, f, ensure_ascii=False, indent=4)
    driver.quit()

get_tweets("https://x.com/7utauta", scroll_timeout=5)
