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

        # Critical: production or business-wide outages
        if self._contains_any(
            text,
            ["production", "prod", "system", "server", "website", "application", "app", "network", "internet"],
        ) and self._contains_any(
            text,
            ["down", "outage", "unavailable", "offline", "not working", "cannot access", "users affected"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.CRITICAL,
                rule_name="critical_outage",
                reason="Ticket matched outage or business-impacting availability keywords.",
            )

        # Critical: security incidents
        if self._contains_any(
            text,
            ["phishing", "malware", "ransomware", "hacked", "compromised", "data breach", "suspicious email"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.CRITICAL,
                rule_name="security_incident",
                reason="Ticket matched security incident keywords.",
            )

        # High: login/access issues
        if self._contains_any(
            text,
            ["cannot login", "can't login", "unable to login", "locked out", "access denied", "account locked"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="login_or_access_issue",
                reason="Ticket matched login or access issue keywords.",
            )

        # High: VPN / remote access issues
        if self._contains_any(text, ["vpn", "remote access"]) and self._contains_any(
            text,
            ["not working", "cannot connect", "can't connect", "down", "failed", "unable to connect"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="vpn_issue",
                reason="Ticket matched VPN or remote access issue keywords.",
            )

        # High: email unavailable
        if self._contains_any(text, ["email", "outlook", "mailbox", "exchange"]) and self._contains_any(
            text,
            ["not working", "cannot send", "can't send", "cannot receive", "can't receive", "down", "unavailable"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="email_service_issue",
                reason="Ticket matched email service disruption keywords.",
            )

        # High: printer needed for business operation
        if self._contains_any(text, ["printer", "printing"]) and self._contains_any(
            text,
            ["department", "office", "clinic", "warehouse", "cannot print", "can't print", "not printing"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="business_printer_issue",
                reason="Ticket matched business-impacting printer issue keywords.",
            )

        # Low: password help
        if self._contains_any(
            text,
            [
                "password reset",
                "reset password",
                "forgot password",
                "forgot my password",
                "change password",
                "update password",
                "unlock account",
                "locked account",
            ],
        ) or (
            self._contains_any(text, ["password", "passcode", "credentials"])
            and self._contains_any(
                text,
                ["reset", "forgot", "change", "update", "unlock", "locked", "expired", "can't remember", "cannot remember"],
            )
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.LOW,
                rule_name="password_help",
                reason="Ticket matched password help keywords.",
            )

        # Low: software install request
        if self._contains_any(text, ["install", "installation", "setup"]) and self._contains_any(
            text,
            ["software", "application", "app", "chrome", "teams", "zoom", "office", "adobe"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.LOW,
                rule_name="software_install_request",
                reason="Ticket matched software installation request keywords.",
            )

        # Low: hardware/peripheral request
        if self._contains_any(
            text,
            ["keyboard", "mouse", "monitor", "dock", "headset", "webcam", "cable", "charger"],
        ) and self._contains_any(
            text,
            ["request", "need", "replace", "replacement", "broken", "not working"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.LOW,
                rule_name="hardware_request",
                reason="Ticket matched common hardware or peripheral request keywords.",
            )

        # Medium: single-user device issue
        if self._contains_any(
            text,
            ["laptop", "desktop", "computer", "pc", "slow", "freezing", "crashing", "blue screen"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.MEDIUM,
                rule_name="device_issue",
                reason="Ticket matched single-user device issue keywords.",
            )

        # Medium: application issue without outage language
        if self._contains_any(
            text,
            ["application", "app", "software", "program", "tool"],
        ) and self._contains_any(
            text,
            ["error", "bug", "issue", "problem", "not loading", "crashing"],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.MEDIUM,
                rule_name="application_issue",
                reason="Ticket matched application issue keywords without outage indicators.",
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