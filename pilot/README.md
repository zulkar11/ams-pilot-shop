# Pilot shop

A small service AMS monitors in its pilot: it quotes shipping for an order.

- `shop/shipping.py` — `quote(order)` returns the shipping cost of an order.
- `tests/` — `python3 -m unittest discover -s tests -t .` from this folder.
- `send_logs.py` — quotes the orders given on the command line and sends any
  error to AMS as an OpenTelemetry log record (`AMS_OTEL_URL`, `AMS_INGEST_TOKEN`).
