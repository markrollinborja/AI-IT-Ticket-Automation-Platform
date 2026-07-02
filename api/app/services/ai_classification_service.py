from app.schemas.ticket import TicketCreate, TicketPriority


class AIClassificationResult:
    def __init__(
        self,
        recommended_priority: TicketPriority,
        confidence: float,
        reason: str,
    ):
        self.recommended_priority = recommended_priority
        self.confidence = confidence
        self.reason = reason


class AIClassificationService:
    def classify_ticket(self, ticket: TicketCreate) -> AIClassificationResult:
        return AIClassificationResult(
            recommended_priority=TicketPriority.MEDIUM,
            confidence=0.75,
            reason="Mock AI classification. Real AI integration will be added later.",
        )


ai_classification_service = AIClassificationService()