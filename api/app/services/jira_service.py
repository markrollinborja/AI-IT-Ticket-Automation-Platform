import requests
from requests.auth import HTTPBasicAuth

from app.core.config import settings
from app.schemas.ticket import TicketPriority


class JiraService:
    PRIORITY_MAP = {
        TicketPriority.CRITICAL: "Highest",
        TicketPriority.HIGH: "High",
        TicketPriority.MEDIUM: "Medium",
        TicketPriority.LOW: "Low",
    }

    def get_issue(self, issue_key: str) -> dict:
        url = f"{settings.jira_base_url}/rest/api/3/issue/{issue_key}"

        response = requests.get(
            url,
            auth=HTTPBasicAuth(settings.jira_email, settings.jira_api_token),
            headers={"Accept": "application/json"},
            timeout=10,
        )

        response.raise_for_status()
        return response.json()

    def update_issue_priority(self, issue_key: str, priority: TicketPriority) -> None:
        url = f"{settings.jira_base_url}/rest/api/3/issue/{issue_key}"

        jira_priority_name = self.PRIORITY_MAP[priority]

        payload = {
            "fields": {
                "priority": {
                    "name": jira_priority_name,
                }
            }
        }

        response = requests.put(
            url,
            json=payload,
            auth=HTTPBasicAuth(settings.jira_email, settings.jira_api_token),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=10,
        )

        response.raise_for_status()


jira_service = JiraService()
