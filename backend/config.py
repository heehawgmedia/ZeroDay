from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    anthropic_api_key: str = ""

    # GitHub
    github_token: Optional[str] = None
    github_username: Optional[str] = None

    # Google Analytics
    ga_property_id: Optional[str] = None
    ga_credentials_path: Optional[str] = None

    # Notion
    notion_token: Optional[str] = None
    notion_database_ids: Optional[str] = None  # comma-separated

    # Linear
    linear_api_key: Optional[str] = None

    # Trello
    trello_api_key: Optional[str] = None
    trello_token: Optional[str] = None

    # Files — comma-separated base paths Jarvis may read
    allowed_file_paths: str = "."

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def allowed_paths(self) -> list[str]:
        return [p.strip() for p in self.allowed_file_paths.split(",") if p.strip()]

    def integration_status(self) -> dict[str, bool]:
        return {
            "github": bool(self.github_token),
            "google_analytics": bool(self.ga_property_id and self.ga_credentials_path),
            "notion": bool(self.notion_token),
            "linear": bool(self.linear_api_key),
            "trello": bool(self.trello_api_key and self.trello_token),
            "files": True,
        }


settings = Settings()
