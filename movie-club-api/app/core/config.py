import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_VERSION: str = "0.1.0"
    API_TITLE: str = "Movie Club API"
    API_DESCRIPTION: str = "API for the Movie Club application"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    
    model_config = {
        "env_file": ".env"
    }

settings = Settings()
