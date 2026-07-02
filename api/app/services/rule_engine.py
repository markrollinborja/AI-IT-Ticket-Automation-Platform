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

        if self._contains_any(text, ["production", "prod", "system", "server", "website"]) and self._contains_any(
            text, ["down", "outage", "unavailable", "not working", "offline"]
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.CRITICAL,
                rule_name="production_outage",
                reason="Ticket matched production outage keywords.",
            )

        if self._contains_any(text, ["cannot login", "can't login", "unable to login", "locked out", "access denied"]):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="login_or_access_issue",
                reason="Ticket matched login or access issue keywords.",
            )

        if self._contains_any(text, ["vpn", "remote access"]) and self._contains_any(
            text, ["not working", "cannot connect", "can't connect", "down", "failed"]
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="vpn_issue",
                reason="Ticket matched VPN connectivity keywords.",
            )

        if self._contains_any(text, ["password reset", "reset password", "forgot password", "change password"]):
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

    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)


rule_engine = RuleEngine()