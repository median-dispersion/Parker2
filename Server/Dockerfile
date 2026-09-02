# Base image
FROM debian:stable-slim

# Setup environment variables
ENV PATH="/Scheduler/.venv/bin:$PATH"
ENV SERVER_HOST="0.0.0.0"
ENV SERVER_PORT=8000
ENV SERVER_WORKERS=1

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