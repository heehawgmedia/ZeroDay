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

    # Google Search Console (can reuse GA4 service account if it has access)
    search_console_credentials_path: Optional[str] = None
    search_console_site_url: Optional[str] = None  # e.g. "https://mysite.com/"

    # Sentry
    sentry_auth_token: Optional[str] = None
    sentry_org: Optional[str] = None
    sentry_project: Optional[str] = None  # default project; sites can override

    # PageSpeed Insights (optional key for higher rate limits)
    pagespeed_api_key: Optional[str] = None

    # Poller schedule (seconds)
    poll_interval_seconds: int = 300     # health checks every 5 min
    sentry_interval_seconds: int = 900   # sentry every 15 min
    pagespeed_interval_seconds: int = 3600  # pagespeed every 1 hr

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
            "search_console": bool(self.search_console_credentials_path),
            "notion": bool(self.notion_token),
            "linear": bool(self.linear_api_key),
            "trello": bool(self.trello_api_key and self.trello_token),
            "sentry": bool(self.sentry_auth_token),
            "files": True,
        }


settings = Settings()
