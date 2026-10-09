import os
import re

# Worker settings
worker_name = os.getenv("WORKER_NAME", "Worker")
worker_threads = int(os.getenv("WORKER_THREADS", "1"))

# Worker settings validation
# The worker name must be at least 1 character long
if len(worker_name) < 1:
    raise ValueError("Worker name too short")

# The worker name can be at most 64 characters long
if len(worker_name) > 64:
    raise ValueError("Worker name too long")

# Raise an exception if the worker name contains illegal characters
if not re.fullmatch("[a-zA-Z0-9-]+", worker_name):
    raise ValueError("Illegal characters in name")

# There must be at least 1 worker thread
if worker_threads < 1:
    raise ValueError("Too few worker threads")

# The can be at most 1 worker thread per CPU core
if worker_threads > (os.cpu_count() or 1):
    raise ValueError("Too many worker threads")

# Manager settings
manager_host = os.getenv("MANAGER_HOST", "0.0.0.0")
manager_port = os.getenv("MANAGER_PORT", "8000")
manager_protocol = os.getenv("MANAGER_PROTOCOL", "http")
manager_url = f"{manager_protocol}://{manager_host}:{manager_port}"

# Manager settings validation
if manager_protocol not in ["http", "https"]:
    raise ValueError("Invalid manager protocol")