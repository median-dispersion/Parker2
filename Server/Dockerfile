# Base image
# Switch to debian:stable-slim once Debian 14 Forky including Python 3.14+ has been released
FROM debian:testing-slim

# Set environment variables
ENV PATH=$PATH:/Manager/.venv/bin
ENV MANAGER_HOST=0.0.0.0
ENV MANAGER_PORT=8000
ENV MANAGER_PROCESSES=1
ENV POSTGRES_HOST=0.0.0.0
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=database
ENV JOB_MINIMUM_SIZE=100000
ENV JOB_MAXIMUM_SIZE=100000000
ENV JOB_UPDATE_INTERVAL_SECONDS=300
ENV JOB_EXPIRATION_TIME_SECONDS=600

# Install system dependencies
RUN apt-get update
RUN apt-get install -y python3 python3-venv tini
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Setup working directory
WORKDIR /Manager
COPY Manager .
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