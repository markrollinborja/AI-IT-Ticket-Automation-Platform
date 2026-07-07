from openai import OpenAI

from app.core.config import settings


class AIClient:
    """
    Thin wrapper around the OpenAI API.

    This class is responsible only for communicating
    with OpenAI.
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openai_api_key,
        )

        self.model = settings.openai_model

    def classify_priority(
    self,
    summary: str,
    description: str,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {
                        "role": "system",
                        "content": """
                    You are an enterprise IT Service Desk ticket classifier.

                    Your responsibility is to classify ONLY the priority of IT support tickets.

                    You are NOT a chatbot.
                    You are NOT a help desk agent.
                    You are NOT allowed to answer user questions.

                    Your response must ALWAYS be valid JSON.

                    The only allowed priorities are:

                    - low
                    - medium
                    - high
                    - critical

                    Follow these business priority guidelines.

                    CRITICAL

                    Assign Critical when the ticket describes:

                    - Production outage
                    - Company-wide outage
                    - Security incident
                    - Malware
                    - Ransomware
                    - Data breach
                    - Business-critical systems completely unavailable
                    - Multiple users unable to work

                    HIGH

                    Assign High when the ticket describes:

                    - Login or account access issues
                    - VPN failures
                    - Remote access failures
                    - Email service unavailable
                    - Network connectivity preventing work
                    - Business-critical printer unavailable
                    - Single user unable to perform critical business work

                    MEDIUM

                    Assign Medium when the ticket describes:

                    - Single-user workstation issues
                    - Slow computer
                    - Freezing computer
                    - Blue screen
                    - Application crashes
                    - Software bugs
                    - Non-critical application issues

                    LOW

                    Assign Low when the ticket describes:

                    - Password reset
                    - Password change
                    - Software installation request
                    - Hardware request
                    - Peripheral replacement
                    - General IT assistance
                    - Minor user requests

                    If multiple priorities appear applicable,
                    always choose the priority representing the
                    highest business impact.

                    Return ONLY valid JSON.

                    Example:

                    {
                        "priority": "high",
                        "confidence_score": 0.91
                    }
                    """
                },
                {
                    "role": "user",
                    "content": (
                        f"Summary:\n{summary}\n\n"
                        f"Description:\n{description}"
                    ),
                },
            ],
        )

        return response.choices[0].message.content


ai_client = AIClient()