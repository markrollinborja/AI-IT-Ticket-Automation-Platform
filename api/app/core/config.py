from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI IT Ticket Automation Platform API"
    app_version: str = "0.1.0"

    # Literal instead of a plain str: a typo like "producton" used to be
    # silently accepted and just... be wrong, possibly for a while before
    # anyone noticed. Now it fails at startup, with a clear pydantic
    # validation error, instead of failing silently at some unknown point
    # later.
    environment: Literal["development", "staging", "production"] = "development"

    # Configurable instead of hardcoded in core/logging.py, so log
    # verbosity can differ between local dev (DEBUG) and a deployed
    # environment (INFO/WARNING) without a code change.
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"

    database_url: str

    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_project_key: str

    slack_webhook_url: str

    # OpenAI
    openai_api_key: str
    openai_model: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
