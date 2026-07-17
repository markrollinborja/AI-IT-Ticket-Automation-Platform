class ApprovalPolicyResult:
    def __init__(
        self,
        approval_required: bool,
        reason: str | None = None,
    ):
        self.approval_required = approval_required
        self.reason = reason


class ApprovalPolicyService:
    """
    Determines whether a ticket needs human approval before the workflow is
    allowed to finalize (update Jira, send the completion notification).

    This is a risk check, not a classification - it runs independently of
    the Rule Engine / AI priority classification. Deterministic keyword
    matching over the ticket title/description, same approach as
    RuleEngine, kept intentionally simple: a handful of categories where
    letting automation act unsupervised is a real business risk, not an
    attempt at a full enterprise approval-routing matrix.
    """

    EXECUTIVE_REPORTERS = {
        "CEO",
        "CIO",
        "CTO",
        "Chief Executive Officer",
    }

    def evaluate(self, reporter: str, title: str, description: str) -> ApprovalPolicyResult:
        text = f"{title} {description}".lower()

        # Executive-impact: either the reporter *is* an executive, or the
        # ticket is filed on someone's behalf (e.g. IT desk logging "CEO
        # laptop won't boot"). Deliberately avoids bare "cio"/"cto" text
        # matching - those are short enough to collide with ordinary words
        # (e.g. "cto" is a substring of "doctor").
        if reporter in self.EXECUTIVE_REPORTERS or self._contains_any(
            text,
            [
                "ceo",
                "chief executive officer",
                "chief information officer",
                "chief technology officer",
                "executive laptop",
                "executive equipment",
            ],
        ):
            return ApprovalPolicyResult(
                approval_required=True,
                reason="Executive-impact request requires manager approval and asset tracking.",
            )

        # Production / business-wide outage: the fix itself may be
        # low-risk, but the response (emergency maintenance, overtime,
        # company-wide comms) is a business decision, not a technical one.
        if self._contains_any(
            text,
            [
                "production website",
                "prod website",
                "customer portal",
                "public website",
                "company-wide",
                "entire company",
            ],
        ) and self._contains_any(
            text,
            ["down", "outage", "unavailable", "cannot access", "unable to access"],
        ):
            return ApprovalPolicyResult(
                approval_required=True,
                reason=(
                    "Production or business-wide outage may trigger emergency maintenance, "
                    "overtime, or company-wide communication - requires manager awareness."
                ),
            )

        # Security-sensitive configuration changes. Deliberately avoids a
        # bare "port" keyword - it's a substring of common words like
        # "support" and "important".
        if self._contains_any(
            text,
            ["firewall", "open port", "security group", "acl rule", "network config"],
        ):
            return ApprovalPolicyResult(
                approval_required=True,
                reason=(
                    "Network or security configuration changes carry risk and must never "
                    "be applied automatically."
                ),
            )

        # Financial / payroll system access.
        if self._contains_any(text, ["payroll", "financial system", "financial data"]):
            return ApprovalPolicyResult(
                approval_required=True,
                reason="Access to financial or payroll systems requires approval due to data sensitivity.",
            )

        # Software purchases: not a technical risk, a spending decision.
        if self._contains_any(
            text,
            ["license", "subscription", "purchase order", "software purchase"],
        ):
            return ApprovalPolicyResult(
                approval_required=True,
                reason="Software purchases involve company spend and require approval.",
            )

        return ApprovalPolicyResult(approval_required=False)

    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(keyword in text for keyword in keywords)


approval_policy_service = ApprovalPolicyService()
