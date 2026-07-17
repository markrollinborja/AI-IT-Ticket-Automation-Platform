"""
Unit tests for the Rule Engine.

These tests deliberately avoid touching the database, network, or any
external service. The Rule Engine is pure text-matching logic, so it's the
cheapest and most reliable place in the codebase to start building test
coverage: no mocking required, fast to run, and it locks in the exact
business rules described in docs/16-ai-classification-strategy.md.

Each case below documents which keyword combination it's meant to exercise,
so a failing test tells you immediately which rule broke.
"""

import pytest
from app.schemas.ticket import TicketPriority
from app.services.rule_engine import rule_engine


def make_ticket(title: str, description: str):
    """Small helper so each test case only has to specify what varies."""
    from app.schemas.ticket import TicketCreate

    return TicketCreate(title=title, description=description, created_by="test-user")


# Each case: (title, description, expected_priority, expected_rule_name)
MATCHING_CASES = [
    pytest.param(
        "Customer portal is unavailable",
        "Customers cannot access the login page",
        TicketPriority.CRITICAL,
        "critical_customer_facing_outage",
        id="critical_customer_facing_outage",
    ),
    pytest.param(
        "Entire company network down",
        "All employees are affected across every department",
        TicketPriority.CRITICAL,
        "critical_business_wide_outage",
        id="critical_business_wide_outage",
    ),
    pytest.param(
        "Suspicious email reported",
        "A user forwarded a phishing attempt from an external sender",
        TicketPriority.CRITICAL,
        "security_incident",
        id="security_incident",
    ),
    pytest.param(
        "VPN not working",
        "Unable to connect to the VPN from home",
        TicketPriority.HIGH,
        "vpn_issue",
        id="vpn_issue",
    ),
    pytest.param(
        "User locked out of account",
        "Cannot access the system after several failed attempts",
        TicketPriority.HIGH,
        "login_or_access_issue",
        id="login_or_access_issue",
    ),
    pytest.param(
        "Outlook is not receiving emails",
        "Mailbox appears unavailable since this morning",
        TicketPriority.HIGH,
        "email_service_issue",
        id="email_service_issue",
    ),
    pytest.param(
        "Printer offline in the front desk area",
        "Cannot print any documents since this morning",
        TicketPriority.HIGH,
        "business_printer_issue",
        id="business_printer_issue",
    ),
    pytest.param(
        "Forgot my password",
        "Need help resetting access to my account",
        TicketPriority.LOW,
        "password_help",
        id="password_help",
    ),
    pytest.param(
        "Please install Zoom for a new hire",
        "Needed before their onboarding call tomorrow",
        TicketPriority.LOW,
        "software_install_request",
        id="software_install_request",
    ),
    pytest.param(
        "Need a new mouse",
        "The old one stopped clicking properly",
        TicketPriority.LOW,
        "hardware_request",
        id="hardware_request",
    ),
]


@pytest.mark.parametrize("title, description, expected_priority, expected_rule_name", MATCHING_CASES)
def test_rule_engine_matches_expected_pattern(title, description, expected_priority, expected_rule_name):
    ticket = make_ticket(title, description)

    result = rule_engine.evaluate_ticket(ticket)

    assert result.matched is True
    assert result.priority == expected_priority
    assert result.rule_name == expected_rule_name
    assert result.reason  # every matched result should explain itself


def test_rule_engine_falls_through_to_ai_when_no_rule_matches():
    """
    Ambiguous tickets must NOT be force-matched by a rule. This is the
    behavior that keeps the Rule Engine safe: when in doubt, defer to AI
    classification instead of guessing.
    """
    ticket = make_ticket(
        "Question about shared calendar visibility",
        "Not urgent, just curious how to let teammates see my availability",
    )

    result = rule_engine.evaluate_ticket(ticket)

    assert result.matched is False
    assert result.priority is None
    assert result.rule_name is None


def test_rule_engine_is_case_insensitive():
    """Ticket text casing shouldn't affect whether a rule matches."""
    ticket = make_ticket("FORGOT MY PASSWORD", "PLEASE RESET IT")

    result = rule_engine.evaluate_ticket(ticket)

    assert result.matched is True
    assert result.rule_name == "password_help"
