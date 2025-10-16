from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://redis:6379/0"
    API_SECRET_KEY: str
    ENV: str = "dev"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001

    YAHOO_CLIENT_ID: str
    YAHOO_CLIENT_SECRET: str
    YAHOO_REDIRECT_URI: str
    YAHOO_SCOPE: str = "openid fspt-r"

settings = Settings()