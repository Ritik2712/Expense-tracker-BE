#!/bin/sh
set -e

required_vars="DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT SECRET_KEY ALGORITHM ACCESS_TOKEN_EXPIRE_MINUTES"
for var in $required_vars; do
  eval "value=\${$var}"
  if [ -z "$value" ]; then
    echo "Missing required environment variable: $var" >&2
    exit 1
  fi
done

# Run FastAPI app only. PostgreSQL must run as a separate service/container.
exec uvicorn main:app --host 0.0.0.0 --port "${APP_PORT:-8000}"
