"""
utils/constants.py
──────────────────
Central place for all constant values used across the project.
"""

# ── Agent roles ────────────────────────────────────────────────────────────────
COORDINATOR_AGENT = "coordinator"
CALDERA_AGENT     = "caldera"
CODE_AGENT        = "code"
TEXT_AGENT        = "text"

# ── Supported LLM models ───────────────────────────────────────────────────────
MODEL_LLAMA_70B  = "llama-3.3-70b-versatile"   # best quality (use this)
MODEL_LLAMA_8B   = "llama3-8b-8192"             # fastest
MODEL_MIXTRAL    = "mixtral-8x7b-32768"         # long context

# ── Caldera operation states ───────────────────────────────────────────────────
CALDERA_OP_RUNNING  = "running"
CALDERA_OP_FINISHED = "finished"
CALDERA_OP_PAUSED   = "paused"

# ── HTTP status codes (shorthand) ─────────────────────────────────────────────
HTTP_OK           = 200
HTTP_CREATED      = 201
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND    = 404

# ── Timeouts (seconds) ────────────────────────────────────────────────────────
REQUEST_TIMEOUT   = 30
AGENT_LOOP_DELAY  = 2    # seconds between agent iterations

# ── Max tokens for LLM responses ──────────────────────────────────────────────
MAX_TOKENS = 4096

# ── Log format ────────────────────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
