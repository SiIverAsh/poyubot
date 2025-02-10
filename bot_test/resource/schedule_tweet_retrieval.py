import schedule
import time
import logging
import os
import re
from scrapy.get_tweets import TweetRetriever

log_dir = "/bot_test/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_filename = os.path.join(log_dir, "auto_tweets_get.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_filename, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class ScheduledTweetRetrieval(TweetRetriever):
    def __init__(self, url, scroll_timeout=20, total_tweets=10):
        super().__init__(url, scroll_timeout)
        self.total_tweets = total_tweets

    def scheduled_task(self):
        try:
            tweets = self.get_tweets()
            if tweets:
                self.save_tweets_to_file(tweets)
        except Exception as e:
            logging.error(f"{e}")

def get_usernames_from_file(file_path):
    usernames = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r"([a-zA-Z0-9_]+)\(", line.strip())
            if match:
                usernames.append(match.group(1))
    return usernames

def get_tweets():
    usernames = get_usernames_from_file("./scrapy/tweets/username_list.txt")
    for username in usernames:
        url = f"https://x.com/{username}"
        task = ScheduledTweetRetrieval(url, scroll_timeout=30)
        task.scheduled_task()
#test
get_tweets()

# schedule.every(40).minutes.do(get_tweets)
# logging.info("定时任务启动...")
# while True:
#     schedule.run_pending()
#     time.sleep(3)
