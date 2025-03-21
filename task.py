import schedule
import time

from autoAnswer.main import timer
from dazhong import fetch_and_process_data
from gewechat import syncGeweStatus

# 设置任务每隔1分钟执行一次
# 获取最新的文章
schedule.every(1).minutes.do(fetch_and_process_data)
# 获取微信的在线状态
schedule.every(2).minutes.do(syncGeweStatus)
# 保持大众账号的登录状态
schedule.every(2).minutes.do(timer)

while True:
    schedule.run_pending()  # 运行所有等待的任务
    time.sleep(1)  # 暂停1秒，防止过度占用 CPU
