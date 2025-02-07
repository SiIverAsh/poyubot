import schedule
import time
from get_tweets import TweetRetriever

class ScheduledTweetRetrieval(TweetRetriever):
    def __init__(self, url, scroll_timeout=20, total_tweets=10):
        super().__init__(url, scroll_timeout)
        self.total_tweets = total_tweets

    def scheduled_task(self):
        tweets = self.get_tweets()
        if tweets:
            print(f"成功获取 {len(tweets)} 条推文")
            self.save_tweets_to_file(tweets)
        else:
            print("没有新推文")

def job():
    task = ScheduledTweetRetrieval(" ", scroll_timeout=30)
    task.scheduled_task()

schedule.every(1).hours.do(job)
while True:
    schedule.run_pending()
    time.sleep(1)
