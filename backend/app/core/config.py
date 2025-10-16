"""
Application configuration
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    VERSION: str = "0.1.0"
    APP_NAME: str = "Fantasy Basketball Oracle"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    # Yahoo Fantasy API
    YAHOO_CONSUMER_KEY: str = ""
    YAHOO_CONSUMER_SECRET: str = ""
    YAHOO_LEAGUE_ID: str = ""
    
    # League Settings
    LEAGUE_SIZE: int = 10
    MAX_ACQUISITIONS_PER_WEEK: int = 5
    PLAYOFF_WEEKS: List[int] = [20, 21, 22]
    IST_WEEKS: List[int] = [5, 6, 7, 8, 9]
    
    # Roster Positions
    ROSTER_POSITIONS: dict = {
        "PG": 1,
        "SG": 1,
        "G": 1,
        "SF": 1,
        "PF": 1,
        "F": 1,
        "C": 1,
        "UTIL": 3,
        "BENCH": 3,
        "IL": 2,
        "IL+": 1
    }
    
    # Categories (9-cat league)
    CATEGORIES: List[str] = [
        "FG%",
        "FT%",
        "3PM",
        "PTS",
        "REB",
        "AST",
        "STL",
        "BLK",
        "TO"
    ]
    
    # Categories where higher is worse
    NEGATIVE_CATEGORIES: List[str] = ["TO"]
    
    # Percentage categories (require special handling)
    PERCENTAGE_CATEGORIES: List[str] = ["FG%", "FT%"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./oracle.db"
    
    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()
