"""
run_servers.py
──────────────
Starts the utility servers used during engagements:
  • HTTP server  — serves payloads/files to target machines
  • FTP server   — receives exfiltrated files

Both run as background daemon threads.

Usage:
    python run_servers.py
"""

import time
import signal
import sys
from utils.logs import get_logger
from utils.web_server import start_web_server
from utils.ftp_server import start_ftp_server

logger = get_logger(__name__)


def handle_signal(sig, frame):
    logger.info("Shutting down servers…")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info("Starting utility servers…")

    # Start HTTP file server (serves from ./payloads/)
    web_thread = start_web_server(serve_dir="payloads")

    # Start FTP server (receives files into ./ftp_root/)
    try:
        ftp_thread = start_ftp_server(serve_dir="ftp_root")
    except ImportError:
        logger.warning("pyftpdlib not installed; FTP server skipped.  pip install pyftpdlib")
        ftp_thread = None

    logger.info("Both servers running.  Press Ctrl+C to stop.")
    while True:
        time.sleep(1)
        if not web_thread.is_alive():
            logger.error("Web server died unexpectedly!")
            break


if __name__ == "__main__":
    main()
