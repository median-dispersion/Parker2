from pydantic_settings import BaseSettings
from pydantic import computed_field
from pathlib import Path

# Define settings class
class Settings(BaseSettings):

    # Search binary settings
    search_binary_path: Path = "../Search/main"

# Create settings instance
settings = Settings()