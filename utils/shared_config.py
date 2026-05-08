"""
utils/shared_config.py
──────────────────────
Loads .env variables once and exposes them as a typed config object
that every module can import.
"""

import os
from dotenv import load_dotenv
from utils.logs import get_logger

load_dotenv()          # reads the .env file (if it exists)
logger = get_logger(__name__)


class Config:
    """Single source of truth for all runtime configuration."""

    # ── LLM ──────────────────────────────────────────────────────────────────
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str    = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str    = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    MAX_TOKENS: int        = int(os.getenv("MAX_TOKENS", "4096"))
    MAX_ITERATIONS: int    = int(os.getenv("MAX_ITERATIONS", "10"))

    # ── Caldera ───────────────────────────────────────────────────────────────
    CALDERA_URL: str     = os.getenv("CALDERA_URL", "http://localhost:8888")
    CALDERA_API_KEY: str = os.getenv("CALDERA_API_KEY", "ADMIN123")

    # ── Internal Servers ──────────────────────────────────────────────────────
    WEB_SERVER_HOST: str = os.getenv("WEB_SERVER_HOST", "0.0.0.0")
    WEB_SERVER_PORT: int = int(os.getenv("WEB_SERVER_PORT", "8080"))
    FTP_SERVER_HOST: str = os.getenv("FTP_SERVER_HOST", "0.0.0.0")
    FTP_SERVER_PORT: int = int(os.getenv("FTP_SERVER_PORT", "2121"))

    def validate(self) -> bool:
        """Returns True if mandatory keys are present."""
        ok = True
        if not self.GROQ_API_KEY:
            logger.warning("No Groq API key found! Set GROQ_API_KEY in .env")
        return ok


# Module-level singleton — import this everywhere:
#   from utils.shared_config import config
config = Config()
