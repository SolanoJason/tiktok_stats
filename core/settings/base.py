from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from fastapi.templating import Jinja2Templates

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        frozen=True,
        extra="ignore"
    )

    DB_DRIVER: str = "postgresql+psycopg"
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    APIFY_API_KEY: str
    APIFY_TIKTOK_SCRAPER_ACTOR_ID: str

    TEMPLATES_DIR: str = "templates"
    STATIC_DIR: str = "static"

    @property
    def templates(self) -> Jinja2Templates:
        return Jinja2Templates(directory=self.TEMPLATES_DIR)

settings = Settings()