"""HTTP server for the pilot shop, so a deployment can be checked over HTTP.

    PILOT_PORT=8765 python3 serve.py

GET /health                         -> 200 "ok"
GET /quote?country=NZ&weight_kg=2   -> 200 {"country": "NZ", "quote": 16.5}
Any exception while quoting         -> 500 "<ExceptionType>: <message>"
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from shop.shipping import quote

HOST = "127.0.0.1"
DEFAULT_PORT = 8765


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        url = urlsplit(self.path)
        if url.path == "/health":
            self._send(200, "text/plain; charset=utf-8", "ok")
        elif url.path == "/quote":
            self._quote(parse_qs(url.query))
        else:
            self._send(404, "text/plain; charset=utf-8", "not found")

    def _quote(self, query: dict) -> None:
        order = {key: values[0] for key, values in query.items()
                 if key in ("country", "weight_kg", "subtotal")}
        try:
            if "subtotal" in order:
                order["subtotal"] = float(order["subtotal"])
            body = json.dumps({"country": order["country"], "quote": quote(order)})
        except Exception as exc:  # noqa: BLE001 - every failure answers 500
            self._send(500, "text/plain; charset=utf-8", f"{type(exc).__name__}: {exc}")
            return
        self._send(200, "application/json", body)

    def _send(self, status: int, content_type: str, body: str) -> None:
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    port = int(os.environ.get("PILOT_PORT") or DEFAULT_PORT)
    server = ThreadingHTTPServer((HOST, port), Handler)
    print(f"pilot shop listening on http://{HOST}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
