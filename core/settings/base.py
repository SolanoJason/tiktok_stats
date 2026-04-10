from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        frozen=True,
        extra="ignore"
    )

    DEBUG: bool

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
        templates = Jinja2Templates(directory=self.TEMPLATES_DIR)
        
        @pass_context
        def custom_url_for(context, name, **path_params):
            request = context.get('request')
            url = request.url_for(name, **path_params)
            if not self.DEBUG:
                url = url.replace(port=81)
            return str(url)
        
        templates.env.globals['url_for'] = custom_url_for
        return templates

settings = Settings() # type: ignore