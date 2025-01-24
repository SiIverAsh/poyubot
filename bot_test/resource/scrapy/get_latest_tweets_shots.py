import json
import time
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image


def get_long_screenshot(url, scroll_timeout=30):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    with open("cookie.json", "r", encoding="utf-8") as f:
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
    time.sleep(3)

    total_height = driver.execute_script("return document.body.scrollHeight")

    screenshots = []
    last_scroll_time = time.time()

    while True:
        screenshot = driver.get_screenshot_as_png()
        screenshots.append(screenshot)

        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(1)

        if time.time() - last_scroll_time >= scroll_timeout:
            last_scroll_time = time.time()
            driver.execute_script("window.scrollBy(0, 3000)")
            time.sleep(1)

        current_position = driver.execute_script("return window.scrollY + window.innerHeight")
        if current_position >= total_height:
            break

    total_width = driver.execute_script("return window.innerWidth")
    total_height = len(screenshots) * driver.execute_script("return window.innerHeight")
    long_image = Image.new('RGB', (total_width, total_height))
    y_offset = 0
    for screenshot in screenshots:
        image = Image.open(BytesIO(screenshot))
        long_image.paste(image, (0, y_offset))
        y_offset += image.height
    long_image.save('./image/long_screenshot.png')
    driver.quit()

get_long_screenshot(" ", scroll_timeout=30)
