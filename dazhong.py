import datetime
import logging

import mysql.connector
import requests

import wechat
from gewechat import sendMsgToTeam

logging.basicConfig(
    filename='C:/work/code/dazhong/app.log',  # 日志文件名
    encoding='utf-8',
    filemode='a',  # 文件模式，'a' 表示追加，'w' 表示覆盖
    level=logging.INFO,  # 日志级别，DEBUG、INFO、WARNING、ERROR、CRITICAL
    format='%(asctime)s %(levelname)s: %(message)s'  # 日志格式
)
# MySQL 配置
DB_CONFIG = {
    'host': 'localhost',  # MySQL 地址
    'user': 'root',  # 用户名
    'password': '123456',  # 密码
    'database': 'dazhong'  # 数据库名
}


# CREATE TABLE errorcount (
# id INT AUTO_INCREMENT PRIMARY KEY,
# fail_count INT NOT NULL,
# notified INT NOT NULL,
# last_failed TIMESTAMP NOT NULL
# );


# 连接 MySQL 数据库
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


# 检查 id 是否已处理过
def is_id_processed(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_ids WHERE id = %s", (id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# 标记 id 为已处理
def mark_id_as_processed(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO processed_ids (id) VALUES (%s)", (id,))
    conn.commit()
    conn.close()


# 判断 artContent 是否包含 V豆奖励
def contains_v_dou_award(artContent):
    return 'V豆奖励' in artContent or 'V豆活动' in artContent or '0V豆' in artContent


# 处理接口返回的数据
def process_data(data):
    for item in data:
        item_id = item['id']
        art_content = item['artContent']
        artCreateTime = item['artCreateTime']
        # 将毫秒级时间戳转换为秒级时间戳
        timestamp_s = artCreateTime / 1000.0

        # 使用 datetime 模块转换为时间字符串
        time_str = datetime.datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')
        # 检查 id 是否已处理过
        if is_id_processed(item_id):
            continue

        # 判断是否包含 V豆奖励关键字
        if contains_v_dou_award(art_content):
            # print(f"发现 V豆奖励内容，ID: {item_id}, 文章标题: {item['artTitle']}，发布时间: {time_str}")
            logging.info(f"发现 V豆奖励内容，ID: {item_id}, 文章标题: {item['artTitle']}，发布时间: {time_str}")
            # 标记该 id 为已处理
            mark_id_as_processed(item_id)
            sendMsgToTeam(f"新V豆奖励\n文章标题: {item['artTitle']}\n发布时间: {time_str}",
                          item['artTitle'],
                          item['artTitle'],
                          item_id)
            # 发送消息


# 检查失败次数
def check_fail_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fail_count FROM errorcount WHERE id = 1")  # 假设只用一个记录来存储
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return 0


# 增加失败次数
def increment_fail_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fail_count FROM errorcount WHERE id = 1")
    result = cursor.fetchone()
    if result:
        new_count = result[0] + 1
        cursor.execute("UPDATE errorcount SET fail_count = %s, last_failed = %s WHERE id = 1",
                       (new_count, datetime.datetime.now()))
    else:
        cursor.execute("INSERT INTO errorcount (fail_count, last_failed) VALUES (1, %s)", (datetime.datetime.now(),))
    conn.commit()
    conn.close()


# 重置失败次数
def reset_fail_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE errorcount SET fail_count = 0 WHERE id = 1")
    conn.commit()
    conn.close()


def fetch_and_process_data():
    try:
        current_time = datetime.datetime.now()
        # 无论是否发生异常，都会执行这个代码块
        # print(f"{current_time}: 开始执行！")
        logging.info("开始执行！")
        # 好物推荐官
        getEssayListByUserId('6700000006198610')
        # 社区小助手
        getEssayListByUserId('6700000006198515')
        # ID君
        getEssayListByUserId('6700000006198043')
        # Hi米多
        getEssayListByUserId('6700000066726146')
        # ID.气氛组
        getEssayListByUserId('6700000014116071')
        # ID. 小掌柜
        getEssayListByUserId('6700000014126436')
        # 你好_大众
        getEssayListByUserId('6700000005339978')
        # 爱车斯坦
        getEssayListByUserId('6700000056834639')

        reset_fail_count()  # 重置失败计数
    except Exception as e:
        logging.error("执行失败！")
        logging.error(e)
        current_time = datetime.datetime.now()
        # 无论是否发生异常，都会执行这个代码块
        increment_fail_count()  # 增加失败计数
        if check_fail_count() >= 3:  # 如果连续失败次数达到3次，发送通知
            if not has_sent_failure_notification():  # 只发送一次通知
                wechat.sendtext(f"{current_time} : 上汽大众定时任务执行失败！")
                mark_failure_notification_sent()  # 标记通知已发送
        # 如果发生异常，执行这个代码块
        pass
    finally:
        # 无论是否发生异常，都会执行这个代码块
        logging.info("执行完成！")
        pass


# 标记失败通知已发送
def mark_failure_notification_sent():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE errorcount SET notified = 1 WHERE id = 1")
    conn.commit()
    conn.close()


# 检查是否已发送通知
def has_sent_failure_notification():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT notified FROM errorcount WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1


def getEssayListByUserId(id):
    url = 'https://m.svw-volkswagen.com/community-api/group/getUserAboutInfo/getEssayListByUserId?userId=' + id + '&page=0&size=10'  # 替换为实际的接口 URL
    response = requests.get(url)
    if response.status_code == 200:
        print(f"ID: {id}请求成功！")
        data = response.json().get('data', [])
        process_data(data)
    else:
        print(f"接口请求失败，状态码: {response.status_code}")


if __name__ == '__main__':
    fetch_and_process_data()
