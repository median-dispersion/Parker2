from pydantic_settings import BaseSettings
from pydantic import computed_field

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

    # SQLAlchemy settings
    sqlalchemy_dialect: str = "postgresql"
    sqlalchemy_driver: str = "asyncpg"

    # Compute SQLAlchemy url
    @computed_field
    @property
    def sqlalchemy_url(self) -> str:

        return (
            f"{self.sqlalchemy_dialect}+{self.sqlalchemy_driver}://"
            f"{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/"
            f"{self.postgres_db}"
        )

# Create settings instance
settings = Settings()