import os
import json
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


def extract_tweet_text(tweet_text_div):
    if not tweet_text_div:
        return "无正文"
    tweet_content = ""
    for element in tweet_text_div.children:
        if element.name == "span":
            tweet_content += element.get_text(strip=True)
        elif element.name == "img":
            emoji_alt = element.get("alt", "")
            tweet_content += emoji_alt
        elif element.name == "a":
            tweet_content += element.get_text(strip=True)

    return tweet_content.strip()


def get_tweets(url, scroll_timeout=20):
    chrome_options = Options()
    proxy_address = "127.0.0.1:4962"
    chrome_options.add_argument(f"--proxy-server={proxy_address}")
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    file_path = "E:/python/bottest/bot_test/config/cookie.json"
    with open(file_path, "r", encoding="utf-8") as f:
        cookies = json.load(f)
        driver.get(url)
        for cookie in cookies:
            if 'sameSite' in cookie:
                cookie['sameSite'] = {'Strict': 'Strict', 'Lax': 'Lax', 'None': 'None'}.get(cookie['sameSite'], None)
                if cookie['sameSite'] is None:
                    del cookie['sameSite']
            driver.add_cookie(cookie)
    driver.get(url)

    tweets = []
    total_tweets = 10
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
                publish_content = extract_tweet_text(tweet_text_div)

                media_links = []
                media_elements = soup.find_all("img", attrs={"alt": "Image"})
                for img in media_elements:
                    media_links.append(img.get("src"))

                author = soup.find("div", attrs={"data-testid": "User-Name"})
                author_name = author.get_text() if author else "未知发布者"

                pinned = False
                pinned_element = soup.find("div", attrs={"data-testid": "socialContext"})
                if pinned_element and pinned_element.get_text().strip() == "Pinned":
                    pinned = True

                reposted = False
                reposted_element = soup.find("span", attrs={"data-testid": "socialContext"})
                if reposted_element and "reposted" in reposted_element.get_text().strip().lower():
                    reposted = True

                print(f"发布时间：", formatted_time)
                print(f"发布者：", author_name)
                print(f"推文地址：", publish_url)
                print(f"推文ID：", tweet_id)
                print(f"推文内容：", publish_content)
                print(f"图片链接：", media_links)
                print(f"是否置顶推文：", pinned)
                print(f"是否转帖推文：", reposted)

                if tweet_id not in [t["推文ID"] for t in tweets]:
                    tweets.append({
                        "作者": author_name,
                        "内容": publish_content,
                        "发送时间": formatted_time,
                        "推文链接": publish_url,
                        "推文ID": tweet_id,
                        "图片链接": media_links,
                        "置顶推文": pinned,
                        "转帖推文": reposted
                    })
                    fetched_tweets += 1

                if time.time() - last_scroll_time >= scroll_timeout:
                    driver.execute_script("window.scrollBy(0, 500)")
                    last_scroll_time = time.time()
                    time.sleep(1)
        except Exception as e:
            print(f"推文获取失败：{str(e)}")

        if fetched_tweets < total_tweets:
            driver.execute_script("window.scrollBy(0, 800)")
            last_scroll_time = time.time()
            time.sleep(10)

    driver.quit()

    file_path = "tweets/latest_tweet.txt"

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                existing_tweets = json.load(f)
                if not isinstance(existing_tweets, list):
                    existing_tweets = []
            except json.JSONDecodeError:
                existing_tweets = []
    else:
        existing_tweets = []
    existing_tweet_ids = {tweet["推文ID"] for tweet in existing_tweets}
    new_tweets = [tweet for tweet in tweets if tweet["推文ID"] not in existing_tweet_ids]

    if new_tweets:
        existing_tweets.extend(new_tweets)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_tweets, f, ensure_ascii=False, indent=4)
        print(f"追加 {len(new_tweets)} 条新推文！")
    else:
        print("没有新推文需要写入！")


get_tweets("", scroll_timeout=30)
