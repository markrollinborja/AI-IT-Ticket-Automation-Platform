from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.jira import JiraWebhookEvent
from app.services.jira_webhook_validation_service import jira_webhook_validation_service
from app.services.workflow_service import workflow_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/jira")
def handle_jira_webhook(
    event: JiraWebhookEvent,
    db: Session = Depends(get_db),
):
    jira_webhook_validation_service.validate(event)

    return workflow_service.process_jira_issue(
        db=db,
        event=event,
    )
