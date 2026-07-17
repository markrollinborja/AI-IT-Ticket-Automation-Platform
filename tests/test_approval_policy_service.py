"""
Unit tests for the Approval Policy Service.

Same philosophy as test_rule_engine.py: pure text-matching logic, no
database or network involved, so these are cheap and fast.

The design principle under test: approval blocks actions that are risky
*and can wait* (security-sensitive changes, financial/payroll access,
software purchases) - it never blocks anything urgent, no matter how
severe. That's why "production outage" and "executive-impact" cases
appear in NO_APPROVAL_CASES below, not REQUIRES_APPROVAL_CASES - an
earlier version of this service gated both, and that was a mistake: an
outage being Critical is exactly why it shouldn't wait on a human
signature. See project-decisions.md, Decision #9.
"""

import pytest
from app.services.approval_policy_service import approval_policy_service

# Each case: (title, description)
REQUIRES_APPROVAL_CASES = [
    pytest.param(
        "Open port 3389 on the production firewall",
        "Need RDP access for a vendor",
        id="firewall_change",
    ),
    pytest.param(
        "Give John access to payroll",
        "He's covering for the payroll admin this week",
        id="payroll_access",
    ),
    pytest.param(
        "Need Adobe Photoshop license",
        "For the new design hire",
        id="software_purchase",
    ),
]


@pytest.mark.parametrize("title, description", REQUIRES_APPROVAL_CASES)
def test_approval_required_for_risky_categories(title, description):
    result = approval_policy_service.evaluate(title=title, description=description)

    assert result.approval_required is True
    assert result.reason  # every approval-required result should explain why


NO_APPROVAL_CASES = [
    pytest.param("Forgot my password", "Need help resetting access to my account", id="password_reset"),
    pytest.param("Can't connect to VPN", "Getting a timeout from home", id="vpn_connectivity"),
    pytest.param(
        "Production website is down",
        "Customers cannot place orders",
        id="production_outage_is_urgent_not_gated",
    ),
    pytest.param(
        "CEO laptop won't boot",
        "Needs a replacement as soon as possible",
        id="executive_impact_is_not_gated",
    ),
]


@pytest.mark.parametrize("title, description", NO_APPROVAL_CASES)
def test_no_approval_required_for_routine_or_urgent_tickets(title, description):
    result = approval_policy_service.evaluate(title=title, description=description)

    assert result.approval_required is False


def test_approval_policy_avoids_common_word_false_positive():
    """
    'port' is a substring of 'support'. A naive bare-keyword match would
    wrongly flag routine tickets that happen to contain that word.
    """
    result = approval_policy_service.evaluate(
        title="Need IT support",
        description="My office portal won't load on the guest wifi",
    )

    assert result.approval_required is False
