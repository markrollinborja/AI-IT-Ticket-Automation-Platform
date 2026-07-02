from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.workflow_run import WorkflowRun

router = APIRouter(tags=["Dashboard"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard")
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    workflow_runs = (
        db.query(WorkflowRun)
        .order_by(WorkflowRun.created_at.desc())
        .limit(25)
        .all()
    )

    return templates.TemplateResponse(
    request=request,
    name="dashboard.html",
    context={
        "workflow_runs": workflow_runs,
        },
    )