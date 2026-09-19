#!/bin/sh

# Exit immediately if a command returns a non-zero status
set -e

# Run Gunicorn
gunicorn --bind $MANAGER_HOST:$MANAGER_PORT --workers $MANAGER_PROCESSES main:main