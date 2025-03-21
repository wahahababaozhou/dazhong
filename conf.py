from pathlib import Path

HEADLESS = False
BASE_DIR = Path(__file__).parent.resolve()
LOCAL_CHROME_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"
# MySQL 配置
DB_CONFIG = {
    'host': 'localhost',  # MySQL 地址
    'user': 'root',  # 用户名
    'password': '123456',  # 密码
    'database': 'dazhong'  # 数据库名
}
