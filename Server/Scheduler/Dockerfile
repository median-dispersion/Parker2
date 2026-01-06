# Create a new build stage from the official python base image
FROM python:latest

# Change the working directory
WORKDIR /Scheduler

# Copy files
COPY ./ ./

# Install dependencies
RUN apt-get update && apt-get install -y tini
RUN pip install --no-cache-dir -r requirements.txt

# Disable pythons print buffering
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8000

# Default entrypoint
ENTRYPOINT ["tini", "--"]
CMD ["python", "main.py"]