"""
Unit tests for the Approval Policy Service.

Same philosophy as test_rule_engine.py: pure text-matching logic, no
database or network involved, so these are cheap and fast. Each case below
maps to one of the real-world examples the approval categories were
designed around (production outage, security-sensitive change, financial
access, executive impact, software spend) plus the routine tickets that
should NOT require approval.
"""

import pytest
from app.services.approval_policy_service import approval_policy_service

# Each case: (reporter, title, description, expected_required)
REQUIRES_APPROVAL_CASES = [
    pytest.param(
        "Jane Doe",
        "Production website is down",
        "Customers cannot place orders",
        id="production_outage",
    ),
    pytest.param(
        "Jane Doe",
        "Open port 3389 on the production firewall",
        "Need RDP access for a vendor",
        id="firewall_change",
    ),
    pytest.param(
        "Jane Doe",
        "Give John access to payroll",
        "He's covering for the payroll admin this week",
        id="payroll_access",
    ),
    pytest.param(
        "IT Help Desk",
        "CEO laptop won't boot",
        "Needs a replacement as soon as possible",
        id="executive_equipment_via_text",
    ),
    pytest.param(
        "CEO",
        "Need a new monitor",
        "Requesting a replacement monitor for my desk",
        id="executive_reporter",
    ),
    pytest.param(
        "Jane Doe",
        "Need Adobe Photoshop license",
        "For the new design hire",
        id="software_purchase",
    ),
]


@pytest.mark.parametrize("reporter, title, description", REQUIRES_APPROVAL_CASES)
def test_approval_required_for_risky_categories(reporter, title, description):
    result = approval_policy_service.evaluate(reporter=reporter, title=title, description=description)

    assert result.approval_required is True
    assert result.reason  # every approval-required result should explain why


NO_APPROVAL_CASES = [
    pytest.param(
        "Jane Doe", "Forgot my password", "Need help resetting access to my account", id="password_reset"
    ),
    pytest.param("Jane Doe", "Can't connect to VPN", "Getting a timeout from home", id="vpn_connectivity"),
]


@pytest.mark.parametrize("reporter, title, description", NO_APPROVAL_CASES)
def test_no_approval_required_for_routine_tickets(reporter, title, description):
    result = approval_policy_service.evaluate(reporter=reporter, title=title, description=description)

    assert result.approval_required is False


def test_approval_policy_avoids_common_word_false_positive():
    """
    'port' is a substring of 'support', and 'cto' is a substring of
    'doctor'. A naive bare-keyword match would wrongly flag routine tickets
    that happen to contain these words.
    """
    result = approval_policy_service.evaluate(
        reporter="Jane Doe",
        title="Need IT support",
        description="My doctor's office portal won't load on the guest wifi",
    )

    assert result.approval_required is False
