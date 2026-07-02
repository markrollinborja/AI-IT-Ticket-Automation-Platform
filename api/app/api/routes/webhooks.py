from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.jira import JiraWebhookEvent
from app.schemas.ticket import TicketResponse
from app.services.workflow_service import workflow_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/jira")
def handle_jira_webhook(
    event: JiraWebhookEvent,
    db: Session = Depends(get_db),
):
    return workflow_service.process_jira_issue(
        db=db,
        event=event,
    )