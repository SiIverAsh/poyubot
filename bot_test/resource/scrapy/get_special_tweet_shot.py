import json
import time
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image

def get_screenshot_of_tweet(url, cookies_path="./cookie.json", wait_time=3):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
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
    image.save(f'./image/{url.split("/")[-1]}.png')

    driver.quit()

# tweets_to_capture = [
#     " "
# ]
# for tweet_url in tweets_to_capture:
#     get_screenshot_of_tweet(tweet_url, wait_time=3)
