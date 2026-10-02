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
job_target_duration_seconds = int(os.getenv("JOB_TARGET_DURATION_SECONDS", "3600"))
job_update_interval_seconds = int(os.getenv("JOB_UPDATE_INTERVAL_SECONDS", "300"))
job_update_timeout_seconds = int(os.getenv("JOB_UPDATE_TIMEOUT_SECONDS", "600"))

# Job settings validation
# The minimum job size is 1
if job_minimum_size < 1:
    raise ValueError("Minimum job size too small")

# The minimum job size must smaller than the maximum job size
if job_minimum_size > job_maximum_size:
    raise ValueError("Minimum job size larger than maximum job size")

# The maximum job size can not be larger than an unsigned 64-Bit integer (2⁶⁴)
if job_maximum_size > 18446744073709551615:
    raise ValueError("Maximum job size too large")

# The job target duration must be at least 1 second long
if job_target_duration_seconds < 1:
    raise ValueError("Job target duration too short")

# The job update interval must be at least 1 second long
if job_update_interval_seconds < 1:
    raise ValueError("Job update interval too short")

# The job update interval must be shorter than the job timeout
if job_update_interval_seconds > job_update_timeout_seconds:
    raise ValueError("Job update interval longer than job timeout")

# The maximum job timeout can't be longer than a PostgreSQL bigint (2⁶⁴/2)
if job_update_timeout_seconds > 9223372036854775807:
    raise ValueError("Job timeout too long")