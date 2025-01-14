import schedule
import time

from dazhong import fetch_and_process_data

# 设置任务每隔1分钟执行一次
schedule.every(1).minutes.do(fetch_and_process_data)

while True:
    schedule.run_pending()  # 运行所有等待的任务
    time.sleep(1)  # 暂停1秒，防止过度占用 CPU
