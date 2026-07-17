from pydantic import BaseModel


class JiraReporter(BaseModel):
    displayName: str


class JiraIssueFields(BaseModel):
    summary: str
    description: str
    reporter: JiraReporter


class JiraIssue(BaseModel):
    key: str
    fields: JiraIssueFields


class JiraWebhookEvent(BaseModel):
    webhookEvent: str
    issue: JiraIssue
