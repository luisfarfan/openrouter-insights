from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings and Environment Variables."""
    
    # Project Info
    PROJECT_NAME: str = "LLMIndex"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # API Keys (Supports both underscored and non-underscored versions)
    OPENROUTER_API_KEY: str = Field("not-set", validation_alias=AliasChoices("OPENROUTER_API_KEY"))
    ARTIFICIAL_ANALYSIS_API_KEY: str = Field(
        "not-set", 
        validation_alias=AliasChoices("ARTIFICIAL_ANALYSIS_API_KEY", "ARTIFICIALANALYSIS_API_KEY")
    )

    # API Endpoints
    OPENROUTER_MODELS_URL: str = "https://openrouter.ai/api/v1/models"
    ARTIFICIAL_ANALYSIS_MODELS_URL: str = "https://artificialanalysis.ai/api/v2/data/llms/models"

    # Database
    DATABASE_URL: str = "sqlite:///./data/openrouter_insights.sqlite"

    # API Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

@lru_cache()
def get_settings() -> Settings:
    return Settings()
