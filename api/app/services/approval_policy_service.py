class ApprovalPolicyResult:
    def __init__(
        self,
        approval_required: bool,
        reason: str | None = None,
    ):
        self.approval_required = approval_required
        self.reason = reason


class ApprovalPolicyService:
    EXECUTIVE_REPORTERS = {
        "CEO",
        "CIO",
        "CTO",
        "Chief Executive Officer",
    }

    def evaluate(self, reporter: str) -> ApprovalPolicyResult:
        if reporter in self.EXECUTIVE_REPORTERS:
            return ApprovalPolicyResult(
                approval_required=True,
                reason="Executive user request requires human approval.",
            )

        return ApprovalPolicyResult(approval_required=False)


approval_policy_service = ApprovalPolicyService()
