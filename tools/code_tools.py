"""
tools/code_tools.py
───────────────────
Tools for executing and analysing code / shell commands safely
inside a sandboxed context.

WARNING: These tools execute real system commands.
         Use ONLY in isolated lab / CTF environments.
"""

import subprocess
import tempfile
import os
import textwrap
from utils.logs import get_logger

logger = get_logger(__name__)

# Maximum execution time per command (seconds)
EXEC_TIMEOUT = 30


def run_shell_command(command: str, timeout: int = EXEC_TIMEOUT) -> dict:
    """
    Execute a shell command and return its output.

    Args:
        command: shell command string
        timeout: max seconds to wait

    Returns:
        dict with keys: stdout, stderr, returncode
    """
    logger.info(f"[CodeTools] Running shell command: {command[:120]}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        logger.warning(f"[CodeTools] Command timed out after {timeout}s")
        return {"stdout": "", "stderr": "TimeoutExpired", "returncode": -1}
    except Exception as exc:
        logger.error(f"[CodeTools] Command error: {exc}")
        return {"stdout": "", "stderr": str(exc), "returncode": -2}


def run_python_code(code: str, timeout: int = EXEC_TIMEOUT) -> dict:
    """
    Write Python code to a temp file and execute it.

    Args:
        code:    Python source code (may be multi-line)
        timeout: max seconds to wait

    Returns:
        dict with keys: stdout, stderr, returncode
    """
    code = textwrap.dedent(code)
    logger.info(f"[CodeTools] Executing Python code ({len(code)} chars)")
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        logger.warning(f"[CodeTools] Python execution timed out after {timeout}s")
        return {"stdout": "", "stderr": "TimeoutExpired", "returncode": -1}
    except Exception as exc:
        return {"stdout": "", "stderr": str(exc), "returncode": -2}
    finally:
        os.unlink(tmp_path)


def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    logger.info(f"[CodeTools] Reading file: {path}")
    with open(path, "r", errors="replace") as fh:
        return fh.read()


def write_file(path: str, content: str) -> bool:
    """Write content to a file, creating parent dirs if needed."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    logger.info(f"[CodeTools] Writing file: {path} ({len(content)} chars)")
    with open(path, "w") as fh:
        fh.write(content)
    return True


def list_directory(path: str = ".") -> list[str]:
    """List files and directories at the given path."""
    logger.info(f"[CodeTools] Listing directory: {path}")
    entries = []
    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        tag = "/" if os.path.isdir(full) else ""
        entries.append(f"{name}{tag}")
    return entries


def search_file_content(pattern: str, path: str, recursive: bool = True) -> dict:
    """
    Search for a string pattern inside files (uses grep).

    Args:
        pattern:   search string
        path:      file or directory to search
        recursive: search sub-directories

    Returns:
        dict with stdout (matching lines) and returncode
    """
    flags = "-r" if recursive else ""
    cmd = f"grep -n {flags} '{pattern}' '{path}'"
    return run_shell_command(cmd)
