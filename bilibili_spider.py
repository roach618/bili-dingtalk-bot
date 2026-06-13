"""B站爬虫模块"""
import requests
import json
import time
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BilibiliSpider:
    """B站UP主动态爬虫"""
    
    def __init__(self, uid: int):
        self.uid = uid
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_user_info(self) -> Optional[Dict]:
        """获取UP主信息"""
        url = f"https://api.bilibili.com/x/space/acc/info"
        params = {
            'mid': self.uid,
            'platform': 'web'
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get('code') == 0:
                logger.info(f"获取UP主信息成功: {data['data']['name']}")
                return data.get('data')
            else:
                logger.error(f"获取UP主信息失败: {data.get('message')}")
                return None
        except Exception as e:
            logger.error(f"获取UP主信息异常: {e}")
            return None
    
    def get_dynamics(self, offset: str = "") -> Optional[Dict]:
        """获取UP主动态"""
        url = "https://api.bilibili.com/x/polymer/web-dynamic/v1/feed"
        params = {
            'host_mid': self.uid,
            'features': 'itemOpusStyle',
            'my_business': 'ugc_timeline',
            'update_baseline': offset,
            'unread_only': False,
            'need_body_topic': 1
        }
        
        try:
            resp = self.session.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get('code') == 0:
                logger.info(f"获取动态成功，获得 {len(data.get('data', {}).get('items', []))} 条")
                return data.get('data')
            else:
                logger.error(f"获取动态失败: {data.get('message')}")
                return None
        except Exception as e:
            logger.error(f"获取动态异常: {e}")
            return None
    
    def parse_dynamics(self, dynamics_data: Dict) -> List[Dict]:
        """解析动态数据"""
        items = dynamics_data.get('items', [])
        parsed_items = []
        
        for item in items:
            try:
                basic = item.get('basic', {})
                if basic.get('comment_type') == 1:  # 文字动态
                    parsed_items.append({
                        'type': 'text',
                        'id': basic.get('rid'),
                        'dynamic_id': basic.get('bid'),
                        'timestamp': item.get('modules', {}).get('module_author', {}).get('pub_ts'),
                        'content': item.get('modules', {}).get('module_desc', {}).get('desc', {}),
                        'url': f"https://t.bilibili.com/{basic.get('bid')}"
                    })
                elif basic.get('comment_type') == 8:  # 视频动态
                    parsed_items.append({
                        'type': 'video',
                        'id': basic.get('rid'),
                        'dynamic_id': basic.get('bid'),
                        'timestamp': item.get('modules', {}).get('module_author', {}).get('pub_ts'),
                        'title': item.get('modules', {}).get('module_dynamic', {}).get('major', {}).get('archive', {}).get('title', ''),
                        'cover': item.get('modules', {}).get('module_dynamic', {}).get('major', {}).get('archive', {}).get('cover', ''),
                        'url': f"https://t.bilibili.com/{basic.get('bid')}"
                    })
            except Exception as e:
                logger.warning(f"解析动态出错: {e}")
        
        return parsed_items