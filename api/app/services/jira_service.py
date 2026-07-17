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

    # Workflow-state priority names, not classifications - must match the
    # exact custom priority names configured in the Jira project.
    PENDING_APPROVAL_PRIORITY_NAME = "Pending"
    REJECTED_PRIORITY_NAME = "Rejected"

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
        self._set_priority(issue_key, self.PRIORITY_MAP[priority])

    def set_issue_priority_name(self, issue_key: str, priority_name: str) -> None:
        """
        Push a raw Jira priority name, bypassing PRIORITY_MAP.

        Used for workflow-state values that aren't ticket classifications
        at all - "Pending" while a ticket awaits approval, "Rejected" if
        it's denied. Keeping these out of TicketPriority/PRIORITY_MAP keeps
        that enum focused on what the Rule Engine/AI actually classify.
        """
        self._set_priority(issue_key, priority_name)

    def _set_priority(self, issue_key: str, jira_priority_name: str) -> None:
        url = f"{settings.jira_base_url}/rest/api/3/issue/{issue_key}"

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
