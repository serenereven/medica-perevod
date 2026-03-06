#!/bin/sh
set -e

if [ -n "${DB_HOST:-}" ]; then
  echo "Waiting for DB ${DB_HOST}:${DB_PORT:-5432}..."
  python - <<'PY'
import os, socket, time, sys
host=os.getenv("DB_HOST")
port=int(os.getenv("DB_PORT","5432"))
deadline=time.time()+30
while time.time()<deadline:
    try:
        with socket.create_connection((host,port),timeout=2):
            print("DB is up")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print("DB not reachable in time")
sys.exit(1)
PY
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"