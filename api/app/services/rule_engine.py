from app.schemas.ticket import TicketCreate, TicketPriority


class RuleEngineResult:
    def __init__(
        self,
        matched: bool,
        priority: TicketPriority | None,
        rule_name: str | None,
        reason: str,
    ):
        self.matched = matched
        self.priority = priority
        self.rule_name = rule_name
        self.reason = reason


class RuleEngine:
    def evaluate_ticket(self, ticket: TicketCreate) -> RuleEngineResult:
        text = f"{ticket.title} {ticket.description}".lower()

        if "production down" in text or "system down" in text or "outage" in text:
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.CRITICAL,
                rule_name="production_outage",
                reason="Ticket matched production outage keywords.",
            )

        if "cannot login" in text or "vpn" in text or "access denied" in text:
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="access_issue",
                reason="Ticket matched access or VPN issue keywords.",
            )

        if "password reset" in text or "reset password" in text:
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.LOW,
                rule_name="password_reset",
                reason="Ticket matched password reset keywords.",
            )

        return RuleEngineResult(
            matched=False,
            priority=None,
            rule_name=None,
            reason="No deterministic rule matched.",
        )


rule_engine = RuleEngine()