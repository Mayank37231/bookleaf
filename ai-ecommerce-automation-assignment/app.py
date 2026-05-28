import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from automation_engine import DATA_DIR, result_to_dict, run_demo, run_ticket


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            return self._send_file(STATIC_DIR / "index.html", "text/html")
        if path == "/api/demo":
            return self._send_json({"results": [result_to_dict(item) for item in run_demo()]})
        if path == "/api/tickets":
            with (DATA_DIR / "tickets.json").open("r", encoding="utf-8") as file:
                return self._send_json({"tickets": json.load(file)})
        if path.startswith("/static/"):
            file_path = STATIC_DIR / path.replace("/static/", "", 1)
            content_type = "text/css" if file_path.suffix == ".css" else "application/javascript"
            return self._send_file(file_path, content_type)
        return self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/analyze":
            return self._send_json({"error": "Not found"}, status=404)

        length = int(self.headers.get("content-length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        ticket = {
            "ticket_id": payload.get("ticket_id") or "LIVE-001",
            "customer_email": payload.get("customer_email") or "",
            "message": payload.get("message") or "",
        }
        if not ticket["message"].strip():
            return self._send_json({"error": "message is required"}, status=400)
        return self._send_json(result_to_dict(run_ticket(ticket)))

    def _send_file(self, file_path, content_type):
        if not file_path.exists():
            return self._send_json({"error": "Not found"}, status=404)
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload, status=200):
        content = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main():
    try:
        server = ThreadingHTTPServer(("127.0.0.1", 8088), Handler)
        print("Demo running at http://127.0.0.1:8088")
        server.serve_forever()
    except Exception as error:
        (BASE_DIR / "server.err").write_text(f"{type(error).__name__}: {error}\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
