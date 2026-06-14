"""配置文件"""
import os
from dotenv import load_dotenv

load_dotenv()

# 钉钉配置
DINGTALK_WEBHOOK_URL = os.getenv('DINGTALK_WEBHOOK_URL', '')
DINGTALK_SECRET = os.getenv('DINGTALK_SECRET', '')

# B站配置 - 支持多个UP主
BILI_UIDS = [1039025435, 773266]  # UP主UID列表
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 5))  # 检查间隔（分钟）

# 数据存储
DATA_DIR = 'data'
HISTORY_FILE = os.path.join(DATA_DIR, 'dynamic_history.json')