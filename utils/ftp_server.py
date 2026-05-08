"""
utils/ftp_server.py
───────────────────
An anonymous FTP server used to exfiltrate / receive files in
penetration test exercises.

Requires:  pip install pyftpdlib
"""

import os
import threading
from utils.shared_config import config
from utils.logs import get_logger

logger = get_logger(__name__)


def start_ftp_server(
    host: str = config.FTP_SERVER_HOST,
    port: int = config.FTP_SERVER_PORT,
    serve_dir: str = "ftp_root",
    daemon: bool = True,
) -> threading.Thread:
    """
    Start an anonymous FTP server in a background thread.

    Args:
        host:      bind address
        port:      TCP port (use 2121 to avoid needing root)
        serve_dir: root directory exposed via FTP
        daemon:    daemon thread flag

    Returns:
        The running Thread object.
    """
    try:
        from pyftpdlib.handlers import FTPHandler
        from pyftpdlib.servers import FTPServer
        from pyftpdlib.authorizers import DummyAuthorizer
    except ImportError:
        logger.error("pyftpdlib not installed.  Run:  pip install pyftpdlib")
        raise

    os.makedirs(serve_dir, exist_ok=True)

    authorizer = DummyAuthorizer()
    # Anonymous user with full permissions on serve_dir
    authorizer.add_anonymous(serve_dir, perm="elradfmwMT")

    handler = FTPHandler
    handler.authorizer = authorizer
    handler.passive_ports = range(60000, 60100)

    server = FTPServer((host, port), handler)
    logger.info(f"[FTPServer] Serving '{serve_dir}' on ftp://{host}:{port}")

    def _run() -> None:
        try:
            server.serve_forever()
        except Exception as exc:
            logger.error(f"[FTPServer] crashed: {exc}")

    thread = threading.Thread(target=_run, name="FTPServer", daemon=daemon)
    thread.start()
    return thread
