from fastapi import HTTPException, status

from app.schemas.jira import JiraWebhookEvent


class JiraWebhookValidationService:
    SUPPORTED_EVENT_TYPE = "jira:issue_created"

    def validate(self, event: JiraWebhookEvent) -> None:
        if event.webhookEvent != self.SUPPORTED_EVENT_TYPE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported Jira webhook event: {event.webhookEvent}",
            )

        if not event.issue.key.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jira issue key is required.",
            )

        if not event.issue.fields.summary.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jira issue summary is required.",
            )

        if not event.issue.fields.description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jira issue description is required.",
            )

        if not event.issue.fields.reporter.displayName.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Jira reporter display name is required.",
            )


jira_webhook_validation_service = JiraWebhookValidationService()