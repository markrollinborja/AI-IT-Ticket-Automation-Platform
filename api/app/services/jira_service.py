from app.schemas.ticket import TicketPriority


class JiraService:
    def update_issue_priority(self, issue_key: str, priority: TicketPriority) -> None:
        print(f"Mock Jira update: issue {issue_key} priority set to {priority.value}")


jira_service = JiraService()