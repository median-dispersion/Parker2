#!/bin/sh

# Exit immediately if a command returns a non-zero status
set -e

# Run gunicorn
gunicorn --bind $GUNICORN_HOST:$GUNICORN_PORT --workers $GUNICORN_WORKERS main:main