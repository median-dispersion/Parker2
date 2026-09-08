#!/bin/sh

# Run gunicorn
gunicorn --bind "$SCHEDULER_HOST:$SCHEDULER_PORT" --workers $SCHEDULER_WORKERS main:main