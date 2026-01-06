from pydantic_settings import BaseSettings

# Define settings class
class Settings(BaseSettings):

    # PostgreSQL settings
    postgres_user: str = "user"
    postgres_password: str = "password"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "database"

    # FastAPI settings
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_workers: int = 1

# Create settings instance
settings = Settings()