"""
Integration tests for the approve/reject endpoints.

These pick up where a gated workflow run leaves off: a ticket that
required approval (via the webhook) sits in `pending_approval` with Jira
already set to "Pending". These tests exercise what happens next - a real
decision, made through POST /workflow-runs/{id}/approve or /reject,
against the real (test) database.
"""

from app.models.approval import Approval
from app.models.ticket import Ticket
from app.models.workflow_run import WorkflowRun


def jira_webhook_payload(key: str, summary: str, description: str, reporter: str) -> dict:
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


def _create_gated_workflow_run(client, key: str) -> str:
    """
    Files a ticket that requires approval (a security-sensitive firewall
    change) and returns its workflow_run_id.

    This text doesn't match any Rule Engine pattern, so classification
    falls through to AI - mock_jira_and_slack mocks that too, returning a
    fixed "high" result (see conftest.py). An outage ticket would be the
    wrong choice here on purpose: outages are urgent and must NOT be
    gated, see test_webhook_completes_critical_outage_without_approval_gate
    in test_webhook_jira.py.
    """
    payload = jira_webhook_payload(
        key=key,
        summary="Open port 3389 on the production firewall",
        description="Need RDP access for a vendor",
        reporter="Jane Doe",
    )

    response = client.post("/webhooks/jira", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "pending_approval"
    assert response.json()["classified_priority"] == "high"

    return response.json()["jira_issue_key"]


def test_approve_resumes_workflow_and_pushes_real_priority_to_jira(client, db_session, mock_jira_and_slack):
    _create_gated_workflow_run(client, key="IT-201")

    workflow_run = db_session.query(WorkflowRun).join(Ticket).filter(Ticket.jira_issue_key == "IT-201").one()

    # The gate step already made one Jira call (set to "Pending") and sent
    # one Slack message - reset the recorders so we only assert on what
    # the approve call itself does.
    mock_jira_and_slack.jira_calls.clear()
    mock_jira_and_slack.slack_messages.clear()

    response = client.post(
        f"/workflow-runs/{workflow_run.id}/approve",
        json={"decided_by": "network-manager@example.com", "decision_notes": "Vendor access confirmed."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"

    # Approving should push the real classified priority, not "Pending".
    assert len(mock_jira_and_slack.jira_calls) == 1
    assert mock_jira_and_slack.jira_calls[0]["issue_key"] == "IT-201"
    assert "priority_name" not in mock_jira_and_slack.jira_calls[0]
    assert len(mock_jira_and_slack.slack_messages) == 1

    db_session.refresh(workflow_run)
    assert workflow_run.status == "completed"

    approval = db_session.query(Approval).filter(Approval.workflow_run_id == workflow_run.id).one()
    assert approval.status == "approved"
    assert approval.decided_by == "network-manager@example.com"
    assert approval.decided_at is not None


def test_reject_marks_workflow_rejected_and_syncs_jira(client, db_session, mock_jira_and_slack):
    _create_gated_workflow_run(client, key="IT-202")

    workflow_run = db_session.query(WorkflowRun).join(Ticket).filter(Ticket.jira_issue_key == "IT-202").one()

    mock_jira_and_slack.jira_calls.clear()
    mock_jira_and_slack.slack_messages.clear()

    response = client.post(
        f"/workflow-runs/{workflow_run.id}/reject",
        json={
            "decided_by": "network-manager@example.com",
            "decision_notes": "Not approved - use the VPN instead.",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

    assert len(mock_jira_and_slack.jira_calls) == 1
    assert mock_jira_and_slack.jira_calls[0]["priority_name"] == "Rejected"
    assert len(mock_jira_and_slack.slack_messages) == 1

    db_session.refresh(workflow_run)
    assert workflow_run.status == "rejected"
    assert workflow_run.completed_at is not None

    approval = db_session.query(Approval).filter(Approval.workflow_run_id == workflow_run.id).one()
    assert approval.status == "rejected"
    assert approval.decision_notes == "Not approved - use the VPN instead."


def test_approve_returns_404_for_unknown_workflow_run(client):
    response = client.post(
        "/workflow-runs/00000000-0000-0000-0000-000000000000/approve",
        json={"decided_by": "someone@example.com"},
    )

    assert response.status_code == 404


def test_approve_returns_409_when_not_pending_approval(client, db_session, mock_jira_and_slack):
    """A ticket that never needed approval is already 'completed' -
    approving it doesn't make sense and should be rejected clearly."""
    payload = jira_webhook_payload(
        key="IT-203",
        summary="Forgot my password",
        description="Need help resetting access to my account",
        reporter="Jane Doe",
    )
    client.post("/webhooks/jira", json=payload)

    workflow_run = db_session.query(WorkflowRun).join(Ticket).filter(Ticket.jira_issue_key == "IT-203").one()

    response = client.post(
        f"/workflow-runs/{workflow_run.id}/approve",
        json={"decided_by": "someone@example.com"},
    )

    assert response.status_code == 409
