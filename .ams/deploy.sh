#!/bin/sh
# Deploy the pilot shop on this host. Run from the repository root:
#     AMS_DEPLOY_COMMIT=<sha> sh .ams/deploy.sh
# An empty AMS_DEPLOY_COMMIT deploys origin/main. Running it again redeploys.
set -eu

RUN_DIR=.ams/run
PIDFILE="$RUN_DIR/pilot.pid"
LOGFILE="$RUN_DIR/pilot.log"
PORT="${PILOT_PORT:-8765}"
HEALTH_TIMEOUT=20

if [ ! -e .git ] || [ ! -d pilot ]; then
    echo "deploy: run this from the repository root" >&2
    exit 1
fi

git fetch origin
git checkout --detach "${AMS_DEPLOY_COMMIT:-origin/main}"
mkdir -p "$RUN_DIR"

# Stop the running server, found by its pidfile only.
if [ -f "$PIDFILE" ]; then
    pid=$(cat "$PIDFILE")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null \
        && ps -p "$pid" -o args= | grep -q 'serve\.py'; then
        kill "$pid"
        i=0
        while kill -0 "$pid" 2>/dev/null; do
            i=$((i + 1))
            if [ "$i" -gt 10 ]; then
                kill -9 "$pid" 2>/dev/null || true
                break
            fi
            sleep 1
        done
    fi
    rm -f "$PIDFILE"
fi

# Start the server in the background.
(cd pilot && PILOT_PORT="$PORT" exec nohup python3 serve.py) >>"$LOGFILE" 2>&1 &
pid=$!
echo "$pid" >"$PIDFILE"

# Wait for GET /health to answer 200.
i=0
while [ "$i" -lt "$HEALTH_TIMEOUT" ]; do
    if ! kill -0 "$pid" 2>/dev/null; then
        echo "deploy: the server exited; see $LOGFILE" >&2
        rm -f "$PIDFILE"
        exit 1
    fi
    if python3 -c 'import sys, urllib.request
sys.exit(0 if urllib.request.urlopen(sys.argv[1], timeout=2).status == 200 else 1)' \
        "http://127.0.0.1:$PORT/health" 2>/dev/null; then
        echo "deploy: pilot shop healthy on port $PORT (pid $pid, $(git rev-parse --short HEAD))"
        exit 0
    fi
    i=$((i + 1))
    sleep 1
done

echo "deploy: GET /health did not answer 200 within ${HEALTH_TIMEOUT}s; see $LOGFILE" >&2
exit 1
