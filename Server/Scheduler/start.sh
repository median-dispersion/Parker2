#!/bin/sh

# Stop the script if any command returns a nonzero exit status
set -e

# Initialize everything
python main.py initialize

# Run gunicorn
gunicorn --bind "$SCHEDULER_HOST:$SCHEDULER_PORT" --workers $SCHEDULER_WORKERS main:main