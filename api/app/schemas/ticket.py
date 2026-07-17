from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class TicketSource(str, Enum):
    JIRA = "jira"
    MANUAL = "manual"


class TicketCreate(BaseModel):
    title: str
    description: str
    created_by: str
    source: TicketSource = TicketSource.MANUAL


class TicketResponse(BaseModel):
    id: UUID
    title: str
    description: str
    created_by: str
    priority: TicketPriority
    status: TicketStatus
    source: TicketSource
    created_at: datetime
    ai_priority: TicketPriority | None = None
    ai_confidence_score: float | None = None
    classification_source: str = "rule_engine"
