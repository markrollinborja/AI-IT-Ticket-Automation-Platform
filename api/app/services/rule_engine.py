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
    """
    Deterministic rule engine for high-confidence, repeatable IT ticket patterns.

    Important design rule:
    The Rule Engine should only classify tickets when the pattern is obvious.
    Ambiguous tickets should fall through to AI classification.
    """

    def evaluate_ticket(self, ticket: TicketCreate) -> RuleEngineResult:
        text = f"{ticket.title} {ticket.description}".lower()

        # Critical: production or customer-facing outage
        if self._contains_any(
            text,
            [
                "production website",
                "prod website",
                "customer portal",
                "public website",
                "website is down",
                "site is down",
            ],
        ) and self._contains_any(
            text,
            [
                "down",
                "outage",
                "unavailable",
                "cannot access",
                "unable to access",
                "customers cannot access",
                "customers unable to access",
            ],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.CRITICAL,
                rule_name="critical_customer_facing_outage",
                reason="Ticket matched a high-confidence customer-facing outage pattern.",
            )

        # Critical: business-wide system outage
        if self._contains_any(
            text,
            [
                "company-wide",
                "entire company",
                "all users",
                "multiple departments",
                "everyone",
            ],
        ) and self._contains_any(
            text,
            [
                "system down",
                "network down",
                "internet down",
                "outage",
                "unavailable",
                "cannot access",
                "unable to access",
            ],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.CRITICAL,
                rule_name="critical_business_wide_outage",
                reason="Ticket matched a high-confidence business-wide outage pattern.",
            )

        # Critical: security incidents
        if self._contains_any(
            text,
            [
                "phishing",
                "malware",
                "ransomware",
                "hacked",
                "compromised",
                "data breach",
                "suspicious email",
                "unauthorized access",
            ],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.CRITICAL,
                rule_name="security_incident",
                reason="Ticket matched security incident keywords.",
            )

        # High: VPN / remote access issues
        if self._contains_any(text, ["vpn", "remote access"]) and self._contains_any(
            text,
            [
                "cannot connect",
                "can't connect",
                "unable to connect",
                "failed to connect",
                "connection failed",
                "not connecting",
                "not working",
            ],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="vpn_issue",
                reason="Ticket matched a high-confidence VPN or remote access issue pattern.",
            )

        # High: login/access issues
        if self._contains_any(
            text,
            [
                "cannot login",
                "can't login",
                "unable to login",
                "cannot log in",
                "can't log in",
                "unable to log in",
                "locked out",
                "access denied",
                "account locked",
            ],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="login_or_access_issue",
                reason="Ticket matched a high-confidence login or access issue pattern.",
            )

        # High: email unavailable
        if self._contains_any(text, ["email", "outlook", "mailbox", "exchange"]) and self._contains_any(
            text,
            [
                "cannot send",
                "can't send",
                "cannot receive",
                "can't receive",
                "not receiving",
                "not sending",
                "unavailable",
                "mailbox down",
                "email down",
                "outlook down",
            ],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="email_service_issue",
                reason="Ticket matched a high-confidence email service disruption pattern.",
            )

        # High: business-impacting printer issue
        if (
            self._contains_any(text, ["printer", "printing"])
            and self._contains_any(
                text,
                [
                    "cannot print",
                    "can't print",
                    "not printing",
                    "print queue",
                    "printer down",
                    "offline",
                ],
            )
            and self._contains_any(
                text,
                [
                    "department",
                    "office",
                    "clinic",
                    "warehouse",
                    "front desk",
                    "shipping",
                    "receiving",
                ],
            )
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.HIGH,
                rule_name="business_printer_issue",
                reason="Ticket matched a high-confidence business-impacting printer issue pattern.",
            )

        # Low: password reset/help
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
                [
                    "reset",
                    "forgot",
                    "change",
                    "update",
                    "unlock",
                    "locked",
                    "expired",
                    "can't remember",
                    "cannot remember",
                ],
            )
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.LOW,
                rule_name="password_help",
                reason="Ticket matched a high-confidence password help pattern.",
            )

        # Low: explicit software install request
        if self._contains_any(
            text,
            [
                "install chrome",
                "install teams",
                "install zoom",
                "install office",
                "install adobe",
                "software installation",
                "install software",
            ],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.LOW,
                rule_name="software_install_request",
                reason="Ticket matched a high-confidence software installation request pattern.",
            )

        # Low: common peripheral replacement/request
        if self._contains_any(
            text,
            [
                "keyboard replacement",
                "mouse replacement",
                "monitor replacement",
                "new keyboard",
                "new mouse",
                "new monitor",
                "replacement charger",
                "need a charger",
                "need a cable",
                "need a headset",
                "webcam request",
            ],
        ):
            return RuleEngineResult(
                matched=True,
                priority=TicketPriority.LOW,
                rule_name="hardware_request",
                reason="Ticket matched a high-confidence hardware or peripheral request pattern.",
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
