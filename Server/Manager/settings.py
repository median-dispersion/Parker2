import os

# PostgreSQL settings
postgresql_host = os.getenv("POSTGRES_HOST", "0.0.0.0")
postgresql_port = os.getenv("POSTGRES_PORT", "5432")
postgresql_user = os.getenv("POSTGRES_USER", "user")
postgresql_password = os.getenv("POSTGRES_PASSWORD", "password")
postgresql_database = os.getenv("POSTGRES_DB", "database")

# Job settings
job_minimum_size = int(os.getenv("JOB_MINIMUM_SIZE", "100000"))
job_maximum_size = int(os.getenv("JOB_MAXIMUM_SIZE", "100000000"))
job_update_interval_seconds = int(os.getenv("JOB_UPDATE_INTERVAL_SECONDS", "300"))
job_expiration_time_seconds = int(os.getenv("JOB_EXPIRATION_TIME_SECONDS", "600"))