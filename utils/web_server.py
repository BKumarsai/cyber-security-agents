"""
utils/web_server.py
───────────────────
A lightweight HTTP server used by agents to serve payloads / files
to target machines during a penetration test exercise.

Usage:
    python run_servers.py          # starts both web + ftp servers
"""

import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from utils.shared_config import config
from utils.logs import get_logger

logger = get_logger(__name__)


class SilentHandler(SimpleHTTPRequestHandler):
    """Same as SimpleHTTPRequestHandler but logs via our logger."""

    def log_message(self, fmt: str, *args) -> None:  # type: ignore[override]
        logger.info(f"[WebServer] {fmt % args}")

    def log_error(self, fmt: str, *args) -> None:  # type: ignore[override]
        logger.error(f"[WebServer] {fmt % args}")


def start_web_server(
    host: str = config.WEB_SERVER_HOST,
    port: int = config.WEB_SERVER_PORT,
    serve_dir: str = "payloads",
    daemon: bool = True,
) -> threading.Thread:
    """
    Start a simple HTTP file server in a background thread.

    Args:
        host:      bind address
        port:      TCP port
        serve_dir: directory whose files will be served (created if missing)
        daemon:    make the thread a daemon so it dies with the main process

    Returns:
        The running Thread object.
    """
    os.makedirs(serve_dir, exist_ok=True)
    os.chdir(serve_dir)

    server = HTTPServer((host, port), SilentHandler)
    logger.info(f"[WebServer] Serving '{serve_dir}' on http://{host}:{port}")

    def _run() -> None:
        try:
            server.serve_forever()
        except Exception as exc:
            logger.error(f"[WebServer] crashed: {exc}")

    thread = threading.Thread(target=_run, name="WebServer", daemon=daemon)
    thread.start()
    return thread
