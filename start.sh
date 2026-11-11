#!/bin/sh
set -eu

uvicorn app.main:app --host 127.0.0.1 --port 8001 &
api_pid=$!

attempt=0
until python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8001/docs', timeout=2)" >/dev/null 2>&1; do
    if ! kill -0 "$api_pid" 2>/dev/null; then
        wait "$api_pid" || true
        echo "FastAPI exited before it became ready." >&2
        exit 1
    fi

    attempt=$((attempt + 1))
    if [ "$attempt" -ge 60 ]; then
        echo "Timed out waiting for FastAPI on port 8001." >&2
        kill "$api_pid" 2>/dev/null || true
        wait "$api_pid" 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

exec streamlit run frontend/app.py \
    --server.address 0.0.0.0 \
    --server.port "${PORT:-7860}" \
    --server.headless true \
    --browser.gatherUsageStats false
