from pydantic_settings import BaseSettings
from pathlib import Path
from pydantic import computed_field

# Define settings class
class Settings(BaseSettings):

    # Search settings
    search_binary_path: Path = "../Search/main"
    search_duration_seconds: int = 300

    # Request settings
    request_attempts: int = 10
    request_timeout_seconds: int = 30
    request_attempt_delay_seconds: int = 1

    # Server settings
    server_protocol: str = "http"
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # Compute server url
    @computed_field
    @property
    def server_url(self) -> str:
        return f"{self.server_protocol}://{self.server_host}:{self.server_port}"

# Create settings instance
settings = Settings()