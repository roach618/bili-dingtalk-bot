"""钉钉消息发送模块"""
import requests
import json
import hmac
import hashlib
import base64
import time
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DingtalkSender:
    """钉钉消息发送器"""
    
    def __init__(self, webhook_url: str, secret: str = ""):
        self.webhook_url = webhook_url
        self.secret = secret
    
    def _generate_sign(self) -> tuple:
        """生成钉钉签名"""
        timestamp = str(int(time.time() * 1000))
        sign_str = f"{timestamp}\n{self.secret}"
        sign = base64.b64encode(
            hmac.new(
                self.secret.encode('utf-8'),
                sign_str.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return timestamp, sign
    
    def send_text(self, text: str) -> bool:
        """发送文本消息"""
        payload = {
            "msgtype": "text",
            "text": {
                "content": text
            }
        }
        return self._send(payload)
    
    def send_markdown(self, title: str, content: str) -> bool:
        """发送Markdown消息"""
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": content
            }
        }
        return self._send(payload)
    
    def send_link(self, title: str, text: str, url: str, pic_url: str = "") -> bool:
        """发送链接消息"""
        payload = {
            "msgtype": "link",
            "link": {
                "title": title,
                "text": text,
                "messageUrl": url,
                "picUrl": pic_url
            }
        }
        return self._send(payload)
    
    def _send(self, payload: dict) -> bool:
        """发送消息"""
        url = self.webhook_url
        
        # 如果有密钥，添加签名
        if self.secret:
            timestamp, sign = self._generate_sign()
            url = f"{url}&timestamp={timestamp}&sign={sign}"
        
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            result = resp.json()
            
            if result.get('errcode') == 0:
                logger.info("消息发送成功")
                return True
            else:
                logger.error(f"消息发送失败: {result.get('errmsg')}")
                return False
        except Exception as e:
            logger.error(f"发送消息异常: {e}")
            return False