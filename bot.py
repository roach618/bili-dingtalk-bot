"""主机器人程序"""
import os
import json
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
import logging

from config import DINGTALK_WEBHOOK_URL, DINGTALK_SECRET, BILI_UIDS, CHECK_INTERVAL, HISTORY_FILE
from bilibili_spider import BilibiliSpider
from dingtalk_sender import DingtalkSender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BilibiliDingtalkBot:
    """B站UP主动态钉钉机器人"""
    
    def __init__(self):
        self.spiders = {uid: BilibiliSpider(uid) for uid in BILI_UIDS}
        self.sender = DingtalkSender(DINGTALK_WEBHOOK_URL, DINGTALK_SECRET)
        self.history = self._load_history()
        self._init_data_dir()
    
    def _init_data_dir(self):
        """初始化数据目录"""
        Path('data').mkdir(exist_ok=True)
    
    def _load_history(self) -> set:
        """加载历史动态ID"""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
        except Exception as e:
            logger.error(f"加载历史记录失败: {e}")
        return set()
    
    def _save_history(self):
        """保存历史动态ID"""
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(list(self.history), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
    
    def _format_dynamic_message(self, dynamic: dict, up_name: str = '') -> str:
        """格式化动态消息"""
        timestamp = datetime.fromtimestamp(dynamic['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        up_info = f"（{up_name}）" if up_name else ""
        
        if dynamic['type'] == 'text':
            content = dynamic.get('content', {})
            text = content.get('text', '暂无内容') if isinstance(content, dict) else str(content)
            return f"""
📝 **新动态更新{up_info}**

{text}

🕐 发布时间: {timestamp}

[查看完整动态]({dynamic['url']})
            """
        
        elif dynamic['type'] == 'video':
            return f"""
🎬 **新视频发布{up_info}**

**标题**: {dynamic.get('title', '暂无标题')}

🕐 发布时间: {timestamp}

[去B站观看]({dynamic['url']})
            """
        
        return ""
    
    def check_and_notify(self):
        """检查并通知新动态"""
        logger.info(f"开始检查 {len(BILI_UIDS)} 个UP主的动态...")
        
        for uid, spider in self.spiders.items():
            logger.info(f"正在检查UP主: {uid}")
            
            # 获取UP主信息
            user_info = spider.get_user_info()
            up_name = user_info.get('name', str(uid)) if user_info else str(uid)
            
            # 获取动态
            dynamics_data = spider.get_dynamics()
            if not dynamics_data:
                logger.warning(f"获取UP主 {uid} 的动态数据失败")
                continue
            
            parsed_items = spider.parse_dynamics(dynamics_data)
            new_items = []
            
            for item in parsed_items:
                dynamic_id = item['dynamic_id']
                if dynamic_id not in self.history:
                    new_items.append(item)
                    self.history.add(dynamic_id)
            
            if new_items:
                logger.info(f"UP主 {up_name} 发现 {len(new_items)} 条新动态")
                for item in new_items:
                    message = self._format_dynamic_message(item, up_name)
                    self.sender.send_markdown("B站UP主动态", message)
            else:
                logger.info(f"UP主 {up_name} 暂无新动态")
        
        self._save_history()
    
    def start(self):
        """启动机器人"""
        logger.info("=" * 50)
        logger.info(f"B站UP主动态钉钉机器人启动")
        logger.info(f"监控UP主数量: {len(BILI_UIDS)}")
        logger.info(f"UP主UID: {', '.join(map(str, BILI_UIDS))}")
        logger.info(f"检查间隔: {CHECK_INTERVAL} 分钟")
        logger.info("=" * 50)
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.check_and_notify, 'interval', minutes=CHECK_INTERVAL)
        scheduler.start()
        
        # 立即执行一次
        self.check_and_notify()
        
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("机器人停止")
            scheduler.shutdown()

if __name__ == "__main__":
    bot = BilibiliDingtalkBot()
    bot.start()