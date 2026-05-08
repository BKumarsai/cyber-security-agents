"""
tools/caldera_tools.py
──────────────────────
REST-API wrappers for MITRE Caldera.

Caldera is an open-source adversary emulation platform.
Each function maps directly to one Caldera REST endpoint.

Docs: https://caldera.readthedocs.io/en/latest/REST-API.html
"""

import requests
from typing import Any
from utils.shared_config import config
from utils.logs import get_logger
from utils.constants import REQUEST_TIMEOUT

logger = get_logger(__name__)


def _headers() -> dict[str, str]:
    return {
        "KEY": config.CALDERA_API_KEY,
        "Content-Type": "application/json",
    }


def _url(path: str) -> str:
    return f"{config.CALDERA_URL}/{path.lstrip('/')}"


# ── Agents ────────────────────────────────────────────────────────────────────

def list_agents() -> list[dict[str, Any]]:
    """Return all beacons/agents currently connected to Caldera."""
    resp = requests.get(_url("/api/v2/agents"), headers=_headers(), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    agents = resp.json()
    logger.info(f"[Caldera] {len(agents)} agent(s) connected")
    return agents


def kill_agent(paw: str) -> dict[str, Any]:
    """Send a kill instruction to a specific agent (identified by 'paw')."""
    resp = requests.delete(_url(f"/api/v2/agents/{paw}"), headers=_headers(), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    logger.info(f"[Caldera] Kill signal sent to agent {paw}")
    return resp.json()


# ── Abilities ─────────────────────────────────────────────────────────────────

def list_abilities() -> list[dict[str, Any]]:
    """Return all abilities (attack techniques) available in Caldera."""
    resp = requests.get(_url("/api/v2/abilities"), headers=_headers(), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    abilities = resp.json()
    logger.info(f"[Caldera] {len(abilities)} abilities loaded")
    return abilities


def get_ability(ability_id: str) -> dict[str, Any]:
    """Fetch a single ability by its UUID."""
    resp = requests.get(_url(f"/api/v2/abilities/{ability_id}"), headers=_headers(), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# ── Adversaries ───────────────────────────────────────────────────────────────

def list_adversaries() -> list[dict[str, Any]]:
    """Return all adversary profiles in Caldera."""
    resp = requests.get(_url("/api/v2/adversaries"), headers=_headers(), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def create_adversary(name: str, description: str, ability_ids: list[str]) -> dict[str, Any]:
    """
    Create a new adversary profile.

    Args:
        name:        human-readable profile name
        description: short description
        ability_ids: list of ability UUIDs to include
    """
    payload = {
        "name": name,
        "description": description,
        "atomic_ordering": ability_ids,
    }
    resp = requests.post(
        _url("/api/v2/adversaries"),
        headers=_headers(),
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    adversary = resp.json()
    logger.info(f"[Caldera] Created adversary '{name}' (id={adversary.get('id')})")
    return adversary


# ── Operations ────────────────────────────────────────────────────────────────

def list_operations() -> list[dict[str, Any]]:
    """Return all operations (past and present)."""
    resp = requests.get(_url("/api/v2/operations"), headers=_headers(), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def get_operation(operation_id: str) -> dict[str, Any]:
    """Fetch a single operation by ID."""
    resp = requests.get(_url(f"/api/v2/operations/{operation_id}"), headers=_headers(), timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def start_operation(
    name: str,
    adversary_id: str,
    group: str = "red",
    planner: str = "atomic",
    auto_close: bool = True,
) -> dict[str, Any]:
    """
    Start a new Caldera operation.

    Args:
        name:         operation display name
        adversary_id: UUID of the adversary profile to run
        group:        agent group to target (default 'red')
        planner:      Caldera planner (default 'atomic')
        auto_close:   automatically close when done
    """
    payload = {
        "name": name,
        "adversary": {"id": adversary_id},
        "group": group,
        "planner": {"id": planner},
        "auto_close": auto_close,
        "state": "running",
    }
    resp = requests.post(
        _url("/api/v2/operations"),
        headers=_headers(),
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    operation = resp.json()
    logger.info(f"[Caldera] Operation '{name}' started (id={operation.get('id')})")
    return operation


def stop_operation(operation_id: str) -> dict[str, Any]:
    """Stop a running operation."""
    resp = requests.patch(
        _url(f"/api/v2/operations/{operation_id}"),
        headers=_headers(),
        json={"state": "finished"},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    logger.info(f"[Caldera] Operation {operation_id} stopped")
    return resp.json()


def get_operation_results(operation_id: str) -> list[dict[str, Any]]:
    """Return all link results (command outputs) for an operation."""
    resp = requests.get(
        _url(f"/api/v2/operations/{operation_id}/links"),
        headers=_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    links = resp.json()
    logger.info(f"[Caldera] {len(links)} link(s) for operation {operation_id}")
    return links
