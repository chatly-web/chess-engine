"""Loopback-only access page. Run with --file /private/path/allowlist.json."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import urlsplit
import webbrowser

from live_allowlist import read_usernames, update_usernames


def make_server(path, port=0):
    nonce = secrets.token_urlsafe(32)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, status, data, mime="application/json"):
            body = data.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", mime + "; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(body)

        def authorized(self):
            # Host verification also prevents DNS rebinding to this loopback service.
            return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}" and urlsplit(self.path).path.startswith(f"/{nonce}/")

        def do_GET(self):
            if not self.authorized():
                return self.send(403, '{"error":"Open the link from Manage Bot Access.command."}')
            route = urlsplit(self.path).path
            if route == f"/{nonce}/":
                return self.send(200, Path(__file__).with_name("access.html").read_text(), "text/html")
            if route == f"/{nonce}/users":
                try:
                    return self.send(200, json.dumps({"users": read_usernames(path)}))
                except (OSError, ValueError):
                    return self.send(503, '{"error":"Cannot read the access list. No changes were made."}')
            self.send(404, '{}')

        def do_POST(self):
            origin = f"http://127.0.0.1:{self.server.server_port}"
            if not self.authorized() or self.headers.get("Origin") != origin or self.headers.get("X-Access-Manager") != "1":
                return self.send(403, '{"error":"Open the local access page to make changes."}')
            route = urlsplit(self.path).path
            action = route.removeprefix(f"/{nonce}/")
            if action not in {"add", "remove"}:
                return self.send(404, '{}')
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 1024:
                    raise ValueError("Request is too large or empty.")
                data = json.loads(self.rfile.read(size))
                name = data.get("username") if isinstance(data, dict) else None
                if not isinstance(name, str):
                    raise ValueError("Enter a username.")
                names = update_usernames(path, name.strip(), remove=action == "remove")
                self.send(200, json.dumps({"users": names}))
            except ValueError as exc:
                self.send(400, json.dumps({"error": str(exc)}))
            except OSError:
                self.send(503, '{"error":"Cannot save the access list. Check the file and try again."}')

    server = HTTPServer(("127.0.0.1", port), Handler)
    server.timeout = 1
    return server, f"http://127.0.0.1:{server.server_port}/{nonce}/"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--ready-file", type=Path)
    args = parser.parse_args()
    read_usernames(args.file)
    server, url = make_server(args.file, args.port)
    if args.ready_file:
        args.ready_file.write_text(json.dumps({"url": url, "pid": __import__("os").getpid()}))
        args.ready_file.chmod(0o600)
    print("Bot access page: " + url, flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
