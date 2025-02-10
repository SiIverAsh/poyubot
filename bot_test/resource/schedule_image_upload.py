import logging
import schedule
import time
import os
from bucket_upload_file import CosUploader


config_file = 'E:/python/bottest/bot_test/config/cos_key.yaml'
local_directory = 'E:/python/bottest/bot_test/resource/image'
cos_directory = 'images'
log_dir = 'E:/python/bottest/bot_test/logs'
log_filename = os.path.join(log_dir, 'auto_image_upload.log')


if not os.path.exists(log_dir):
    os.makedirs(log_dir)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding="utf-8",
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def upload_image():
    uploader = CosUploader(config_file)
    try:
        urls, errors = uploader.batch_upload_images(local_directory, cos_directory)
        logging.info("上传完成")
        logging.info(f"成功列表: {urls}")
        logging.info(f"失败文件: {errors}" if errors else "所有文件上传成功")
    except Exception as e:
        logging.error(f"上传过程中发生错误: {e}")

#test
upload_image()

# schedule.every(40).minutes.do(upload_image)
# logging.info("定时任务启动，每 40 分钟上传一次图片...")
# while True:
#     schedule.run_pending()
#     time.sleep(1)
