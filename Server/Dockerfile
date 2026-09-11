# Base image
# Switch to debian:stable-slim once Debian 14 Forky including Python 3.14+ has been released
FROM debian:testing-slim

# Setup environment variables
ENV PATH="/Scheduler/.venv/bin:$PATH"
ENV POSTGRES_HOST=postgresql
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=database
ENV SCHEDULER_HOST=0.0.0.0
ENV SCHEDULER_PORT=8000
ENV SCHEDULER_WORKERS=1

# Install system dependencies
RUN apt-get update
RUN apt-get install -y python3 python3-venv tini
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Setup working directory
WORKDIR /Scheduler
COPY Scheduler .
RUN find -type d -name .venv -prune -exec rm -rf {} +
RUN find -type d -name __pycache__ -prune -exec rm -rf {} +

# Install python dependencies
RUN python3 -m venv .venv
RUN pip install --no-cache-dir -r requirements.txt
RUN rm -rf requirements.txt

# Setup start script
RUN chmod +x start.sh

# Container entrypoint
ENTRYPOINT ["tini", "--"]
CMD ["./start.sh"]