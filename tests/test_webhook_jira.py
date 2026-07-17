"""
Integration tests for the Jira webhook endpoint.

These exercise the real workflow end-to-end: webhook validation, ticket
persistence, Rule Engine classification, workflow run tracking, and audit
logging, all against the real (test) database via the `client` and
`db_session` fixtures from conftest.py.

The only things faked are the outbound HTTP calls to Jira and Slack (see
`mock_jira_and_slack` in conftest.py) - everything else in this request
path is the app's real code.
"""

from app.models.ticket import Ticket
from app.models.workflow_run import WorkflowRun


def jira_webhook_payload(key: str, summary: str, description: str, reporter: str) -> dict:
    """Builds a minimal, valid Jira webhook payload matching app/schemas/jira.py."""
    return {
        "webhookEvent": "jira:issue_created",
        "issue": {
            "key": key,
            "fields": {
                "summary": summary,
                "description": description,
                "reporter": {"displayName": reporter},
            },
        },
    }


def test_webhook_classifies_via_rule_engine_and_completes_workflow(client, db_session, mock_jira_and_slack):
    payload = jira_webhook_payload(
        key="IT-101",
        summary="Forgot my password",
        description="Need help resetting access to my account",
        reporter="Jane Doe",
    )

    response = client.post("/webhooks/jira", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["priority"] == "low"
    assert body["classification_source"] == "rule_engine"

    # "Forgot my password" matches a Rule Engine pattern, so this ticket
    # should never reach the AI classification path - it should go
    # straight to updating Jira and notifying Slack.
    assert len(mock_jira_and_slack.jira_calls) == 1
    assert mock_jira_and_slack.jira_calls[0]["issue_key"] == "IT-101"
    assert len(mock_jira_and_slack.slack_messages) == 1

    ticket = db_session.query(Ticket).filter(Ticket.jira_issue_key == "IT-101").one()
    assert ticket.title == "Forgot my password"

    workflow_run = db_session.query(WorkflowRun).filter(WorkflowRun.ticket_id == ticket.id).one()
    assert workflow_run.status == "completed"
    assert workflow_run.final_priority == "low"


def test_webhook_requires_approval_for_executive_reporter(client, db_session, mock_jira_and_slack):
    payload = jira_webhook_payload(
        key="IT-102",
        summary="Need a new monitor",
        description="Requesting a replacement monitor for my desk",
        reporter="CEO",
    )

    response = client.post("/webhooks/jira", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending_approval"
    assert body["approval_required"] is True

    # The approval policy short-circuits the workflow before classification
    # runs, so Jira should never be touched here - only the Slack
    # "approval required" notification goes out.
    assert len(mock_jira_and_slack.jira_calls) == 0
    assert len(mock_jira_and_slack.slack_messages) == 1

    workflow_run = db_session.query(WorkflowRun).join(Ticket).filter(Ticket.jira_issue_key == "IT-102").one()
    assert workflow_run.status == "pending_approval"
    assert workflow_run.approval_required is True


def test_webhook_rejects_unsupported_event_type(client, mock_jira_and_slack):
    """
    Validation should reject the request before any workflow logic runs.
    No mocking of DB state needed here - if this passes, nothing should
    have been written or sent anywhere.
    """
    payload = jira_webhook_payload(
        key="IT-103",
        summary="Irrelevant",
        description="Irrelevant",
        reporter="Jane Doe",
    )
    payload["webhookEvent"] = "jira:issue_updated"

    response = client.post("/webhooks/jira", json=payload)

    assert response.status_code == 400
    assert len(mock_jira_and_slack.jira_calls) == 0
    assert len(mock_jira_and_slack.slack_messages) == 0
