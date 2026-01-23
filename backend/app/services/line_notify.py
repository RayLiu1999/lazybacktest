"""
LINE Bot 通知服務

使用 LINE Messaging API 發送即時通知。
"""
import os
import httpx
from typing import Optional
from datetime import datetime


class LineNotifyService:
    """
    LINE Bot 通知服務
    
    使用 LINE Messaging API 推送訊息至指定使用者。
    """
    
    MESSAGING_API_URL = "https://api.line.me/v2/bot/message/push"
    
    def __init__(self):
        self.channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
        self.user_id = os.getenv("LINE_USER_ID", "")
    
    def is_configured(self) -> bool:
        """檢查是否已設定 LINE Bot 金鑰"""
        return bool(self.channel_access_token and self.user_id)
    
    async def send_feedback_notification(
        self,
        feedback_type: str,
        title: str,
        description: str,
        email: Optional[str] = None,
        client_ip: Optional[str] = None
    ) -> bool:
        """
        發送問題回報通知
        
        Args:
            feedback_type: 回報類型 (bug, feature, question)
            title: 標題
            description: 詳細說明
            email: 聯絡信箱
            client_ip: 客戶端 IP
            
        Returns:
            是否發送成功
        """
        if not self.is_configured():
            print("警告: LINE Bot 未設定，跳過通知")
            return False
        
        # 格式化訊息
        type_emoji = {
            "bug": "🐛",
            "feature": "💡",
            "question": "❓"
        }.get(feedback_type, "📝")
        
        type_label = {
            "bug": "Bug 回報",
            "feature": "功能建議",
            "question": "使用問題"
        }.get(feedback_type, "其他")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message_text = f"""
{type_emoji} LazyBacktest 問題回報

📌 類型: {type_label}
📝 標題: {title}

📄 詳細說明:
{description[:500]}{'...' if len(description) > 500 else ''}

📧 Email: {email or '未提供'}
🌐 IP: {client_ip or '未知'}
⏰ 時間: {timestamp}
""".strip()
        
        # 發送訊息
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.MESSAGING_API_URL,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.channel_access_token}"
                    },
                    json={
                        "to": self.user_id,
                        "messages": [
                            {
                                "type": "text",
                                "text": message_text
                            }
                        ]
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return True
                else:
                    print(f"LINE API 錯誤: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            print(f"LINE 通知發送失敗: {e}")
            return False


# 全域服務實例
line_notify_service = LineNotifyService()
