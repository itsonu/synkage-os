"""Local HTTP server for the mock pages, and a headless session with a throwaway profile."""

import functools
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGES = Path(__file__).resolve().parent / "mock_pages"
ROUTES = {"/whatsapp/": "whatsapp.html", "/mail/": "gmail.html", "/mail-broken/": "gmail.html"}


class MockHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        page = next((f for prefix, f in ROUTES.items() if path.startswith(prefix)), None)
        if page is None:
            self.send_error(404)
            return
        body = (PAGES / page).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def start_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(MockHandler, directory=str(PAGES)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"
