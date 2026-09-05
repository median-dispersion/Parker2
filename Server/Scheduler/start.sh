#!/bin/sh

# Run gunicorn in ASGI mode
gunicorn --bind "$SCHEDULER_HOST:$SCHEDULER_PORT" --workers $SCHEDULER_WORKERS --worker-class asgi main:main