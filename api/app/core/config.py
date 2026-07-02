from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI IT Ticket Automation Platform API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str

    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_project_key: str

    slack_webhook_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()