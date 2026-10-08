# Base image
FROM debian:stable-slim

# Set environment variables
ENV PATH=$PATH:/Client/Worker/.venv/bin

# Install system dependencies
RUN apt-get update
RUN apt-get install -y make g++ libgmp-dev python3 python3-venv tini
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Setup working directory
WORKDIR /Client
COPY Search Search
COPY Worker Worker
RUN find -type d -name .venv -prune -exec rm -rf {} +
RUN find -type d -name __pycache__ -prune -exec rm -rf {} +

# Build search binary
WORKDIR /Client/Search
RUN make clean
RUN make -j$(nproc)
RUN rm -rf Build Include Libraries Source Makefile

# Install python dependencies
WORKDIR /Client/Worker
RUN python3 -m venv .venv
RUN pip install --no-cache-dir -r requirements.txt
RUN rm -rf requirements.txt

# Setup start script
RUN chmod +x start.sh

# Container entrypoint
ENTRYPOINT ["tini", "--"]
CMD ["./start.sh"]