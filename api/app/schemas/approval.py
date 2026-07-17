from pydantic import BaseModel, Field


class ApprovalDecision(BaseModel):
    """
    Request body for approving or rejecting a workflow run.

    decided_by is free text, not a verified identity - there's no
    authentication in this project yet (see docs/09-authentication-strategy.md),
    so this is a self-reported name/email for the audit trail, not a
    guarantee of who actually made the call.
    """

    decided_by: str = Field(min_length=1)
    decision_notes: str | None = None
