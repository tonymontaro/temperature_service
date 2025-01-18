#!/usr/bin/env sh

set -e

alembic upgrade head

if [ "$ENVIRONMENT" = "local" ]; then
    exec uvicorn --host 0.0.0.0 --port 8000 main:app --reload
else
    exec uvicorn --host 0.0.0.0 --port 8000 main:app
fi
