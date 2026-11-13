"""Quote each order given as COUNTRY:WEIGHT_KG and send any error to AMS as an
OpenTelemetry log record (OTLP/HTTP JSON).

    AMS_OTEL_URL=http://localhost:8000/v1/logs AMS_INGEST_TOKEN=... \
        python3 send_logs.py NZ:2 US:1
"""

import json
import os
import sys
import time
import traceback
import urllib.request
from pathlib import Path

from shop.shipping import quote

SERVICE = "pilot-shop"
REPO_ROOT = str(Path(__file__).resolve().parent.parent) + os.sep


def _attr(key: str, value: str) -> dict:
    return {"key": key, "value": {"stringValue": value}}


def _record(order: dict, exc: BaseException) -> dict:
    # Paths relative to the repository, as a deployed service would print them.
    stack = traceback.format_exc().replace(REPO_ROOT, "")
    return {
        "timeUnixNano": str(time.time_ns()),
        "severityNumber": 17,
        "severityText": "ERROR",
        "body": {"stringValue": f"shipping quote failed for order to {order['country']}"},
        "attributes": [
            _attr("exception.type", type(exc).__name__),
            _attr("exception.message", str(exc)),
            _attr("exception.stacktrace", stack),
        ],
    }


def main(args: list[str]) -> int:
    records = []
    for arg in args:
        country, _, weight = arg.partition(":")
        order = {"country": country, "weight_kg": float(weight or 1), "subtotal": 40.0}
        try:
            print(f"{country}: {quote(order)}")
        except Exception as exc:  # noqa: BLE001 - every failure is reported
            print(f"{country}: {type(exc).__name__}: {exc}")
            records.append(_record(order, exc))
    if not records:
        return 0
    payload = {
        "resourceLogs": [
            {
                "resource": {"attributes": [_attr("service.name", SERVICE)]},
                "scopeLogs": [{"scope": {"name": "pilot.shop"}, "logRecords": records}],
            }
        ]
    }
    request = urllib.request.Request(
        os.environ.get("AMS_OTEL_URL", "http://localhost:8000/v1/logs"),
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['AMS_INGEST_TOKEN']}",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        print(f"sent {len(records)} error record(s): HTTP {response.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
