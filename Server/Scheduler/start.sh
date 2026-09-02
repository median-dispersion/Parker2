#!/bin/sh

# Run gunicorn in ASGI mode
gunicorn --bind "$SERVER_HOST:$SERVER_PORT" --workers $SERVER_WORKERS --worker-class asgi main:main