from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    ticket_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="processing")

    ai_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_priority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_support_team: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_missing_information: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_suggested_response: Mapped[str | None] = mapped_column(Text, nullable=True)

    final_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    final_priority: Mapped[str | None] = mapped_column(String(50), nullable=True)
    final_support_team: Mapped[str | None] = mapped_column(String(100), nullable=True)

    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approval_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    error_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )