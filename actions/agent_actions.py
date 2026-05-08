"""
actions/agent_actions.py
────────────────────────
Defines the "action" schema that LLM agents emit as structured JSON,
plus a dispatcher that maps action names to real tool calls.

Flow:
  LLM response ──► parse_action() ──► dispatch_action() ──► tool function
"""

import json
from typing import Any
from tools import caldera_tools, code_tools, web_tools
from utils.logs import get_logger

logger = get_logger(__name__)


# ── Action schema ─────────────────────────────────────────────────────────────

class Action:
    """Represents a single structured action emitted by an LLM agent."""

    def __init__(self, name: str, parameters: dict[str, Any]):
        self.name = name
        self.parameters = parameters

    def __repr__(self) -> str:
        return f"Action(name={self.name!r}, params={self.parameters})"


# ── Parser ────────────────────────────────────────────────────────────────────

def parse_action(llm_output: str) -> Action | None:
    """
    Try to extract a JSON action block from the LLM's text output.

    The agent is prompted to wrap actions in ```json ... ``` fences.
    Returns None if no valid action is found (i.e., the agent is done
    or just providing commentary).
    """
    import re
    match = re.search(r"```json\s*(\{.*?\})\s*```", llm_output, re.DOTALL)
    if not match:
        # Also try bare JSON
        match = re.search(r"(\{[^{}]*\"action\"[^{}]*\})", llm_output, re.DOTALL)
    if not match:
        return None

    try:
        data = json.loads(match.group(1))
        action_name = data.get("action", "")
        params = data.get("parameters", {})
        if not action_name:
            return None
        return Action(name=action_name, parameters=params)
    except json.JSONDecodeError as exc:
        logger.warning(f"[Actions] JSON parse error: {exc}")
        return None


# ── Dispatcher ────────────────────────────────────────────────────────────────

ACTION_REGISTRY: dict[str, Any] = {
    # ── Caldera ──────────────────────────────────────────────────────────────
    "caldera_list_agents":       caldera_tools.list_agents,
    "caldera_list_abilities":    caldera_tools.list_abilities,
    "caldera_list_adversaries":  caldera_tools.list_adversaries,
    "caldera_list_operations":   caldera_tools.list_operations,
    "caldera_get_operation":     caldera_tools.get_operation,
    "caldera_start_operation":   caldera_tools.start_operation,
    "caldera_stop_operation":    caldera_tools.stop_operation,
    "caldera_get_results":       caldera_tools.get_operation_results,
    "caldera_create_adversary":  caldera_tools.create_adversary,

    # ── Code / Shell ─────────────────────────────────────────────────────────
    "run_shell":                 code_tools.run_shell_command,
    "run_python":                code_tools.run_python_code,
    "read_file":                 code_tools.read_file,
    "write_file":                code_tools.write_file,
    "list_directory":            code_tools.list_directory,
    "search_file":               code_tools.search_file_content,

    # ── Web ───────────────────────────────────────────────────────────────────
    "http_get":                  web_tools.http_get,
    "http_post":                 web_tools.http_post,
    "extract_links":             web_tools.extract_links,
    "extract_forms":             web_tools.extract_forms,
    "check_paths":               web_tools.check_common_paths,
    "server_info":               web_tools.get_server_info,
}


def dispatch_action(action: Action) -> Any:
    """
    Execute an action by looking it up in ACTION_REGISTRY and calling it
    with the provided parameters.

    Returns:
        Whatever the underlying tool function returns.

    Raises:
        ValueError if the action name is not recognised.
    """
    func = ACTION_REGISTRY.get(action.name)
    if func is None:
        raise ValueError(f"Unknown action: '{action.name}'.  "
                         f"Valid actions: {sorted(ACTION_REGISTRY.keys())}")
    logger.info(f"[Actions] Dispatching → {action.name}({action.parameters})")
    result = func(**action.parameters)
    logger.debug(f"[Actions] Result: {str(result)[:200]}")
    return result


def list_available_actions() -> str:
    """Return a formatted string listing all registered action names."""
    lines = ["Available actions:"]
    for name in sorted(ACTION_REGISTRY.keys()):
        func = ACTION_REGISTRY[name]
        doc = (func.__doc__ or "").strip().split("\n")[0]
        lines.append(f"  • {name:35s} — {doc}")
    return "\n".join(lines)
