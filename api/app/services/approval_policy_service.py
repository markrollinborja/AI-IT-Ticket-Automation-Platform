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

    Design principle: approval blocks actions that are risky *and can
    wait* - never anything urgent. An incident being Critical is exactly
    why it should NOT be gated: the whole value of a fast priority
    classification is a fast response, and holding it for a human
    signature works against that. Gating only makes sense where waiting
    doesn't cost anything real - changing security posture or spending
    company money can sit for an hour without harm, so a human should
    sign off before automation acts.

    This mirrors how real IT service management works: incident response
    gets an expedited path (ITIL's "emergency change"), while security and
    financial changes go through normal approval. Earlier versions of this
    service also gated executive-impact requests and outages - both were
    reconsidered and removed for exactly this reason: identity and urgency
    aren't good approval signals, risk-that-can-wait is.

    Deterministic keyword matching over the ticket title/description, same
    approach as RuleEngine, kept intentionally simple: a handful of
    categories, not an attempt at a full enterprise approval-routing
    matrix. See project-decisions.md, Decision #9.
    """

    def evaluate(self, title: str, description: str) -> ApprovalPolicyResult:
        text = f"{title} {description}".lower()

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
