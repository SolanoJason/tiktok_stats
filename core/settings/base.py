from pydantic_settings import BaseSettings, SettingsConfigDict

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

settings = Settings()