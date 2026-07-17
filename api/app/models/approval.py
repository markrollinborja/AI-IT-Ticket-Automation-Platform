from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    workflow_run_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workflow_runs.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    workflow_run = relationship("WorkflowRun")

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    decided_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    decision_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
