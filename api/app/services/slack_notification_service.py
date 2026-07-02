import requests

from app.core.config import settings


class SlackNotificationService:
    def send_message(self, message: str) -> None:
        payload = {
            "text": message,
        }

        response = requests.post(
            settings.slack_webhook_url,
            json=payload,
            timeout=10,
        )

        response.raise_for_status()


slack_notification_service = SlackNotificationService()