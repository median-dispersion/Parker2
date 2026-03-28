# Create a new build stage from the official python base image
FROM python:latest

# Change the working directory
WORKDIR /Client

# Copy files
COPY ./Search ./Search
COPY ./Worker ./Worker

# Install dependencies
RUN apt-get update && apt-get install -y tini build-essential
RUN pip install --no-cache-dir -r ./Worker/requirements.txt

# Build search binary
RUN make -C ./Search

# Change into the worker directory
WORKDIR ./Worker

# Disable pythons print buffering
ENV PYTHONUNBUFFERED=1

# Default entrypoint
ENTRYPOINT ["tini", "--"]
CMD ["python", "main.py"]