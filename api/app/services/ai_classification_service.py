import json

from app.schemas.ticket import TicketCreate, TicketPriority
from app.services.ai_client import ai_client


class AIClassificationResult:
    def __init__(
        self,
        recommended_priority: TicketPriority,
        confidence: float,
    ):
        self.recommended_priority = recommended_priority
        self.confidence = confidence


class AIClassificationService:
    def classify_ticket(self, ticket: TicketCreate) -> AIClassificationResult:
        """
        Classifies a ticket using OpenAI when the Rule Engine
        cannot determine a priority.
        """

        response = ai_client.classify_priority(
            summary=ticket.title,
            description=ticket.description,
        )

        data = json.loads(response)

        priority_map = {
            "low": TicketPriority.LOW,
            "medium": TicketPriority.MEDIUM,
            "high": TicketPriority.HIGH,
            "critical": TicketPriority.CRITICAL,
        }

        priority = priority_map.get(
            data["priority"].lower(),
            TicketPriority.MEDIUM,
        )

        confidence = float(data["confidence_score"])

        return AIClassificationResult(
            recommended_priority=priority,
            confidence=confidence,
        )


ai_classification_service = AIClassificationService()